#!/usr/bin/env python3
"""Enrich the mined bullet bank: data/bullets.tsv -> data/bullets.json

The TSV carries only what had to be mined (org, useCount, lastUsed, source, text).
Everything else is derived HERE so the rules live in git where Hannah can edit them,
and so the dashboard and this script stay in sync from one source of truth.

Rule sources (quoted verbatim in comments where they matter):
  - resume-subskill.md  -> format rules, the Ten Rules, bullet mechanics
  - aislop/SKILL.md     -> the 14 slop categories and their kill lists
  - hannah-profile.md   -> employment status (Walmart ENDED 2026)

Usage: python3 scripts/enrich.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stories as story_table  # noqa: E402  (needs sys.path above)

ROOT = Path(__file__).resolve().parent.parent
TSV = ROOT / "data" / "bullets.tsv"
OUT = ROOT / "data" / "bullets.json"

# --------------------------------------------------------------------------
# Taxonomy: skills + archetypes. Keyword-driven so it is auditable and instant.
# --------------------------------------------------------------------------
SKILLS = {
    "ml-ranking":        ["ranking", "buybox", "buy box", "relevance", "machine learning", "ml system", "model"],
    "experimentation":   ["a/b", "experiment", "lift", "conversion rate", "feature testing", "guardrail"],
    "0-to-1":            ["0-to-1", "0 to 1", "0→1", "launch", "founding", "incubat", "prototype", "first hire", "from scratch"],
    "adoption":          ["adoption", "rollout", "rolled out", "enablement", "onboard", "adopted"],
    "agents-llm":        ["agent", "llm", "genai", "gen ai", "chatbot", "eval", "prompt", "ai assistant", "claude"],
    "analytics":         ["sql", "python", "dashboard", "reporting", "data analysis", "kpi", "analytics"],
    "marketplace":       ["marketplace", "seller", "offer", "gmv", "add-to-cart", "shopper", "ecommerce", "ecomm"],
    "stakeholder":       ["stakeholder", "cross-functional", "executive", "leadership", "vp", "c-suite"],
    "growth":            ["growth", "conversion", "funnel", "retention", "engagement", "acquisition"],
    "strategy":          ["strategy", "roadmap", "positioning", "market analysis", "competitive", "thesis", "gtm"],
    "ops-process":       ["operating", "process", "workflow", "playbook", "planning", "allocation", "churn", "tracking"],
    "revenue":           ["revenue", "pricing", "monetization", "ltv", "subscription", "freemium", "capital", "raised", "fundrais"],
    "customer-research": ["interview", "customer research", "user research", "pain point", "segment", "discovery"],
    "data-labeling":     ["labeling", "labelling", "human-in-the-loop", "training data", "annotat"],
}

ARCHETYPES = {
    "ecomm-marketplace": ["marketplace", "seller", "offer", "gmv", "shopper", "add-to-cart", "ecommerce", "retail", "buybox"],
    "ai-native":         ["agent", "llm", "genai", "gen ai", "eval", "prototype", "claude", "ai "],
    "platform-ml":       ["ml", "ranking", "platform", "pipeline", "upstream", "api", "data contract"],
    "enterprise-b2b":    ["enterprise", "b2b", "stakeholder", "adoption", "enablement", "internal tool", "org"],
    "ops-generalist":    ["operating", "chief of staff", "process", "planning", "allocation", "workflow", "reporting"],
    "consumer-growth":   ["consumer", "shopper", "growth", "conversion", "funnel", "engagement", "customer experience"],
}

# --------------------------------------------------------------------------
# aislop: the encodable categories. Each entry is (category, [literal phrases]).
# Judgment-only categories (8 template phrasing, 10 jargon grounding,
# 9 missing "so what", 14f rhetorical claims) are NOT here -- they need the LLM
# pass at Final Check and would false-positive as regex.
# --------------------------------------------------------------------------
SLOP = {
    "passive-framing":  ["was responsible for", "helped to", "contributed to", "assisted with",
                         "played a role in", "was involved in"],
    "corporate-filler": ["partnered with", "collaborated with", "worked closely with",
                         "engaged stakeholders", "aligned teams", "drove alignment",
                         "fostered collaboration"],
    "vague-scope":      ["large-scale", "significant impact", "major initiative", "various projects",
                         "numerous", "multiple stakeholders", "key metrics"],
    "adverb-stuffing":  ["effectively", "strategically", "proactively", "seamlessly", "holistically",
                         "successfully", "significantly", "substantially", "autonomously"],
    "bland-verb":       ["managed", "oversaw", "handled", "utilized", "ensured", "facilitated",
                         "coordinated", "maintained"],
    "hedging":          ["helped drive", "played a key role in", "was instrumental in",
                         "contributed to the success of", "supported the launch of"],
    # 14b honesty rule: "used daily by X" is a specific empirical claim that can be
    # challenged. Prefer org-scale ("across our 200+ person org") over usage frequency.
    "usage-overclaim":  ["used daily by", "daily by", "every day by", "uses it daily"],
    "kill-list":        ["leveraged", "spearheaded", "orchestrated", "synergized", "operationalized",
                         "fostered", "empowered", "championed", "endeavored", "best-in-class",
                         "world-class", "cutting-edge", "transformative", "impactful", "actionable",
                         "holistic", "seamless", "robust", "superpower", "entities"],
}

# 14c -- adjectives the number already implies
ADJ_IMPLIED = [
    (re.compile(r"\bbankable\b", re.I),               "bankable beside a $ figure"),
    (re.compile(r"\bsignificant\s+\$", re.I),         "significant beside a $ figure"),
    (re.compile(r"\$[\d.,]+[MBK]?\+?\s*(AUM)\b", re.I), "AUM after a $ figure"),
]
# 13 -- preposition imprecision: capital comes FROM people, not ACROSS them
PREP_IMPRECISE = re.compile(r"\$[\d.,]+[MBK]?\+?\s+across\s+\d[\d,]*\+?\s*(investors|lps|backers)", re.I)

NUM = re.compile(r"(~?\$?\d[\d,.]*\s?(?:%|M\+?|B\+?|K\+?|x\b)|\$\d[\d,.]*|\+\d+\.?\d*%|\b\d{2,}\+?\b)")
# Walmart ended 2026 -> present tense on Walmart bullets is blocking.
WALMART_PRESENT = re.compile(r"\b(owns|leads|builds|ships|manages|is responsible)\b", re.I)
BERKELEY_EMAIL = re.compile(r"berkeley\.edu", re.I)
COURSEWORK = re.compile(r"^\s*(select\s+)?coursework\s*:", re.I)
COMMUNITY = re.compile(
    r"congress|testif|cnn|forbes|fox|nonprofit|advocacy|campus|summit|diplomacy|"
    r"alumni chapter|hanukkah|philanthrop|student (safety|leaders)",
    re.I,
)


def tags(text: str, table: dict) -> list:
    low = text.lower()
    return sorted({k for k, words in table.items() if any(w in low for w in words)})


def slop_flags(text: str) -> list:
    low = text.lower()
    out = []
    for cat, phrases in SLOP.items():
        hits = [p for p in phrases if p in low]
        # bland verbs only count as the OPENING verb; "managed" mid-sentence is often fine
        if cat == "bland-verb":
            first = low.split()[0].strip(",;:") if low.split() else ""
            hits = [p for p in hits if p == first]
        if hits:
            out.append({"category": cat, "hits": hits[:4]})
    for rx, why in ADJ_IMPLIED:
        if rx.search(text):
            out.append({"category": "adjective-number-implies", "hits": [why]})
    if PREP_IMPRECISE.search(text):
        out.append({"category": "preposition-imprecision",
                    "hits": ["capital comes *from* investors, not *across* them"]})
    return out


def main() -> int:
    raw = TSV.read_text(encoding="utf-8")
    records, anomalies = [], []
    seen = {}

    for line in raw.split("\n"):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 5:
            anomalies.append({"type": "malformed-row", "text": line[:120]})
            continue
        org, use_count, last_used, source, text = parts

        # FIX 2: several bullets merged onto one line in the 2022 resume -- split them.
        pieces = [p.strip() for p in re.split(r"\s*●\s*", text) if p.strip()]
        for piece in pieces:
            if len(piece) < 40:
                continue

            # FIX 1: detect a spliced bullet (damage in the SOURCE doc, not the parse).
            # Signature: a lowercase run glued to a capitalised sentence start mid-word.
            if re.search(r"[a-z]{3}[A-Z][a-z]+ed\b.*\b[a-z]{2,}ics\b", piece) or \
               re.search(r"\b\w+[a-z](?=[A-Z][a-z]{4,})", piece) and piece.count("  ") == 0 and \
               re.search(r"[a-z]{4}(Streamlined|Deployed|Improved|Designed|Launched)", piece):
                anomalies.append({"type": "spliced-bullet-in-source", "source": source,
                                  "org": org, "text": piece[:240]})

            section = "bullet"
            bucket = org
            # FIX 3: coursework is education metadata, not an achievement bullet.
            if COURSEWORK.match(piece):
                section = "coursework"
            # FIX 4: community/advocacy inherited the preceding project org -- give it its own.
            elif org in ("aiprojects", "misc", "edu_berkeley") and COMMUNITY.search(piece):
                bucket = "community"

            key = re.sub(r"[^a-z0-9%$+. ]", " ", piece.lower())
            key = re.sub(r"\s+", " ", key).strip()
            if key in seen:
                seen[key]["useCount"] += int(use_count)
                continue

            flags = []
            if bucket == "walmart" and (WALMART_PRESENT.search(piece)
                                        or "2024–present" in piece.lower()
                                        or "2024-present" in piece.lower()):
                flags.append("walmart-present")          # blocking: role ended 2026
            if BERKELEY_EMAIL.search(piece):
                flags.append("berkeley-email")           # blocking: always hbschlac@gmail.com
            low = piece.lower()
            if "gmv" in low and "$400m" not in low and \
               piece.split()[0].lower() in ("owned", "shipped", "drove", "delivered"):
                flags.append("gmv-headline")             # warning: charter leads, GMV supports

            story_id, story_score = story_table.assign(piece, bucket)
            rec = {
                "id": f"{bucket}-{hashlib.md5(key.encode()).hexdigest()[:8]}",
                "experienceId": bucket,
                # Which of the ~5-10 real accomplishments this is a telling of. The bank is
                # browsed by story; the variants underneath are interchangeable wordings.
                "storyId": story_id,
                "storyScore": story_score,
                "section": section,
                "text": piece,
                "verb": piece.split()[0].strip(",;:") if piece.split() else "",
                "metrics": [m if isinstance(m, str) else m[0] for m in NUM.findall(piece)][:6],
                "hasMetric": bool(NUM.search(piece)),
                "chars": len(piece),
                # 2-line rule proxy; calibrate against real wrap before trusting (see plan).
                "estLines": 1 if len(piece) <= 105 else (2 if len(piece) <= 215 else 3),
                "skills": tags(piece, SKILLS),
                "archetypes": tags(piece, ARCHETYPES),
                "useCount": int(use_count),
                "lastUsed": last_used,
                "current": last_used >= "2026-08-01",
                "source": source,
                "flags": flags,
                "slop": slop_flags(piece),
            }
            seen[key] = rec
            records.append(rec)

    records.sort(key=lambda r: (r["experienceId"], -r["useCount"], -r["chars"]))
    OUT.write_text(json.dumps({"bullets": records, "anomalies": anomalies,
                               "stories": story_table.catalog()},
                              ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"bullets: {len(records)}")
    print("by experience:", dict(Counter(r["experienceId"] for r in records).most_common()))
    print("by section   :", dict(Counter(r["section"] for r in records).most_common()))
    print(f"current (Aug 2026+): {sum(1 for r in records if r['current'])}")
    print(f"with metric        : {sum(1 for r in records if r['hasMetric'])}")
    print(f"clean of slop      : {sum(1 for r in records if not r['slop'])}")
    print("slop categories:", dict(Counter(
        s["category"] for r in records for s in r["slop"]).most_common()))
    print("blocking flags :", dict(Counter(
        f for r in records for f in r["flags"]).most_common()))
    unfiled = [r for r in records if r["storyId"].endswith("-other")]
    per_exp = Counter(r["experienceId"] for r in records)
    print(f"stories        : {sum(len(v) for v in story_table.STORIES.values())} named")
    for exp, n in per_exp.most_common():
        named = len(story_table.STORIES.get(exp, []))
        o = sum(1 for r in unfiled if r["experienceId"] == exp)
        print(f"   {exp:14s} {n:4d} variants -> {named:2d} stories"
              + (f"   ({o} unfiled)" if o else ""))
    print(f"unfiled        : {len(unfiled)} ({100*len(unfiled)/max(len(records),1):.1f}%)"
          "  <- if this grows, add a story, don't lower MIN_SCORE")
    print(f"anomalies      : {len(anomalies)}")
    for a in anomalies[:5]:
        print(f"   [{a['type']}] {a.get('source','')}: {a.get('text','')[:110]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
