---
name: portfolio-dev
description: >
  Accelerates development on Hannah's portfolio site (schlacter.me) and
  similar Next.js + Vercel + Tailwind projects. Encodes the content data
  model, visual design system, page creation workflow, case study template,
  and deployment patterns so Claude doesn't need to rediscover them each
  session. Auto-activates when working in hannah-portfolio or any Next.js
  App Router project that matches the stack fingerprint. Announces activation
  so Hannah knows the skill is active.
---

# portfolio-dev

Encodes the architecture, patterns, and conventions of schlacter.me so every
session starts with full context instead of rediscovery.

## When this skill activates

**Explicit triggers:**
- `/portfolio-dev`
- "work on my portfolio", "update schlacter.me", "add a new project"
- "new case study", "new page", "add a route"
- "portfolio-dev" mentioned in conversation

**Implicit triggers:**
- Working directory is `hannah-portfolio` or contains `content/projects.ts`
- Working in a Next.js App Router project with `app/` directory + Tailwind + Vercel config
- User mentions schlacter.me, portfolio, case study, or project page
- File being edited matches `app/*/page.tsx` or `content/projects.ts`

**Do NOT activate:**
- Working on mcp-contributor, code-builder, or other skill repos
- Pure API/backend work unrelated to the portfolio
- Non-Next.js projects

## Announcement (required, every activation)

Print one line:
`portfolio-dev activated — [context]. [<=15-word summary of what's loaded.]`

Example: `portfolio-dev activated — hannah-portfolio detected. Design system + content model + 20 routes loaded.`

## Architecture

### Stack
- **Framework:** Next.js 15+ App Router (server components by default)
- **Styling:** Tailwind CSS with custom theme
- **Hosting:** Vercel (auto-deploy on push to main)
- **Font:** Inter (variable weight)
- **Palette:** warm neutral — `#F8F6F2` background, `#1A1A1A` text, `#8A8A8A` muted

### Directory structure
```
app/
  [slug]/page.tsx          ← catch-all for dynamic project/case study routes
  projects/page.tsx        ← projects index with Manifesto + GitHub Activity
  claude-code/page.tsx     ← Claude Code stats (server component, reads JSON)
  contact/page.tsx
  api/                     ← API routes
  layout.tsx               ← root layout (metadata, font, analytics)
  globals.css              ← Tailwind directives + custom properties
  page.tsx                 ← home page
components/                ← shared components
content/
  projects.ts              ← canonical project data model (see below)
lib/                       ← utilities
public/                    ← static assets, JSON data files
```

### Content data model (projects.ts)

Every project is defined as an object in `content/projects.ts`. The schema:

```typescript
interface Project {
  slug: string           // URL path segment, used for routing
  title: string          // Display name
  description: string    // One-line summary shown on /projects
  url?: string           // Live URL if deployed
  problem?: string       // What problem it solves
  details?: string       // Extended description / build narrative
  stack?: string[]       // Technologies used
  metrics?: string[]     // Quantified outcomes
  screenshots?: string[] // Image paths in /public
  status?: 'live' | 'prototype' | 'archived'
}
```

When adding a new project, ALWAYS update `content/projects.ts` first. The
`/projects` page and `[slug]` route read from this file.

## Workflow: Adding a new project/case study

### Step 1 — Update content/projects.ts
Add a new entry to the projects array. Follow the existing pattern exactly:
- slug: kebab-case, matches the route directory name
- description: one sentence, present tense, starts with "A" or verb
- Include problem, details, stack, and metrics if available

### Step 2 — Create the route directory
```bash
mkdir -p app/{slug}
```

Create `app/{slug}/page.tsx` as a server component. Match the existing pattern:
- Import shared components from `components/`
- Use the warm neutral palette (don't introduce new colors)
- Server component unless interactivity is required
- If client interactivity needed, extract to a separate `Client.tsx` with `'use client'` directive

### Step 3 — Visual consistency check
Before marking done, verify against the design system:
- Background: `bg-[#F8F6F2]` or `bg-stone-50`
- Text: `text-[#1A1A1A]` for headings, `text-[#8A8A8A]` for muted
- Font: Inter (inherited from layout)
- Spacing: consistent with existing pages (check neighboring routes)
- No emojis in page content unless the existing page uses them
- Responsive: check at mobile (375px) and desktop (1440px) widths

### Step 4 — Verify deployment
- Run `npm run build` to catch build errors
- Check for TypeScript errors: `npx tsc --noEmit`
- If dev server is running, check the new page in browser
- Vercel will auto-deploy on push to main

## Workflow: Updating an existing page

### Step 1 — Locate the source of truth
- Page content in `app/{slug}/page.tsx`
- Project metadata in `content/projects.ts`
- Shared components in `components/`
- Static data in `public/`

### Step 2 — Make changes
- Keep changes scoped to the specific page/component
- Don't refactor shared components unless the change requires it
- If updating project metadata, update `content/projects.ts` AND the page

### Step 3 — Verify no regressions
- `npm run build` must pass
- Check the changed page + the /projects index (it reads from projects.ts)

## Design system rules

1. **No new colors** without explicit approval. The palette is intentionally constrained.
2. **No component libraries** (no shadcn, no MUI). Hand-rolled Tailwind components.
3. **Server components by default.** Only use `'use client'` when React hooks or browser APIs are needed.
4. **No loading spinners** — use Suspense boundaries with skeleton fallbacks if needed.
5. **Links use muted gray** (`text-[#8A8A8A]`) with hover darkening.
6. **Minimal UI** — if in doubt, remove rather than add. White space is a feature.
7. **No tooltips or popovers** — content should be self-explanatory.
8. **Images in /public** — never use external image URLs without explicit approval.

## Common patterns

### Server component with data
```tsx
import { projects } from '@/content/projects'

export default function Page() {
  const project = projects.find(p => p.slug === 'my-project')
  return (/* ... */)
}
```

### Client component extraction
```tsx
// app/my-page/page.tsx (server)
import { InteractiveSection } from './InteractiveSection'

export default function Page() {
  return <InteractiveSection data={staticData} />
}

// app/my-page/InteractiveSection.tsx (client)
'use client'
export function InteractiveSection({ data }: Props) {
  const [state, setState] = useState(/* ... */)
  return (/* ... */)
}
```

### API route
```tsx
// app/api/my-endpoint/route.ts
import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({ data })
}
```

## Conflict resolution

If **code-builder** is also active, let code-builder handle the implementation
quality (parallel drafts, scoring) while this skill provides the architectural
context (data model, design system, conventions). They complement, don't conflict.

## Current learnings

Last synced: 2026-05-12 (initial — from build-log + repo structure analysis)

**A. Architecture patterns:**
1. `content/projects.ts` is the single source of truth for project metadata — never duplicate project info in page components
2. The `[slug]` catch-all route handles dynamic pages — don't create top-level route dirs for one-off content that fits the project template
3. Static JSON files in `public/` (like claude-code-stats.json) are read at build time by server components — no runtime fetch needed
4. The /projects page uses a Manifesto component and GitHub Activity component — new projects auto-appear if added to projects.ts

**B. Common mistakes to avoid:**
1. Don't add `'use client'` to page.tsx — extract interactive parts to separate client components
2. Don't import from `next/router` (Pages Router) — use `next/navigation` (App Router)
3. Don't hardcode the color palette in components — use the Tailwind classes consistently
4. Build must pass before considering any task done — `npm run build` catches SSR issues that dev mode misses
