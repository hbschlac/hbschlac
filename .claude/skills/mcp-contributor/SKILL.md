---
name: mcp-contributor
description: >
  Skill for contributing upstream to the Model Context Protocol (MCP)
  governance org — the spec, official SDKs, and docs at
  github.com/modelcontextprotocol. Covers triage (small change vs SEP),
  env setup, fork/branch/PR workflow, schema changes, docs changes, full
  SEP lifecycle, and AI-contribution disclosure. Includes drift detection
  with auto-remediation. NOT for building your own MCP servers.
---

# MCP Contributor

End-to-end guide for contributing to the **Model Context Protocol** governance org (`github.com/modelcontextprotocol`). Covers the spec repo, all 10 official SDKs, tools, extensions, and docs.

**Not for:** building your own MCP servers/clients.

**Conflict:** When active, code-builder defers to this skill's workflow for code changes.

---

## Step 0: Announce activation

> `mcp-contributor activated — [triage | spec PR | SDK PR | SEP draft | drift fix]. [one-line reason]`

---

## Step 0.5: Protocol primer

**Three participants:**
- **MCP Host** — the AI app (Claude Desktop, VS Code, Cursor) that orchestrates clients
- **MCP Client** — lives inside the host, maintains one dedicated connection per server
- **MCP Server** — provides context/tools to a client. Local (STDIO) or remote (HTTP).

**Two layers:**
- **Data layer** — JSON-RPC 2.0. Lifecycle, capability negotiation, primitives, notifications.
- **Transport layer** — stdio (local) or Streamable HTTP (remote). Transport is swappable.

**Server primitives:** Tools (functions), Resources (data), Prompts (templates).
**Client primitives:** Sampling (LLM completion), Elicitation (user input), Logging, Roots (filesystem boundaries).

**Lifecycle:** initialize → initialized notification → operation → shutdown.
**Versioning:** current spec rev is `2025-11-25` (date-based).

---

## Step 1: Triage the contribution type

### 1.1 The core question

"Does this change what goes on the wire between client and server?"
- Yes → SEP (section 5)
- No, but changes how SDKs expose the protocol → issue + PR in the SDK repo
- No, purely docs/examples → direct PR

For protocol capability questions, see §0.5 Protocol Primer.

### 1.2 Small changes — Direct PR (no SEP)

- Bug fixes and typo corrections
- Documentation improvements, broken links, incomplete examples
- Adding examples to existing features (JSON in `schema/draft/examples/[TypeName]/`)
- Minor schema fixes that don't change behavior
- Test improvements

### 1.3 Major changes — SEP required (section 5)

- New protocol features or API methods
- Breaking changes to existing behavior
- Message format or schema structure changes
- New interoperability standards
- Governance or process changes

### 1.4 Non-spec repo PRs

Bug fixes in SDKs, Inspector, Registry, ext-* repos go through section 4 (issue first, then PR). If the bug is actually a spec ambiguity, escalate to SEP.

SDK-local breaking changes (dropping a dep, renaming public API, raising language min version) do NOT change the MCP wire protocol and do NOT require an SEP.

---

## Step 2: Environment setup

### 2.1 Fork and clone

```bash
gh repo fork modelcontextprotocol/{repo} --clone
cd {repo}
```

### 2.2 Repo map

| Repo | Language | What |
|------|----------|------|
| `specification` | TypeScript (schema), Markdown (spec) | Protocol spec + JSON Schema |
| `typescript-sdk` | TypeScript | Reference SDK |
| `python-sdk` | Python | Official SDK |
| `java-sdk` | Java | Official SDK |
| `kotlin-sdk` | Kotlin | Official SDK |
| `csharp-sdk` | C# | Official SDK |
| `swift-sdk` | Swift | Official SDK |
| `go-sdk` | Go | Official SDK |
| `rust-sdk` | Rust | Official SDK |
| `ruby-sdk` | Ruby | Official SDK |
| `elixir-sdk` | Elixir | Official SDK |
| `inspector` | TypeScript | MCP debugging tool |
| `registry` | TypeScript | Server registry |
| `docs` | MDX | modelcontextprotocol.io |
| `ext-*` | Various | Extension repos |
| `access` | — | Governance / access control |
| `.github` | — | Org-level config |

### 2.3 Branch naming

`{type}/{short-description}` — e.g., `fix/sampling-timeout-handling`, `feat/task-progress-events`, `docs/elicitation-examples`.

---

## Step 3: Spec and schema changes

### 3.1 Schema location

`schema/draft/schema.json` — the canonical JSON Schema for the protocol.

### 3.2 Change process

1. Make schema changes in `schema/draft/schema.json`
2. Run `npm run validate` to check schema validity
3. If adding a new type, add examples in `schema/draft/examples/{TypeName}/`
4. Update the corresponding spec prose in `docs/specification/draft/`
5. Run `npm test` for full validation

### 3.3 Schema change rules

- All new fields must have `description` in the schema
- Enum values use lowercase_snake_case
- New capabilities go under `capabilities` in InitializeResult
- Backward compatibility: new optional fields OK, removing/renaming fields requires SEP

---

## Step 4: Non-spec repo PRs

### 4.1 Issue first

Open an issue describing the bug or enhancement. Wait for maintainer acknowledgment before investing in a PR. Exception: obvious typos and broken links.

### 4.2 PR process

1. Branch from `main` (or the repo's default branch)
2. Follow the repo's existing code style and patterns
3. Add/update tests
4. Update docs if behavior changes
5. Reference the issue: `Fixes #123`

### 4.3 CI requirements

Most repos have CI that must pass. Common checks: lint, test, typecheck, build. Fix failures before requesting review.

---

## Step 5: SEP lifecycle

### 5.1 What is a SEP?

Specification Enhancement Proposal. A structured document proposing a significant protocol change, discussed in public before implementation.

### 5.2 SEP stages

1. **Draft** — Author writes the proposal
2. **Review** — Community discussion (GitHub issue + spec discussion)
3. **Accepted** — Maintainers approve
4. **Implemented** — Code lands in spec + reference SDK
5. **Stable** — Released in a dated spec revision

### 5.3 Writing a SEP

Required sections:
- **Motivation:** Why this change? What problem does it solve?
- **Design:** Technical specification of the change
- **Alternatives considered:** What else was evaluated and why this approach wins
- **Backward compatibility:** Impact on existing clients/servers
- **Security considerations:** Any security implications

### 5.4 SEP discussion

Open an issue titled `SEP: {short title}` with the full proposal. Tag it `sep` if the label exists. Link to any related issues or prior art.

---

## Step 6: AI-contribution disclosure

All contributions made with AI assistance must be disclosed. Add to the PR description:

> This contribution was made with AI assistance (Claude Code).

This is a governance requirement, not optional.

---

## Step 7: Drift detection (automated)

The mcp-contributor repo includes a weekly GitHub Action that:
1. SHA-256 hashes each source page from modelcontextprotocol.io
2. Compares against stored hashes in `sources.yml`
3. Files a GitHub issue if drift is detected or new pages appear

### Known issue: anchor mismatches

`sources.yml` references heading anchors like `## Step 11.1:` but SKILL.md
uses `### 11.1 Design Principles`. This causes 11 false-positive anchor misses
every week (issues #4-#8). **Fix:** update `sources.yml` anchors to match
actual SKILL.md headings. Requires laptop execution in the mcp-contributor repo.

**Escalation:** If the same anchor miss appears in 3+ consecutive reports, it's
stale — fix the source, don't keep triaging it.

### Drift response protocol

When a drift issue is filed:
1. Check if the changed content affects SKILL.md guidance
2. If yes: update SKILL.md, close the issue with the commit SHA
3. If no: close with "reviewed, no skill impact"
4. If new pages: classify as covered / gap-high / gap-med / gap-low in sources.yml

---

## Changelog

- **2026-05-24 — v2: consolidated from 25 session branches**
  - Added complete repo map (was missing Inspector, Registry, ext-*, access, .github)
  - Added cross-reference from triage (S1) to Protocol Primer (S0.5)
  - Retitled S4 from "SDK workflow" to "Non-spec repo workflow" (covers Inspector, Registry, etc.)
  - Documented anchor-mismatch bug explicitly with fix instructions
  - Added drift response protocol with escalation rule
  - Added conflict declaration (code-builder defers to this skill)
