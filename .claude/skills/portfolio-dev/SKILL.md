---
name: portfolio-dev
description: >
  Development patterns for schlacter.me (hannah-portfolio repo). Covers Next.js
  App Router conventions, the projects data model, case study pages, Vercel
  deployment, and the warm-neutral design system. Activates on portfolio site work.
---

# portfolio-dev

## Activation

Triggers when working in `hannah-portfolio` or on schlacter.me-related tasks.

Explicit: `/portfolio-dev`, "update my portfolio," "add a project to the site."
Implicit: editing files in `hannah-portfolio`, discussing case studies or project pages,
working on schlacter.me content.

Do NOT activate for: other repos, non-portfolio tasks.

**Relationship to code-builder:** portfolio-dev provides domain context. code-builder
provides the execution framework (parallel/single/debug). Both can be active simultaneously —
portfolio-dev informs the task, code-builder executes it.

---

## Architecture

### Stack

- **Framework:** Next.js (App Router)
- **Styling:** Tailwind CSS
- **Deployment:** Vercel
- **Repo:** `hbschlac/hannah-portfolio`

### Key directories

```
app/
  page.tsx              # Landing page
  projects/
    page.tsx            # Projects index
    [slug]/page.tsx     # Individual project pages
  layout.tsx            # Root layout
lib/
  projects.ts           # Project data model — source of truth for all projects
public/
  images/               # Project screenshots, assets
```

### Data model: `projects.ts`

All projects are defined in `lib/projects.ts`. Each project has:
- `slug` — URL-safe identifier
- `title` — display name
- `description` — one-line summary
- `longDescription` — case study body (markdown or JSX)
- `stack` — technology tags
- `links` — live site, repo, etc.
- `image` — hero image path
- `featured` — whether it appears on the landing page
- `category` — grouping (shipped product, research, skill, etc.)

**When adding a new project:** add it to `projects.ts` first. The page routes
read from this file. Don't create a page without a data entry.

---

## Design System

### Colors (warm-neutral palette)

The site uses a warm-neutral palette. Do not introduce cold blues, saturated
primary colors, or neon accents. Stay within the existing color variables
defined in `globals.css` or `tailwind.config`.

### Typography

- Headings: clean sans-serif, not decorative
- Body: readable at small sizes, generous line-height
- Code: monospace for technical content

### Tone

Hannah's voice: direct, specific, slightly irreverent. Not corporate. Not "passionate
about leveraging AI to streamline workflows." More like "No CS degree. Built it anyway."

Invoke the content-quality skill for any user-facing text.

---

## Common Tasks

### Adding a new project

1. Add entry to `lib/projects.ts` with all required fields
2. Add hero image to `public/images/`
3. Verify the project page renders at `/projects/{slug}`
4. If `featured: true`, verify it appears on the landing page
5. Run `npm run build` — catches missing imports, broken links

### Writing a case study

1. Lead with the most interesting specific fact, not a summary paragraph
2. Include concrete numbers (users, requests, improvements) where available
3. "What I built" → "Why it matters" → "How it works" (briefly) → "What I learned"
4. No throat-clearing. No "In today's rapidly evolving landscape."
5. Invoke content-quality skill on the final text

### Updating the landing page

1. The landing page pulls featured projects from `projects.ts`
2. Don't hardcode project content on the landing page — keep it data-driven
3. Test at mobile (375px), tablet (768px), and desktop (1280px) breakpoints

---

## Deployment

### Vercel specifics

- Push to `main` triggers production deploy
- Preview deployments on PRs
- No `fs` module in any server component or API route
- Environment variables must be set in Vercel dashboard, not `.env` files
- Image optimization: use `next/image` with explicit `width`/`height`

### Pre-deploy checklist

- [ ] `npm run build` succeeds locally
- [ ] No TypeScript errors (`tsc --noEmit`)
- [ ] All external URLs verified
- [ ] Images have alt text
- [ ] Mobile layout tested
- [ ] No hardcoded localhost URLs

---

## Known Patterns

- **Projects page loads from `projects.ts`.** Don't create standalone pages that bypass the data model.
- **Case study content lives in `projects.ts`.** Not in separate markdown files (unless the repo migrates to MDX — check current state).
- **Image paths must match `public/images/` structure.** Don't reference images that don't exist.
- **Tailwind classes follow the repo's existing patterns.** Check adjacent components before introducing new utility patterns.

---

## Changelog

- **2026-05-27 — v1: initial skill (addresses 65% of actual usage)**
  - Covers: architecture, data model, design system, common tasks, deployment
  - Based on: 28 session branches where portfolio work was the primary activity
