# mcp-contributor — Required Updates (June 2026)

## Severity: HIGH — Skill content is materially wrong

The MCP specification underwent its largest revision since launch between April–May 2026. The skill's sources were last fetched **April 16**. Since then:

### Protocol-breaking changes (skill is now incorrect on these)

1. **MCP is stateless at the protocol layer.** The initialize/initialized handshake and `Mcp-Session-Id` header are removed. Any skill content describing sessions, handshakes, or session IDs gives wrong guidance.
2. **MCP Apps (SEP-1865)** — servers can ship interactive HTML UIs in sandboxed iframes. Entirely new concept not in the skill.
3. **Tasks moved to extensions** — no longer experimental core feature; now `tasks/get`, `tasks/update`, `tasks/cancel` under the extensions framework.
4. **Full JSON Schema 2020-12** for tool inputSchema/outputSchema (oneOf, anyOf, allOf, conditionals, refs). Previous version was limited.
5. **Extensions framework (SEP-2133)** — reverse-DNS IDs, independent versioning, negotiation via capabilities map. New architecture.
6. **Standards Track SEPs now require conformance suite scenarios (SEP-2484).** Changes the contribution process itself.

### Governance changes

7. **SEP-1302** formalized Working Groups and Interest Groups — the skill covers these but from the pre-formalization era.
8. **SEP-2085** established succession procedures for governance.
9. **Contributor Ladder SEP** in progress — skill covers the draft but should track the live version.

### SDK changes

10. **TypeScript SDK patched CVE-2026-0621 (ReDoS)** — security-relevant for contributors.
11. **Go SDK added OAuth client credentials** — new capability.
12. **All Tier 1 SDKs** (Python, TypeScript, Go, C#, Ruby) had releases in May-June 2026.

---

## Issue triage

### Collapse weekly drift issues (#4–#10)

These 7 issues represent a single root cause: the April → May 2026 MCP RC. Action:
- Create one tracking issue: "[tracking] SKILL.md re-fetch for 2026-07-28 RC"
- Close #4–#10 as duplicates linking to the tracker
- Update the GitHub Action to **reopen a single tracking issue** instead of creating new ones each week

### Fix structural issues (#1–#3)

**#3 — §4 "SDK workflow" applies to all non-spec repos:**
- Rename §4 to "Repository contribution workflow"
- Generalize the content to cover spec, SDK, docs, Inspector, Registry, and ext-* repos

**#2 — §6 repo map missing repos:**
Add to the repo map:
- `modelcontextprotocol/inspector` — MCP Inspector tool
- `modelcontextprotocol/registry` — MCP Registry (now live at registry.modelcontextprotocol.io)
- `modelcontextprotocol/ext-*` — Extension repos under the new framework
- `modelcontextprotocol/apps` — MCP Apps reference implementations

**#1 — No pointer from capability questions → §11.7 lifecycle:**
Add a routing rule early in the skill:
> "If the user asks 'can MCP do X?' or 'does MCP support Y?', check §11.7 (lifecycle/capabilities) first, then §11.4-11.5 (server/client concepts)."

---

## Automation improvements

### 1. Deduplicate drift issues

Change `refresh.sh` / the GitHub Action to:
- Check if an open issue with label `drift` exists
- If yes: add a comment with the new drift report, don't create a new issue
- If no: create one

### 2. Add auto-resolution suggestions

`refresh.sh` currently detects that a source URL changed. It should also:
- Diff the old hash against the new content
- Output a summary of what changed (paragraph-level, not line-level)
- Suggest which SKILL.md sections need updating

### 3. Increase refresh cadence during RC window

The 2026-07-28 RC validation window (now through late July) has rapid spec and SDK changes. Bump from weekly to **twice-weekly** during this period, then revert.

---

## sources.yml updates needed

All sources should be re-fetched. Priority additions:

```yaml
# New sources to add
- url: https://modelcontextprotocol.io/extensions/overview
  status: gap-high
  reason: "Extensions framework (SEP-2133) is architecturally new"

- url: https://modelcontextprotocol.io/seps/1865-mcp-apps-interactive-user-interfaces-for-mcp
  status: gap-high
  reason: "MCP Apps — new capability category"

- url: https://modelcontextprotocol.io/seps/2484-conformance-suite-scenarios
  status: gap-high
  reason: "Changes contribution requirements for Standards Track SEPs"

- url: https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/
  status: gap-high
  reason: "RC announcement — stateless protocol, summary of all changes"

- url: https://registry.modelcontextprotocol.io
  status: gap-med
  reason: "Registry is now live — contributors need to know it exists"
```

Promote existing gap-med sources that are now critical:
- `extensions/overview` → gap-high (extensions framework is now real)
- `extensions/apps/overview` → gap-high (MCP Apps is a major feature)
- `specification/2025-11-25/basic/lifecycle` → re-fetch urgently (stateless change invalidates this)
- `specification/2025-11-25/basic/transports` → re-fetch urgently (session removal affects this)

---

## Token budget consideration

The current SKILL.md is very large (likely 400+ lines with all the governance, SEP, and protocol content). With the 25,000-token shared skill budget after compaction, this skill may be crowding out code-builder.

Recommendation: split into:
- **SKILL.md** — core contribution workflow (triage, PR process, SEP lifecycle) — target 200 lines
- **reference/protocol.md** — protocol fundamentals (read on-demand when contributor asks about architecture)
- **reference/governance.md** — governance details (read on-demand for SEP/WG questions)

This reduces the always-loaded footprint while keeping deep reference accessible.
