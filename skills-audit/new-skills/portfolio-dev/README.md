# portfolio-dev

A Claude Code skill that encodes the architecture, design system, and conventions
of schlacter.me (hannah-portfolio) so Claude starts every session with full context.

## Why this exists

schlacter.me represents 65% of April Claude Code usage and 95% of March usage.
Without a skill, every new session requires re-explaining the stack, data model,
design palette, and deployment workflow. This skill eliminates that overhead.

## Install

```bash
cp SKILL.md ~/.claude/skills/portfolio-dev/SKILL.md
```

Claude Code will auto-discover it. Triggers on any work in the hannah-portfolio
repo or explicit `/portfolio-dev` invocation.

## What it covers

- Next.js 15 App Router architecture (server components by default)
- Content data model (`content/projects.ts` schema)
- Visual design system (warm neutral palette, Inter font, Tailwind)
- New project/case study creation workflow
- Deployment patterns (Vercel auto-deploy)
- Common mistakes to avoid

## Keeping it current

Update the `## Current learnings` section in SKILL.md as new patterns emerge.
If the portfolio's architecture changes significantly (new framework, new hosting),
update the Architecture section.
