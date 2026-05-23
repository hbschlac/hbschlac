# Skill Review — May 2026

## Scope

Reviewed `code-builder` and `mcp-contributor` skills against all recent
session activity (April–May 2026) across hannah-portfolio, interior-designer-portfolio,
libby-hold-monitor, muse-shopping, and build-log repos.

---

## code-builder: What Changed and Why

### Pain points not met by the original skill

| Gap | Evidence | Fix applied |
|-----|----------|-------------|
| **Rubric ignores UI/visual work** | >60% of May commits are styling/layout changes (fonts, colors, grids, mobile fixes). Rubric only scored correctness, tests, typecheck. | Added **UI & UX criteria** (15 pts): mobile responsiveness, visual consistency, accessibility baseline |
| **Mobile is a recurring blindspot** | "fix cramped mobile header," "mobile shortcuts," separate mobile-fix commits appear repeatedly | Added **375px/768px/1024px breakpoint checks** as scoring criterion and post-merge verification step |
| **No visual mode for design tasks** | Binary parallel/single decision misses styling tasks (10-30 lines, subjective design space) | Added **visual mode**: 3 drafts for CSS/styling tasks |
| **No post-merge browser verification** | Skill ended at merge — no check that the UI actually looked right | Added **Step 5: Post-Merge Verification** with browser + mobile checks |
| **No framework-specific intelligence** | User works exclusively in Next.js/React/Tailwind. Skill was framework-agnostic | Added **Section 8: Framework Awareness** with Next.js, React, and Tailwind checks |
| **No error recovery** | What happens when worktrees fail, agents timeout, all drafts are bad? Undefined. | Added **Section 9: Error Recovery** with fallback paths |
| **Security was an afterthought** | Only "no hardcoded tokens" in learnings. User builds auth flows, payment integrations. | Added **security overlay** as deduction-based criterion with disqualification floor |
| **Learnings were stale** | 12 bullets, never updated since April 14 backfill | Expanded to 4 categories (Process, Code, UI/Visual, Framework), raised cap to 40, added staleness rule |
| **Gap between 10-30 lines** | No guidance for medium-sized tasks | Visual mode covers this range for UI tasks |

### Tasks that could have been done faster

| Task pattern | What happened | What code-builder should have done |
|--------------|--------------|-----------------------------------|
| Event site styling iterations (Jamie's bach) | Multiple commit cycles: try color → fix contrast → fix mobile → fix font spacing | Visual mode (3 drafts) would have explored the design space in one pass |
| Portrait grid layout | Separate commits for headshot processing, grid layout, responsive fixes | Single parallel run with UI criteria would have caught mobile and consistency issues upfront |
| Job tracker UX fixes | "fix three issues from code review" — multiple small bugs shipped, then fixed | Rubric scoring would have caught these before merge |

### Tasks you asked Claude to do that it couldn't

Based on commit patterns (fix-after-fix sequences), Claude likely couldn't:
- **Predict visual design preferences** — color/font choices required iteration
- **Test mobile rendering without a browser** — responsive issues were found after deployment
- **Cross-page visual regression detection** — changes to shared styles broke other pages

### Blindspots the original skill missed

1. **Image optimization** — recent work adding portraits, venue photos, design assets. No criterion for image handling (sizing, format, alt text, lazy loading)
2. **SEO/metadata** — public-facing sites (portfolio, event page) need OpenGraph, title, description. Not checked
3. **Performance/bundle size** — Next.js apps should track bundle size. No criterion
4. **Cross-browser consistency** — only mobile width was a problem; cross-browser not tested
5. **Content/copy quality** — event site copy, portfolio text — no review layer
6. **Deployment pipeline awareness** — Vercel builds can fail on things that pass locally (env vars, edge runtime limits)
7. **Persistent state handling** — "persist unlock across tabs + sessions" commit suggests localStorage/sessionStorage patterns needed attention

---

## mcp-contributor: Findings

### Status: Functional but unmaintained

The skill is thorough (~970 lines) and well-structured. However:

| Issue | Status | Impact |
|-------|--------|--------|
| **5 consecutive weeks of unresolved drift** (issues #4-#8) | Open since April 19 | SKILL.md may contain stale information about MCP governance, spec, WG list |
| **§4 titled "SDK workflow" but applies to all non-spec repos** (issue #3) | Open | Misleading — users following §4 only for SDKs miss applicable guidance |
| **§6 repo map missing Inspector, Registry, ext-* repos** (issue #2) | Open | Incomplete reference — contributor won't find all relevant repos |
| **No pointer from capability questions to §11.7 lifecycle** (issue #1) | Open | Navigation gap — users asking "what can MCP do?" don't find lifecycle spec |
| **Empty session log** | Structural | Skill has never been used for an actual MCP contribution |
| **WG/IG list snapshot from April 16** | Stale | Over 5 weeks old — groups may have formed, dissolved, or changed cadence |

### Recommended changes (not implemented — separate repo)

1. **Auto-consolidate drift issues** — instead of 5 separate weekly issues, consolidate into one rolling issue
2. **Fix §4 title** to "Non-Spec Repository Workflow" and make SDK a subsection
3. **Update §6 repo map** to include Inspector, Registry, and ext-* repos
4. **Add cross-references** from §11.4-11.5 capability sections to §11.7 lifecycle
5. **Add a "Quick Start" section** at the top — the 970-line document is overwhelming for first use
6. **Consider splitting** into core skill + appendix sections that load on demand

---

## Cross-Cutting Recommendations

1. **Skills should compose** — when mcp-contributor triggers a coding task, code-builder should activate for the implementation portion
2. **Build-log has no May entries** despite active development — consider automating build-log entries from run logs
3. **The most active workflow has no skill** — portfolio/event site development is highest-volume but unassisted by any skill
4. **Drift detection pattern from mcp-contributor should apply to code-builder** — the learnings section should be validated against recent sessions automatically
