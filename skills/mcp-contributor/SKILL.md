---
name: mcp-contributor
description: >
  Skill for contributing upstream to the Model Context Protocol governance org —
  the spec, official SDKs, and docs at github.com/modelcontextprotocol.
  Not for building your own MCP servers — use mcp-builder for that.
---

# mcp-contributor

## 0. Announcement (every activation)

```
🔧 mcp-contributor activated — [triage | spec PR | SDK PR | SEP draft | good-first-issue]. [one-line reason].
```

## 0b. Staleness guard (NEW)

Before proceeding, check: are there unresolved drift issues in the mcp-contributor repo?

- If ≥2 drift issues are open: announce "⚠ Skill content may be outdated ({N} drift issues unresolved since {oldest date}). Governance details and repo maps should be verified against source before relying on them. Run `refresh.sh` to update."
- Proceed with the task but flag any governance/process claims as "verify against source."

---

## 1. Triage decision (critical path)

### Quick-start: "I just want to contribute something" (NEW)

If you're new to MCP or want a low-friction first contribution:

1. Run: `gh search issues 'org:modelcontextprotocol label:"good first issue" state:open' --limit 30`
2. Pick one that matches your language/area interest
3. Follow the §3 small-change workflow below
4. Skip SEP entirely — good-first-issues never need one

This is the realistic starting point. Most first contributions are doc fixes, test improvements, or example additions — not spec changes.

### Small changes → Direct PR (§3)
- Bug fixes and typos
- Documentation improvements
- Adding examples to existing features
- Minor schema fixes without behavior changes
- Test improvements

### Major changes → SEP required (§5)
- New protocol features or API methods
- Breaking changes to existing behavior
- Changes to the message format or schema structure
- New interoperability standards
- Governance or process changes

### Gray-zone decision tree
1. Does this change what's on the wire between client and server? → SEP
2. Does it add, rename, or remove a field, method, or capability? → SEP
3. Could a conformant existing implementation break? → SEP
4. Is this a new interop standard? → SEP
5. Does it change how maintainers make decisions? → SEP
6. None of the above and ≤~200 lines? → Direct PR
7. Still unsure? → Post description in Discord `#general` or GitHub Discussions first

### Capability questions → lifecycle docs (NEW — fixes issue #1)

If the user asks "can MCP do X?" or "does MCP support Y?":
1. Check the protocol primer (§10) for current primitives
2. Check the roadmap priorities (§9) for planned features
3. If the capability exists: point to the relevant spec section
4. If planned: point to the relevant SEP and its status in the lifecycle (§5)
5. If neither: suggest filing a Discussion or drafting an SEP

---

## 2. Prerequisites

**All contributions:**
- Git (recent version)
- GitHub account with 2FA enabled

**Spec repo (`modelcontextprotocol/modelcontextprotocol`):**
- Node.js 24+, npm 11+

**SDK contributions:**
- Install per-language toolchain per repo's `CONTRIBUTING.md` and `.tool-versions`/`mise.toml`/`asdf`

---

## 3. Small-change workflow

```bash
gh repo fork modelcontextprotocol/modelcontextprotocol --clone=false
git clone https://github.com/YOUR-USERNAME/modelcontextprotocol.git
cd modelcontextprotocol
npm install
npm run check
git checkout -b fix/<short-description>
# Make changes
npm run generate:schema   # if schema changed
npm run check
npm run format
git commit -m "Fix typo in tools documentation (#123)"
git push origin fix/<short-description>
gh pr create --fill
```

**Schema source of truth:** `schema/draft/schema.ts`. After editing, always run `npm run generate:schema`.

---

## 3.5. MDX + Mintlify for docs

MCP docs use MDX (Markdown + JSX) and Mintlify rendering.

**Key rules:**
- File extension `.mdx` for files using components
- Standard Markdown still works
- Leave blank lines between Markdown and JSX blocks
- Escape `{` and `}` as `\{` `\}` for literals

**Common Mintlify components:**
`<Note>`, `<Tip>`, `<Warning>`, `<Info>`, `<Check>`, `<Steps>`, `<Step>`, `<Card>`, `<CardGroup>`, `<Accordion>`, `<Tab>`, `<Tabs>`, `<CodeGroup>`, `<Frame>`, `<Icon>`

**Required page frontmatter:**
```yaml
---
title: "Page Title"
description: "One-line description"
icon: "book"
sidebarTitle: "Short"
---
```

**Validation:**
```bash
npm run serve:docs     # live preview :3000
npm run check:docs     # link-check + formatting
npm run check          # full pre-PR validation
npm run format         # auto-fix formatting
```

---

## 4. Repository contribution workflow

> Previously titled "SDK workflow" — renamed because this applies to all non-spec repos, not just SDKs. (Fixes issue #3)

1. **Open an issue first** describing your approach
2. **Join the relevant Discord channel** (`#general-sdk-dev` for cross-SDK work)
3. **Read the repo's CONTRIBUTING.md** — setup and style vary per repo
4. **Write tests** — bug fix includes repro test; new feature includes coverage

---

## 5. SEP (Specification Enhancement Proposal) process

### SEP types
- **Standards Track:** New feature / implementation / interop standard
- **Informational:** Design issue or guideline; no new feature
- **Process:** Change to MCP process itself

### SEP lifecycle

```
Idea → (PR with SEP file) → Awaiting Sponsor (up to 6mo)
         ↓         ↓           ↓
       Draft    Dormant    Withdrawn
         ↓
      In-Review
         ↓
    Accepted  |  Rejected
         ↓
     Final (reference impl merged)
```

**Status definitions:**
- `draft`: Has sponsor; informal review
- `in-review`: Ready for Core Maintainer review
- `accepted`: Approved; awaiting reference implementation
- `rejected`: Declined
- `withdrawn`: Author pulled it
- `final`: Reference impl merged
- `superseded`: Replaced by newer SEP
- `dormant`: No sponsor within 6 months — NOT rejected; revivable

### Pre-draft checklist
1. Validate idea in relevant WG/IG Discord channel or GitHub Discussions
2. Check alignment with project roadmap and design principles (§8)
3. Build a prototype (mandatory before acceptance)
4. Identify 1-2 candidate sponsors from MAINTAINERS.md

### Prototype requirement
**Mandatory before acceptance.** Acceptable forms:
- Working branch/fork in an official SDK
- Standalone proof-of-concept
- Integration tests showing proposed behavior
- Reference server/client implementing the feature

Must be runnable by reviewers. Does NOT need to be production-ready.

### SEP file structure

**Filename:** `0000-your-feature-title.md` initially; rename using PR number after opening.

**Required sections:**
1. Preamble (title, authors, status, type, PR number)
2. Abstract (~200 words)
3. Motivation (why current spec is inadequate — weak motivation = auto-reject)
4. Specification (syntax + semantics for independent implementations)
5. Rationale (design decisions, alternatives, community consensus)
6. Backward Compatibility (incompatibilities, migration path)
7. Reference Implementation (required for `final`)
8. Security Implications (explicit; no hand-waving)

### Submission steps
1. Draft `0000-<title>.md` following structure
2. Open PR adding it to `seps/`
3. Rename using PR number; update header
4. Tag 1-2 relevant maintainers as sponsor candidates; cross-post in Discord
5. No response after 2 weeks → ask in `#general`
6. Sponsor assigns + sets status to `draft`
7. Iterate in PR comments
8. Sponsor flips to `in-review` → biweekly Core Maintainer meeting
9. Resolution: `accepted` / `rejected` / returned
10. If accepted: complete reference implementation → sponsor flips to `final`

---

## 6. Repo map

| Repo | Contents | Notes |
|------|----------|-------|
| [`modelcontextprotocol`](https://github.com/modelcontextprotocol/modelcontextprotocol) | Spec, docs, SEPs | Primary |
| [`typescript-sdk`](https://github.com/modelcontextprotocol/typescript-sdk) | TS/JS SDK | |
| [`python-sdk`](https://github.com/modelcontextprotocol/python-sdk) | Python SDK | |
| [`go-sdk`](https://github.com/modelcontextprotocol/go-sdk) | Go SDK | Partner co-maintained |
| [`java-sdk`](https://github.com/modelcontextprotocol/java-sdk) | Java SDK | |
| [`kotlin-sdk`](https://github.com/modelcontextprotocol/kotlin-sdk) | Kotlin SDK | JetBrains co-maintained |
| [`csharp-sdk`](https://github.com/modelcontextprotocol/csharp-sdk) | C# SDK | Microsoft co-maintained |
| [`swift-sdk`](https://github.com/modelcontextprotocol/swift-sdk) | Swift SDK | |
| [`rust-sdk`](https://github.com/modelcontextprotocol/rust-sdk) | Rust SDK | |
| [`ruby-sdk`](https://github.com/modelcontextprotocol/ruby-sdk) | Ruby SDK | |
| [`php-sdk`](https://github.com/modelcontextprotocol/php-sdk) | PHP SDK | |
| [`inspector`](https://github.com/modelcontextprotocol/inspector) | MCP Inspector — debug/test tool | **(NEW — fixes issue #2)** |
| [`registry`](https://github.com/modelcontextprotocol/registry) | MCP Server Registry | **(NEW — fixes issue #2)** |
| `ext-*` repos | Extension experiments | **(NEW — fixes issue #2)** Check org for current list; these follow the Extensions Framework (SEP-2133) |

---

## 7. Governance structure

### Role hierarchy

| Role | Scope | Authority |
|------|-------|-----------|
| Lead Maintainers (BDFL) | Final decision authority | Veto any decision; appoint/remove Core Maintainers |
| Core Maintainers | Project direction + spec | Veto by majority; resolve disputes |
| Maintainers | Specific area (SDK, docs, WG) | Write access to their repo(s) |
| Contributors | Anyone filing issues/PRs | Default participation |

### Contributor ladder (SEP-2148)

| Role | Min timeline | Sponsorship | Key privileges | Inactivity |
|------|-------------|-------------|----------------|------------|
| Contributor | Immediate | None | Open issues/PRs, join discussions | — |
| Member | 2-3 mo active | 2 Members (different orgs) OR 1 Core/Lead | Org membership, triage, `/lgtm` | 3 mo |
| Maintainer | 6+ mo as Member | 1 Maintainer/Core + Core approval | Merge in area, sponsor Maintainers | 6 mo |
| Core Maintainer | 6+ mo as Maintainer | Majority Core + Lead approval | Final approval on breaking changes, SEP voting | 6 mo |
| Lead Maintainer | Succession only | Existing Leads appoint | Veto, appoint Core | Lifetime |
| Community Moderator | Parallel track | 1 Core/Lead | Moderation, CoC enforcement | Removable for cause |

2FA required at all non-Contributor levels.

### Escalation matrix

| Issue | First escalation | Second | Timeline |
|-------|-----------------|--------|----------|
| Technical disagreement in PR | Maintainer | Core Maintainer | 5 biz days |
| Technical disagreement in WG | WG Lead | Core Maintainer | 5 biz days |
| Dispute with WG Lead/IG Facilitator | Core Maintainer | Lead Maintainer | 7 biz days |
| Dispute with Maintainer | Core Maintainer | Lead Maintainer | 7 biz days |
| Core Maintainer disagreement | Lead Maintainer | — | 10 biz days |
| CoC violation | Community Moderator | Core Maintainer | Immediate |
| Security issue | Core Maintainer | Lead Maintainer | Immediate |

---

## 7b. Working groups & interest groups

| | Interest Group (IG) | Working Group (WG) |
|---|---|---|
| Purpose | Identify + discuss problems | Build concrete solutions |
| Output | Problem statements, use cases | SEPs, implementations, code |
| Duration | Ongoing | Until deliverables done |
| Decisions | Rough consensus, non-binding | Binding (lazy consensus → vote → escalation) |

**Active WGs:** Registry, Triggers & Events, Server Identity, Agents, Inspector V2, MCP Apps, Fine-Grained Auth, Transports, Mixup Protection, SDKs

**Active IGs:** Primitive Grouping, Skills Over MCP, Gateways, Financial Services

Charter files: `docs/community/<group-name>/charter.mdx`

---

## 8. Design principles (SEP pre-flight)

1. **Convergence over choice** — one way to solve a problem
2. **Composability over specificity** — don't add features buildable from primitives
3. **Interoperability over optimization** — degrade gracefully via capability negotiation
4. **Stability over velocity** — "no" leaves door open; "yes" closes it
5. **Capability over compensation** — don't add structure for temporary model limitations
6. **Demonstration over deliberation** — working prototype > theory
7. **Pragmatism over purity** — accept inconsistency for adoption
8. **Standardization over innovation** — codify proven patterns

---

## 8b. Communication & Discord

### Channel map

| Channel | Purpose |
|---------|---------|
| Discord | Real-time contributor chat |
| meet.modelcontextprotocol.io | Live WG/IG meetings |
| GitHub Discussions | Proposals, roadmap, feature requests |
| GitHub Issues | Bug reports with repro, documented fixes |
| PR to `seps/` | SEP submission (NOT Issues) |
| SECURITY.md | Vulnerability reports ONLY |

**Critical:** Feature requests → Discussions. Bugs → Issues. SEPs → PR.

### Discord rules (strict)
1. Server advances MCP as protocol — not user support
2. No self-promotion beyond introduction
3. Solicitation of work is bannable
4. Display name: `name (company)` or `username (company)` before first post
5. Use threads for multi-message discussions
6. No vendor marketing
7. Security issues → SECURITY.md only
8. Decisions heading toward action → move to GitHub

### Before first Discord post
1. Set display name to `name (company)` format
2. Read server-wide rules channel
3. Read pinned messages in target channel
4. Check channel description
5. Scroll back ~50 messages to observe norms
6. Start a thread for anything multi-message
7. **Check employer OSS policy** — some employers require approval before contributing to open-source projects under your company affiliation (v0.2.3)

---

## 9. Roadmap-aligned priorities

SEPs aligned with these areas get expedited review:

1. **Transport Evolution** — Streamable HTTP, session handling, Server Cards
2. **Agent Communication** — Tasks primitive (SEP-1686) lifecycle gaps
3. **Governance Maturation** — Contributor Ladder, WG delegation, charter template
4. **Enterprise Readiness** — audit trails, SSO, gateway/proxy patterns

### On the horizon
- Triggers & Event-Driven Updates
- Result Type Improvements
- Security & Authorization (DPoP SEP-1932, Workload Identity SEP-1933)
- Extensions Ecosystem (SEP-2133)

---

## 10. Protocol primer

**Three participants:**
- MCP Host (AI app orchestrating clients)
- MCP Client (one connection per server)
- MCP Server (provides context/tools)

**Server primitives:** Tools, Resources, Prompts
**Client primitives:** Sampling, Elicitation, Logging, Roots
**Utility:** Tasks (experimental, SEP-1686)

**Lifecycle:** initialize → capabilities exchange → initialized notification → normal flow

**Current spec version:** `2025-11-25`

---

## 11. Licensing & IP

MCP is under Linux Foundation governance.

| Contribution | License |
|-------------|---------|
| Code | Apache 2.0 |
| Specification | Apache 2.0 |
| Docs (non-spec) | CC-BY 4.0 |
| SEP documents | Public domain / CC0 |

No CLA. Contributors retain copyright. Outbound = inbound.

### AI contribution disclosure
Disclose in PR body: "Drafted with Claude; I reviewed and tested all changes."
You must be able to explain, justify, and verify the change.

---

## 12. Good PR checklist

- [ ] Focused on ONE issue
- [ ] Descriptive commits
- [ ] Issue number referenced
- [ ] All CI checks green
- [ ] `npm run check` passes locally
- [ ] Tests/examples added where applicable
- [ ] AI-assist disclosed if used

---

## Session log

<!-- 2026-04-16: skill scaffolded from modelcontextprotocol.io/community/contributing -->
<!-- 2026-05-14: v0.3.0 — addressed issues #1 (capability→lifecycle pointer in §1), #2 (repo map in §6), #3 (§4 title rename). Added staleness guard, good-first-issue fast path, employer OSS check. -->
