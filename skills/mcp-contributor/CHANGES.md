# mcp-contributor: Audit Changes (2026-05-21)

## Context
Audit of skill usage, effectiveness, and gaps based on build-log analysis, session patterns, and cross-skill review.

## Finding: Zero real-world usage in 5 weeks
The session log at the bottom of SKILL.md is empty beyond two dry-run comments from April 16. The skill was built and validated but never deployed on an actual MCP contribution.

**Recommendation:** Pick a concrete first contribution (a good-first-issue from the SDK repos) and use the skill end-to-end. The skill's value can only be validated through real usage. The dry-runs tested triage logic; real usage will test the workflow and surface missing guidance.

## Change 1: Add code-builder composability note

After the "Not for:" line at the top, add:

```md
**Composability:** When this skill triggers for code work (SDK bug fix, prototype implementation, schema changes), also activate `code-builder` for the coding portion. mcp-contributor handles process/governance; code-builder handles code quality. They don't conflict.
```

## Change 2: Fix mcp-builder reference

Line 5 references `mcp-builder` but no such skill exists in any repo. Either:
- A) Create mcp-builder as a real skill
- B) Remove the reference and replace with: "Not for: building your own MCP servers/clients. For that, use Claude's standard coding capabilities or the code-builder skill."

## Change 3: Add token budget awareness

The skill is 1,176 lines / ~77KB. When loaded into a Claude Code session, this consumes substantial context window. Add a note at the top:

```md
**Token budget:** This skill is large (~1,200 lines). For quick triage questions ("is this an SEP or a PR?"), Claude should answer from Steps 1-2 without loading the full reference appendix into working memory. Steps 11.x are reference material — consult only when actively drafting a spec PR, schema change, or SEP.
```

## Change 4: Update sources.yml freshness

The sources were fetched 2026-04-16. The MCP spec and governance docs may have changed in the 5 weeks since. Run `./refresh.sh` to check for drift before next use.

## Change 5: Session log activation

Replace the empty session log section with a stronger prompt:

```md
## Session log

Record every real use below. Format: `YYYY-MM-DD: [triage|PR|SEP] repo#number — one-line outcome + lesson`

**Goal: 3 real entries before next sync.** Dry-runs don't count.

<!-- 2026-04-16: skill scaffolded from modelcontextprotocol.io/community/contributing -->
<!-- 2026-04-16: dry-run #2 on modelcontextprotocol/inspector#832 — triage correct, no new bugs -->
```

## Change 6: Weekly refresh workflow may be inactive

The GitHub Actions workflow (.github/workflows/weekly-refresh.yml) runs on Sundays at 05:05 UTC. Verify:
1. Is the workflow enabled in the repo settings?
2. Has it run since April 16? Check Actions tab.
3. If the repo is private, Actions may be disabled by default.
