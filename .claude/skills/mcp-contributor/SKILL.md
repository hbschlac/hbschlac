# mcp-contributor

Claude Code skill for contributing upstream to the Model Context Protocol (MCP) — spec, SDKs, docs. Includes drift detection with auto-remediation.

## Activation

Triggers on: "contribute to MCP", "write an SEP", "MCP pull request", "update mcp-contributor", "fix drift", or any reference to modelcontextprotocol.io governance.

## Quick Reference: Three Contribution Paths

| Change type | Path | Decision rule |
|------------|------|---------------|
| Typos, docs, examples | Direct PR (section 3) | No wire-format change |
| Any non-spec repo work | Issue-first PR (section 4) | Inspector, Registry, SDKs, extensions |
| Spec/wire-format changes | SEP (section 5) | "Does this change what's on the wire between client and server?" |

**Gray-zone check (section 1.5):** Is this wiring up a capability/notification that already exists in the current spec rev (section 11.7)? If yes, it's a small change (section 3/4 PR), not an SEP.

## Prerequisites (section 2)

- Git + GitHub account with 2FA
- Spec repo: Node 24+, npm 11+
- SDK repos: per-language toolchain (Python 3.10+, Rust stable, Go 1.21+, etc.)

## Small PR Workflow (section 3)

```bash
gh repo fork modelcontextprotocol/modelcontextprotocol --clone=false
git clone https://github.com/YOUR-USERNAME/modelcontextprotocol.git
npm install && npm run check
git checkout -b fix/<desc>
# make changes
npm run generate:schema   # if schema touched
npm run format && git commit
gh pr create --fill
```

Docs authoring: MDX + Mintlify components (`<Note>`, `<Tip>`, `<Warning>`, `<Steps>`, `<Tabs>`). Validate with `npm run serve:docs`.

## Non-Spec Repo Workflow (section 4)

Applies to ALL non-spec repos, not just SDKs: Inspector, Registry, ext-* repos, infrastructure.

1. Open an issue first describing the change
2. Follow the repo's own CONTRIBUTING.md
3. Include tests matching the repo's test framework
4. PR against the repo's default branch

### Repo Map (section 6)

| Category | Repos |
|----------|-------|
| Specification | modelcontextprotocol/modelcontextprotocol |
| SDKs (Tier 1) | python-sdk, typescript-sdk |
| SDKs (Tier 2) | java-sdk, kotlin-sdk, csharp-sdk, swift-sdk, go-sdk, rust-sdk, ruby-sdk, elixir-sdk |
| Tools | inspector, inspector-v2 (in development), registry |
| Extensions | ext-* repos (per SEP-2133) |
| Infrastructure | access (per SEP-2149), .github |
| Governance | MAINTAINERS.md, CODE_OF_CONDUCT.md, SECURITY.md, CONTRIBUTING.md, ANTITRUST.md, GOVERNANCE.md |

## SEP Workflow (section 5)

1. Pre-discuss in Discord or relevant Working Group — validate the idea
2. Build a working prototype (mandatory)
3. Draft markdown with sections: preamble, motivation, spec changes, rationale, backward compat
4. Open PR; assign 1-2 sponsor candidates
5. Progress: Draft -> In-Review -> Accepted -> Final (requires reference implementation)

### Design Principles (section 11.1)

SEPs evaluated against: convergence, composability, interoperability, stability, capability, demonstration, pragmatism, standardization.

## Governance (section 5.5)

| Role | Access | Path |
|------|--------|------|
| Lead Maintainers (BDFL) | Final say | - |
| Core Maintainers | Biweekly meetings, dispute resolution | 6+ months as Maintainer |
| Maintainers | Repo-level write access | 6+ months as Member |
| Members | Triage | 2-3 months as Contributor |
| Contributors | PRs | Anyone |

Active Working Groups: Registry, Transports, Server Identity, Agents, Inspector V2, SDKs, Auth.

## Communication Rules (section 8)

**Discord non-negotiables:**
- Set display name to `name (company)` before posting
- Read server rules first — no self-promotion (rule #2 is strictly enforced)
- Check your employer's OSS policy before your first post
- Feature ideas go to GitHub Discussions, not Discord
- Bugs go to Issues with repro steps
- Use threads for multi-message conversations
- Security issues go through SECURITY.md private flow

**Antitrust:** Never discuss pricing, market allocation, or competitive strategy.

## Protocol Basics (section 0.5)

Three roles: MCP Host (AI app), MCP Client (connection manager), MCP Server (context provider).

Server primitives: Tools (functions), Resources (data), Prompts (templates).
Client primitives: Sampling (LLM completion), Elicitation (user input), Logging, Roots (file boundaries).

Current spec version: date-based (e.g. 2025-11-25).

## Drift Detection and Auto-Remediation

### Detection (refresh.sh — runs weekly via GitHub Actions)

Compares tracked source URLs against current state. Outputs:
- New pages in llms.txt not yet catalogued
- Broken anchor references in SKILL.md
- Content hash changes on covered pages

### Auto-Remediation (new)

When drift is detected, the skill doesn't just file an issue — it attempts to fix it:

**For new uncatalogued pages:**
1. Fetch the new page content
2. Classify priority: high (governance, spec changes), medium (SDK docs, guides), low (tutorials, examples)
3. For high-priority pages: draft the new section content and add to sources.yml
4. For medium/low: add to sources.yml with `status: gap` and appropriate priority tag

**For broken anchors:**
1. Fetch the current page and find the nearest matching heading
2. Update the anchor reference in both SKILL.md and sources.yml
3. If no match found, flag for manual review

**For content hash changes:**
1. Diff the old and new content
2. If the change is additive (new sections, expanded details): update SKILL.md to incorporate
3. If the change is structural (reorg, renamed sections): flag for manual review with a summary of what changed
4. If the change is a removal: flag for manual review

**Remediation output:**
- Auto-fixable changes: committed directly with message `[auto-remediate] {description}`
- Manual-review changes: filed as a single consolidated issue (not one per drift item) with a checklist of what needs human judgment

### Staleness Guard

If 3+ consecutive drift issues go unresolved, the next refresh adds a warning header to SKILL.md:

```
<!-- STALE: drift issues #N-#M unresolved. Sections may be outdated. -->
```

This makes staleness visible to anyone using the skill, rather than silently degrading.

## Key Reference Links

- Contributor Ladder: https://modelcontextprotocol.io/seps/2148-contributor-ladder
- SEP Guidelines: https://modelcontextprotocol.io/community/sep-guidelines
- Working Groups: https://modelcontextprotocol.io/community/working-interest-groups
- Communication: https://modelcontextprotocol.io/community/communication
- Roadmap: https://modelcontextprotocol.io/development/roadmap
- MAINTAINERS.md: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/MAINTAINERS.md
