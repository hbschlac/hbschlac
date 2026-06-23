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

**Usage note:** As of June 2026, this skill has had zero real-world contributions beyond dry runs. The drift detection automation is active but the anchor bug (see Known Issues) generates false positives weekly. Fix the anchor bug before investing in new features.

**Investment status: OVER-INVESTED.** This is the most maintained skill relative to its actual usage (zero). 10 open issues in the mcp-contributor repo, none resolved. Before doing ANY work on this skill: (1) fix the anchor bug, (2) close the stale issues, (3) make one real contribution to the MCP org. Until then, no further skill iteration.

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
**Versioning:** protocol version strings are date-based (`YYYY-MM-DD`). Check the current rev at the spec repo — do not trust a hardcoded value here.

---

## Step 1: Triage

"Does this change what goes on the wire between client and server?"
- Yes → SEP (section 5)
- No, but changes SDK API → issue + PR in the SDK repo (section 4)
- No, purely docs/examples → direct PR

If yes or unsure → read the lifecycle spec to understand capability negotiation before proceeding. Many "small" changes inadvertently affect the initialize/capabilities handshake.

### Small changes (direct PR, no SEP)

Bug fixes, typos, doc improvements, broken links, adding examples, test improvements.

### Major changes (SEP required)

New protocol features, breaking changes, message format changes, new interoperability standards, governance changes.

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
| `inspector` | TypeScript | MCP debugging tool — test servers interactively |
| `registry` | TypeScript | MCP server registry — discover and share servers |
| `docs` | MDX | modelcontextprotocol.io |
| `ext-*` (e.g. `ext-auth`) | Various | Official extensions — closely tied to SEPs |
| `access` | — | Member access management (internal, rarely needs external contribution) |
| `.github` | — | Shared org templates (meta-fixes via direct PR) |

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

## Step 4: Non-spec repo workflow (SDKs, Inspector, Registry, Extensions)

This workflow applies to any repo in the org that is NOT the main spec repo. Most commonly used for SDK contributions, but the same fork/branch/PR pattern works for Inspector, Registry, and extension repos.

1. **Issue first.** Describe the bug/enhancement. Wait for maintainer acknowledgment. Exception: obvious typos.
2. **Branch from default.** Follow repo's code style. Add/update tests. Reference: `Fixes #123`.
3. **CI must pass.** Fix failures before requesting review.

---

## Step 5: SEP lifecycle

1. Draft → 2. Review → 3. Accepted → 4. Implemented → 5. Stable

Required sections: Motivation, Design, Alternatives considered, Backward compatibility, Security considerations.

Open an issue titled `SEP: {short title}` with the full proposal.

SEP counts change regularly. Check the current index at the spec repo's SEPs directory before citing specific numbers.

### Finding a sponsor

SEPs require a Core Maintainer sponsor. To find one:

1. **Check MAINTAINERS.md** in the spec repo — lists who owns which area
2. **Look at recent SEP sponsors** — `git log --oneline seps/` shows who sponsored what
3. **Join the relevant Working Group** — WG leads are often willing to sponsor related SEPs
4. **Post in Discord** — describe your SEP in 3 sentences and ask if anyone is interested in sponsoring
5. **Attend a Core Maintainer review meeting** — present informally first

Don't DM maintainers without prior public discussion. Don't submit the SEP without a sponsor — it will stall.

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

## Step 8: Auth landscape

MCP auth is actively evolving. Key specs and SEPs:

- **RFC 8414** — OAuth 2.0 Authorization Server Metadata (discovery)
- **RFC 9728** — Protected Resource Metadata (how servers advertise auth requirements)
- **OAuth 2.1** — baseline authorization framework for MCP
- **DPoP** — Demonstration of Proof-of-Possession; prevents token replay
- **Workload Identity Federation** — machine-to-machine auth without shared secrets

**Before proposing auth changes:**
1. Check current SEP status for auth-related proposals — they may already address your concern
2. Read the auth tutorial at modelcontextprotocol.io
3. Auth SEPs require prototype implementations in at least one SDK before acceptance
4. Expect high scrutiny from Core Maintainers on any auth-related change

---

## Known Issues

1. **Anchor bug in refresh.sh (P0):** `sources.yml` references `## Step 11.1:` but SKILL.md uses `### 11.1`. This generates false-positive anchor misses every week (issues #4-8). **Fix:** update `sources.yml` anchors. Requires laptop execution in the mcp-contributor repo.

2. **Issues #1-3 unresolved since April 17:** Structural fixes documented but not applied.

3. **Zero real-world usage:** The skill was designed and validated but never deployed on an actual MCP contribution. The drift detection runs, but no PR to the MCP org has been submitted using this skill.

4. **Active working groups change.** Do not hardcode the list. Fetch the current groups from the MCP community page before citing.

5. **Discord invite link may rotate.** Reference the community page URL instead of a direct invite link.

6. **Over-maintenance without usage.** This skill has been iterated 4 times across 30+ sessions without a single real MCP contribution. Future sessions should NOT audit/improve this skill — instead, use it to make an actual contribution.

---
