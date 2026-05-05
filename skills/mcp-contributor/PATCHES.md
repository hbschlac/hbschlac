# mcp-contributor — Improvement Patches

Specific, copy-pasteable fixes for the 6 open issues plus systemic improvements. Apply these to the `hbschlac/mcp-contributor` repo.

---

## Issue #3: "§4 titled 'SDK workflow' but applies to all non-spec repos"

**Problem:** Section 4 is titled "SDK workflow" but the steps (fork, branch, PR) apply to all non-spec repos — Inspector, Registry, ext-*, .github, etc. Contributors working on non-SDK repos skip this section.

**Fix in SKILL.md:**

Replace the §4 heading:
```diff
-## §4 — SDK workflow
+## §4 — Non-spec repo workflow (SDKs, Inspector, Registry, extensions)
```

Add a clarifying note immediately after the heading:
```markdown
This workflow applies to **all repos in the MCP org except the spec repo itself** — the 10 official SDKs, Inspector, Registry, ext-* extension repos, the .github org-config repo, and the access repo. The spec repo follows §3 (small changes) or §5 (SEPs).
```

---

## Issue #2: "§6 repo map missing Inspector, Registry, ext-* repos"

**Problem:** The repo map in §6 only covers the spec repo and SDKs. Contributors encountering Inspector issues, Registry PRs, or extension repos have no guidance on which section applies.

**Fix:** Add these entries to the §6 repo map table:

```markdown
| Repo | What it is | Contribution path |
|------|-----------|-------------------|
| `inspector` | Browser-based MCP debugging tool | §4 non-spec workflow |
| `registry` | MCP server package registry | §4 non-spec workflow |
| `ext-*` (e.g., ext-auth) | Official protocol extensions | §4 for code; §5 SEP for new extension proposals |
| `access` | Access control tooling | §4 non-spec workflow |
| `.github` | Org-level config (templates, workflows) | §4 non-spec workflow; changes here affect all repos |
```

---

## Issue #1: "No discoverable pointer from capability questions to §11.7 lifecycle"

**Problem:** Users asking "can MCP do X?" enter at §1 (triage) which routes them to either §3 (small change) or §5 (SEP). But "can it do X?" is a capability question, not a change request — they need §11.7 (lifecycle/capabilities primer) first.

**Fix:** Add a third route to the §1 triage decision tree:

```markdown
### §1 triage — where does your contribution start?

| Question | Route |
|----------|-------|
| "I want to fix/improve something" | → §3 (small PR) or §5 (SEP) |
| "Can MCP do X?" / "Does MCP support Y?" | → **§11.7 first** (protocol capabilities primer), then §1 again with a concrete proposal |
| "I'm not sure if this is a bug or a feature gap" | → Check §11.7 for current capabilities, then file an issue in the appropriate repo (see §6) |
```

---

## Issues #4, #5, #6: Unresolved weekly drift detections

**Problem:** Automated drift detection (via `.github/workflows/weekly-refresh.yml` running `refresh.sh`) has been opening issues weekly since Apr 19 but none have been resolved. The issues say "Content has drifted from authoritative MCP source" but don't include specifics about what changed or proposed fixes.

**Root cause:** `refresh.sh` outputs a human-readable report (`refresh-report.md`) but the GitHub Action workflow likely only posts a generic issue body. The action should include the drift details and proposed patches.

### Fix 1: Improve the GitHub Action issue body

In `.github/workflows/weekly-refresh.yml`, modify the issue creation step to include the refresh report content:

```yaml
- name: Create drift issue
  if: steps.refresh.outputs.drift == 'true'
  uses: actions/github-script@v7
  with:
    script: |
      const fs = require('fs');
      const report = fs.readFileSync('refresh-report.md', 'utf8');
      await github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: `[refresh ${new Date().toISOString().split('T')[0]}] drift or gaps detected`,
        body: `## Drift Report\n\n${report}\n\n## Next Steps\n\n- [ ] Review each drifted URL\n- [ ] Update SKILL.md sections listed above\n- [ ] Update \`fetched\` dates in sources.yml\n- [ ] Run \`./refresh.sh\` locally to verify fix`,
        labels: ['drift', 'refresh']
      });
```

### Fix 2: Enhance refresh.sh to generate proposed SKILL.md patches

Add a `--propose-patches` flag to `refresh.sh` that, for each drifted URL:
1. Fetches the new content
2. Finds the corresponding anchor in SKILL.md
3. Generates a diff between the old synthesis and the new source content
4. Outputs a `proposed-patches.md` with copy-pasteable edits

This transforms drift issues from "something changed" into "here's what to update."

### Fix 3: Immediate backlog resolution strategy

For the 3 stacked drift issues (#4 Apr 19, #5 Apr 26, #6 May 3):
1. Only issue #6 matters — it contains the latest hashes, which encompass all prior drift
2. Close #4 and #5 as superseded by #6
3. Run `./refresh.sh` locally to get the current drift report
4. Update SKILL.md for all drifted sections
5. Update `fetched` dates in sources.yml
6. Run `./refresh.sh` again to verify clean
7. Close #6

---

## Systemic improvement: Close the detection-to-resolution loop

The current flow is: detect drift → open issue → manual resolution (never happens).

Better flow: detect drift → open issue with specific diffs → optionally auto-PR the changes.

Add to `refresh.sh`:
```bash
# After generating refresh-report.md, if --auto-pr flag is set:
if [ "$AUTO_PR" = "true" ] && [ "$DRIFT_FOUND" = "true" ]; then
    git checkout -b "refresh/$(date +%Y-%m-%d)"
    # Apply proposed patches to SKILL.md
    # Update fetched dates in sources.yml
    git add SKILL.md sources.yml
    git commit -m "refresh: update drifted sections from $(date +%Y-%m-%d) scan"
    git push origin "refresh/$(date +%Y-%m-%d)"
    gh pr create --title "[refresh] Update drifted sections" \
                 --body "$(cat refresh-report.md)" \
                 --label "drift,refresh"
fi
```

This makes drift resolution a one-click PR merge instead of a manual editing task.

---

## Priority for gap-med sources

The 20 `gap-med` URLs in sources.yml should be prioritized by contributor impact. Recommended order:

### Tier 1 — Highest impact (unblocks SDK contributors immediately)
1. `docs/sdk` — SDK overview page, first thing SDK contributors read
2. `docs/tools/debugging` — debugging MCP connections
3. `docs/tools/inspector` — Inspector usage guide
4. `specification/2025-11-25/server/tools` — tools spec (most-used primitive)
5. `specification/2025-11-25/server/resources` — resources spec

### Tier 2 — Security and auth (blocks enterprise contributors)
6. `docs/tutorials/security/authorization` — auth tutorial
7. `docs/tutorials/security/security_best_practices` — security practices
8. `specification/2025-11-25/basic/authorization` — already covered but linked
9. `extensions/auth/overview` — auth extension overview

### Tier 3 — Advanced protocol (needed for SEP authors)
10. `specification/2025-11-25/server/prompts` — prompts spec
11. `specification/2025-11-25/client/sampling` — sampling spec
12. `specification/2025-11-25/client/elicitation` — elicitation spec
13. `specification/2025-11-25/schema` — JSON schema reference
14. `specification/2025-11-25/basic/utilities/tasks` — tasks (SEP-1686)

### Tier 4 — Registry and extensions (growing importance)
15. `registry/about` — registry overview
16. `extensions/overview` — extensions lifecycle
17. `extensions/apps/overview` — apps extension
18. `clients` — client implementations list
19. `docs/develop/build-server` — server building guide
20. `docs/develop/build-client` — client building guide
