# mcp-contributor: Recommended Patches

These patches address staleness and coverage gaps identified in the 2026-05-28 skills audit.
Apply to `hbschlac/mcp-contributor` repo.

---

## Patch 1: Fix hardcoded snapshots (HIGH — prevents rot)

### 1A. Protocol version (SKILL.md, Step 0.5)

Replace:
```
**Versioning:** current spec rev is **`2025-11-25`**
```

With:
```
**Versioning:** protocol version strings are date-based (`YYYY-MM-DD`). Check the current rev at https://modelcontextprotocol.io/specification/ — do not trust a hardcoded value here.
```

### 1B. Active working groups (SKILL.md, Step 5.5.4 or equivalent)

Replace the hardcoded list of 13 groups with:
```
**Active groups:** fetch the current list from https://meet.modelcontextprotocol.io before citing. Groups form and dissolve regularly; any snapshot here will rot within weeks.
```

### 1C. SEP index (SKILL.md, Step 11.11)

Replace:
```
27 Final / 2 Accepted / 1 Draft at fetch
```

With:
```
SEP counts change weekly. Check the current index at https://modelcontextprotocol.io/seps before citing specific numbers.
```

### 1D. Discord invite link

Replace all instances of `https://discord.gg/6CSzBmMkjX` with:
```
the Discord invite link at https://modelcontextprotocol.io/community/communication
```

This way, if the invite link rotates, the skill still points to the right place.

---

## Patch 2: Add missing repos to Step 6 repo map (HIGH — coverage gap)

Add after the existing SDK repo table:

```markdown
### Non-SDK repos in the org

| Repo | Purpose | Contribution path |
|---|---|---|
| `inspector` | MCP debugging tool — test servers interactively | Bug fixes + features via §4 |
| `registry` | MCP server registry — discover and share servers | Bug fixes via §4; new features may need SEP |
| `ext-*` (e.g. `ext-auth`) | Official extensions to the core protocol | Closely tied to SEPs; check extension's README |
| `access` | Member access management for the GitHub org | Internal; rarely needs external contribution |
| `.github` | Shared GitHub org templates (issue templates, etc.) | Meta-fixes via direct PR |
```

---

## Patch 3: Rename Step 4 title (MEDIUM — clarity)

Replace:
```
## Step 4: SDK workflow
```

With:
```
## Step 4: Non-spec repo workflow (SDKs, Inspector, Registry, Extensions)
```

And add a note at the top:
```
This workflow applies to any repo in the org that is NOT the main spec repo. Most commonly used for SDK contributions, but the same fork/branch/PR pattern works for Inspector, Registry, and extension repos.
```

---

## Patch 4: Add cross-reference from Step 1.5 to Step 11.7 (MEDIUM)

In the gray-zone decision tree (Step 1.5), after question 1 ("Does this change what's on the wire between client and server?"), add:

```
   If yes or unsure → read §11.7 (Lifecycle spec) to understand capability negotiation before proceeding. Many "small" changes inadvertently affect the initialize/capabilities handshake.
```

---

## Patch 5: Expand auth section (MEDIUM — depth)

Step 11.9 is ~30 lines covering OAuth 2.1 + DPoP + Workload Identity Federation. Expand to include:

```markdown
### Auth landscape (as of last refresh)

MCP auth is actively evolving. Key specs and SEPs:

- **RFC 8414** — OAuth 2.0 Authorization Server Metadata (discovery)
- **RFC 9728** — Protected Resource Metadata (how servers advertise auth requirements)
- **OAuth 2.1** — baseline authorization framework for MCP
- **SEP-1932 (DPoP)** — Demonstration of Proof-of-Possession; prevents token replay
- **SEP-1933 (Workload Identity Federation)** — machine-to-machine auth without shared secrets

**Before proposing auth changes:**
1. Check the status of SEP-1932 and SEP-1933 — they may already address your concern
2. Read the auth tutorial at https://modelcontextprotocol.io/tutorials/security/authorization
3. Auth SEPs require prototype implementations in at least one SDK before acceptance
4. Expect high scrutiny from Core Maintainers on any auth-related change
```

---

## Patch 6: Add "finding a sponsor" mini-playbook (LOW — practical gap)

After Step 5.3, add:

```markdown
### Finding a sponsor (practical steps)

SEPs require a Core Maintainer sponsor. To find one:

1. **Check MAINTAINERS.md** in the spec repo — it lists who owns which area
2. **Look at recent SEP sponsors** — `git log --oneline seps/` shows who sponsored what
3. **Join relevant Working Group** — WG leads are often willing to sponsor related SEPs
4. **Post in Discord #general** — describe your SEP in 3 sentences and ask if anyone is interested in sponsoring
5. **Attend a Core Maintainer review meeting** — present your proposal informally first

**Don't:**
- DM maintainers directly without prior public discussion
- Expect a response within 24 hours — maintainers are often at companies with their own priorities
- Submit the SEP without a sponsor — it will be marked "needs sponsor" and may stall
```

---

## Patch 7: Run refresh.sh and update hashes (HIGH — operational)

The weekly refresh hasn't run since April 16. Run:

```bash
cd /path/to/mcp-contributor
./refresh.sh
```

Review `refresh-report.md` for drift. Update `hashes.json` for any legitimate content changes. File issues for any real semantic drift discovered.

---

## Patch 8: Add "question" issue template (LOW — OSS completeness)

Currently 4 templates (bug, drift, hallucination, feature). Add:

```markdown
---
name: Question
about: Ask about skill coverage, usage, or interpretation
labels: question
---

**What's the question?**


**Context (what you were trying to do when this came up)**


**Which section of SKILL.md is relevant?**

```
