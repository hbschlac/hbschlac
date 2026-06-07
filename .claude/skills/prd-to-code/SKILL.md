---
name: prd-to-code
description: >
  Translates a PRD (Product Requirements Document) into a sequenced
  technical plan with stacked PRs. Covers PRD decomposition, schema design
  from user stories, PR ordering, scope management, and handoff documentation.
  Built from recs.community (7 PRs from PRD) and kindle-schlacter-me (10 features).
---

# prd-to-code

Translates product requirements into a sequenced implementation plan. Handles the gap between "here's what to build" and "here's the first PR."

**Not for:** writing PRDs (that's product work), executing individual PRs (code-builder does that), or deployment (vercel-ship does that).

**Relationship to code-builder:** prd-to-code sequences the work. code-builder executes each PR. Both can be active — prd-to-code provides the plan, code-builder builds each piece.

**Relationship to session-safety:** prd-to-code creates stacked PRs. session-safety's stacked PR guidance handles the git mechanics of managing them.

---

## Announce activation

> **prd-to-code activated** — [decompose PRD | plan feature round | sequence PRs]. [project.]

---

## Step 1: Read the PRD and extract P0 user stories

Read the entire PRD. Identify user stories by priority:
- **P0:** Must ship for the product to function at all (auth, core data model, primary user flow)
- **P1:** Important but the product works without them (settings, secondary flows, polish)
- **P2:** Nice-to-have (analytics, export, integrations)

If the PRD doesn't have explicit priorities, infer from dependencies: anything that other features depend on is P0.

State the P0 list in one block:
```
P0 user stories:
1. User can sign up and log in
2. User can create a community
3. User can join a community via invite link
4. Members can post recs to a community
5. Members can see recs from their communities
```

---

## Step 2: Map user stories to technical layers

For each P0 story, identify what needs to exist:

| Story | Database | Auth | Routes | Components | API |
|-------|----------|------|--------|------------|-----|
| Sign up / log in | `profiles` table, trigger | Supabase auth wiring, middleware | `/login`, `/signup` | LoginForm, SignupForm | — |
| Create community | `communities`, `memberships` tables | requireUser | `/communities/new` | CommunityForm | server action |
| Join via invite | `invite_links` table | requireUser | `/join/[token]` | — | server action |

This mapping reveals the natural PR sequence: you can't build "create community" without auth, and you can't build auth without the database schema.

---

## Step 3: Sequence into stacked PRs

Order PRs by dependency chain, not by feature importance. Each PR must be deployable and reviewable independently.

### Canonical ordering for a greenfield Next.js + Supabase project

| PR # | Content | Depends on | Complexity |
|------|---------|------------|------------|
| 1 | **Scaffold** — `create-next-app`, Tailwind, TypeScript, basic file structure | nothing | Low |
| 2 | **Schema + route stubs** — migration files, RLS policies, empty page files | #1 | Medium |
| 3 | **Auth wiring** — Supabase client, middleware, login/signup forms, server actions | #2 | Medium |
| 4 | **CI** — lint + typecheck + build on every PR | #1 (but review after #3) | Low |
| 5 | **Onboarding docs** — CLAUDE.md, COORDINATION.md, review checklist | any | Low |
| 6 | **Core feature** — the first real user flow (create + list) | #3 | High |
| 7+ | **Secondary features** — invite links, settings, export, admin tools | #6 | Varies |

### Rules for PR sequencing

- **Infrastructure before features.** Schema, auth, and CI must land before feature PRs.
- **Each PR adds one capability.** Not "auth + communities + invites" in one PR.
- **Stubs are OK.** Route stubs (`export default function Page() { return <div>TODO</div> }`) let the build pass and establish the routing structure for later PRs.
- **CI in its own PR.** Don't couple CI setup with feature code — it blocks review of both.
- **Docs PRs are separate.** CLAUDE.md, review checklists, and coordination docs are separate PRs so another developer's Claude can self-orient immediately.

---

## Step 4: Plan each PR before writing code

For each PR in the sequence, write a brief plan:

```
PR #3: Supabase auth wiring
  Files: src/lib/supabase/{server,client,middleware}.ts, src/middleware.ts, 
         src/lib/auth.ts, src/app/login/*, src/app/signup/*
  Auth pattern: @supabase/ssr three-file pattern
  Depends on: PR #2 (profiles table, on_auth_user_created trigger)
  Verifies: signup seeds profiles row, login establishes cookie, middleware refreshes
  Out of scope: 2FA, email confirmation, password reset, real community queries
```

The "out of scope" line prevents feature creep. Write it before coding.

---

## Step 5: Feature rounds (for existing products)

For products past the greenfield phase, batch related features into numbered rounds:

```
Round 2 (kindle-schlacter-me):
  R0 — Per-address delivery banners (requires webhook)
  R1 — Real torrent send stages (bridge job polling)
  R2/R3 — Search ranking (relevance scorer + dedup)
  R4 — Library sort (newest/oldest/author/rated)
  R6 — Goodreads CSV export
  R7 — Dedicated /library page + shared AppHeader
  R8/R10 — Book modal + star ratings (Google Books metadata)
  R9 — Footer
```

### Rules for feature rounds

- **Group by theme.** Round 2 is "make the library useful." Don't mix unrelated features.
- **Number features within the round.** R0-R10, not "feature A, B, C." Numbers create a natural review order and make PR descriptions scannable.
- **Ship the round in one PR if features are interdependent.** If R2 (search ranking) affects R7 (library page), they should be in the same PR.
- **Ship separately if features are independent.** Resilience fixes (cross-source fallback) are a separate PR from UI features.

---

## Step 6: Handoff documentation

Every PR that requires human action must end with a clear handoff section:

### Pattern: "What you need to do"

```markdown
## What you need to do (N quick things)

1. **[Action] — [where]:**
   - Step-by-step instructions
   - Expected result to verify it worked

2. **[Action] — [where]:**
   - Step-by-step instructions
```

### What to include

- **External dashboard actions.** Webhook activation, env var creation, DNS records, OAuth app registration.
- **Deploy commands.** `git pull && ./deploy.sh`, k8s rebuild, Vercel redeploy.
- **Verification steps.** "After setting the env var, POST to the webhook endpoint — expect 401 (not 503)."

### What NOT to include

- Steps Claude already completed (don't list things done in the PR).
- Vague instructions ("update the config as needed" — say exactly which config and which value).
- Steps that block the PR from being reviewed (handoffs should be post-merge, not pre-merge).

---

## Step 7: Scope management

### "Out of scope (intentional)" sections

Every PR should list what it deliberately doesn't do:

```markdown
## Out of scope (intentional)
- 2FA enrollment UI — Supabase supports MFA; will add after auth works end-to-end
- Email confirmation page — will add if email confirmation is enabled
- Password reset flow — separate PR
- Real /communities query — separate PR
```

**Rules:**
- State WHY it's out of scope (not ready, separate concern, blocked on something else).
- If it's the next PR, say so ("separate PR" or "next PR").
- Don't list things nobody would expect to be in this PR. Only list things a reviewer might wonder about.

### Scope creep signals

Stop and check scope if you find yourself:
- Adding a feature not in the current PR plan
- Fixing a bug in code from a different PR in the stack
- Adding styling/polish to stub pages
- Writing tests for code that isn't in this PR yet

---

## Anti-patterns

- **Don't plan 20 PRs.** If your sequence has more than 8 PRs, you're over-decomposing. Some PRs can be combined.
- **Don't build auth from scratch.** Use the framework's auth (Supabase Auth, NextAuth, Clerk). The PRD says "users can log in," not "build an auth system."
- **Don't design the database in code.** Write migration SQL first, then build the code around it. The schema IS the design.
- **Don't sequence by user story.** Sequence by technical dependency. "Create community" depends on "auth" even if it's a higher-priority user story.
- **Don't skip route stubs.** Empty pages that show "TODO" are better than missing routes. They prove the routing works and give a surface for `npm run build` to validate.

---

## Changelog

- **2026-06-07 — v1: Initial skill from gap analysis of 15 PRs**
  - Covers: PRD decomposition, PR sequencing, feature rounds, handoff docs, scope management
  - Evidence: recs.community PRs #1-7 (greenfield from PRD), kindle-schlacter-me PR #1 (Round 2, 10 features)
  - Addresses CLAUDE.md known issue #4
