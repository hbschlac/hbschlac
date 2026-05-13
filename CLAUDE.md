# hbschlac/hbschlac — GitHub Profile README

This repo contains Hannah Schlacter's public GitHub profile page (`README.md`)
and skill-related artifacts.

## Owner context

Hannah Schlacter — Senior PM at Walmart (BuyBox, ~400M daily product page views).
No CS degree. Builds consumer products and AI tools. Primary dev environment is
Claude Code (~800+ hours, 300+ sessions, 8 shipped projects).

## Critical: Read before doing anything

### The Groundhog Day problem (DO NOT REPEAT)

Between April 14 and May 13, 2026, **14 separate sessions** audited the same
skills, proposed the same improvements, and pushed to isolated branches that
never merged. If you are about to audit skills, update the README, or improve
code-builder — **check the existing branches first**. The work may already exist.

Key branches with unmerged work:
- `claude/eloquent-euler-TZDUi` — code-builder v2 (debug loop, pre-flight, 25K words)
- `claude/eloquent-euler-8Exat` — Full skills audit + portfolio-dev skill proposal
- `claude/eloquent-euler-OdhHA` — Cross-skill audit + insight-detector.py implementation
- `claude/eloquent-euler-7gZPQ` — Best README version + Skills arc narrative
- `claude/review-code-skill-plan-5p6Yc` — 19K-word backfill plan
- `claude/eloquent-euler-6IX8U` — Meta-audit + consolidated improvements (THIS branch)

### Sandbox constraint

Web sessions are scope-locked to `hbschlac/hbschlac`. You CANNOT push to
`code-builder`, `mcp-contributor`, `claude-config`, or any other repo. If you
need to change those repos, write the changes here with clear instructions for
Hannah to apply from her laptop.

## What matters for edits

- The README is a portfolio landing page. Tone: direct, concise, evidence over adjectives.
- Every project claim must be verifiable — link to live site, repo, or deployment.
- The "Skills arc" section tells a specific narrative: designed the concept before
  Anthropic shipped it, then built production skills. Keep this arc intact.
- Don't add projects that aren't shipped. Don't inflate descriptions.

## Related repos

| Repo | What | Public | Status |
|------|------|--------|--------|
| `code-builder` | Claude Code skill: parallel drafts, self-scoring, self-learning | yes | v1 in repo; v2 on TZDUi branch here; v3 on 6IX8U branch here |
| `mcp-contributor` | Claude Code skill for MCP governance contributions | yes | 7 open issues, anchor bug in refresh.sh |
| `claude-code-insights-dashboard` | Session transcript analytics | yes | insight-detector.py stub; full impl on OdhHA branch here |
| `hannah-portfolio` | schlacter.me — Next.js portfolio site | yes | Active |
| `skills-gallery` | Consumer-friendly Skills concept site | no | skills-roan.vercel.app |
| `claude-config` | Claude Code config, skills, memory | no | ~/.claude/ versioning |
| `interior-designer-skill` | AI design advisor skill | no | — |
| `muse-shopping` | Muse e-commerce platform | yes | — |
| `libby-hold-monitor` | Kindle x Libby automation | no | — |
| `managed-agents-pulse` | Managed agents research collector | yes | Only skill actually running |

## Known issues awaiting laptop execution

1. **mcp-contributor refresh.sh anchor bug** — grep expects `## Step 11.1:` but
   SKILL.md uses `### 11.1 Design Principles`. Causes 11 false-positive anchor
   misses every week. 5-minute fix. Has been creating noise issues for 4+ weeks.
2. **code-builder sync has never run** — No GH Action or cron exists. The learning
   loop (the skill's core differentiator) is inert.
3. **insight-detector.py is a stub in the live repo** — Full implementation with
   8 detection algorithms exists on the OdhHA branch of THIS repo.
4. **14 branches of work need selective merging** — See INTEGRATION-PLAYBOOK.md.

## Deployment

The README renders automatically on github.com/hbschlac. No build step, no CI.
