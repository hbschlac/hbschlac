#!/usr/bin/env bash
# rules_preserved.sh [CAREER_SKILLS_DIR]
#
# Every rule that existed in the pre-split resume files must still exist somewhere in the
# split tree. The marker list (tests/fixtures/rule-markers.txt) was generated from the
# ORIGINAL files at career-skills 04ab6b3 — every ##/### heading of resume-subskill.md except
# the dropped legacy publisher, every bold-lead "Key rule" of the entry skill, and the literals
# that have been lost before. Em-dashes are normalised to "-" on both sides. Exit 1 on any loss.
set -uo pipefail
CS="${1:-/home/user/career-skills}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MARKERS="$HERE/fixtures/rule-markers.txt"
TREE=("$CS/skills/resume" "$CS/skills/product-networking/references/resume-subskill.md" "$CS/skills/product-networking/SKILL.md")
corpus="$(mktemp)"
find "${TREE[@]}" -type f -name '*.md' -print0 | xargs -0 cat | sed 's/—/-/g; s/–/-/g' > "$corpus"
missing=0; total=0
while IFS= read -r m; do
  [[ -z "$m" || "$m" == \#* ]] && continue
  total=$((total+1))
  if ! grep -qF -- "$m" "$corpus"; then echo "  LOST: $m"; missing=$((missing+1)); fi
done < "$MARKERS"
rm -f "$corpus"
echo "rules preserved: $((total-missing))/$total markers found in the split tree"
(( missing == 0 )) || { echo "rules preserved: FAIL"; exit 1; }
echo "rules preserved: PASS"
