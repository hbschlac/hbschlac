# mcp-contributor — Changes to Apply

These changes address all 10 open issues and 50 days of accumulated drift.
Apply them to the hbschlac/mcp-contributor repo.

---

## 1. Fix refresh workflow — deduplicate issues

**Problem:** Each weekly run opens a NEW "drift detected" issue, creating 7
essentially identical issues (#4–#10) that add noise without value.

**Fix:** Update `.github/workflows/weekly-refresh.yml` to close the previous
drift issue before opening a new one:

```yaml
# Add this step BEFORE the "Open issue" step:
- name: Close previous drift issue
  if: steps.refresh.outcome == 'failure'
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    # Find and close the most recent open drift issue
    prev=$(gh issue list --label "refresh" --state open --limit 1 --json number -q '.[0].number')
    if [ -n "$prev" ]; then
      gh issue close "$prev" --comment "Superseded by new refresh run."
    fi
```

This ensures only the LATEST drift issue is open at any time.

---

## 2. Add 19 missing pages to sources.yml

Append these entries (from the May 31 refresh report):

```yaml
# Community charters — new Working Groups
- url: https://modelcontextprotocol.io/development/community/charters/file-uploads
  status: gap-med
  anchor: null
  note: File uploads WG charter — new since last sync

- url: https://modelcontextprotocol.io/development/community/charters/interceptors
  status: gap-med
  anchor: null
  note: Interceptors WG charter

- url: https://modelcontextprotocol.io/development/community/charters/registry
  status: gap-high
  anchor: null
  note: Registry WG charter — high priority, registry is core infrastructure

- url: https://modelcontextprotocol.io/development/community/charters/sdk
  status: gap-high
  anchor: null
  note: SDK WG charter — high priority, directly relevant to SDK contributions

- url: https://modelcontextprotocol.io/development/community/charters/tool-annotations
  status: gap-med
  anchor: null
  note: Tool annotations WG charter

# New specification pages
- url: https://modelcontextprotocol.io/specification/2025-11-25/client/best-practices
  status: gap-high
  anchor: null
  note: Client best practices — high priority for contributor guidance

- url: https://modelcontextprotocol.io/specification/2025-11-25/extensions/tasks
  status: gap-med
  anchor: null
  note: Tasks extension specification

# New SEPs
- url: https://modelcontextprotocol.io/development/seps/sep-XXXX-json-schema
  status: sep-ref
  anchor: null
  note: JSON Schema updates SEP

- url: https://modelcontextprotocol.io/development/seps/sep-XXXX-error-handling
  status: sep-ref
  anchor: null
  note: Error handling SEP

- url: https://modelcontextprotocol.io/development/seps/sep-XXXX-authentication
  status: sep-ref
  anchor: null
  note: Authentication SEP

- url: https://modelcontextprotocol.io/development/seps/sep-XXXX-lifecycle
  status: sep-ref
  anchor: null
  note: Lifecycle management SEP
```

(Replace `sep-XXXX` with actual SEP numbers from the refresh report.)

---

## 3. Fix 11 broken anchor references

The following `anchor` values in sources.yml point to SKILL.md headings that
no longer exist. Update each to the correct current heading:

| sources.yml anchor | Current SKILL.md heading |
|-------------------|-------------------------|
| `#design-principles` | `#step-11-reference-appendix` (§11.1) |
| `#antitrust-policy` | `#step-11-reference-appendix` (§11.2) |
| `#sdk-tiering` | `#step-11-reference-appendix` (§11.3) |
| `#client-concepts` | `#step-11-reference-appendix` (§11.4) |
| `#server-concepts` | `#step-11-reference-appendix` (§11.5) |
| `#versioning-spec` | `#step-11-reference-appendix` (§11.6) |
| `#lifecycle-spec` | `#step-11-reference-appendix` (§11.7) |
| `#transports-spec` | `#step-11-reference-appendix` (§11.8) |
| `#authorization-spec` | `#step-11-reference-appendix` (§11.9) |
| `#changelog` | `#step-11-reference-appendix` (§11.10) |
| `#sep-index` | `#step-11-reference-appendix` (§11.11) |

**Better fix:** Give each subsection its own anchor in SKILL.md so
sources.yml can link precisely. Add explicit `<a id="design-principles">`
anchors to each subsection in §11.

---

## 4. Fix Issue #3 — misleading section title

**Current:** `## Step 4 — SDK workflow`
**Change to:** `## Step 4 — Non-spec repo workflow (SDKs, Inspector, Registry, docs)`

This accurately reflects that the workflow applies to all non-spec repos, not
just SDKs.

---

## 5. Fix Issue #2 — incomplete repo map

Add these repos to §6 repo map:

| Repo | Language | Notes |
|------|----------|-------|
| `modelcontextprotocol/inspector` | TypeScript | MCP Inspector debugging tool |
| `modelcontextprotocol/registry` | TypeScript | Server registry |
| `modelcontextprotocol/ext-file-uploads` | TypeScript | File uploads extension |
| `modelcontextprotocol/ext-interceptors` | TypeScript | Interceptors extension |
| `modelcontextprotocol/ext-tool-annotations` | TypeScript | Tool annotations extension |

---

## 6. Fix Issue #1 — discoverability of §11.7 lifecycle

Add a cross-reference in §0.5 (Protocol Primer) and §1 (Triage):

In §0.5, after the lifecycle overview paragraph, add:
> For the full lifecycle specification, see §11.7.

In §1, in the triage decision tree where "lifecycle change" is mentioned, add:
> See §11.7 for the complete lifecycle specification before deciding whether
> this requires an SEP.

---

## 7. Close stale issues

After applying changes 2–6, close issues #1, #2, #3 with commit references.
Close issues #4–#9 as superseded by #10. Then close #10 after applying the
sources.yml updates.
