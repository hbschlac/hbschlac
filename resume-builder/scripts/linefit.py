#!/usr/bin/env python3
"""
linefit.py — measure how many lines each CV paragraph actually occupies in the
exported PDF, instead of guessing from character count.

WHY THIS EXISTS
---------------
Through most of the 2026-09-15 Anthropic session the 2-line bullet cap was an
estimate: guessed at ~224 chars, revised after a 231-char bullet wrapped to three
lines, and in the end Hannah was the line checker ("siemens bullet is 3 lines in
doc"). Character count is a bad proxy — Calibri renders "Illinois" and "WWWWWWWW"
at very different widths.

HOW IT WORKS
------------
Google Docs' PDF export writes one BT/ET block per *text run*, not per paragraph,
using Identity-H CID fonts (hex glyph ids, no literal text). So this script:

  1. resolves each /Fn resource to its /ToUnicode CMap and decodes the glyph ids
  2. replays the content stream's graphics state (q/Q, cm, Tm, Td) to get each
     run's true device position
  3. groups runs into baselines by Y, and baselines into paragraphs: a line that
     starts with a bullet, or sits at the left margin, opens a paragraph; an
     indented line continues the one above it

Body leading is 12.2pt, so a 2-line bullet spans 12.2 and a 3-line bullet 24.4.

Stdlib only — no dependencies, runs in any sandbox.

USAGE
-----
    curl -sSL "https://docs.google.com/document/d/<DOC_ID>/export?format=pdf" -o cv.pdf
    python3 linefit.py cv.pdf                # full report
    python3 linefit.py cv.pdf --over 2       # only over-long bullets; exit 1 if any

Exit code is 1 if the CV runs past one page or any bullet exceeds --over, so it
works as a pre-send gate.

NEVER export the PDF into the conversation. The 2026-09-15 session ran 27 PDF
exports through the Drive MCP tool and all 27 blew the token limit — which is what
exhausted the context window at 19:37. Write it to a path and point this at it.
"""

import re
import signal
import sys
import zlib
from collections import defaultdict

# allow `linefit.py cv.pdf | head` without a BrokenPipeError traceback
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except (AttributeError, ValueError):
    pass

LEADING_PT = 12.2      # one line of body text
INDENT_EPS = 4.0       # x within this of the margin counts as "at the margin"
MAX_CONT_INDENT = 40.0  # a wrapped line indents ~14pt; a CENTERED HEADING sits 180pt+
LEAD_TOL = 0.30        # how far the gap may stray from one leading
IDENTITY = (1, 0, 0, 1, 0, 0)


# ---------- PDF plumbing ----------

def indirect_objects(raw):
    return {int(m.group(1)): m.group(2)
            for m in re.finditer(rb"(\d+)\s+0\s+obj(.*?)endobj", raw, re.S)}


def inflate(chunk):
    try:
        return zlib.decompress(chunk)
    except zlib.error:
        return chunk


def font_cmaps(raw, objs):
    """Map /Fn -> {glyph_id: character} via each font's /ToUnicode CMap."""
    refs = {}
    for m in re.finditer(rb"/Font\s*<<(.*?)>>", raw, re.S):
        for name, num in re.findall(rb"/(F\d+)\s+(\d+)\s+0\s+R", m.group(1)):
            refs[name.decode()] = int(num)

    out = {}
    for name, num in refs.items():
        body = objs.get(num, b"")
        m = re.search(rb"/ToUnicode\s+(\d+)\s+0\s+R", body)
        if not m:
            out[name] = {}
            continue
        sm = re.search(rb"stream\r?\n(.*?)endstream", objs.get(int(m.group(1)), b""), re.S)
        if not sm:
            out[name] = {}
            continue
        data = inflate(sm.group(1))
        cm = {}
        for blk in re.finditer(rb"beginbfchar(.*?)endbfchar", data, re.S):
            for g, u in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk.group(1)):
                cm[int(g, 16)] = chr(int(u[:4], 16))
        for blk in re.finditer(rb"beginbfrange(.*?)endbfrange", data, re.S):
            for lo, hi, u in re.findall(
                    rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk.group(1)):
                lo, hi, u = int(lo, 16), int(hi, 16), int(u[:4], 16)
                for i in range(lo, hi + 1):
                    cm[i] = chr(u + i - lo)
        out[name] = cm
    return out


def mul(m1, m2):
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return (a1 * a2 + b1 * c2, a1 * b2 + b1 * d2,
            c1 * a2 + d1 * c2, c1 * b2 + d1 * d2,
            e1 * a2 + f1 * c2 + e2, e1 * b2 + f1 * d2 + f2)


TOKEN = re.compile(
    rb"(?P<hex><[0-9A-Fa-f]*>)\s*Tj"
    rb"|/(?P<font>F\d+)\s+[\d.]+\s+Tf"
    rb"|(?P<nums>[\d.\-]+(?:\s+[\d.\-]+){5})\s+(?P<op>cm|Tm)"
    rb"|(?P<tx>[\d.\-]+)\s+(?P<ty>[\d.\-]+)\s+Td"
    rb"|(?P<tok>\bq\b|\bQ\b|\bBT\b|\bET\b)")


def positioned_runs(stream, cmaps):
    """Replay the graphics state; yield (y, x, text) for every shown run."""
    runs = []
    ctm, stack, font = IDENTITY, [], None
    tm = tlm = IDENTITY
    for m in TOKEN.finditer(stream):
        if m.group("tok"):
            t = m.group("tok")
            if t == b"q":
                stack.append(ctm)
            elif t == b"Q":
                ctm = stack.pop() if stack else ctm
            elif t == b"BT":
                tm = tlm = IDENTITY
        elif m.group("op"):
            M = tuple(float(x) for x in m.group("nums").split())
            if m.group("op") == b"cm":
                ctm = mul(M, ctm)
            else:
                tm = tlm = M
        elif m.group("tx") is not None:
            tlm = mul((1, 0, 0, 1, float(m.group("tx")), float(m.group("ty"))), tlm)
            tm = tlm
        elif m.group("font"):
            font = m.group("font").decode()
        elif m.group("hex"):
            hx = m.group("hex")[1:-1]
            cm = cmaps.get(font, {})
            text = "".join(cm.get(int(hx[i:i + 4], 16), "")
                           for i in range(0, len(hx), 4))
            M = mul(tm, ctm)
            runs.append((M[5], M[4], text))
    return runs


# ---------- structure ----------

def baselines(runs):
    """Collapse runs into lines. Returns [(y, x_start, text)] in reading order."""
    rows = defaultdict(list)
    for y, x, t in runs:
        rows[round(y, 1)].append((x, t))
    out = []
    for y in sorted(rows, reverse=True):          # page reads top-down as y descends
        seg = sorted(rows[y], key=lambda s: s[0])
        text = "".join(s[1] for s in seg).rstrip()
        if text:
            out.append((y, seg[0][0], text))
    return out


def paragraphs(lines):
    """Group lines into paragraphs.

    A line continues the paragraph above it only when BOTH hold:
      * it is indented past the margin but by no more than MAX_CONT_INDENT, and
      * it sits exactly one leading below the previous line.

    Both tests are needed. A centered section heading ("AI PROJECTS & VENTURES")
    is far right of the margin, so an indent-only test swallows it into the bullet
    above and reports that bullet as four lines instead of two.
    """
    if not lines:
        return []
    margin = min(x for _, x, _ in lines)
    paras, cur, prev_y = [], None, None
    for y, x, text in lines:
        indented = margin + INDENT_EPS < x <= margin + MAX_CONT_INDENT
        one_leading = prev_y is not None and abs((prev_y - y) - LEADING_PT) <= LEAD_TOL
        continues = cur is not None and indented and one_leading \
            and not text.lstrip().startswith(("●", "•", "·"))
        if continues:
            cur["lines"].append(text)
            cur["ys"].append(y)
        else:
            if cur:
                paras.append(cur)
            cur = {"lines": [text], "ys": [y], "x": x}
        prev_y = y
    if cur:
        paras.append(cur)

    for p in paras:
        span = max(p["ys"]) - min(p["ys"])
        p["n"] = 1 if span < LEADING_PT * 0.65 else int(round(span / LEADING_PT)) + 1
        p["text"] = " ".join(s.strip() for s in p["lines"])
        p["bullet"] = p["text"].lstrip().startswith(("●", "•", "·"))
    return paras


def page_count(raw):
    counts = [int(m.group(1)) for m in re.finditer(rb"/Count\s+(\d+)", raw)]
    return max(counts) if counts else 0


# ---------- cli ----------

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2

    path = sys.argv[1]
    limit = None
    if "--over" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--over") + 1])

    raw = open(path, "rb").read()
    objs = indirect_objects(raw)
    cmaps = font_cmaps(raw, objs)

    streams = [inflate(m.group(1))
               for m in re.finditer(rb"stream\r?\n(.*?)endstream", raw, re.S)]
    content = max(streams, key=len)

    paras = paragraphs(baselines(positioned_runs(content, cmaps)))
    pages = page_count(raw)

    bullets = [p for p in paras if p["bullet"]]
    over = [p for p in bullets if limit is not None and p["n"] > limit]

    print(f"{path}")
    print(f"pages: {pages}" + ("   ← OVER ONE PAGE" if pages > 1 else "   ✓")
          + f"    paragraphs: {len(paras)}    bullets: {len(bullets)}")
    print()
    print(f"{'lines':>5}  {'chars':>5}  text")
    print("-" * 104)

    for p in paras:
        if limit is not None and not (p["bullet"] and p["n"] > limit):
            continue
        flag = "  ← OVER" if p in over else ""
        print(f"{p['n']:>5}  {len(p['text']):>5}  {p['text'][:88]}{flag}")

    if limit is not None:
        print("-" * 104)
        print(f"{len(over)} bullet(s) exceed {limit} lines."
              if over else f"All {len(bullets)} bullets within {limit} lines.")

    return 1 if (pages > 1 or over) else 0


if __name__ == "__main__":
    sys.exit(main())
