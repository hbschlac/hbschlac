# mcp-contributor — Skill Improvement Spec

Addresses the 4 open GitHub issues plus gaps identified from source coverage analysis.

---

## Issue #1: No discoverable pointer from capability questions to §11.7 lifecycle

**Problem:** A user asking "how do capabilities work?" or "what happens during initialization?" has no navigation path to §11.7 (lifecycle), which contains the answers.

**Fix:** Add a cross-reference index after Step 0.5 (Protocol primer).

```markdown
### Quick-find index

| If you're asking about... | Go to |
|---------------------------|-------|
| Capabilities, negotiation, initialization | §11.7 Lifecycle |
| "Can I add a new method?" | §1 Triage → §5 SEP workflow |
| "Is this a breaking change?" | §1.4 Major-change criteria |
| SDK-specific contribution | §4 SDK workflow |
| Governance, roles, who decides | §5.5 Governance model |
| Transport, HTTP, SSE, stdio | §11.8 Transports |
| Auth, OAuth, tokens | §11.9 Authorization |
| Where to ask questions | §8 Communication channels |
```

---

## Issue #2: §6 repo map missing Inspector, Registry, ext-* repos

**Problem:** Repo map only lists the spec + 10 SDKs. Missing key repos.

**Fix:** Add these to the §6 repo map table:

```markdown
| Repo | Purpose | Primary language |
|------|---------|-----------------|
| `modelcontextprotocol/inspector` | Interactive debugging tool for MCP servers | TypeScript |
| `modelcontextprotocol/registry` | Server registry and discovery | TypeScript |
| `modelcontextprotocol/ext-auth` | OAuth/authentication extension | TypeScript |
| `modelcontextprotocol/ext-validation` | Schema validation utilities | TypeScript |
| `modelcontextprotocol/create-python-server` | Scaffolding for new Python MCP servers | Python |
| `modelcontextprotocol/create-typescript-server` | Scaffolding for new TypeScript MCP servers | TypeScript |
```

Also add a note: "Run `gh repo list modelcontextprotocol --limit 50` to get the current full inventory — new repos appear regularly."

---

## Issue #3: §4 titled 'SDK workflow' but applies to all non-spec repos

**Problem:** Section 4 is titled "SDK workflow" but its guidance (open issue first, follow repo CONTRIBUTING.md, write tests) applies equally to Inspector, Registry, ext-* repos.

**Fix:** Retitle and broaden:

```markdown
## Step 4: Non-spec repository workflow

This applies to all repositories outside the core spec — SDKs, Inspector, Registry,
extensions, scaffolding tools, and any new repos added to the org.

1. Check for an existing issue before starting work
2. Join the repo's Discord channel (if one exists) — see §8
3. Follow the repo-specific CONTRIBUTING.md (overrides this skill where they conflict)
4. Write tests before submitting — coverage expectations vary by repo
5. For SDK repos specifically: match the SDK's language idioms, not just the spec's patterns
```

---

## Issue #4: [refresh 2026-04-19] drift or gaps detected

**Problem:** Automated refresh detected content drift from upstream sources.

**Fix:** This requires running `refresh.sh` and updating SKILL.md sections that have drifted. Specific actions:

1. Run `./refresh.sh` to generate `refresh-report.md` with specific URLs that drifted
2. For each drifted URL, fetch current content and update the corresponding SKILL.md section
3. Update `hashes.json` with new SHA-256 hashes
4. Commit with message: `chore: sync with upstream MCP docs (refresh 2026-04-23)`

---

## Gap: No worked example for small-change PRs

**Problem:** §6.6 has a worked example for SEP-2133 (a major change), but there's no equivalent for the more common small-change path (§3). New contributors are more likely to start with a typo fix or doc improvement.

**Fix:** Add a §3.5.1 worked example:

```markdown
### §3.5.1 Worked example — docs typo fix

**Scenario:** You notice a broken link on modelcontextprotocol.io/community/contributing.

1. Fork `modelcontextprotocol/docs` → your-username/docs
2. `git clone` your fork; `cd docs`
3. `git checkout -b fix/contributing-broken-link`
4. Find and fix the link in the MDX source
5. `npm run dev` — verify the fix renders correctly locally
6. `git commit -m "fix: repair broken link in contributing guide"`
7. `git push origin fix/contributing-broken-link`
8. Open PR:
   - Title: `fix: repair broken link in contributing guide`
   - Body: "Fixes broken link to [page]. Verified locally with `npm run dev`."
   - Labels: `documentation`

**Timeline:** Typically reviewed within 48 hours for docs-only changes.
**Common mistake:** Editing the wrong file — Mintlify docs sometimes have source files
in unexpected directories. Use `grep -r "broken text"` to find the right file.
```

---

## Gap: 17 GAP-MED sources not yet ingested

**Problem:** `sources.yml` shows 17 sources marked `gap-med` — these include tutorials, SDK-specific docs, debugging tools, and specification details that would help contributors but aren't in the skill.

**Priority ingestion candidates (highest value for contributors):**

1. **Inspector usage guide** — Contributors need to test their changes; Inspector is the primary debugging tool
2. **SDK-specific CONTRIBUTING.md files** — Each SDK has its own requirements; the skill should at least summarize the key differences
3. **Transport specification details** — Needed for anyone working on transport-related changes (HTTP, SSE, stdio)
4. **Registry documentation** — Increasingly important as the ecosystem grows

**Fix:** For each priority source:
1. Fetch current content
2. Distill into 3-5 actionable bullets (not full reproduction)
3. Add as a subsection of the relevant step
4. Mark as `covered` in `sources.yml`
5. Add SHA-256 hash to `hashes.json`

---

## Gap: Stale source inventory

**Problem:** `sources.yml` was indexed 2026-04-16. The MCP ecosystem moves fast — new repos, new docs pages, and new SEPs appear regularly.

**Fix:** Add to `refresh.sh`:

```bash
# Check for new pages not in sources.yml
echo "## New pages scan" >> "$REPORT"
curl -s https://modelcontextprotocol.io/llms.txt | while read -r url; do
  if ! grep -q "$url" sources.yml; then
    echo "NEW: $url" >> "$REPORT"
  fi
done
```

This surfaces new docs pages that should be triaged into covered/gap-med/gap-low.

---

## Gap: No contribution tracking across sessions

**Problem:** The skill has a `## Session log` placeholder but no structured format for tracking contributions in progress. A contributor might start a PR in one session and need to continue in another.

**Fix:** Define the session log format:

```markdown
## Session log

| Date | Repo | Type | Status | Branch | PR | Notes |
|------|------|------|--------|--------|----|-------|
| 2026-04-23 | docs | typo fix | merged | fix/broken-link | #456 | — |
| 2026-04-20 | spec | SEP | draft | sep/new-transport | — | Awaiting sponsor |
```

Populate on every activation. Check for in-progress contributions at session start.
