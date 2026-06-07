---
name: testing-strategy
description: >
  Guidance on what to test, when to test, and test architecture per stack.
  Covers unit tests, integration tests, regression tests, and mocking
  patterns. Built from patterns across kindle-schlacter-me (71 tests),
  muse-shopping (63 tests), and recs.community (CI, 0 tests).
---

# testing-strategy

Decides WHAT to test and HOW to structure tests. code-builder handles execution; this skill handles test design decisions.

**Not for:** running tests (code-builder does that), CI setup (session-start-hook / project-bootstrap), or E2E browser testing (separate concern).

**Relationship to code-builder:** code-builder's pre-flight checks verify tests pass. testing-strategy decides what tests to write in the first place.

---

## Announce activation

> **testing-strategy activated** — [new tests | regression test | test architecture]. [context.]

---

## When to write tests

### Always test

- **Business logic with conditional paths.** Relevance scoring, quota enforcement, search ranking, permission checks. If there's an `if/else` that affects user-visible behavior, test both branches.
- **Data transformation and validation.** Parsing external data (infohash decoding, CSV export, metadata matching), format conversions, serialization. These break silently.
- **External API response handling.** Not the API itself — your code's reaction to success, failure, timeout, malformed response, and empty response. Mock the API, test your handler.
- **Resilience and fallback logic.** Cross-source fallback chains, retry behavior, deadline enforcement, graceful degradation. These have the most edge cases and break the hardest.
- **State machines and transitions.** Delivery status (sending -> delivered -> bounced), membership status (pending -> active -> removed), job stages. Test valid transitions AND invalid ones.
- **Bug fixes.** Every bug fix gets a regression test that fails before the fix and passes after. Non-negotiable.

### Don't test

- **Simple CRUD with no business logic.** A function that inserts a row and returns it doesn't need a unit test. The integration test or E2E covers it.
- **Framework behavior.** Don't test that Next.js renders a component, that Supabase returns rows, or that Express routes match. Trust the framework.
- **UI layout and styling.** Visual regressions need visual testing tools (Chromatic, Percy), not unit tests. A unit test that asserts `className="mt-4"` is worthless.
- **Config and constants.** Don't test that `MAX_QUOTA = 20`. If it's wrong, you'll know immediately.
- **One-off scripts and migrations.** If it runs once and is verified by inspection, a test adds no value.

### Gray area — test if complexity warrants

- **API route handlers.** Test if they contain business logic beyond "call service, return result."
- **React hooks with complex state.** Test custom hooks; don't test `useState` wrappers.
- **Database queries with JOINs or RLS.** Test the query logic if it's complex; trust Supabase/Prisma for simple queries.

---

## Test architecture by stack

### Next.js + TypeScript (Jest or Vitest)

```
__tests__/          or    src/**/*.test.ts
  lib/                    (co-located with source)
    relevance.test.ts
    goodreadsCsv.test.ts
  api/
    send.test.ts
```

**Pattern: co-locate tests with source for libraries, separate for API routes.**

```typescript
// lib/relevance.test.ts — pure function test
import { scoreRelevance } from '../lib/relevance';

describe('scoreRelevance', () => {
  it('ranks exact title match highest', () => {
    expect(scoreRelevance('Little Women', 'Little Women', 'Alcott')).toBeGreaterThan(
      scoreRelevance('Little Women', 'Little Women in Space', 'Other')
    );
  });

  it('returns 0 for empty query', () => {
    expect(scoreRelevance('', 'Any Title', 'Any Author')).toBe(0);
  });
});
```

**Mocking Vercel KV:**
```typescript
// Mock at module level, not per-test
jest.mock('@vercel/kv', () => ({
  kv: {
    get: jest.fn(),
    set: jest.fn(),
    incr: jest.fn(),
  }
}));

import { kv } from '@vercel/kv';

beforeEach(() => jest.clearAllMocks());

it('does not increment quota on failed send', async () => {
  (kv.get as jest.Mock).mockResolvedValue(null); // no existing quota
  await sendBook({ /* ... fails */ });
  expect(kv.incr).not.toHaveBeenCalled();
});
```

**Mocking external APIs (Google Books, OpenLibrary):**
```typescript
// Mock fetch globally for external API tests
const mockFetch = jest.fn();
global.fetch = mockFetch;

it('falls back to "No description" when Google Books returns no match', async () => {
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ totalItems: 0, items: [] }),
  });
  const result = await getBookMetadata('nonexistent-isbn');
  expect(result.description).toBeNull();
});

it('rejects study guides from metadata results', async () => {
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({
      totalItems: 1,
      items: [{ volumeInfo: { title: "Study Guide: Little Women" } }],
    }),
  });
  const result = await getBookMetadata('little-women');
  expect(result.description).toBeNull(); // study guide rejected
});
```

### Python (pytest)

```
tests/
  test_search.py
  test_torrent.py
  conftest.py        # shared fixtures
```

**Pattern: `conftest.py` for shared fixtures, parametrize for variant testing.**

```python
# tests/conftest.py
import pytest

@pytest.fixture
def mock_qbit(monkeypatch):
    """Mock qBittorrent API responses."""
    responses = {}
    def mock_get(endpoint, **kwargs):
        return responses.get(endpoint, [])
    monkeypatch.setattr('bridge.app.qbit_get', mock_get)
    return responses

# tests/test_torrent.py
import pytest
from bridge.app import parse_infohash

@pytest.mark.parametrize("magnet,expected", [
    ("magnet:?xt=urn:btih:aabbccdd" + "0" * 32, "aabbccdd" + "0" * 32),
    ("magnet:?xt=urn:btih:VKZGY33M", "abc123..."),  # base32
    ("https://example.com/file.torrent", None),        # no magnet
])
def test_parse_infohash(magnet, expected):
    assert parse_infohash(magnet) == expected
```

---

## Regression test pattern

When fixing a bug:

1. **Write the test FIRST** — it must fail with the current (broken) code
2. **Test the exact scenario that broke** — not a generalized version
3. **Name it after the symptom** — `test_quota_not_charged_on_failed_send`, not `test_quota_logic`

```typescript
// Regression: failed sends were consuming daily quota
it('does not charge quota when download fails', async () => {
  mockDownload.mockRejectedValue(new Error('fetch failed'));
  const quotaBefore = await getQuota(testEmail);
  await expect(sendBook(testEmail, bookId)).rejects.toThrow();
  const quotaAfter = await getQuota(testEmail);
  expect(quotaAfter).toBe(quotaBefore); // quota unchanged
});
```

---

## Resilience testing patterns

For code with fallback chains, timeouts, or external dependencies:

```typescript
describe('resilientDownload', () => {
  it('falls back to second source when first fails', async () => {
    mockSources[0].download.mockRejectedValue(new Error('503'));
    mockSources[1].download.mockResolvedValue(epubBuffer);
    const result = await resolveAndDownload(bookId);
    expect(result.source).toBe('gutenberg'); // fell back
  });

  it('respects deadline even if sources are slow', async () => {
    mockSources.forEach(s => s.download.mockImplementation(
      () => new Promise(r => setTimeout(r, 60000)) // never resolves in time
    ));
    await expect(resolveAndDownload(bookId, { deadlineMs: 1000 }))
      .rejects.toThrow(/deadline/);
  });

  it('caps archive.org to one attempt', async () => {
    mockSources.find(s => s.name === 'archive.org')
      .download.mockRejectedValue(new Error('403'));
    await resolveAndDownload(bookId);
    expect(archiveSource.download).toHaveBeenCalledTimes(1);
  });
});
```

---

## What NOT to do in tests

- **Don't test implementation details.** Test behavior ("returns correct score"), not mechanics ("calls helper function X").
- **Don't snapshot complex objects.** Snapshots of API responses or large objects break on every change and teach nothing. Assert specific fields.
- **Don't mock everything.** If a function calls three internal utilities, let them run. Only mock external boundaries (network, database, filesystem).
- **Don't write tests that pass when the feature is broken.** If you can delete the feature code and the test still passes, the test is useless.
- **Don't aim for coverage numbers.** 71 focused tests on business logic beats 200 tests that assert `expect(true).toBe(true)`.

---

## Starting tests in a project with zero tests

When a project has CI but no tests (like recs.community):

1. **Don't boil the ocean.** Don't try to add tests for everything. Start with 5-10 tests on the most critical paths.
2. **Pick the highest-risk code first:** auth flows, permission checks, data mutations.
3. **Set up the test infrastructure in its own PR.** Jest/Vitest config, test scripts in package.json, CI integration. Separate from actual tests.
4. **First test should be the simplest possible passing test.** Proves the infrastructure works before writing real tests.
5. **Add tests alongside new features.** Don't backfill old code — just test everything new going forward.

---

## Changelog

- **2026-06-07 — v1: Initial skill from gap analysis of 15 PRs**
  - Covers: when to test, test architecture per stack, mocking patterns, resilience testing, regression tests
  - Evidence: kindle-schlacter-me (71 tests, resilientDownload.test.ts), muse-shopping (63 tests), kindle-connector (py_compile only), recs.community (CI, 0 tests)
  - Addresses CLAUDE.md known issue #8
