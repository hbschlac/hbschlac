---
name: mcp-contributor
description: >
  Skill for contributing upstream to the Model Context Protocol (MCP)
  governance org — the spec, official SDKs, and docs at
  github.com/modelcontextprotocol. Covers triage (small change vs SEP),
  env setup, fork/branch/PR workflow, schema changes, docs changes, full
  SEP lifecycle, and AI-contribution disclosure. Includes drift detection
  with auto-remediation. NOT for building your own MCP servers — that's
  mcp-builder.
---

# MCP Contributor

End-to-end guide for contributing to the **Model Context Protocol** governance org (`github.com/modelcontextprotocol`). Covers the spec repo, all 10 official SDKs, tools, extensions, and docs.

**Not for:** building your own MCP servers/clients. Use `mcp-builder` for that.

---

## Step 0: Announce activation

Announce: `mcp-contributor activated — [triage | spec PR | SDK PR | SEP draft | drift fix]. [one-line reason]`

---

## Step 0.5: Protocol primer

Before touching schema or spec, know these. Full detail: https://modelcontextprotocol.io/docs/learn/architecture

**Three participants:**
- **MCP Host** — the AI app (Claude Desktop, VS Code, Cursor) that orchestrates clients
- **MCP Client** — lives inside the host, maintains one dedicated connection per server
- **MCP Server** — provides context/tools to a client. Local (STDIO) or remote (HTTP).

**Two layers:**
- **Data layer** — JSON-RPC 2.0. Lifecycle, capability negotiation, primitives, notifications.
- **Transport layer** — stdio (local) or Streamable HTTP (remote). Transport is swappable.

**Server primitives:** Tools (functions), Resources (data), Prompts (templates).
**Client primitives:** Sampling (LLM completion), Elicitation (user input), Logging, Roots (filesystem boundaries).
**Experimental:** Tasks (SEP-1686) — durable execution wrappers.

**Lifecycle:** initialize → initialized notification → operation → shutdown.
**Versioning:** current spec rev is `2025-11-25` (date-based).
**What MCP is NOT:** defines how context is exchanged, not how LLMs use that context.

---

## Step 1: Triage the contribution type

### 1.1 The core decision

If it changes the protocol spec or schema semantics → SEP (section 5). Otherwise → direct PR (section 3 or 4).

### 1.2 Small changes — Direct PR (no SEP needed)

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
- Complex/controversial topics with multiple valid designs

### 1.4 Non-spec repo PRs

Bug fixes in SDKs, Inspector, Registry, ext-* repos go through section 4 (issue first, then PR). If the bug is actually a spec ambiguity, escalate to SEP.

**SDK-local breaking changes** (dropping a dep, renaming a public API, raising a language min version): these do NOT change the MCP wire protocol and do NOT require an SEP — stay in section 4.

### 1.5 Gray-zone decision tree

Ask in order:

1. **Is this wiring up a capability/notification that already exists in the current spec rev (section 11.7)?** → Small change, section 3/4 PR. (Not an SEP.)
2. **Does this change what's on the wire between client and server?** → SEP.
3. **Does this add, rename, or remove a field, method, or capability?** → SEP.
4. **Could a conformant existing implementation break?** → SEP.
5. **Is this a new interop standard?** → SEP.
6. **Does this change how maintainers make decisions or the SEP process?** → SEP (Process type).
7. **None of the above, ≤~200 lines?** → Direct PR.
8. **Still unsure?** → Post in Discord `#general` or GitHub Discussions BEFORE writing code.

### 1.6 Quick reference

| Signal | Type | Path |
|---|---|---|
| Typo, broken link, docs clarity | Small | Direct PR (section 3) |
| Adding example to existing feature | Small | Direct PR (section 3) |
| Test improvement | Small | Direct PR (section 3) |
| Bug fix in SDK / Inspector / Registry | Non-spec repo PR | Issue first, then section 4 |
| New RPC method | Major | SEP section 5 |
| Any breaking change | Major | SEP section 5 |
| Schema structure change | Major | SEP section 5 |
| Auth / transport change | Major | SEP section 5 |
| Governance change | Major | SEP section 5 (Process type) |
| Not sure | Discuss first | Discord or Discussions |

---

## Step 2: Verify prerequisites

**Required for any contribution:**
- Git (any recent version)
- GitHub account with 2FA enabled

**Required for spec repo (`modelcontextprotocol/modelcontextprotocol`):**
- Node.js 24+, npm 11+
- Verify: `node --version && npm --version && git --version`

**Required for SDK/tool contributions:**

| Repo | Toolchain |
|---|---|
| `typescript-sdk` | Node 20+, npm or pnpm |
| `python-sdk` | Python 3.10+, uv or pip, pytest |
| `go-sdk` | Go 1.22+ |
| `java-sdk` | JDK 17+, Maven or Gradle |
| `kotlin-sdk` | JDK 17+, Gradle |
| `csharp-sdk` | .NET 8+ SDK |
| `swift-sdk` | Xcode 15+ / Swift 5.9+ |
| `rust-sdk` | Rust stable (cargo) |
| `ruby-sdk` | Ruby 3.1+, bundler |
| `php-sdk` | PHP 8.2+, composer |

Always check the target repo's README + CONTRIBUTING.md for exact version floors.

---

## Step 3: Small-change workflow (spec repo)

```bash
gh repo fork modelcontextprotocol/modelcontextprotocol --clone=false
git clone https://github.com/YOUR-USERNAME/modelcontextprotocol.git
cd modelcontextprotocol
npm install
npm run check                    # verify clean baseline
git checkout -b fix/<desc>       # or feat/<desc>, docs/<desc>
# make changes
npm run generate:schema          # if schema touched
npm run check && npm run format
git commit -m "Fix typo in tools documentation (#123)"
git push origin fix/<desc>
gh pr create --fill
```

**Schema source of truth:** `schema/draft/schema.ts`. Always `npm run generate:schema` after editing.
**Docs preview:** `npm run serve:docs` → localhost:3000. Validate with `npm run check:docs`.

### 3.5 Docs authoring — MDX + Mintlify

MCP docs use MDX + Mintlify. Key components: `<Note>`, `<Tip>`, `<Warning>`, `<Steps>`, `<Tabs>`, `<Card>`, `<Accordion>`, `<CodeGroup>`.

Common gotchas:
- Blank lines around components required or content won't render
- No `import` statements — Mintlify components are globally registered
- Escape `{` and `}` as `\{` `\}` in prose
- MDX ≠ GitHub README rendering — use `npm run serve:docs` for real preview
- Adding a new page requires updating `docs.json` (sidebar config)

---

## Step 4: Non-spec repo workflow (SDKs, Inspector, Registry, extensions)

Each non-spec repo has its own maintainers, CONTRIBUTING.md, and Discord channel. Don't assume spec-repo patterns apply.

**Before code:**
1. Open an issue first describing the approach
2. Join the relevant Discord channel (`#general-sdk-dev` for SDK coordination; per-language channels may exist)
3. Read that repo's CONTRIBUTING.md
4. Write tests — bug fix → reproducing test; new feature → coverage

Some SDKs are co-maintained with partners (Google, Microsoft, JetBrains).

---

## Step 5: SEP workflow

The slow, social path — weeks to months. SEP files live in `seps/` in the spec repo.

### 5.1 When required vs not

Required: new feature/protocol change, breaking change, governance change, complex topic.
Skip: bug fixes, typos, docs, examples, minor schema fixes.

### 5.2 SEP types

| Type | Purpose |
|---|---|
| Standards Track | New feature / implementation / interop standard |
| Informational | Design issue or guideline; no new feature |
| Process | Change to MCP process itself |

### 5.3 Pre-draft checklist

1. Validate idea in relevant WG/IG Discord channel
2. Check alignment with roadmap and design principles
3. Build a prototype (mandatory before acceptance)
4. Identify 1-2 sponsor candidates from MAINTAINERS.md

### 5.4 Lifecycle

```
Idea → PR → Awaiting Sponsor (up to 6mo)
                ↓
              Draft → In-Review → Accepted → Final
                                     ↓
                                  Rejected
```

Sponsor updates status (both markdown and PR label). Author does NOT edit status directly.

### 5.5 Prototype requirement

Mandatory before acceptance. Must demonstrate core functionality, show API ergonomics, surface edge cases, be runnable by reviewers. Pseudocode alone is NOT sufficient.

### 5.6 SEP file structure

Filename: `0000-title.md` initially; rename using PR number after opening.

Required sections: Preamble, Abstract (~200 words), Motivation (weak motivation = auto-reject), Specification, Rationale, Backward Compatibility, Reference Implementation, Security Implications.

### 5.7 Submission steps

1. Draft markdown following section 5.6
2. Open PR adding to `seps/`
3. Rename file using PR number
4. Tag 1-2 maintainers as sponsor candidates
5. If no response after 2 weeks → ask in `#general`
6. Sponsor assigns themselves → status `draft`
7. Informal review → iterate
8. Sponsor flips to `in-review` → biweekly Core Maintainer meeting
9. Resolution: accepted / rejected / returned for revision
10. If accepted: complete reference impl → `final`

---

## Step 5.5: Governance model

MCP is under Linux Foundation governance. Understanding who decides what saves weeks.

### 5.5.1 Role hierarchy

| Role | Authority |
|---|---|
| Lead Maintainers (BDFL) | Final decision; veto; appoint/remove Cores |
| Core Maintainers | Project direction; spec stewardship; veto Maintainer decisions by majority |
| Maintainers | Area-specific write access; decide for their area |
| Contributors | Anyone filing issues / PRs |

Contributor Ladder: https://modelcontextprotocol.io/seps/2148-contributor-ladder

| Role | Min timeline | Key privileges |
|---|---|---|
| Contributor | Immediate | Open issues/PRs |
| Member | 2-3 months active | Org membership, triage, `/lgtm` |
| Maintainer | 6+ months as Member | Merge rights, sponsor new Maintainers |
| Core Maintainer | 6+ months as Maintainer | SEP voting, admin access |

### 5.5.4 Working Groups vs Interest Groups

| | Interest Group | Working Group |
|---|---|---|
| Purpose | Identify + discuss problems | Build concrete solutions |
| Output | Problem statements, recommendations | SEPs, implementations, code |
| Decisions | Rough consensus, non-binding | Binding (lazy consensus → vote → escalation) |

Current active groups (verify at meet.modelcontextprotocol.io): Registry WG, Triggers & Events WG, Server Identity WG, Agents WG, Inspector V2 WG, MCP Apps WG, Fine-Grained Auth WG, Transports WG, Mixup Protection WG, SDKs WG, Primitive Grouping IG, Skills Over MCP IG, Gateways IG, Financial Services IG.

### 5.5.10 Licensing

| Contribution type | License |
|---|---|
| Code | Apache 2.0 |
| Specification | Apache 2.0 |
| Docs (non-spec) | CC-BY 4.0 |
| SEPs | Public domain / CC0 |

No CLA / no copyright assignment. Outbound = inbound.

---

## Step 6: Repo map

| Category | Repo | Notes |
|---|---|---|
| **Specification** | `modelcontextprotocol/modelcontextprotocol` | Spec, docs, SEPs |
| **SDKs (Tier 1)** | `typescript-sdk`, `python-sdk` | |
| **SDKs (Tier 2)** | `go-sdk`, `java-sdk`, `kotlin-sdk`, `csharp-sdk`, `swift-sdk`, `rust-sdk`, `ruby-sdk`, `php-sdk` | Some co-maintained |
| **Tools** | `inspector`, `inspector-v2` (in development) | TypeScript React app |
| **Registry** | `registry` | Server discovery |
| **Extensions** | `ext-*` repos (per SEP-2133) | Reverse-domain identifiers |
| **Infrastructure** | `access` (per SEP-2149), `.github` | Member lists, org config |
| **Governance** | `MAINTAINERS.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CONTRIBUTING.md`, `ANTITRUST.md`, `GOVERNANCE.md` | In spec repo |

---

## Step 6.5: Roadmap-aligned priorities

From https://modelcontextprotocol.io/development/roadmap. SEPs aligned with these get expedited review.

**Priority areas:** Transport Evolution & Scalability, Agent Communication (Tasks lifecycle), Governance Maturation, Enterprise Readiness.
**On the horizon:** Triggers & Events, Result Type Improvements, Security & Authorization, Extensions Ecosystem.

---

## Step 7: Finding something to work on

```bash
# Org-wide good first issues (most useful):
gh search issues 'org:modelcontextprotocol label:"good first issue" state:open' --limit 30

# Specific repo:
gh issue list --repo modelcontextprotocol/modelcontextprotocol --label "good first issue" --state open
```

---

## Step 8: Communication channels

### 8.1 Channel map

| Channel | When to use |
|---|---|
| Discord | Quick questions, coordination, WG/IG discussions |
| meet.modelcontextprotocol.io | WG/IG meetings |
| GitHub Discussions | Proposals, roadmap planning, **feature requests** |
| GitHub Issues | **Bug reports with repro steps** |
| PR to `seps/` | SEP submissions |
| SECURITY.md | Vulnerability reports — **NEVER post publicly** |

**Critical:** feature requests → Discussions, NOT Issues. This is the most common newcomer mistake.

### 8.2 Discord rules (STRICTER than most OSS Discords)

1. Server exists to advance MCP as a protocol. Not a user-support forum.
2. **No self-promotion. Period.** Don't bring up your project unless directly relevant to discussion.
3. Solicitation of work is bannable.
4. Usage questions are out of scope — use GitHub Discussions.
5. **Display name: `name (company)` required** before first post.
6. Use threads for anything beyond a single message.
7. No vendor or product marketing.
8. Security issues → SECURITY.md private flow only.
9. Decisions from Discord MUST move to GitHub for persistent record.
10. Private channels are incident rooms only.

### 8.2a Before first post checklist

1. Set display name to `name (company)` or `name (employer, personal)`
2. Read server rules and pinned messages
3. Scroll back ~50 messages to see norms
4. Start a thread for multi-message topics

### 8.2b No standalone tool/project announcements

Rule #2 bans "I built X, here it is" posts. Alternatives:
- Wait for a discussion where your tool is the natural answer; reply in-thread
- Open a GitHub Discussion describing the tool
- Propose documenting it via a PR

### 8.2c Employer OSS policy

**Before ANY post:** confirm your employer's OSS policy allows personal MCP contribution. Check IP/outside-work clauses, pre-approval requirements, disclosure format. Resolve this FIRST.

---

## Step 9: AI-contribution disclosure

Disclose in PR body: "Drafted with Claude; I reviewed and tested all changes."

The human must be able to explain the change, articulate why it's needed, and verify it works.

---

## Step 10: Good PR checklist

- [ ] Focused on ONE issue
- [ ] Descriptive commits with issue numbers
- [ ] All CI checks green
- [ ] `npm run check` passes locally
- [ ] Tests/examples added where applicable
- [ ] AI-assist disclosed if used

---

## Step 11: Reference appendix

### 11.1 Design Principles

Source: https://modelcontextprotocol.io/community/design-principles. SEPs evaluated against 8 principles:

1. **Convergence over choice** — one way to solve a problem in the spec
2. **Composability over specificity** — don't add features buildable from primitives
3. **Interoperability over optimization** — degrade gracefully via capability negotiation
4. **Stability over velocity** — "no" leaves the door open; "yes" closes it forever
5. **Capability over compensation** — don't add permanent structure for temporary model limitations
6. **Demonstration over deliberation** — working prototype > theoretical argument
7. **Pragmatism over purity** — accept some inconsistency for adoption
8. **Standardization over innovation** — codify proven patterns; experiment via extensions

### 11.2 Antitrust Policy

Never discuss: pricing, margins, bidding, market shares, competitive strategy. If a discussion crosses the line: protest + leave + insist it's noted in minutes.

### 11.3 SDK Tiering

| Tier | Conformance | New features | Critical bug fix |
|---|---|---|---|
| 1 Fully Supported | 100% | Before spec release | 7 days |
| 2 Commitment | 80% | ≤6 months | 2 weeks |
| 3 Experimental | no min | none | none |

### 11.7 Lifecycle spec

Source: https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle

Three phases: Initialization → Operation → Shutdown.

Client capabilities: `roots`, `sampling`, `elicitation`, `tasks`, `experimental`.
Server capabilities: `prompts`, `resources`, `tools`, `logging`, `completions`, `tasks`, `experimental`.

### 11.8 Transports

Two standard: stdio, Streamable HTTP. Security: servers MUST validate `Origin` header; SHOULD bind localhost when local.

### 11.9 Authorization

Optional. OAuth 2.1 basis. MUST implement PKCE (S256). Resource Indicators (RFC 8707) required.

### 11.10 Changelog — `2025-11-25` vs `2025-06-18`

Major changes: OpenID Connect Discovery, icons for tools/resources/prompts, incremental scope consent, tool-name format, ElicitResult standards, URL mode elicitation, tool calling in sampling, Client ID Metadata Documents, experimental Tasks primitive.

### 11.11 SEP index

27 Final / 2 Accepted / 1 Draft as of 2026-04-16. Check https://modelcontextprotocol.io/seps/index before drafting to avoid duplicating existing SEPs.

---

## Step 12: Drift Detection and Auto-Remediation

### 12.1 Detection (refresh.sh — runs weekly via GitHub Actions)

Compares tracked source URLs (sources.yml) against current state:
- New pages in llms.txt not yet catalogued
- Broken anchor references in SKILL.md
- Content hash changes on covered pages

### 12.2 Auto-Remediation (runs after detection)

When drift is detected, the skill attempts to fix it rather than just filing an issue.

**For new uncatalogued pages:**
1. Fetch the new page content
2. Classify priority: high (governance, spec changes), medium (SDK docs, guides), low (tutorials, examples)
3. High-priority: draft section content and add to sources.yml with `status: covered`
4. Medium/low: add to sources.yml with `status: gap` and priority tag

**For broken anchors:**
1. Fetch current page and find nearest matching heading
2. Update anchor reference in both SKILL.md and sources.yml
3. If no match found, flag for manual review

**For content hash changes:**
1. Diff old and new content
2. Additive (new sections): update SKILL.md to incorporate
3. Structural (reorg, renames): flag for manual review with summary
4. Removal: flag for manual review

**Output:**
- Auto-fixable: committed with `[auto-remediate] {description}`
- Manual-review: filed as single consolidated issue with checklist (not one issue per drift item)

### 12.3 Staleness Guard

If 3+ consecutive drift issues go unresolved, the next refresh adds a warning:

```
<!-- STALE: drift issues #N-#M unresolved. Sections may be outdated. -->
```

This makes staleness visible rather than silently degrading.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `npm run check` fails | Check Node >=24; re-run `npm install`; `npm run generate:schema`; `npm run format` |
| PR sitting for weeks | CI green? Polite ping in PR comment; cross-post in Discord; last resort → Core Maintainer |
| No SEP sponsor | Discussed in Discord/WG first? Split smaller? Demonstrated interest? |
| SEP rejected | Not permanent. Address feedback, try different angle, or wait. |

---

## Reference links

- Contributing: https://modelcontextprotocol.io/community/contributing
- SEP Guidelines: https://modelcontextprotocol.io/community/sep-guidelines
- Design Principles: https://modelcontextprotocol.io/community/design-principles
- Governance: https://modelcontextprotocol.io/community/governance
- Contributor Ladder: https://modelcontextprotocol.io/seps/2148-contributor-ladder
- WG/IG Governance: https://modelcontextprotocol.io/seps/2149-working-group-charter-template
- Working Groups: https://modelcontextprotocol.io/community/working-interest-groups
- Communication: https://modelcontextprotocol.io/community/communication
- Roadmap: https://modelcontextprotocol.io/development/roadmap
- MAINTAINERS.md: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/MAINTAINERS.md
- Antitrust: https://modelcontextprotocol.io/community/antitrust
- Charter Template: https://modelcontextprotocol.io/community/charter-template
- Meeting Calendar: https://meet.modelcontextprotocol.io
- Spec Changelog: https://modelcontextprotocol.io/specification/draft/changelog
- SEP Index: https://modelcontextprotocol.io/seps/index
- SECURITY.md: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/SECURITY.md
- Code of Conduct: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/CODE_OF_CONDUCT.md

---

## Session log

Append one-liners when this skill is used on real contributions — SHA, PR URL, lessons.

<!-- 2026-04-16: skill scaffolded from modelcontextprotocol.io/community/contributing -->
<!-- 2026-04-16: dry-run #2 on modelcontextprotocol/inspector#832 — all dry-run #1 bugs held -->
