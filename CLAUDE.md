# hbschlac/hbschlac

This repo is Hannah Schlacter's GitHub profile README and the canonical staging area for Claude Code skills.

## STOP -- Read this before doing anything

Between April 14 and June 23, 2026, **45+ Claude Code web sessions** audited and improved these skills. 30 sessions (Apr-Jun 4) produced orphaned branches. 13 sessions (Jun 4-17) merged daily review PRs. 2 sessions (Jun 17-23) trimmed 584 lines of bloat. The skills are comprehensive. They do not need more review.

**If your task involves "review skills," "audit skills," "improve skills," or "consolidate sessions":**
1. **Do not do a full review.** The meta-review circuit breaker in session-safety is BLOCKING.
2. If you found ONE specific gap in real work, make a targeted edit.
3. EDIT existing skill files. Do not rewrite from scratch.
4. When done, create a PR via MCP tools and merge it.

## Skills inventory

| Skill | Version | What it does |
|-------|---------|-------------|
| code-builder | v8.9 | Execution engine: single-pass, debug loop, visual mode, rapid shipping. MCP integration patterns. Parallel mode collapsed to stub. Learnings in LEARNINGS.md |
| vercel-ship | v1.8 | Pre-deploy validation for Next.js + Vercel + Docker/k8s + concrete MCP deployment workflows |
| content-quality | v11 | Anti-AI-slop, voice matching, hallucination prevention, UX copy, wizard flow copy |
| session-safety | v20 | Groundhog Day prevention, BLOCKING review circuit breaker, Step 0 productive work routing, branch cleanup, scheduled routine templates, concurrent-merge discipline (rebase-before-merge + SHA-pinned force-with-lease + reconcile-not-duplicate) |
| debug-escalation | v12.1 | Fix-churn breaker, cross-skill routing, pipeline hardening, scheduled routine failure handling |
| portfolio-dev | v3.2 | schlacter.me / Next.js portfolio patterns + end-to-end new project workflow |
| session-start-hook | v6 | SessionStart hook creation + hook debugging |
| project-bootstrap | v1.3 | Auto-generate CLAUDE.md + session-start hooks for repos |
| research-pipeline | v1.3 | Scrape, classify, analyze, present research data + Claude Code session research with WebSearch/WebFetch |
| job-fetch | v1.0 | **Packaged as a plugin** (`plugins/job-fetch/`, served from this repo's `.claude-plugin/marketplace.json`). Fetch + ingest a JD past the web sandbox's 403 egress block: ATS public APIs, with a Composio remote-exec MCP fallback when in-sandbox fetch is blocked. Auto-fires on job URLs (UserPromptSubmit hook). Ingest-and-acknowledge, no JD echo. Enabling it via a repo `.claude/settings.json` DOES NOT WORK in cloud sessions — see "Repo settings.json does not load" below. |
| mcp-contributor | v4.1 | FROZEN -- zero usage, anchor bug unfixed. Do not iterate. |

## Personal skills live in a SEPARATE repo (add_repo first)

Hannah's personal **resume, outreach, and networking** skill is NOT in this repo and NOT in `.claude/skills/` here — don't search for it locally. It lives in **`hbschlac/product-networking-skills`** (old name `career-skills`, which still redirects).

- **Trigger phrase:** "use the product networking skill"
- **Entry file:** `skills/product-networking/SKILL.md` → routes to `references/resume-subskill.md` (rules/format/publishing) → `references/resume.md` (base content + verb bank) → `references/hannah-profile.md` (story bank).
- **Attach it first:** a remote session does NOT clone it automatically. Run `add_repo` before use. **Redirect gotcha:** the session access grant currently resolves the OLD name — if `add_repo hbschlac/product-networking-skills` returns "not accessible," retry with `hbschlac/career-skills`.
- **Resume editing needs the Google Docs (Workspace) MCP**, not just Drive — see that skill's Step 2 preflight for the Drive-only fallback.

## What to work on (not another skill review)

**High-priority (stuck work):**
- Merge or close muse-shopping #1 (draft PR, 30+ days old)

**Feature work:**
- Build features on kindle-schlacter-me, kindle-connector, or recs.community
- Update the portfolio site (schlacter.me) with new projects
- Set up monitoring/health checks for any deployed project

**Structural (only if specifically asked):**
- Clean up orphaned branches (54 across hbschlac/hbschlac — commands now in session-safety)
- Reconfigure scheduled routines from "review skills" to health checks/PR hygiene

## Active known issues

1. **mcp-contributor anchor bug (still unfixed, no longer firing).** refresh.sh:100 greps `^## Step 11.N[: ]` but SKILL.md's appendix uses `### 11.N`, so all 11 subsection anchors miss and the job always exits non-zero. The skill is FROZEN, so this is left alone deliberately. Fix the anchors before ever restoring a schedule.
2. **mcp-contributor cron noise: RESOLVED 2026-09-01.** It filed 10 identical issues (#4-#13, Apr 19 - Jun 21), all closed as not_planned. GitHub had auto-disabled the workflow on Jun 21 after 60 days of repo inactivity, which was an accident, not a fix: any push re-enables it. The `schedule:` trigger is now removed from `weekly-refresh.yml`; `workflow_dispatch` remains. Do not re-add a schedule while issue 1 stands.
3. **code-builder parallel mode collapsed.** Stub-only in SKILL.md (full spec in git history). Laptop-only, never tested.
4. **No project has monitoring configured.** Incidents are discovered reactively. Use Vercel MCP tools + WebFetch in scheduled routines for health checks.
5. **muse-shopping #1 draft PR.** Created by vibe-improver, 50+ days in draft limbo. Close or merge.
6. **100% of sessions since Jun 4 did skill reviews, 0% did feature work.** Productive Work Accelerator moved to Step 0 (first thing sessions see). Circuit breaker now sends PushNotification when routines are misconfigured.
7. **Scheduled routines misconfigured.** Routines configured to "review skills" hit the circuit breaker every time. Reconfigure to: health check, PR hygiene, or dependency freshness.
8. **54 orphaned branches.** Branch cleanup commands now in session-safety. Run them.
9. **recs.community 4 stacked PRs open 30+ days.** PRs #4-7 in dependency chain, none merged. Merge #4 first.

## Repo settings.json does not load in cloud sessions

**A `.claude/settings.json` committed to a repo is INERT in Claude Code web/iOS
sessions, and it fails SILENTLY.** Those sessions clone every source repo as a
SUBDIRECTORY of the session root (`/home/user/hbschlac`, `/home/user/kindle-schlacter-me`),
and the root itself is not a repo. Project settings load from the session root, so
nothing in `<repo>/.claude/settings.json` is ever read. `CLAUDE.md` IS read from each
added directory, which is what makes this so confusing: the repo clearly influences
the session, so the settings file looks like it must be working too.

Verified 2026-09-01: PR #23 added Composio `permissions.allow` rules and
`enabledPlugins: {"job-fetch@hbschlac": true}` to `.claude/settings.json`. In a live
session `ListPlugins` returned EMPTY and no `job-fetch` skill existed, while
`/root/.claude/settings.json` (user level, inside the container) carried the same
three Composio rules and those DID apply. The repo file did nothing.

Consequences, both of which were live that day:
- **Permission rules must be set at the ACCOUNT/user level**, not committed to a repo.
  A rule in a repo file will never suppress a prompt.
- **A plugin enabled only in a repo file is off.** A session that needs `job-fetch`
  will not have it and will improvise — one was caught hand-rolling a scrape of a
  vendor's minified JS to find GraphQL endpoints, precisely the thing the skill's
  ATS-public-API path exists to avoid.

Two more traps on top of the location problem:
- **An allow rule is an exact tool-name match, and the MCP name is not stable.** The
  Composio server is exposed as `mcp__Composio_Docs_Drive__*` but ALSO, after a
  reconnect, as its raw UUID `mcp__ae6e71d8-77c8-4c40-b774-fbaa2ceaa0c1__*`. A rule
  naming the friendly form cannot match the UUID form.
- **Auto mode's classifier can override an allowlist in BOTH directions.** It denied
  allowlisted `Bash` (`ps`, reading `/proc/<pid>/cmdline`) with "Blocked by
  classifier", and it approved a Composio call under the UUID name that no rule
  covered. So an allow rule is not a guarantee, and a prompt does not prove a rule is
  missing. Do not conclude anything about permissions from a benign test command:
  auto mode approves those on their own merits, which reads as a working allow rule
  when there is none.

## Sandbox constraint

Web sessions can only push to `hbschlac/hbschlac`. To change other repos, use GitHub MCP tools to create a PR. If MCP tools can't reach the repo, send a PushNotification with exact commands instead of writing laptop instructions.

## README editing rules

- Tone: direct, concise, evidence over adjectives. Hannah writes like a builder, not a marketer.
- Every project claim must be verifiable (live site, repo, or deployment).
- Don't add projects that aren't shipped. Don't inflate descriptions.
