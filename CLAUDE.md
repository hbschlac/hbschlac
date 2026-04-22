# Hannah Schlacter — Profile Repo

This is a GitHub profile README repo (`hbschlac/hbschlac`). It renders at github.com/hbschlac.

## Cross-Project Learnings

These patterns recur across Hannah's projects. Apply them in every session.

### A. Env var hygiene

Vercel env values frequently contain trailing newlines or whitespace from the dashboard paste UX. Always `.trim()` env vars at the read-site. This has caused production outages 5+ times across schlacter.me (SYNC_SECRET), Muse (GOOGLE_CLIENT_ID, password hash), and interior-designer-portfolio.

When writing code that reads `process.env.*`, trim it:
```js
const SECRET = process.env.MY_SECRET?.trim();
```

### B. Vercel entry point parity

Many projects have both `src/app.js` (standalone Node server) and `api/index.js` (Vercel serverless entry). These MUST stay in sync for:
- Middleware registration (errorHandler, trust proxy, CORS)
- Route mounting order
- Any Express configuration

When modifying one, always check and update the other.

### C. URL verification

Claude can hallucinate URLs. Before committing any curated/external URL list:
- Verify each URL is real (fetch it, check for 200)
- Never ship placeholder or example URLs to production
- This burned the schlacter.me Reddit Pulse feature (fabricated Reddit post URLs deployed live)

### D. Commit completeness

After generating new files in a session, verify they are staged before pushing. Missing files cause Vercel build failures. Run `git status` after `git add` to confirm nothing was missed. This happened with ShareDropdown.tsx and PreviewBanner.tsx on interior-designer-portfolio.

### E. Auth flow testing

Auth code has cascading failure modes that only surface in production:
- Test OAuth redirects against the actual production domain, not just localhost
- Verify frontend reads the exact response envelope the backend sends
- Handle OAuth-only accounts (no password hash) explicitly
- Check that migrations have been run in prod before referencing new columns

### F. GitHub API writes

When writing multiple files to GitHub via API (e.g., data sync endpoints), writes MUST be sequential — parallel PUTs cause SHA conflicts. This has been fixed and re-broken twice.

## Portfolio Projects (schlacter.me)

| Slug | Project | Status |
|------|---------|--------|
| muse | Muse Shopping | Active — full-stack shopping platform |
| home-design | Interior Design Tool | Active — private, built for specific user |
| vantara-agent-studio | Vantara Agent Studio | Demo — Vercel PM application piece |
| claude-skills | Claude Skills | Concept — persistent AI instruction sets |
| claude-wishlist | Claude Wishlist | Active |
| kindle-libby | Kindle × Libby | Shipped — automated library delivery |
| ldor | L'dor | Portfolio piece |
| llm-explainer | LLM Explainer | Portfolio piece |

## README Guidelines

The README is a GitHub profile page. Keep it:
- Concise — scannable in 10 seconds
- Builder-first — lead with what was built, not credentials
- Current — project list should reflect active work
