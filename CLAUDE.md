# hbschlac/hbschlac

This repo is Hannah Schlacter's GitHub profile README and the canonical staging area for Claude Code skills.

## STOP — Read this before doing anything

Between April 14 and June 4, 2026, **30+ Claude Code web sessions** audited these skills, produced improvements on isolated branches, and none ever merged to main. This is called the **Groundhog Day problem**. You are reading this because session #31 finally landed a CLAUDE.md on main to break the cycle.

**If your task involves "review skills," "audit skills," "improve skills," or "consolidate sessions":**
1. The skills in `.claude/skills/` are the consolidated output of 30 iterations. They are good.
2. Do NOT create new audit/review documents (AUDIT.md, REVIEW.md, SKILLS-AUDIT.md).
3. EDIT the existing skill files. Do not rewrite from scratch.
4. When done, create a PR via MCP tools and merge it — do not just push to a branch.

## Skills inventory

| Skill | Status | What it does |
|-------|--------|-------------|
| code-builder | v8.5 | Parallel drafts, self-scoring, debug loop, visual mode. Rapid shipping mode. Graceful degradation + UX discovery. Learnings in LEARNINGS.md |
| vercel-ship | v1.6 | Pre-deploy validation for Next.js + Vercel + Docker/k8s + migration coordination + ISR debugging |
| mcp-contributor | v4.1 | MCP governance contribution workflow (FROZEN) |
| content-quality | v10 | Anti-AI-slop, voice matching, hallucination prevention, ship announcements, commit/PR quality, in-app UX copy |
| session-safety | v15 | Groundhog Day + automated system noise + cross-repo escalation + rollback patterns + scheduled/autonomous sessions |
| portfolio-dev | v3.2 | schlacter.me / Next.js portfolio patterns + end-to-end new project workflow |
| session-start-hook | v6 | SessionStart hook creation + hook debugging + project-bootstrap cross-reference |
| project-bootstrap | v1.3 | Auto-generate CLAUDE.md + session-start hooks for repos |
| debug-escalation | v11 | Fix-churn cycle breaker + invisible downstream failures + pipeline hardening + client-state debugging |
| research-pipeline | v1.1 | Scrape, classify, analyze, present research data + Claude API integration |

## Sandbox constraint

Web sessions can only push to `hbschlac/hbschlac`. To change other repos, write full file contents under `.claude/skills/` here, then use GitHub MCP tools to create a PR and merge it to main. If MCP merge isn't available, add laptop instructions below.

## Laptop instructions (pending)

```bash
# Copy skills to Claude Code runtime
cp -r ~/hbschlac/.claude/skills/* ~/.claude/skills/

# Fix mcp-contributor anchor bug + close stale issues (5 min)
cd ~/mcp-contributor
# In refresh.sh: change heading grep from "## Step N.N:" to "### N.N"
# Then: git commit -am "fix: anchor grep pattern" && git push
# Then: gh issue close 4 5 6 7 8 9 10 11 -c "Fixed anchor pattern"
# OR: Disable the cron entirely if mcp-contributor remains FROZEN:
#   Delete/disable .github/workflows/refresh.yml

# Merge recs.community stacked PRs (open 15+ days!)
cd ~/recs.community
gh pr merge 1 --squash  # scaffold
gh pr edit 2 --base main && gh pr merge 2 --squash  # schema
gh pr edit 3 --base main && gh pr merge 3 --squash  # auth
# Continue for PRs 4-7, retargeting each to main after its base merges

# Merge muse-shopping PR (open 20+ days!)
cd ~/muse-shopping
gh pr merge 1 --squash  # PR test gate

# Run first-ever code-builder sync
cd ~/.claude/skills/code-builder && code-builder sync

# Clean orphaned branches
cd ~/hbschlac
git branch -r | grep 'claude/eloquent-euler' | xargs -I{} basename {} | xargs -I{} git push origin --delete {}
```

## Known issues

1. ~~**code-builder learning sync has never run.**~~ **RESOLVED**: GH Action deployed at `.github/workflows/code-builder-sync.yml` (2026-06-10). Learnings extracted to `LEARNINGS.md`.
2. **mcp-contributor refresh.sh anchor bug.** Grep expects `## Step 11.1:` but SKILL.md uses `### 11.1`. Creates false-positive issues weekly.
3. **mcp-contributor has zero real-world usage** despite extensive maintenance.
4. ~~**No skill for PM workflows**~~ **RESOLVED**: code-builder v7.4 adds PRD-to-code section (stacked PR decomposition, vertical slicing, schema-first, out-of-scope patterns). Evidence: recs.community 7 PRs from PRD.
5. ~~**No skill for the research pipeline**~~ **RESOLVED**: research-pipeline v1 created 2026-06-05.
6. **mcp-contributor is FROZEN** — over-invested (v4.1 across 30+ sessions, zero real contributions). No further iteration until: anchor bug fixed, stale issues closed, one real MCP contribution made.
7. ~~**Supabase patterns are uncovered.**~~ **RESOLVED**: code-builder v7.3 and vercel-ship v1.2 include Supabase learnings.
8. ~~**No testing strategy skill.**~~ **RESOLVED**: code-builder v7.4 adds testing strategy section (what to test, test-with-bugfix, gradual CI adoption, CI workflow template). Evidence: kindle-schlacter-me 71 tests, muse-shopping CI gate.
9. ~~**Non-Vercel deployment is barely covered.**~~ **RESOLVED**: vercel-ship v1.4 adds Docker/k8s deployment checklists and debugging patterns. Evidence: kindle-connector deploys Python + Flask to k8s.
10. **No production incident response pattern existed.** debug-escalation v5 now covers production incident triage and resilient fix patterns. Evidence: kindle-schlacter-me PR#2 archive.org outage.
11. ~~**Cross-repo coordination was missing.**~~ **RESOLVED**: session-safety v8 now covers coupled repos (deploy order, shared env vars, sandbox limitations). Evidence: kindle-schlacter-me + kindle-connector coupled PRs.
12. ~~**No performance optimization patterns.**~~ **RESOLVED**: code-builder v7.5 adds performance optimization section (profile→parallelize→benchmark). debug-escalation v6 adds performance escalation. Evidence: kindle-connector PR#1 30s→3s.
13. ~~**No async workflow / state machine patterns.**~~ **RESOLVED**: code-builder v7.5 adds async multi-step workflow section (state transitions, event-time ordering, idempotent handlers). Evidence: kindle-schlacter-me send stages + Resend webhooks.
14. ~~**No domain migration guidance.**~~ **RESOLVED**: vercel-ship v1.3 adds domain migration checklist (repo rename, DNS, OAuth, webhooks, SEO). Evidence: recs.community PR#7 domain rename.
15. ~~**MCP deployment tools were a blindspot.**~~ **RESOLVED**: vercel-ship v1.3 adds MCP tools section for deployment verification. Evidence: every web session has Vercel MCP tools but no skill mentioned them.
16. **recs.community has 7 stacked PRs open for 15+ days with zero merges.** session-safety v9 adds stuck stack detection, v11 adds cross-repo merge workflow. PRs still need to be merged — requires laptop or adding repo to web session via `list_repos`/`add_repo`.
17. **mcp-contributor cron creates false-positive issues weekly.** 6 identical issues May-Jun 2026 (all reporting 11 anchor misses). The cron should be disabled or the anchor bug fixed — "FROZEN" doesn't stop the automation.
18. **muse-shopping #1 is open 20+ days (since May 22).** PR adds test gate for broken-in-prod. Not tracked previously — same stuck-PR pattern as recs.community.
19. **code-builder parallel mode has never been used in production.** 7 versions of the most complex execution mode with zero run logs. First real use should be N=3 with full logging.
20. **No project has monitoring/alerting configured.** Incidents are discovered reactively. debug-escalation v7 adds proactive monitoring patterns but no project has implemented them yet.
21. ~~**Profile README is stale.**~~ **RESOLVED**: README.md updated with kindle-schlacter-me and recs.community (2026-06-12).
22. **No Claude Code web session patterns in any skill.** Sessions run in ephemeral containers with MCP tools, subagents, and network constraints — none of this was covered. code-builder v8.2, debug-escalation v8, session-start-hook v6 now address this.
23. **No ship/launch announcement patterns.** content-quality covered portfolio copy but not "I just shipped, tell people." content-quality v8 adds ship announcement templates.
24. **No database migration + deploy coordination.** Supabase/Prisma migrations must run before Vercel deploy. vercel-ship v1.6 adds migration coordination checklist.
25. **No test framework setup guidance.** Projects starting tests from zero had no patterns for Jest/Vitest/pytest initial setup. code-builder LEARNINGS.md now covers this.
26. **project-bootstrap and session-start-hook were disconnected.** Bootstrapping a repo should generate hooks too. project-bootstrap v1.3 cross-references session-start-hook.
27. **ISR/SSG stale data debugging was missing from vercel-ship.** Added revalidation debugging patterns to vercel-ship v1.6.
28. **research-pipeline had no Claude API integration guidance.** v1.1 adds model selection, batching patterns, and data viz library comparison.
29. ~~**No pipeline hardening pattern.**~~ **RESOLVED**: code-builder LEARNINGS.md adds pipeline hardening checklist (map→audit→validate→escape hatch). debug-escalation v9 adds pipeline hardening section. Evidence: kindle-schlacter-me PRs #6-#20 (15 iterations on same pipeline).
30. ~~**No PWA/mobile web patterns.**~~ **RESOLVED**: code-builder LEARNINGS.md adds iOS Safari (auto-zoom, safe-area, lost responses), durable client state, and test-on-real-device guidance. Evidence: kindle-schlacter-me PR#4 (iPhone fixes).
31. ~~**No file format compliance / content integrity patterns.**~~ **RESOLVED**: code-builder LEARNINGS.md + pre-flight check for format validation before point of no return. Evidence: kindle-schlacter-me PR#7 (EPUB mimetype), PR#17 (fake torrents).
32. ~~**No error/status copy patterns.**~~ **RESOLVED**: content-quality v9 adds error and status copy section (honest messaging, visible failures, actionable next steps). Evidence: kindle-schlacter-me PR#13, PR#16, PR#18.
33. ~~**No search engineering patterns.**~~ **RESOLVED**: code-builder LEARNINGS.md adds query parsing, multi-source ranking, user override, parallel fan-out. Evidence: kindle-schlacter-me PR#5 (recall), PR#12 (auto-pick).
34. ~~**No client-server state sync patterns.**~~ **RESOLVED**: code-builder LEARNINGS.md adds polling, durable status, failure visibility, optimistic UI reconciliation. Evidence: kindle-schlacter-me PR#18 (stuck "Sending"), PR#13 (lost state on reload).
35. ~~**No feature gating patterns.**~~ **RESOLVED**: code-builder LEARNINGS.md adds gate-risky-features-off, narrow gating point, env var pattern. Evidence: kindle-schlacter-me PR#14 (summary embed gated off for deliverability).
36. ~~**Stuck PR escalation lacked time-based urgency.**~~ **RESOLVED**: session-safety v13 adds escalation table: 7d→14d→21d→30d with progressively stronger actions (flag→block new PRs→rebase/squash→abandon). Evidence: recs.community #4-7 (17+ days) and muse-shopping #1 (22+ days) treated the same as 7-day-old PRs.
37. **mcp-contributor cron noise is escalating.** 7 identical "11 anchor misses" issues filed May 3 - Jun 14, all unactioned. This is negative-value automation — it trains people to ignore all alerts. session-safety v14 adds automated system noise triage with disable-or-fix rule.
38. **No rapid shipping mode for batch feature development.** kindle-schlacter-me shipped 20 PRs in 2 sessions. PRs #6-20 all targeted the same pipeline, with each PR discovering a new failure mode reactively. code-builder v8.4 adds rapid shipping mode with scope management and the "5-PR pipeline audit" rule.
39. **No invisible downstream failure patterns.** Amazon silently rejects EPUBs with no error callback. 6 kindle-schlacter-me PRs (#7, #8, #9, #14, #15, #17) discovered validation layers empirically. debug-escalation v10 adds invisible downstream failures section with progressive validation checklist.
40. **No in-app UX copy guidance.** content-quality covered error/status messages (v9) but not button labels, modals, empty states, or confirmation dialogs. content-quality v10 adds full in-app UX copy section. Evidence: kindle-schlacter-me PRs #1-20 produced extensive UX copy.
41. **`list_repos`/`add_repo` tools are not available in all web sessions.** session-safety v11 assumed they existed. Confirmed unavailable in Jun 14 session — no fallback existed. session-safety v14 adds concrete cross-repo escalation (GHA merge workflow, direct session in target repo).
42. **recs.community PRs #4-7 are now 18+ days old and in "critical" territory.** PRs #1-3 were merged Jun 12, but #4-7 remain open. PR #6 still targets stale branch `hannah/supabase-auth` (needs retarget to main). Requires laptop or opening a web session directly in recs.community.
43. **muse-shopping #1 is a draft PR open 23+ days.** Created by automated "vibe-improver" job, never promoted to ready-for-review. Vercel preview passed. session-safety v14 adds draft PR triage rules.
44. **No two-person development patterns.** kindle-connector is co-developed with Sam (segiddins) with deploy coordination challenges (Hannah writes code, Sam controls k8s host). code-builder LEARNINGS.md adds two-person/multi-agent development patterns.
45. ~~**No graceful degradation patterns.**~~ **RESOLVED**: code-builder v8.5 adds graceful degradation (try/catch/degrade, enhancement isolation, escape hatches). LEARNINGS.md includes try/catch pattern and key insight from kindle-schlacter-me EPUB corruption. Evidence: PRs #9, #14 (summary embed broke core EPUB — needed degradation, not just feature flags).
46. ~~**No post-ship UX discovery checklist.**~~ **RESOLVED**: code-builder v8.5 adds 7-point post-ship UX discovery checklist (real device, state persistence, failure paths, deep links, correction flows). Evidence: 15 of 20 kindle-schlacter-me PRs were reactive UX fixes catchable by proactive testing.
47. ~~**No client-state debugging patterns.**~~ **RESOLVED**: debug-escalation v11 adds client-state debugging (stuck UI, lost state, stale closures, lost HTTP responses). Evidence: kindle-schlacter-me PR#13 (state lost on reload), PR#18 (stuck "Sending" — lost response).
48. ~~**No scheduled/autonomous session patterns.**~~ **RESOLVED**: session-safety v15 adds scheduled session patterns (notification thresholds, self-contained analysis, prohibited autonomous actions). Evidence: scheduled routines produce transcripts nobody reads — PushNotification is the only output that reaches the user.
49. ~~**No untrusted source validation patterns.**~~ **RESOLVED**: code-builder LEARNINGS.md adds 5-layer trust model (format, authenticity, plausibility, integrity, safety) with stub detection and rate-limit detection. Evidence: kindle-schlacter-me PRs #7, #8, #15, #17 — 4 PRs addressing different layers of content trust.
50. **recs.community PRs #4-7 are now 19+ days old (critical → approaching abandon).** At 21+ days, session-safety v13 says: rebase + force-push or close and recreate from main. These are approaching that threshold.
51. **muse-shopping #1 is now 24+ days old (past critical, nearing abandon).** Draft PR with passing preview deploy. Should be merged or closed — draft limbo generates noise and blocks clean PR lists.

## What to work on next (not another skill review)

The skills have been reviewed and improved 8 times in 11 days (Jun 4-15). They are comprehensive. Before doing another review, consider:

**Productive work that moves projects forward:**
- Merge the recs.community PR stack (#4-7, open 18+ days) — open a web session in recs.community, or laptop
- Retarget recs.community PR #6 base branch from `hannah/supabase-auth` to `main` (then merge)
- Merge or close muse-shopping #1 (draft, 23+ days) — promote to ready-for-review and merge, or close
- Disable mcp-contributor cron (7 identical unactioned issues) — or fix the anchor bug
- Build features on kindle-schlacter-me, kindle-connector, or recs.community
- Update the portfolio site (schlacter.me) with new projects (see portfolio-dev end-to-end workflow)
- Set up monitoring/health checks for any deployed project (see debug-escalation v11)

**Remaining structural issues (only if specifically asked):**
- mcp-contributor: fix anchor bug or disable the cron (requires laptop, 5 min)
- mcp-contributor: make one real contribution to the MCP org to validate the skill
- First real code-builder parallel mode run with N=3 and full logging
- Clean up orphaned branches (35+ across hbschlac/hbschlac)

**Do NOT do:** another full skill review. If you found a specific gap, make a targeted edit.

## README editing rules

- Tone: direct, concise, evidence over adjectives. Hannah writes like a builder, not a marketer.
- Every project claim must be verifiable (live site, repo, or deployment).
- Don't add projects that aren't shipped. Don't inflate descriptions.
