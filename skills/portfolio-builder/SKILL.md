---
name: portfolio-builder
description: >
  Streamlines the schlacter.me development cycle: case study creation, content
  iteration, feature builds, research data pipelines, and deploy validation.
  Optimized for the actual workload — portfolio updates, admin tools, and
  content shipping.
---

# portfolio-builder

## 0. Announcement (every activation)

```
🔧 portfolio-builder activated — [case-study | feature | content-edit | research-pipeline | deploy-fix]. [one-line reason].
```

---

## 1. Activation triggers

### Explicit
- `/portfolio-builder` slash command
- "add a case study," "new project page," "update the portfolio"

### Implicit
- Working in `hannah-portfolio` repo or a repo that deploys to schlacter.me
- Adding/editing content in `content/projects.ts` or `app/` route directories
- Wiring screenshots, GIFs, or media into pages
- Building admin features for sub-apps (job-tracker, jamie-bach, etc.)
- Research data work that feeds into a portfolio dashboard
- Phrases: "ship this page," "add this section," "tighten the copy," "wire in the screenshots"

### Do NOT activate
- Pure code-builder tasks (greenfield features, refactors with no content component)
- Work on non-portfolio repos
- Pure research with no portfolio output planned

---

## 2. Mode selection

| Mode | When | Process |
|------|------|---------|
| **Case study** | New project page from scratch | Full pipeline: §3 |
| **Feature** | New functionality in existing sub-app | Code-first with §5 deploy validation |
| **Content edit** | Copy rewrite, section addition, media wiring | Content checklist: §4 |
| **Research pipeline** | Data collection → analysis → visualization | Research flow: §6 |
| **Deploy fix** | Broken deploy, build error, runtime bug | Diagnose → fix → validate: §5 |

---

## 3. Case study pipeline

### 3a. Project definition

Every case study needs these fields in `content/projects.ts`:

```typescript
{
  slug: string,           // URL path
  title: string,          // Display name
  oneLiner: string,       // One sentence
  tileInsight: string,    // What makes this interesting (for the grid tile)
  tags: string[],         // e.g. ["AI", "Research", "Product Design"]
  thumbnailColor: string, // Hex color for tile background
  thumbnailImage?: string,// Optional tile image path
  problem: string,        // What was wrong
  hypothesis: string,     // What you bet on
  built: string,          // What you shipped
  broke: string,          // What went wrong
  learned: string,        // Specific, falsifiable takeaway
  nextSteps: string,      // What's next
  keyLearning: string,    // One-line summary
  artifacts: {
    screenshots: string[],
    screenshotCaptions?: string[],
    liveUrl?: string,
    videoUrl?: string,
  }
}
```

### 3b. Quality gates for case study content

Before marking a case study complete:

- [ ] **"So what" test**: The `learned` field must be specific enough to be falsifiable. "I learned a lot about X" fails. "Users who saw methodology first trusted the data 2x more" passes.
- [ ] **Problem→hypothesis→built→broke→learned** arc is complete and coherent
- [ ] **tileInsight** is distinct from oneLiner (tile catches attention; oneLiner explains)
- [ ] **Screenshots exist** at referenced paths in `public/projects/{slug}/`
- [ ] **Screenshot captions** describe what the reader should notice, not just what's shown
- [ ] **liveUrl** resolves (or is explicitly undefined for concept-stage projects)
- [ ] **Tags** are consistent with existing tag vocabulary (check other projects)
- [ ] **thumbnailColor** has sufficient contrast with white text

### 3c. Page route

Create `app/{slug}/page.tsx` using the shared case study layout. Don't build a custom layout unless the project genuinely needs one.

---

## 4. Content edit checklist

For copy rewrites, section additions, and media wiring:

- [ ] **Read existing copy first** — match voice and register. Rewrites that shift tone feel jarring even when technically better.
- [ ] **Accuracy**: claims match source data; no hallucinated stats or inflated numbers
- [ ] **Link integrity**: all URLs resolve; internal links use relative paths
- [ ] **Media committed**: screenshots/GIFs at referenced paths exist in `public/` and are git-added
- [ ] **Mobile readability**: check for overly wide elements, tiny tap targets, horizontal scroll
- [ ] **No orphan content**: new pages linked from navigation; new sections linked from page TOC
- [ ] **Diff is minimal**: don't reformat surrounding code; change only what's needed

---

## 5. Deploy validation

### Pre-push
1. `git status` — working tree must be clean. If dirty: commit or stash first. **Never push with uncommitted changes.**
2. `git diff --cached` — review what's staged. No secrets, no debug logs, no TODO comments.
3. Push once. Do not re-push the same commit.

### Post-deploy
1. Wait for Vercel deployment to reach READY state
2. Check the live URL loads without errors
3. For content changes: spot-check that new sections/images render correctly
4. For feature changes: test the golden path in browser

### Common deploy issues (from recent history)
- **gitDirty deploys**: 14/20 recent deploys had uncommitted changes. Always commit everything before pushing.
- **Duplicate deploys**: Same commit pushed multiple times creates redundant builds. Push once, wait for READY.
- **Build failures from missing images**: Referencing screenshots not yet committed to `public/`. Always `git add` images before the code that references them.

---

## 6. Research pipeline pattern

Many portfolio projects follow this arc:

```
Data source (Reddit, HN, App Store, etc.)
  → Collection script (scraper, API client)
  → Raw dataset (JSON/CSV in repo or KV)
  → Analysis (aggregation, categorization, sentiment)
  → Visualization (dashboard component)
  → Case study page (with methodology + findings)
```

### Research quality gates

- [ ] **Methodology documented**: readers should understand how data was collected before seeing results
- [ ] **Sample size stated**: "1,183 data points" not "lots of feedback"
- [ ] **Collection date range stated**: data has a shelf life
- [ ] **Source attribution**: link to the platform/community where data originated
- [ ] **Deduplication applied**: raw scrapes often contain duplicates
- [ ] **Refresh mechanism exists**: if data goes stale, there should be a way to re-collect (cron, manual script, GitHub Action)

---

## 7. Sub-app patterns

The portfolio contains several sub-apps (job-tracker, jamie-bach-2026, claude-code stats, claude-ideas). Common patterns:

### Auth
- Use the same auth pattern as the main site
- Admin routes: `app/{slug}/admin/` with server-side auth check
- Don't invent a new auth mechanism per sub-app

### State
- Vercel KV for persistent state (todos, preferences, survey responses)
- Always wrap KV reads in error handling — KV timeouts return `undefined`, not errors
- Use server actions for mutations, not client-side API calls

### Styling
- Match the site's existing design tokens (colors, fonts, spacing)
- Sub-apps can have their own palette (jamie-bach has sail palette) but should share layout structure

---

## 8. Learnings

**Last synced:** 2026-05-14

1. "Case study 'so what' must be falsifiable. 'I learned about X' is a diary entry; 'users who saw Y did Z' is a portfolio piece." (tinker-flywheel April 2026)

2. "Research dashboards: methodology before data. Readers who don't trust collection won't trust analysis." (managed-agents-pulse, workspace-ai patterns)

3. "Match existing voice on rewrites. Register shifts feel jarring even when the new copy is better." (tinker-flywheel tightening)

4. "Admin features should use the same auth as the main site. Inconsistent auth UX confuses users." (jamie-bach admin May 2026)

5. "Vercel KV operations need explicit error boundaries. Timeouts return undefined, causing silent data loss." (jamie-bach KV rebuild)

6. "Commit images before the code that references them. Missing images cause silent 404s on deploy." (kindle-libby content wiring)

7. "Push once per commit. Duplicate pushes create redundant Vercel builds." (deployment audit)

8. "Always check git status clean before pushing. 70% of recent deploys shipped dirty." (deployment audit)

9. "When populating screenshot sections, write captions that tell the reader what to notice — not just what's shown." (ldor prototype section)

10. "For scheduled scrapers (claude-wishlist, managed-agents-pulse), log the collection timestamp and record count. Silent failures in crons go unnoticed for days." (claude-wishlist pattern)
