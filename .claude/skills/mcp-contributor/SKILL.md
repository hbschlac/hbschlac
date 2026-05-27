---
name: mcp-contributor
description: >
  Skill for contributing upstream to the Model Context Protocol (MCP)
  governance org. Covers triage, env setup, fork/branch/PR workflow,
  schema changes, SEP lifecycle, and AI-contribution disclosure.
  NOT for building your own MCP servers.
---

# MCP Contributor

End-to-end guide for contributing to the **Model Context Protocol** governance org (`github.com/modelcontextprotocol`). Covers the spec repo, official SDKs, tools, extensions, and docs.

**Not for:** building your own MCP servers/clients.

**Conflict:** When active, code-builder defers to this skill's workflow for code changes.

**Usage note:** As of May 2026, this skill has had zero real-world contributions beyond dry runs. The drift detection automation is active but the anchor bug (see Known Issues) generates false positives weekly. Fix the anchor bug before investing in new features.

---

## Step 0: Announce activation

> `mcp-contributor activated — [triage | spec PR | SDK PR | SEP draft | drift fix]. [reason]`

---

## Step 0.5: Protocol primer

**Three participants:**
- **MCP Host** — the AI app (Claude Desktop, VS Code, Cursor) that orchestrates clients
- **MCP Client** — lives inside the host, one dedicated connection per server
- **MCP Server** — provides context/tools to a client. Local (STDIO) or remote (HTTP).

**Two layers:**
- **Data layer** — JSON-RPC 2.0. Lifecycle, capability negotiation, primitives, notifications.
- **Transport layer** — stdio (local) or Streamable HTTP (remote). Swappable.

**Server primitives:** Tools (functions), Resources (data), Prompts (templates).
**Client primitives:** Sampling (LLM completion), Elicitation (user input), Logging, Roots.

**Lifecycle:** initialize → initialized notification → operation → shutdown.
**Versioning:** current spec rev is `2025-11-25` (date-based).

---

## Step 1: Triage

"Does this change what goes on the wire between client and server?"
- Yes → SEP (section 5)
- No, but changes SDK API → issue + PR in the SDK repo (section 4)
- No, purely docs/examples → direct PR

### Small changes (direct PR, no SEP)

Bug fixes, typos, doc improvements, broken links, adding examples to
`schema/draft/examples/[TypeName]/`, test improvements.

### Major changes (SEP required)

New protocol features, breaking changes, message format changes, new
interoperability standards, governance changes.

---

## Step 2: Environment setup

```bash
gh repo fork modelcontextprotocol/{repo} --clone
cd {repo}
```

### Repo map

| Repo | Language | What |
|------|----------|------|
| `specification` | TypeScript/Markdown | Protocol spec + JSON Schema |
| `typescript-sdk` | TypeScript | Reference SDK |
| `python-sdk` | Python | Official SDK |
| `java-sdk` / `kotlin-sdk` / `csharp-sdk` / `swift-sdk` / `go-sdk` / `rust-sdk` / `ruby-sdk` / `elixir-sdk` | Various | Official SDKs |
| `inspector` | TypeScript | MCP debugging tool |
| `registry` | TypeScript | Server registry |
| `docs` | MDX | modelcontextprotocol.io |
| `ext-*` | Various | Extension repos |
| `access` / `.github` | — | Governance / org config |

### Branch naming

`{type}/{short-description}` — e.g., `fix/sampling-timeout-handling`.

---

## Step 3: Spec and schema changes

Schema: `schema/draft/schema.json`. Validate: `npm run validate`. Test: `npm test`.

- All new fields must have `description`
- Enum values use lowercase_snake_case
- New capabilities go under `capabilities` in InitializeResult
- Backward compat: new optional fields OK; removing/renaming requires SEP

---

## Step 4: Non-spec repo PRs

1. **Issue first.** Describe the bug/enhancement. Wait for maintainer acknowledgment. Exception: obvious typos.
2. **Branch from default.** Follow repo's code style. Add/update tests. Reference: `Fixes #123`.
3. **CI must pass.** Fix failures before requesting review.

---

## Step 5: SEP lifecycle

1. Draft → 2. Review → 3. Accepted → 4. Implemented → 5. Stable

Required sections: Motivation, Design, Alternatives considered, Backward compatibility, Security considerations.

Open an issue titled `SEP: {short title}` with the full proposal.

---

## Step 6: AI-contribution disclosure

All AI-assisted contributions must be disclosed in the PR description:

> This contribution was made with AI assistance (Claude Code).

---

## Step 7: Drift detection

Weekly GitHub Action hashes modelcontextprotocol.io pages and compares against `sources.yml`. Files issues on drift.

### Drift response

1. Check if changed content affects SKILL.md guidance
2. If yes: update SKILL.md, close issue with commit SHA
3. If no: close with "reviewed, no skill impact"
4. If new pages: classify in sources.yml

### Escalation

If the same anchor miss appears in 3+ consecutive reports, it's stale — fix the source.

---

## Known Issues

1. **Anchor bug in refresh.sh (P0):** `sources.yml` references `## Step 11.1:` but SKILL.md uses `### 11.1 Design Principles`. This generates 11 false-positive anchor misses every week (issues #4-8). **Fix:** update `sources.yml` anchors. Requires laptop execution in the mcp-contributor repo.

2. **Issues #1-3 unresolved since April 17:** Structural fixes documented but not applied. See CLAUDE.md laptop instructions.

3. **Zero real-world usage:** The skill was designed and validated but never deployed on an actual MCP contribution. The drift detection runs, but no PR to the MCP org has been submitted using this skill.

---

## Changelog

- **2026-05-27 — v3: added zero-usage disclosure and known issues section**
  - Added: explicit "zero real-world usage" note
  - Added: Known Issues section with anchor bug, unresolved issues, and usage status
  - Condensed: repo map into a more compact format
  - Kept: all v2 structural improvements
- **2026-05-24 — v2: consolidated from 25 session branches**
- **2026-04-17 — v1: initial version**
