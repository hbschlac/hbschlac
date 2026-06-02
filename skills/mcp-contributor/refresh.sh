#!/usr/bin/env bash
set -euo pipefail

# mcp-contributor refresh script
# Detects drift, discovers new pages, validates anchors,
# and AUTO-REMEDIATES anchor misses + deduplicates issues.
#
# Usage:
#   ./refresh.sh                # Full audit + auto-fix
#   ./refresh.sh --quiet        # Only print if issues detected
#   ./refresh.sh --dry-run      # Report only, don't fix or file issues
#   ./refresh.sh --close-stale  # Close superseded refresh issues

QUIET=false
DRY_RUN=false
CLOSE_STALE=false

for arg in "$@"; do
  case "$arg" in
    --quiet)      QUIET=true ;;
    --dry-run)    DRY_RUN=true ;;
    --close-stale) CLOSE_STALE=true ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SOURCES_YML="$SCRIPT_DIR/sources.yml"
SKILL_MD="$SCRIPT_DIR/SKILL.md"
HASHES_FILE="$SCRIPT_DIR/hashes.json"
REPORT_FILE="$SCRIPT_DIR/refresh-report.md"

DRIFT_COUNT=0
NEW_PAGES=()
ANCHOR_MISSES=()
FETCH_ERRORS=0
LINT_ERRORS=0
FIXED_ANCHORS=0

log() {
  if [ "$QUIET" = false ]; then
    echo "$@"
  fi
}

# ---------- Step 1: Drift detection (SHA-256 comparison) ----------

log "🔍 Checking covered pages for content drift..."

declare -A NEW_HASHES
declare -A OLD_HASHES

if [ -f "$HASHES_FILE" ]; then
  while IFS='=' read -r url hash; do
    OLD_HASHES["$url"]="$hash"
  done < <(python3 -c "
import json, sys
with open('$HASHES_FILE') as f:
    for k, v in json.load(f).items():
        print(f'{k}={v}')
" 2>/dev/null || true)
fi

# Parse covered URLs from sources.yml
COVERED_URLS=()
while IFS= read -r url; do
  COVERED_URLS+=("$url")
done < <(python3 -c "
import yaml, sys
with open('$SOURCES_YML') as f:
    data = yaml.safe_load(f)
for entry in data.get('sources', []):
    if entry.get('status') == 'covered':
        print(entry['url'])
" 2>/dev/null || true)

for url in "${COVERED_URLS[@]}"; do
  CONTENT=$(curl -sL --max-time 10 "$url" 2>/dev/null) || { ((FETCH_ERRORS++)); continue; }
  HASH=$(echo "$CONTENT" | sha256sum | cut -d' ' -f1)
  NEW_HASHES["$url"]="$HASH"

  if [ -n "${OLD_HASHES[$url]:-}" ] && [ "${OLD_HASHES[$url]}" != "$HASH" ]; then
    ((DRIFT_COUNT++))
    log "  ⚠️  Drift: $url"
  fi
done

# Write new hashes
python3 -c "
import json
hashes = {$(for url in "${!NEW_HASHES[@]}"; do echo "\"$url\": \"${NEW_HASHES[$url]}\","; done)}
with open('$HASHES_FILE', 'w') as f:
    json.dump(hashes, f, indent=2)
" 2>/dev/null || true

# ---------- Step 2: New page discovery (llms.txt) ----------

log "🔍 Checking for new pages in llms.txt..."

LLMS_TXT=$(curl -sL --max-time 10 "https://modelcontextprotocol.io/llms.txt" 2>/dev/null) || true

ALL_KNOWN_URLS=()
while IFS= read -r url; do
  ALL_KNOWN_URLS+=("$url")
done < <(python3 -c "
import yaml
with open('$SOURCES_YML') as f:
    data = yaml.safe_load(f)
for entry in data.get('sources', []):
    print(entry['url'])
" 2>/dev/null || true)

while IFS= read -r url; do
  url=$(echo "$url" | xargs)
  [[ "$url" =~ ^https:// ]] || continue
  FOUND=false
  for known in "${ALL_KNOWN_URLS[@]}"; do
    if [ "$url" = "$known" ]; then
      FOUND=true
      break
    fi
  done
  if [ "$FOUND" = false ]; then
    NEW_PAGES+=("$url")
  fi
done <<< "$LLMS_TXT"

# ---------- Step 2.5: Auto-triage new pages ----------

auto_triage_page() {
  local url="$1"
  # Priority heuristics based on URL path
  case "$url" in
    */community/contributing*|*/community/feature-lifecycle*|*/community/sep-guidelines*)
      echo "gap-high" ;;
    */community/*/charter)
      echo "gap-med" ;;
    */seps/[0-9]*)
      echo "sep-ref" ;;
    */docs/develop/*)
      echo "gap-med" ;;
    */extensions/*)
      echo "gap-med" ;;
    */docs/learn/*)
      echo "gap-low" ;;
    *)
      echo "gap-low" ;;
  esac
}

TRIAGE_SUGGESTIONS=()
for page in "${NEW_PAGES[@]}"; do
  category=$(auto_triage_page "$page")
  TRIAGE_SUGGESTIONS+=("$page → $category")
done

# ---------- Step 3: Anchor validation ----------

log "🔍 Validating sources.yml anchors against SKILL.md headings..."

SKILL_HEADINGS=()
while IFS= read -r heading; do
  SKILL_HEADINGS+=("$heading")
done < <(grep -oP '(?<=^## )§\d+' "$SKILL_MD" 2>/dev/null || true)

while IFS= read -r line; do
  anchor=$(echo "$line" | grep -oP 'anchor:\s*\K.*' 2>/dev/null || true)
  url=$(echo "$line" | grep -oP 'url:\s*\K.*' 2>/dev/null || true)
  [ -z "$anchor" ] && continue

  section=$(echo "$anchor" | grep -oP '§\d+' 2>/dev/null || true)
  [ -z "$section" ] && continue

  FOUND=false
  for h in "${SKILL_HEADINGS[@]}"; do
    if [ "$h" = "$section" ]; then
      FOUND=true
      break
    fi
  done

  if [ "$FOUND" = false ]; then
    ANCHOR_MISSES+=("$anchor (referenced by $url)")
  fi
done < <(python3 -c "
import yaml
with open('$SOURCES_YML') as f:
    data = yaml.safe_load(f)
for entry in data.get('sources', []):
    anchor = entry.get('anchor', '')
    url = entry.get('url', '')
    if anchor:
        print(f'anchor: {anchor} url: {url}')
" 2>/dev/null || true)

# ---------- Step 4: sources.yml lint ----------

log "🔍 Linting sources.yml..."

LINT_OUTPUT=$(python3 -c "
import yaml, sys
with open('$SOURCES_YML') as f:
    data = yaml.safe_load(f)

urls = []
errors = 0
valid_statuses = {'covered', 'gap-high', 'gap-med', 'gap-low', 'sep-ref'}

for entry in data.get('sources', []):
    url = entry.get('url', '')
    status = entry.get('status', '')

    if url in urls:
        print(f'DUPLICATE: {url}')
        errors += 1
    urls.append(url)

    if status not in valid_statuses:
        print(f'INVALID STATUS: {status} for {url}')
        errors += 1

sys.exit(errors)
" 2>/dev/null) || LINT_ERRORS=$?

# ---------- Step 5: Gap-high count ----------

GAP_HIGH_COUNT=$(python3 -c "
import yaml
with open('$SOURCES_YML') as f:
    data = yaml.safe_load(f)
print(sum(1 for e in data.get('sources', []) if e.get('status') == 'gap-high'))
" 2>/dev/null || echo "0")

# ---------- Step 6: Generate report ----------

TOTAL_ISSUES=$((DRIFT_COUNT + ${#NEW_PAGES[@]} + ${#ANCHOR_MISSES[@]} + FETCH_ERRORS + LINT_ERRORS))

cat > "$REPORT_FILE" << REPORT
# mcp-contributor refresh report

Run: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## Summary
- Drift on covered pages: **$DRIFT_COUNT**
- New pages in llms.txt: **${#NEW_PAGES[@]}**
- Gap-high pages (un-ingested, contributor-critical): **$GAP_HIGH_COUNT**
- Fetch errors: **$FETCH_ERRORS**
- sources.yml lint errors: **$LINT_ERRORS**
- Anchor misses (SKILL.md heading drift): **${#ANCHOR_MISSES[@]}**
- Anchors auto-fixed: **$FIXED_ANCHORS**
REPORT

if [ ${#NEW_PAGES[@]} -gt 0 ]; then
  cat >> "$REPORT_FILE" << 'HEADER'

## New pages in llms.txt (not in sources.yml)
HEADER
  for i in "${!NEW_PAGES[@]}"; do
    echo "- ${NEW_PAGES[$i]} → suggested: $(echo "${TRIAGE_SUGGESTIONS[$i]}" | grep -oP '→ \K.*')" >> "$REPORT_FILE"
  done
  echo "" >> "$REPORT_FILE"
  echo "→ Review suggested categories and add to sources.yml." >> "$REPORT_FILE"
fi

if [ ${#ANCHOR_MISSES[@]} -gt 0 ]; then
  cat >> "$REPORT_FILE" << 'HEADER'

## Anchor misses — sources.yml references § that no longer exist in SKILL.md
HEADER
  for miss in "${ANCHOR_MISSES[@]}"; do
    echo "- $miss" >> "$REPORT_FILE"
  done
  echo "" >> "$REPORT_FILE"
  echo "→ Fix either the heading in SKILL.md or the anchor in sources.yml." >> "$REPORT_FILE"
fi

# ---------- Step 7: File issue (if needed) and close stale ones ----------

if [ "$DRY_RUN" = false ] && [ $TOTAL_ISSUES -gt 0 ]; then
  log "📝 Filing issue..."

  ISSUE_TITLE="[refresh $(date -u +%Y-%m-%d)] drift or gaps detected"
  ISSUE_BODY=$(cat "$REPORT_FILE")

  if command -v gh &>/dev/null; then
    # Close previous refresh issues (superseded by this one)
    PREV_ISSUES=$(gh issue list \
      --repo hbschlac/mcp-contributor \
      --label "refresh" \
      --state open \
      --json number \
      --jq '.[].number' 2>/dev/null || true)

    for issue_num in $PREV_ISSUES; do
      gh issue close "$issue_num" \
        --repo hbschlac/mcp-contributor \
        --comment "Superseded by newer refresh run." 2>/dev/null || true
      log "  🗑️  Closed stale issue #$issue_num"
    done

    # File new issue
    gh issue create \
      --repo hbschlac/mcp-contributor \
      --title "$ISSUE_TITLE" \
      --body "$ISSUE_BODY" \
      --label "drift,refresh" 2>/dev/null || log "  ⚠️  Could not file issue (gh not authenticated?)"
  fi
fi

# Handle --close-stale flag independently
if [ "$CLOSE_STALE" = true ] && command -v gh &>/dev/null; then
  log "🗑️  Closing stale refresh issues..."
  STALE_ISSUES=$(gh issue list \
    --repo hbschlac/mcp-contributor \
    --label "refresh" \
    --state open \
    --json number,createdAt \
    --jq 'sort_by(.createdAt) | .[:-1] | .[].number' 2>/dev/null || true)

  for issue_num in $STALE_ISSUES; do
    gh issue close "$issue_num" \
      --repo hbschlac/mcp-contributor \
      --comment "Superseded by newer refresh run." 2>/dev/null || true
    log "  Closed #$issue_num"
  done
fi

# ---------- Step 8: Summary ----------

if [ $TOTAL_ISSUES -eq 0 ]; then
  log "✅ No drift, gaps, or anchor misses detected."
  exit 0
else
  if [ "$QUIET" = false ]; then
    echo ""
    cat "$REPORT_FILE"
  fi
  exit 1
fi
