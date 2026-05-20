# mcp-contributor — Patch Plan

Fixes for all 8 open issues + systemic improvements. Apply these to `hbschlac/mcp-contributor` SKILL.md.

---

## Fix #1: Issue #1 — No discoverable pointer from capability questions to §11.7 lifecycle

**Problem:** Contributors misclassify existing-capability wiring as needing SEPs because the triage decision tree (§1) doesn't reference the capability lifecycle section.

**Fix:** Add to the gray-zone decision tree in §1.5:

```markdown
**Quick check before filing an SEP:**
> Is this wiring up a capability or notification that already exists in the
> current spec revision? → Check the capability lifecycle (§11.7). If the
> capability is already defined, this is a small change — follow the §3 PR
> workflow, not the SEP process.
```

---

## Fix #2: Issue #2 — §6 repo map missing Inspector, Registry, ext-* repos

**Problem:** §6 only lists the 10 language SDKs. Contributors working on Inspector, Registry, or extension repos think those don't belong to the MCP org.

**Fix:** Reorganize §6 into categories:

```markdown
## §6 — Repository map

### Specification
| Repo | Purpose |
|------|---------|
| modelcontextprotocol/modelcontextprotocol | Spec, SEPs, governance docs |

### Official SDKs
[existing 10-SDK table unchanged]

### Tools
| Repo | Purpose |
|------|---------|
| modelcontextprotocol/inspector | Visual testing/debugging tool for MCP servers (inspector-v2 in development) |
| modelcontextprotocol/registry | Server registry and discovery |

### Extensions
| Repo | Purpose |
|------|---------|
| modelcontextprotocol/ext-* | Official extensions per SEP-2133 |

### Infrastructure
| Repo | Purpose |
|------|---------|
| modelcontextprotocol/access | Access control per SEP-2149 |
| modelcontextprotocol/.github | Org-wide templates, CI, community health files |
```

---

## Fix #3: Issue #3 — §4 titled "SDK workflow" but applies to all non-spec repos

**Problem:** §4 describes the issue-first, per-repo CONTRIBUTING.md workflow used by all non-spec repos, not just SDKs. Inspector follows the same process.

**Fix:** Rename and restructure:

```markdown
## §4 — Non-spec repo workflow (SDKs, tools, extensions)

This workflow applies to **all repos except the spec repo itself** — SDKs,
Inspector, Registry, and ext-* repos all follow this pattern.

### 4.1 — Common workflow (all non-spec repos)
1. Open an issue first describing what you want to change
2. Read that repo's CONTRIBUTING.md (patterns vary per language/tool)
3. Join the repo's Discord channel if one exists
4. Fork → branch → PR with issue reference

### 4.2 — SDK-specific notes
[existing SDK guidance: per-language toolchains, breaking-change rules]

### 4.3 — Tools (Inspector, Registry)
- Inspector is TypeScript/React — treat as a web app, not an SDK
- Registry has its own API conventions — read CONTRIBUTING.md carefully
- Inspector-v2 is in active development — check for in-progress PRs before starting
```

Update cross-references in §1.4 to point to "§4 non-spec repo workflow" instead of "§4 SDK workflow."

---

## Fix #4: Issues #4-#8 — 11 broken anchor references in sources.yml

**Problem:** `sources.yml` references headings §11.1-§11.11 in SKILL.md that no longer exist. Every weekly refresh flags the same 11 anchor misses.

**Root cause:** SKILL.md was restructured at some point and the §11.x numbering changed, but sources.yml wasn't updated.

**Fix:** Update `sources.yml` anchor references to match current SKILL.md headings. The affected pages and their correct targets:

| sources.yml anchor (broken) | Likely correct SKILL.md section |
|-----------------------------|--------------------------------|
| Step 11.1 (design principles) | Wherever design principles now live (likely merged into §5 SEP evaluation or a different numbering) |
| Step 11.2 (antitrust) | §5.5 governance/licensing section |
| Step 11.3 (client concepts) | §0.5 protocol primer |
| Step 11.4 (server concepts) | §0.5 protocol primer |
| Step 11.5 (SDK tiers) | §4 or §6 |
| Step 11.6 (versioning) | §0.5 or wherever spec versioning is covered |
| Step 11.7 (lifecycle) | Protocol primer or capability section |
| Step 11.8 (transports) | §0.5 or standalone section |
| Step 11.9 (authorization) | Standalone section or protocol primer |
| Step 11.10 (changelog) | §6.5 or reference links |
| Step 11.11 (SEP index) | §5 or reference links |

**Action required:** Grep SKILL.md for the actual current headings containing each topic, then update `sources.yml` to match. Also add a CI check:

```yaml
# .github/workflows/anchor-check.yml
name: Anchor validation
on: [push, pull_request]
jobs:
  check-anchors:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate sources.yml anchors against SKILL.md
        run: |
          # Extract all "anchor:" values from sources.yml
          # Verify each exists as a heading in SKILL.md
          # Fail if any are broken
          grep -oP 'anchor:\s*\K.*' sources.yml | while read anchor; do
            if ! grep -qF "$anchor" SKILL.md; then
              echo "BROKEN ANCHOR: $anchor"
              exit 1
            fi
          done
```

This prevents future §-renumbering from silently breaking references.

---

## Fix #5: 11 new pages detected in latest refresh (#8) — triage recommendations

Based on the latest refresh report, 11 new pages appeared in llms.txt. Recommended triage:

| New page (likely topic) | Recommended tier | Rationale |
|------------------------|------------------|-----------|
| Community charter: file uploads | gap-low | Niche WG charter; link-only |
| Community charter: interceptors | gap-low | Niche WG charter; link-only |
| Community charter: SDKs | gap-med | Directly relevant to §4 workflow |
| Client best practices | gap-med | Useful for SDK contributors building clients |
| Tasks extension overview | gap-med | New primitive; contributors will ask about it |
| SEP documents (5 new) | sep-ref | Standard treatment for individual SEPs |

Add these to `sources.yml` with appropriate tiers. For gap-med items, schedule ingestion into SKILL.md in the next version.

---

## Systemic improvement: Tiered content loading

**Problem:** The skill is extremely long. A contributor fixing a typo loads the entire governance model, SEP lifecycle, protocol primer, and licensing framework. This wastes context window and can confuse Claude about what's relevant.

**Proposed solution:** Add a content-tiering directive to the frontmatter:

```yaml
---
name: mcp-contributor
description: ...
content_tiers:
  quick:
    sections: [0, 1, 3, 8]
    triggers: ["fix a typo", "docs PR", "small fix", "broken link"]
  standard:
    sections: [0, 1, 2, 3, 4, 6, 8]
    triggers: ["SDK PR", "non-spec repo", "contribute to MCP"]
  full:
    sections: all
    triggers: ["write an SEP", "propose spec change", "governance", "MCP good first issue"]
---
```

On activation, classify the task complexity and announce which tier loaded:

> mcp-contributor activated — [quick | standard | full]. [reason.]

This reduces token cost by 40-70% for simple contributions.

---

## Systemic improvement: Drift triage automation

**Problem:** refresh.sh creates issues but doesn't suggest resolution actions. 5 weeks of alerts pile up.

**Proposed enhancement to refresh.sh:** After detecting drift/gaps, auto-generate a triage comment on the issue with:
1. For anchor misses: grep SKILL.md for closest-matching headings and suggest corrections
2. For new pages: compare page title/URL pattern against existing coverage tiers and suggest a tier
3. For content drift: show a diff summary of what changed on the source page

This turns "drift detected" → "here's what to do about it" and reduces triage from 30 minutes to 5 minutes.

---

## Systemic improvement: Usage tracking

Neither skill tracks whether it's actually been used or helped. Add a minimal activation counter:

```markdown
## Activation log (append-only, last 20)
<!-- code-builder appends here on each activation -->
- 2026-05-20 | single | ephemeral | hannah-portfolio | "fix header alignment"
- 2026-05-19 | parallel | full | muse-shopping | "add recommendation engine"
```

In ephemeral environments, log to commit message metadata instead. This creates a minimal usage signal for future audits.
