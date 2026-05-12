#!/usr/bin/env bash
# Patch for refresh.sh — fixes the anchor-miss grep pattern
#
# PROBLEM: refresh.sh uses `grep -q "^## ${ref}[: ]" SKILL.md` to verify
# that each source in sources.yml maps to a heading in SKILL.md.
# But SKILL.md's Step 11.x headings use the format:
#   ### 11.1 Design Principles
# not:
#   ## Step 11.1: Design Principles
#
# This causes 11 false-positive anchor misses every weekly refresh,
# creating noise issues (#4, #5, #6, #7) that obscure real drift signals.
#
# FIX: Replace the rigid heading grep with a flexible pattern that matches:
#   - "## Step 11.1:" (original expected format)
#   - "### 11.1 "    (actual SKILL.md format)
#   - "## 11.1"      (alternate format)
#
# APPLY: In refresh.sh, find the anchor-check loop and replace the grep line.
#
# BEFORE (approximate — locate the anchor-verification section):
#   if ! grep -q "^## ${ref}[: ]" SKILL.md; then
#     anchor_misses+=("${ref}")
#   fi
#
# AFTER:
#   # Match headings at any level (##, ###) with or without "Step" prefix
#   ref_num="${ref#Step }"  # strip "Step " prefix if present
#   if ! grep -qE "^#{2,4} (Step )?${ref_num}[: ]" SKILL.md; then
#     anchor_misses+=("${ref}")
#   fi
#
# Additionally, update sources.yml anchor references to use the actual
# heading format. For each Step 11.x entry in sources.yml, change:
#   anchor: "Step 11.1"
# to:
#   anchor: "11.1"
# (or whichever format matches the actual SKILL.md heading)

echo "This is a patch description file, not meant to be executed directly."
echo "Apply the changes described above to the actual refresh.sh in hbschlac/mcp-contributor."
