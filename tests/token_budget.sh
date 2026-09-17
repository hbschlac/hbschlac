#!/usr/bin/env bash
# token_budget.sh [CAREER_SKILLS_DIR]
#
# Tokens a resume session loads BEFORE reading the JD, before vs after the 2026-09-17 split.
# "Before" is the frozen snapshot in tests/fixtures/before-2026-09-17.txt (taken at career-skills
# 04ab6b3). "After" is measured live. Tokens ≈ bytes/4, the same estimator both times.
# Exit 1 if the per-gate load is not below the old mandatory read-list, or a rule file regrew.
set -euo pipefail
CS="${1:-/home/user/career-skills}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BEFORE="$HERE/fixtures/before-2026-09-17.txt"
tok() { echo $(( $(wc -c < "$1") / 4 )); }
b() { awk -v k="$1" '$1==k {print $2}' "$BEFORE"; }

R="$CS/skills/resume"; PN="$CS/skills/product-networking/references"
router=$(tok "$R/SKILL.md"); s0=$(tok "$R/references/step0-facts.md"); s1=$(tok "$R/references/step1-write.md")
s2=$(tok "$R/references/step2-voice.md"); s3=$(tok "$R/references/step3-score.md"); s4=$(tok "$R/references/step4-apply.md")
s5=$(tok "$R/references/step5-publish.md"); resume=$(tok "$PN/resume.md"); index=$(tok "$PN/resume-subskill.md")
learn=$(tok "$CS/skills/interview-prep-dust-sierra/references/learnings.md")
grep_out=$(bash "$R/scripts/ledger_grep.sh" security | wc -c); grep_tok=$(( grep_out / 4 ))
ledger_full=$(( ( $(wc -c < "$PN/evidence.md") + $(wc -c < "$PN/hannah-profile.md") ) / 4 ))

before_list=$(awk -F': ' '/MANDATORY READ-LIST/ {print $2}' "$BEFORE")
before_entry=$(b resume/SKILL.md); before_sub=$(b resume-subskill.md); before_learn=$(b learnings.md)
max_step=$(printf '%s\n' "$s0" "$s1" "$s2" "$s3" "$s4" "$s5" | sort -n | tail -1)
gate1=$(( router + s1 + resume )); gate4=$(( router + s4 ))
all_steps=$(( s0 + s1 + s2 + s3 + s4 + s5 ))

printf '%-46s %10s %10s\n' "load (tokens ≈ bytes/4)" "before" "after"
printf '%-46s %10s %10s\n' "entry skill (resume/SKILL.md)" "$before_entry" "$router"
printf '%-46s %10s %10s\n' "resume-subskill.md (now an index)" "$before_sub" "$index"
printf '%-46s %10s %10s\n' "mandatory read-list before the JD" "$before_list" "$router"
printf '%-46s %10s %10s\n' "heaviest single gate (router + step)" "-" "$(( router + max_step ))"
printf '%-46s %10s %10s\n' "Gate 1 write (router + step1 + resume.md)" "-" "$gate1"
printf '%-46s %10s %10s\n' "Gate 4 apply (router + step4)" "-" "$gate4"
printf '%-46s %10s %10s\n' "all six gate files (content conserved)" "$(( before_entry + before_sub ))" "$all_steps"
printf '%-46s %10s %10s\n' "facts lookup: read ledger+profile vs grep" "$ledger_full" "$grep_tok"
printf '%-46s %10s %10s\n' "interview learnings.md" "$before_learn" "$learn"
echo
fail=0
(( router < 1500 ))            || { echo "!! router is $router tokens; must stay under 1500"; fail=1; }
(( router + max_step < before_list )) || { echo "!! heaviest gate is not below the old read-list"; fail=1; }
(( gate1 < before_list / 2 ))  || { echo "!! Gate 1 load is not under half the old read-list"; fail=1; }
(( grep_tok < ledger_full / 5 )) || { echo "!! ledger_grep is not at least 5x cheaper than reading"; fail=1; }
(( learn < before_learn / 2 )) || { echo "!! learnings.md did not halve"; fail=1; }
(( all_steps > (before_entry + before_sub) * 6 / 10 )) || { echo "!! gate files hold <60% of the old content — something was dropped, not moved"; fail=1; }
if (( fail )); then echo "token budget: FAIL"; exit 1; fi
echo "token budget: PASS — before-the-JD load $before_list → $router; heaviest gate $(( router + max_step ))"
