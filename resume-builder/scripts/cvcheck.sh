#!/usr/bin/env bash
# cvcheck.sh DOC_ID_OR_URL [--over N]
#
# Export the CV's PDF to a FILE and print only linefit's summary: page count and any bullet
# over N lines (default 2). The PDF never enters the conversation — 27 exports pulled into the
# chat exhausted the 2026-09-15 session. ~30 tokens of output instead of ~15,000.
#
# Exit codes: 0 fits · 1 over one page or a bullet too long · 3 export failed (doc not
# link-readable) · 2 usage.
# Canonical copy: hbschlac/career-skills skills/resume/scripts/cvcheck.sh (loads with the resume
# skill). This copy stays for the Bullet Bench; change career-skills first.
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ $# -ge 1 ]] || { echo "usage: cvcheck.sh DOC_ID_OR_URL [--over N]" >&2; exit 2; }
id="$(sed -nE 's#.*/d/([A-Za-z0-9_-]+).*#\1#p' <<<"$1")"; [[ -n "$id" ]] || id="$1"; shift
over=2
if [[ "${1:-}" == "--over" && -n "${2:-}" ]]; then over="$2"; fi
[[ "$id" =~ ^[A-Za-z0-9_-]{20,}$ ]] || { echo "cvcheck: '$id' does not look like a Google Doc id" >&2; exit 2; }

out="${TMPDIR:-/tmp}/cv-$id.pdf"
if ! curl -sSL --max-time 60 "https://docs.google.com/document/d/$id/export?format=pdf" -o "$out" \
   || ! head -c 4 "$out" 2>/dev/null | grep -q '%PDF'; then
  rm -f "$out"
  echo "cvcheck: export failed — the doc is not link-readable. Share it as 'anyone with the link: viewer' (or run on the Mac), then retry. Nothing was printed into the chat."
  exit 3
fi
echo "cvcheck: $(wc -c < "$out") bytes -> $out (file only; not shown)"
python3 "$HERE/linefit.py" "$out" --over "$over" | tail -n 12
exit "${PIPESTATUS[0]}"
