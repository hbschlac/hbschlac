# mcp-contributor Structural Fixes

Addresses open issues #1, #2, #3 from dry-run testing on April 17.

---

## Issue #3: Rename S4 "SDK workflow" → "Non-spec repo workflow"

**Problem:** Inspector is a TypeScript React app, not an SDK, but its PR process
follows S4 mechanics. The title "SDK workflow" is misleading.

**Fix in SKILL.md:**

```diff
-## Step 4 — SDK workflow
+## Step 4 — Non-spec repo workflow
```

Update all cross-references in S1.4:
```diff
-See S4 (SDK workflow) for the fork → branch → PR process.
+See S4 (non-spec repo workflow) for the fork → branch → PR process.
```

Also update the S1.6 quick reference table if it references "SDK workflow."

---

## Issue #2: Expand S6 repo map to include non-SDK repos

**Problem:** S6 only lists the spec + 10 official language SDKs. Missing:
Inspector, Registry, ext-*, access, .github.

**Fix in SKILL.md — restructure S6 into subsections:**

```markdown
## Step 6 — Repo map

### 6.1 Spec
| Repo | Description |
|------|-------------|
| `modelcontextprotocol/specification` | The protocol spec, SEPs, and governance docs |

### 6.2 Official SDKs
| Repo | Language | Notes |
|------|----------|-------|
| `modelcontextprotocol/typescript-sdk` | TypeScript | Reference implementation |
| `modelcontextprotocol/python-sdk` | Python | |
| `modelcontextprotocol/java-sdk` | Java/Kotlin | |
| `modelcontextprotocol/csharp-sdk` | C# | |
| `modelcontextprotocol/swift-sdk` | Swift | |
| `modelcontextprotocol/go-sdk` | Go | |
| `modelcontextprotocol/rust-sdk` | Rust | |
| `modelcontextprotocol/ruby-sdk` | Ruby | |
| `modelcontextprotocol/php-sdk` | PHP | |
| `modelcontextprotocol/elixir-sdk` | Elixir | |

### 6.3 Tools
| Repo | Description |
|------|-------------|
| `modelcontextprotocol/inspector` | MCP Inspector — testing/debugging tool for MCP servers |
| `modelcontextprotocol/registry` | MCP server registry |

### 6.4 Extensions & Infrastructure
| Repo | Description |
|------|-------------|
| `modelcontextprotocol/ext-*` | Extension repos (per SEP-2133 Extensions Framework) |
| `modelcontextprotocol/access` | Access control (per SEP-2149) |
| `modelcontextprotocol/.github` | Org-level GitHub config (templates, workflows) |
```

---

## Issue #1: Cross-reference S11.7 from S1.5 decision tree

**Problem:** When triaging "is this an SEP?", the key question is often "does this
capability already exist in the current spec revision?" S11.7 answers that but
isn't discoverable from the triage flow.

**Fix in SKILL.md — add to S1.5 gray-zone decision tree, early in the flow:**

```markdown
### 1.5 Gray-zone decision tree

1. **Does this capability/notification already exist in the current spec revision?**
   → Check S11.7 (Lifecycle spec). If yes → small change (S3 PR workflow).
   If no → continue to question 2.

2. Does this change the wire protocol or add a new primitive?
   → Yes: SEP required (S5).
   → No: continue.
[... rest of existing decision tree ...]
```

This surfaces S11.7 at the exact moment it's needed — during triage — instead
of burying it in the reference appendix.
