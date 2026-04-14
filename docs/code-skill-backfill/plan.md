# Code Skill Backfill — Revised Plan

## Context

`SKILL.md` for the Code skill loads into every Claude invocation at nonzero
context cost. The prior plan proposed 15 learnings consolidated from 27 raw
patterns, but the bullets skewed toward generic React/JS wisdom (useEffect
cleanup, env var validation) that any competent dev — or Claude — already
gets right. Burning tokens on textbook advice is net-negative; the skill only
pays rent if it captures **things Claude specifically gets wrong** in Hannah's
repos.

This revision reorders the backfill around Claude's actual process failures,
tightens evidence standards, bounds the mining cost, and adds a post-write
sanity check so we know the learnings actually load.

**Scope:** retrospective backfill only. No rubric calibration — we have zero
scored parallel runs, so any weight change would be fabrication.

---

## The 10 Fixes (what changes vs. the prior plan)

| # | Fix | Where it lands below |
|---|-----|----------------------|
| 1 | Lead with Claude process failures, not generic code hygiene | §3 ordering |
| 2 | Show raw 27 → deduped → final 12 mapping in the plan itself | §2 |
| 3 | Every bullet carries commit SHA or `summary:filename.md` anchor | §3 citation format |
| 4 | Concrete failure-mode phrasing, not generic advice | §3 style rules |
| 5 | Explicit do-not-learn list (UI churn, pivots, aesthetic reversals) | §4 |
| 6 | Rubric is frozen; backfill cannot touch weights | §5 |
| 7 | External-repo scans bounded by `--since` + `--max-count=50` | §6 |
| 8 | Session-summary mining is backfill-only, not recurring | §6 |
| 9 | Repo-level CLAUDE.md overrides cross-repo SKILL.md | §7 |
| 10 | Post-write sanity test: run one dev task, verify a rule fires | §8 |

---

## 1. Target output

- **File:** `SKILL.md` (Code skill)
- **Cap:** ~12 bullets on this first backfill pass (err tight; the weekly
  Sunday sync grows it from here)
- **Structure:**
  - §A. Claude process failures (5–7 bullets) — highest-value, non-obvious
  - §B. Concrete code-level patterns (5–7 bullets) — cross-repo first
- **Citation format per bullet:** `(N citations: <sha-or-summary-anchor>, ...)`
  - Git evidence: short SHA + 1-line commit subject, e.g. `a1b2c3d "fix Libby poll crash on null hold"`
  - Summary evidence: `summary:2026-03-14-muse-checkout.md`
  - Cross-repo tagged: `[schlacter.me]`, `[kindle]`, `[muse]`, `[hbschlac]`

---

## 2. Raw-pattern audit trail (must appear in this plan before writing SKILL.md)

Populate these three blocks during execution. Do not proceed to §3 until all
three are filled in this file.

### 2a. Raw 27 patterns (unabridged)
```
1. [repo] <short SHA> — <one-line pattern description>
2. ...
...
27. ...
```

### 2b. Dedupe trail
```
{1, 5, 19} → merged: "<consolidated phrasing>"   — reason: same root cause (X)
{3, 11}    → merged: "<consolidated phrasing>"   — reason: ...
{7}        → dropped                              — reason: UI/aesthetic churn (see §4)
{22}       → dropped                              — reason: product pivot, not a failure
...
```

### 2c. Final 12 (with the §A/§B split)
```
§A process failures:  [indices from 2a]
§B code patterns:     [indices from 2a]
```

This is what makes the consolidation auditable. Hannah should be able to
click any final bullet, trace it back to its raw-pattern indices, and follow
those to commits.

---

## 3. The 12 bullets — format, ordering, and style

### §A. Claude process failures (lead here — 5–7 bullets)

These are the non-obvious ones that justify the skill's existence. Examples of
the *kind* of failure that belongs here (final wording determined by §2
evidence, not guessed in this plan):

- **Recursive skill invocation.** Do not call `Skill()` from inside a
  scheduled task or hook body — it re-triggers on the next tick and loops
  until rate-limit. Concrete: *"scheduled sync called the sync skill, which
  re-scheduled itself"* → cite the actual commit.
- **Client-side secret leakage.** API tokens referenced in `NEXT_PUBLIC_*` or
  imported into a `"use client"` module ship to the browser. Cost: credential
  rotation + disclosure. Cite the actual commit that fixed it.
- **"Done" declared before tests run.** After editing, run the test/lint
  command the repo actually uses; do not claim completion based on "code
  compiles" or "looks right."
- **Merge-conflict code loss.** When resolving conflicts, diff against both
  parents before committing — prior fixes have been silently dropped.
- **Destructuring unverified responses.** KV/API reads may return `undefined`;
  render `<EmptyState />` or early-return, do not `const { foo } = res` at the
  top of a component. Cost of getting wrong: full-page crash.

Each final bullet must end with `(N citations: ...)` per §1 format.

### §B. Concrete code-level patterns (5–7 bullets, cross-repo first)

Cross-repo evidence (≥2 repos) sorts above single-repo. Example shape:

- **Gmail/Libby poll loops need idempotency keys.** Without one, retries
  double-create holds/receipts. Cross-repo ×2: `[kindle]`, `[muse]`.

### Style rules for every bullet

- **Concrete, not generic.** ❌ "guard nullable data with a fallback UI."
  ✅ "KV GET returning `null` must render `<EmptyState />`, not destructure."
- **Name the cost.** Every bullet says what breaks when the rule is violated
  (crash / leak / data loss / loop / silent regression).
- **Imperative voice, ≤2 sentences.**
- **No bullet without a citation.** If you can't cite ≥1 commit or summary,
  the pattern isn't backfill-ready — defer to the sync.

---

## 4. Do-not-learn list (explicit exclusions)

Drop these from §2b even if they appear in the 27:

- UI/styling churn (colors, spacing, copy tweaks)
- Aesthetic reversals (Hannah changed her mind — sage → terracotta → sage)
- Product pivots (feature added, feature removed — the add isn't a "rule")
- One-off debugging that didn't generalize
- Anything already covered by the repo's own CLAUDE.md (see §7)

Mark each exclusion in §2b with the reason so the trail is auditable.

---

## 5. Rubric discipline

**The 100-pt rubric is frozen for this backfill.** Do not adjust weights.

Rationale: rubric weights are calibrated from scored parallel runs (same task,
rubric on vs. off, compare outcomes). We have zero such runs. Retrospective
git-diff mining tells us what Claude got wrong — it does not tell us how much
weight a rule should carry relative to others. Defer all weight changes until
≥5 scored parallel runs exist.

If during mining a pattern feels weight-worthy, note it in a separate
`rubric-candidates.md` — do not edit the rubric from this plan.

---

## 6. Mining sources (bounded)

| Source | Scope | Bound | Recurring? |
|---|---|---|---|
| 1. `hbschlac/hbschlac` recent diffs | since last sync | `--max-count=100` | yes (weekly sync) |
| 2. `hbschlac/hbschlac` since last sync | since last sync | `--max-count=100` | yes |
| 5. Cross-repo: `schlacter.me`, `libby-hold-monitor` (Kindle), `muse-shopping` | **since last sync date** | **`--max-count=50` per repo** | yes |
| 6. Session summaries | all existing | — | **backfill-only; drop from weekly sync** |

Rationale for each bound:

- **Source 5 cap.** The prior plan said "scan recent commits in 5 repos" with
  no window. That's unbounded. Match Source 2's `since last sync` and add a
  hard `--max-count=50` per repo so a noisy repo can't dominate.
- **Source 6 is backfill-only.** Session summaries rarely surface failures
  that git diffs miss; re-reading them every Sunday is expensive redundancy.
  After this backfill, drop them from the weekly sync entirely.

---

## 7. Precedence: repo CLAUDE.md beats cross-repo SKILL.md

State this explicitly in `SKILL.md` header:

> If a repo's `CLAUDE.md` contradicts a rule here, the repo rule wins. This
> file captures cross-repo patterns; per-repo rules override.

Before adding any bullet, grep each repo's CLAUDE.md — if the rule is already
there, drop the bullet (it's not cross-repo, it's single-repo already
handled).

---

## 8. Post-write sanity test

After writing `SKILL.md`, verify the learnings actually load and fire:

1. Pick one real pending dev task from any of the 4 repos (e.g. a known bug
   ticket or a small feature).
2. Start a fresh Claude session on that task.
3. Observe: does Claude reference at least one of the §A or §B bullets, or
   avoid a pattern listed there?
4. If no rule fires and the task was in-scope for the skill, the learnings
   aren't loading — debug the skill registration before declaring the
   backfill done.

Record the test task + outcome at the bottom of `SKILL.md` as a changelog
entry: `YYYY-MM-DD backfill sanity test: <task> — <rule(s) fired>`.

---

## 9. Critical files

| Path | Action |
|---|---|
| `SKILL.md` (Code skill location — confirm path during execution) | rewrite |
| `rubric-candidates.md` (new, sibling to SKILL.md) | create, empty-ish |
| Each repo's `CLAUDE.md` (4 repos) | **read only** — for precedence check in §7 |
| `/root/.claude/plans/parsed-petting-frost.md` (this file) | update §2 with raw trail before §3 |

---

## 10. Durable versioning: `~/.claude/` → GitHub

Nothing touched this session (SKILL.md, run logs, this plan, MEMORY.md) lives
in an existing git repo — `~/.claude/` isn't tracked. Before the backfill
lands there's no rollback path. Fix this by turning `~/.claude/` into a git
repo and pushing to a new GitHub remote.

### 10a. Pre-flight sanity

Before `git init`, audit what's inside `~/.claude/`:

```
~/.claude/
  skills/        → yes, version
  memory/        → yes, version (MEMORY.md etc.)
  plans/         → yes, version
  settings.json  → yes, version
  settings.local.json → **exclude via .gitignore** (local-only, may hold keys)
  credentials/, *.token, *.key, .env* → **exclude via .gitignore**
  projects/ (session transcripts) → **exclude** (large, chatty, low value)
  statsig/, cache/, *.log → **exclude**
```

Write a `.gitignore` that allowlists `skills/`, `memory/`, `plans/`,
`settings.json`, `CLAUDE.md`, and denies everything else (`*` then
`!<allowed>`). Safer than blocklist.

### 10b. Secret scan before first commit

Run a local secret scan (`gitleaks detect` or equivalent) on the staged tree
before the initial commit. If any hit, fix the `.gitignore` — do not commit
and clean up after.

### 10c. Remote + push

Once the account/org, repo name, and visibility are confirmed (see §11):

1. `git init` in `~/.claude/`
2. Write `.gitignore` per §10a; `git add` only allowlisted paths
3. Secret scan per §10b
4. Initial commit: `init: claude config, skills, memory, plans`
5. Create GitHub repo via `mcp__github__create_repository` (private unless
   told otherwise)
6. `git remote add origin <url>` then `git push -u origin main`

### 10d. Ongoing hygiene

- After the backfill lands, commit + push as a second commit so the diff
  between "pre-backfill" and "post-backfill" SKILL.md is inspectable.
- Consider a `post-commit` hook later that warns on staged files matching
  `*token*|*key*|*.env*` — not in scope for this plan.

---

## 11. Versioning repo — confirmed answers

- **Owner:** `hbschlac`
- **Repo name:** `claude-config`
- **Visibility:** **private**
- **Remote URL (post-create):** `git@github.com:hbschlac/claude-config.git`
  (or `https://...` per local auth setup)

---

## 12. Evals — does the skill actually work?

§8 is N=1 ("did one rule fire on one task"). That's a smoke test, not an
eval. To call this skill validated we need:

### 12a. Holdout-commit eval (offline, run once at backfill)
- **Setup:** reserve the **most recent 10 commits NOT used in mining** as a
  holdout (e.g., bump `--since` window back by 2 weeks for mining; the last 2
  weeks become holdout).
- **For each holdout commit that fixes a bug or removes bad code:** ask "would
  any rule in §A or §B have caught this in the diff before commit?"
- **Pass bar:** ≥40% catch rate. Lower → rules are too narrow or wrong-shape.
  Higher → rules may be overfit to the mining window (re-check generalization).
- **Record results in `/root/.claude/plans/eval-holdout-<date>.md`.**

### 12b. Live-task eval (online, ≥5 tasks before declaring success)
- Generalize §8 from N=1 to **N=5 fresh dev tasks** across ≥2 of the 4 repos.
- For each task, log: which rules fired, which rules *should have* fired but
  didn't, any rule that fired *incorrectly* (over-application).
- Aggregate: precision (fired & relevant) and recall (relevant & fired).
- Pass bar: precision ≥80%, recall ≥50%. Below either → revisit phrasing.

### 12c. Token-budget eval
- Measure: tokens added by SKILL.md per invocation (e.g., via tokenizer on
  the file).
- **Hard cap: 1,500 tokens.** Soft cap: 1,000.
- If §A+§B exceeds, drop lowest-citation-count bullets first.
- Record measured token count in the SKILL.md changelog.

### 12d. Citation-validity lint (continuous)
- Pre-commit hook on `claude-config`: every `<sha>` in SKILL.md must resolve
  via `git -C <repo-path> cat-file -e <sha>^{commit}` for the cited repo.
- If any citation fails (squashed, rebased, force-pushed away), CI flags it
  and the rule must be re-anchored or dropped.
- Stale-citation = rotting evidence. Don't tolerate it silently.

### 12e. Stale-rule audit (quarterly)
- Each rule must cite ≥1 commit from the past 6 months OR be re-justified by
  a freshly-mined example.
- Otherwise: drop. The skill is for active patterns, not lore.

### 12f. Cross-skill conflict scan
- Before publishing SKILL.md, grep other loaded skills for overlapping/
  contradicting rules. If overlap exists, declare the precedence explicitly
  in this skill's header (or remove the duplicate).

---

## 13. Guardrails & edge cases

### 13a. Self-fulfilling-prophecy detection
A rule whose only evidence is "we stopped doing X after we added this rule"
is unfalsifiable — it looks "right" because nothing tests it anymore. Tag
such rules with `[unfalsifiable: re-validate]` and revisit at the quarterly
audit. Don't let entrenched rules hide.

### 13b. Workaround-vs-root-cause check
Before adding a rule, ask: "is this a real pattern, or is it a band-aid for a
deeper bug we haven't fixed?" Workarounds belong in repo CLAUDE.md, not in
cross-repo SKILL.md. The skill is for *patterns*, not *symptoms*.

### 13c. Author filter on mining
Mining commits should filter to **authors == Hannah OR `claude[bot]` OR
Claude's local commit identity**. Exclude PRs from outside contributors —
their patterns aren't Claude's failures, and learning from them muddies
attribution.

### 13d. Work/personal firewall
**No Walmart / internal session content enters SKILL.md.** Tag-list of
allowed personal repos (`hbschlac/hbschlac`, `schlacter.me`,
`libby-hold-monitor`, `muse-shopping`); session summaries from anything else
are excluded from mining by default. State this in §6 mining preflight.

### 13e. PII / secret scan on the SKILL.md text itself
Run `gitleaks detect` on SKILL.md before each commit, not just on the repo
init. Commit subjects sometimes include API URLs, customer names, or test
emails. Failing scan = block commit, not warn.

### 13f. Conflict-resolution policy for the weekly sync
When the Sunday sync proposes a new rule that contradicts an existing rule,
**both go to a `conflicts.md` queue for explicit Hannah review** — never
silently overwrite. Auto-resolution = drift.

### 13g. Sync rate-limit
If the weekly sync proposes >3 new rules in one week, halt and require
manual review. >3 = either a noisy week (refactor, dependency upgrade) or
the mining bounds in §6 are too loose.

### 13h. Repo-set drift
Maintain `mining-repos.txt` (list of cross-repo sources). When a repo is
archived, renamed, or added, update this file in the same commit. §6 reads
from it; nothing is hard-coded in the skill.

### 13i. Stale local clones
Source 5 mining must run `git fetch --all` per repo first. Stale clone =
false negatives = silently missed patterns.

### 13j. Negative examples per rule
Every rule should optionally include a 1-line "DOES NOT apply when…" so
Claude's rule application has an off-switch. Without it, rules over-fire.
Example: "Idempotency keys for poll loops — *does not apply to read-only
queries*."

### 13k. Disaster recovery
Document in `claude-config/README.md`: where the canonical copy lives
(`~/.claude/` + GitHub `hbschlac/claude-config`), how to restore from
GitHub if `~/.claude/` is wiped, and how to re-bootstrap on a new machine.

### 13l. Spec/version pinning
Note in SKILL.md header which Claude model + Skill spec version this file
was authored against (e.g., `Authored: Claude Opus 4.6, Skill spec v1.x`).
If the spec changes, the format may need migration.

---

## 14. Additional manager-recommended fixes (extending the original 10)

| # | Fix | Section |
|---|-----|---------|
| 11 | Hard token-budget cap (1,500 tokens) on SKILL.md | §12c |
| 12 | Holdout-commit eval at backfill, ≥40% catch rate | §12a |
| 13 | Live-task eval over N=5 tasks before declaring success | §12b |
| 14 | Citation-validity lint (pre-commit) | §12d |
| 15 | Stale-rule quarterly audit | §12e |
| 16 | Cross-skill conflict scan before publish | §12f |
| 17 | Self-fulfilling-prophecy tag | §13a |
| 18 | Workaround-vs-root-cause check before adding rule | §13b |
| 19 | Author filter on mining (Hannah / `claude[bot]` only) | §13c |
| 20 | Work/personal firewall — explicit allowed-repo list | §13d |
| 21 | gitleaks scan on SKILL.md text per commit | §13e |
| 22 | Conflict queue (`conflicts.md`) instead of silent overwrite | §13f |
| 23 | Sync rate-limit (>3 new rules → manual review) | §13g |
| 24 | `mining-repos.txt` for repo-set drift | §13h |
| 25 | `git fetch --all` before each Source 5 mining run | §13i |
| 26 | Optional "does not apply when…" line per rule | §13j |
| 27 | Disaster-recovery doc in `claude-config/README.md` | §13k |
| 28 | Pin Claude model + Skill spec version in SKILL.md header | §13l |

---

## 15. Execution order

1. Confirm SKILL.md path and read current contents.
2. **Reserve holdout window** per §12a (push `--since` back 2 weeks; reserve
   those 2 weeks).
3. Run bounded mining per §6 (with §13c author filter, §13d work/personal
   firewall, §13i `git fetch --all`) → produce raw 27 (or whatever N) in §2a.
4. Grep each repo's CLAUDE.md; drop any raw pattern already covered (§7).
5. Apply §4 exclusions and §13a/§13b checks; fill §2b dedupe trail.
6. Finalize §2c split (§A vs §B, ≤12 total).
7. Write §A + §B bullets per §1/§3, including §13j "does not apply" lines
   where useful, §13l version header, §7 precedence note.
8. Run §12c token-budget check; if over cap, drop lowest-citation bullets.
9. Run §12d citation lint and §13e gitleaks on SKILL.md.
10. Run §12f cross-skill conflict scan.
11. Run §12a holdout eval; record results.
12. Run §8 / §12b live-task eval (start with N=1 for §8, schedule remaining 4
    over the next week for §12b — don't block initial commit).
13. Commit inside the target SKILL.md repo: `code-skill: backfill learnings (12 bullets, N citations)`.
14. `~/.claude/` versioning per §10 — can run in parallel with steps 1–13,
    but secret scan (§10b) must complete before the first push.
15. After §12b eval completes (N=5), update SKILL.md changelog with
    precision/recall numbers.
