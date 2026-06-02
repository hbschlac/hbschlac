# mcp-contributor

> Navigate the Model Context Protocol governance process — spec, SDKs, tools, and extensions.

## §0 — Activation

**Triggers** (quoted phrases that activate this skill):
"contribute to MCP", "MCP PR", "MCP pull request", "MCP contribution",
"write an SEP", "draft an SEP", "SEP proposal", "submit to MCP",
"MCP spec change", "MCP SDK", "MCP governance", "MCP contributor",
"modelcontextprotocol", "MCP working group", "MCP interest group",
"MCP Discord", "MCP community", "MCP design principles",
"MCP antitrust", "MCP licensing", "MCP roadmap",
"contribute to the spec", "contribute to the SDK",
"MCP Inspector", "MCP Registry"

**On activation, announce:**
`🔧 mcp-contributor activated — [triage | direct-PR | SEP | communication | governance]. [reason].`

**Does NOT activate for:**
- Building MCP servers/clients (that's app development, not upstream contribution)
- Using MCP tools in Claude Code
- General questions about what MCP is

---

## §1 — Triage: what kind of contribution is this?

### 1.1 — Small change → direct PR (§3)
Typo fix, docs clarification, test improvement, bug fix with obvious root cause.

### 1.2 — Major change → SEP required (§5)
New RPC method, new capability/notification, breaking change to existing behavior, schema restructure, new extension.

### 1.3 — SDK/tool bug → issue-first, then PR (§4)
Open an issue in the specific repo first. Reference the issue in your PR.

### 1.4 — Gray zone decision tree
When it's unclear whether something is small or major:

1. Does it add a new field to the protocol schema? → SEP
2. Does it change behavior for existing clients/servers? → SEP
3. Does it touch only one repo's internal implementation? → Direct PR
4. Is it wiring up a capability/notification that already exists in the current spec? → Direct PR via §4 (check §11 lifecycle for what's already in the spec)
5. Could two reasonable people disagree on the design? → SEP
6. Still unsure? → Ask in Discord (#general or relevant WG channel) before coding

---

## §2 — Prerequisites

### Spec repo (`modelcontextprotocol/modelcontextprotocol`)
- Node 24+ and npm 11+
- `npm install` → `npm run check` to validate

### SDKs (language-specific)
| SDK | Toolchain |
|-----|-----------|
| TypeScript | Node 20+, npm |
| Python | Python 3.10+, uv or pip |
| Java | JDK 17+, Gradle |
| Kotlin | JDK 17+, Gradle |
| C# | .NET 8+ |
| Go | Go 1.22+ |
| Ruby | Ruby 3.2+ |
| Rust | Rust 1.75+ |
| Swift | Swift 5.9+ |
| Elixir | Elixir 1.15+ |

### Tools
| Repo | Toolchain |
|------|-----------|
| Inspector | Node 20+, npm (TypeScript React app) |
| Registry | See repo README |

---

## §3 — Direct PR workflow (small changes)

```bash
# 1. Fork
gh repo fork modelcontextprotocol/<repo> --clone=false
git clone https://github.com/YOUR-USERNAME/<repo>.git
cd <repo>

# 2. Branch
git checkout -b fix/<short-description>

# 3. Install + validate baseline
npm install && npm run check   # (spec repo)
# or: language-specific setup per §2

# 4. Make changes
# If modifying the protocol schema: npm run generate:schema

# 5. Format + commit
npm run format   # (spec repo)
git add -A && git commit -m "<type>: <description>"

# 6. Push + open PR
git push -u origin fix/<short-description>
gh pr create --fill
```

**Commit types:** `fix:`, `feat:`, `docs:`, `test:`, `refactor:`, `chore:`

**PR checklist:**
- [ ] Linked to an issue (if one exists)
- [ ] Tests pass
- [ ] No unrelated changes
- [ ] AI disclosure if applicable (see §10)

---

## §4 — Non-spec repo workflow (SDKs, tools, extensions)

> Previously titled "SDK workflow" — applies to ALL non-spec repos including Inspector, Registry, and ext-* repos.

### 4.1 — SDKs
Each SDK has its own CONTRIBUTING file. Read it first — build commands, test commands, and review norms vary by language.

General pattern:
1. Open an issue describing the bug or desired behavior
2. Fork + branch
3. Implement with tests
4. Run the SDK's own CI checks locally
5. PR references the issue

### 4.2 — Tools (Inspector, Registry)
Same issue-first pattern as SDKs. Inspector is a TypeScript React app — its PR process follows §4.1 mechanics but with web-app-specific considerations (browser testing, UI changes need screenshots).

### 4.3 — Extensions (`ext-*` repos)
Extensions live in `modelcontextprotocol/ext-*` repos (per SEP-2133). Follow the extension's own CONTRIBUTING file. Major new extensions require an SEP first.

---

## §5 — SEP (Substantial Enhancement Proposal) workflow

### 5.1 — Pre-discussion
Before writing the SEP:
- Check the roadmap: https://modelcontextprotocol.io/development/roadmap
- Search existing SEPs: https://modelcontextprotocol.io/seps/index
- Check the feature lifecycle: https://modelcontextprotocol.io/community/feature-lifecycle
- Discuss in Discord (#general or the relevant WG/IG channel)
- Gauge interest before investing in a full proposal

### 5.2 — Draft the SEP
Use the template in the spec repo under `seps/`. Key sections:
- **Motivation:** What problem does this solve? Who is affected?
- **Proposal:** Technical design with schema changes, new methods, etc.
- **Alternatives considered:** What else could work? Why is this better?
- **Backwards compatibility:** What breaks? Migration path?

### 5.3 — Submit
```bash
# Branch from latest main
git checkout -b sep/<short-name>
# Write seps/NNNN-<short-name>.md
# PR to seps/ directory
gh pr create --title "SEP: <title>" --body "..."
```

### 5.4 — Lifecycle
1. **Draft** → PR open, community feedback
2. **Sponsor** → Find 1–2 Core Maintainers to sponsor
3. **Prototype** → Working implementation required (can be in any SDK)
4. **Review** → Biweekly Core Maintainer review
5. **Accepted** / **Rejected** / **Deferred**

SEPs are licensed CC0-1.0-Universal (public domain).

---

## §6 — Repo map

### Spec
| Repo | Description |
|------|-------------|
| `modelcontextprotocol/modelcontextprotocol` | Protocol spec, schema, SEPs |

### Official SDKs (Tier 1: TypeScript, Python; Tier 2+: others)
| Repo | Language |
|------|----------|
| `modelcontextprotocol/typescript-sdk` | TypeScript |
| `modelcontextprotocol/python-sdk` | Python |
| `modelcontextprotocol/java-sdk` | Java |
| `modelcontextprotocol/kotlin-sdk` | Kotlin |
| `modelcontextprotocol/dotnet-sdk` | C# |
| `modelcontextprotocol/go-sdk` | Go |
| `modelcontextprotocol/ruby-sdk` | Ruby |
| `modelcontextprotocol/rust-sdk` | Rust |
| `modelcontextprotocol/swift-sdk` | Swift |
| `modelcontextprotocol/elixir-sdk` | Elixir |

### Tools
| Repo | Description |
|------|-------------|
| `modelcontextprotocol/inspector` | MCP Inspector — TypeScript React debugging tool |
| `modelcontextprotocol/registry` | MCP server registry |

### Extensions
| Repo pattern | Description |
|-------------|-------------|
| `modelcontextprotocol/ext-*` | Protocol extensions (per SEP-2133) |

### Infrastructure
| Repo | Description |
|------|-------------|
| `modelcontextprotocol/access` | Access control (per SEP-2149) |
| `modelcontextprotocol/.github` | Org-wide GitHub config (templates, workflows) |

---

## §7 — Governance

### Contributor ladder
| Level | Tenure | Key rights |
|-------|--------|-----------|
| Contributor | Day 1 | Open issues, submit PRs, join discussions |
| Member | 2–3 months sustained | Triage issues, review PRs (2FA required) |
| Maintainer | 6+ months | Merge PRs, approve releases |
| Core Maintainer | 6+ months as Maintainer | Vote on SEPs, shape roadmap |
| Lead | Succession | Final call on contested decisions |

### Working Groups (WGs)
Drive spec changes. Each WG has a charter in `community/<name>/charter`. Current WGs include file-uploads, interceptors, SDK.

### Interest Groups (IGs)
Discuss problems without binding decisions. Lower commitment than WGs.

---

## §8 — Communication

### Discord rules (strictly enforced)
- Display name: `name (company)` or `username (company)`
- No self-promotion of tools/products
- Use threads for multi-message discussions
- Security issues → SECURITY.md private flow only (never in public channels)

### Channel map
| Channel | Use for |
|---------|---------|
| Discord #general | Quick coordination, questions |
| GitHub Discussions | Feature proposals, roadmap discussion |
| GitHub Issues | Bugs with repro steps |
| SEPs | New protocol features |

---

## §9 — Licensing and legal

| Content | License |
|---------|---------|
| Code and specs | Apache 2.0 |
| Documentation | CC-BY 4.0 |
| SEPs | CC0-1.0-Universal (public domain) |

No CLA required. Contributors retain copyright. Antitrust policy applies to all discussions — see https://modelcontextprotocol.io/community/antitrust.

---

## §10 — AI-assisted contributions

If you used AI to help write code, docs, or an SEP:
- Disclose in the PR/issue body: "Drafted with Claude; I reviewed and tested all changes."
- The human submitter must be able to explain every line and verify correctness.
- AI-generated tests still need a human to confirm they test the right behavior.

---

## §11 — Reference pointers

| Resource | URL |
|----------|-----|
| Spec (latest) | https://modelcontextprotocol.io/specification/2025-11-25 |
| Feature lifecycle | https://modelcontextprotocol.io/community/feature-lifecycle |
| Contributing guide | https://modelcontextprotocol.io/community/contributing |
| SEP guidelines | https://modelcontextprotocol.io/community/sep-guidelines |
| SEP index | https://modelcontextprotocol.io/seps/index |
| Roadmap | https://modelcontextprotocol.io/development/roadmap |
| Contributor ladder | https://modelcontextprotocol.io/community/contributor-ladder |
| Design principles | https://modelcontextprotocol.io/community/design-principles |
| SDK tiers | https://modelcontextprotocol.io/community/sdk-tiers |
| Antitrust policy | https://modelcontextprotocol.io/community/antitrust |
| Discord | https://discord.gg/6CSzBmMkjX |
| Client concepts | https://modelcontextprotocol.io/docs/learn/client-concepts |
| Server concepts | https://modelcontextprotocol.io/docs/learn/server-concepts |
| Versioning | https://modelcontextprotocol.io/docs/learn/versioning |
| Lifecycle (spec) | https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle |
| Transports (spec) | https://modelcontextprotocol.io/specification/2025-11-25/basic/transports |
| Authorization (spec) | https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization |
| Changelog | https://modelcontextprotocol.io/specification/2025-11-25/changelog |
| Client best practices | https://modelcontextprotocol.io/docs/develop/clients/client-best-practices |
| Tasks extension | https://modelcontextprotocol.io/extensions/tasks/overview |
