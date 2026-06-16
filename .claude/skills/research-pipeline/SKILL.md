---
name: research-pipeline
description: >
  Scrape, classify, analyze, and present research data. Covers the full pipeline
  from data collection through dashboard/report delivery. Used in twitch-community-research,
  workspace-ai-research, claude-code-insights-dashboard, managed-agents-pulse.
---

# research-pipeline

End-to-end pattern for research projects: collect data from public sources, classify/analyze
it, and present findings in a dashboard or report. Built from patterns across 4 repos.

**Not for:** ML model training, academic paper writing, or proprietary data analysis.

**Relationship to content-quality:** When writing the final report/dashboard copy, invoke
content-quality. Lead with findings, not methodology.

**Relationship to code-builder:** code-builder handles the code execution. research-pipeline
provides the domain-specific steps and data integrity checks.

---

## Announce activation

> **research-pipeline activated** — [scrape | classify | analyze | dashboard | full pipeline]. [source/topic.]

---

## Step 1: Define the research question

Before writing any code:

1. **State the question in one sentence.** "What do Twitch viewers want from notifications?" not "Analyze Twitch feedback."
2. **Define the data source.** Reddit, Twitter/X, forums, app reviews, public APIs, web scraping.
3. **Estimate volume.** <100 items: manual is fine. 100-1000: script it. >1000: need rate limiting and incremental collection.
4. **Define the output.** Dashboard? Static report? Dataset for someone else? This determines the tech stack.

---

## Step 2: Data collection

### 2A. Source selection

| Source | Method | Rate limits | Notes |
|---|---|---|---|
| Reddit | PRAW (Python) or pushshift API | 60 req/min (OAuth) | Use `.submission.comments.replace_more()` for full threads |
| Twitter/X | API v2 (academic access) or scraping | Varies by tier | Academic access gives historical, free tier is limited |
| App store reviews | google-play-scraper / app-store-scraper | Gentle — 1 req/sec | Filter by date to avoid stale reviews |
| Public forums | BeautifulSoup + requests | Be respectful — 1 req/sec | Check robots.txt. Cache everything. |
| YouTube comments | youtube-data-api-v3 | 10K units/day | Comments are paginated, need `nextPageToken` loop |

### 2B. Collection patterns

```python
# Always: cache raw data before processing
import json
from pathlib import Path

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

def save_raw(items, source_name):
    path = RAW_DIR / f"{source_name}_{datetime.now():%Y%m%d_%H%M}.json"
    path.write_text(json.dumps(items, default=str, indent=2))
    return path
```

**Rules:**
- Cache raw data before ANY processing. You can re-process; you can't re-scrape deleted content.
- Add `sleep(1)` between requests minimum. Respect rate limits.
- Store metadata: collection date, source URL, query parameters.
- For incremental collection: store the last-seen ID/timestamp. Don't re-fetch everything.
- Never commit raw data with PII (usernames are borderline — anonymize if publishing).

### 2C. Data integrity checks

Before moving to classification:
- [ ] Total count matches expected range (not 0, not suspiciously round)
- [ ] Date range is correct (no data from wrong time period)
- [ ] No duplicate entries (dedupe by ID or content hash)
- [ ] Encoding is correct (no mojibake in non-English content)
- [ ] Sample 10 random entries and verify they match the source

---

## Step 3: Classification

### 3A. Manual taxonomy first

Before using any automated classification:
1. Read 50 random items from your dataset
2. Write down the categories that emerge naturally (don't force a taxonomy)
3. Merge similar categories until you have 5-10 distinct ones
4. Write a one-sentence definition for each category
5. Test: can you classify 20 new items with >80% confidence? If not, refine categories.

### 3B. Automated classification

For >200 items, use LLM classification:

```python
# Batch classification prompt pattern
CLASSIFY_PROMPT = """Classify this feedback into exactly one category:

Categories:
- {cat1}: {definition}
- {cat2}: {definition}
...

Feedback: "{text}"

Respond with only the category name."""
```

**Rules:**
- Validate against a human-labeled gold set (50+ items). If accuracy <85%, refine the prompt.
- Use the cheapest model that achieves target accuracy (Haiku before Sonnet before Opus).
- Batch API calls with rate limiting. Don't blow through API credits on iteration 1.
- Store the model + prompt version alongside classifications. You'll need to re-run when you refine.

### 3C. Sentiment and theme extraction

- Sentiment: positive / negative / neutral / mixed. Don't over-granularize (1-5 scales are noise at this volume).
- Themes: extract 2-3 key themes per item, not just the category.
- Quotes: flag the 10-20 most quotable items for the final report. These are your evidence.

---

## Step 4: Analysis

### 4A. Quantitative

- Category distribution (bar chart / pie chart)
- Sentiment by category (which topics are most negative?)
- Volume over time (is this growing or shrinking?)
- Top requests / complaints (rank by frequency)

### 4B. Qualitative

- **Representative quotes** for each category (3-5 per category)
- **Outlier analysis**: what's in the "other" category? Often the most interesting insights.
- **Contradictions**: where do users disagree with each other? These are product decisions.

### 4C. "So what?" test

For every finding, answer: "What should the product team do differently because of this?"
If the answer is "nothing" or "we already knew that," the finding isn't worth including.

---

## Step 5: Presentation

### 5A. Dashboard (interactive)

Use for: ongoing monitoring, datasets that update, audiences that want to explore.

Tech stack: Next.js + Recharts/Chart.js + static JSON data (no backend needed for <10K items).

```
app/
  page.tsx           # Overview with key metrics
  [category]/page.tsx # Deep-dive per category
lib/
  data.ts            # Processed data as typed arrays
  charts.ts          # Reusable chart components
public/
  data/              # JSON data files (committed, not fetched)
```

### 5B. Static report (portfolio case study)

Use for: one-time research, portfolio pieces, sharing with stakeholders.

Structure: finding first, methodology last.
1. **Headline finding** (one sentence, with a number)
2. **Key findings** (3-5 bullet points with evidence)
3. **Methodology** (brief — how collected, how classified, sample size)
4. **Data** (link to repo or dashboard)

Invoke content-quality before publishing.

### 5C. Dataset (for others)

Use for: when the data itself is the deliverable.

Include: README with schema, collection methodology, date range, limitations.
Format: CSV for broad compatibility, JSON for structured data, both if possible.

---

## Claude API for Classification

When using Claude for automated classification (Step 3B), use the cheapest model that meets accuracy targets:

| Model | Model ID | Use when |
|---|---|---|
| Haiku 4.5 | `claude-haiku-4-5-20251001` | Simple categorization (3-5 categories), sentiment analysis |
| Sonnet 4.6 | `claude-sonnet-4-6` | Complex taxonomy (10+ categories), theme extraction, nuanced sentiment |
| Opus 4.6 | `claude-opus-4-6` | Multi-dimensional coding, disagreement resolution, taxonomy generation |
| Fable 5 | `claude-fable-5` | Long-context research analysis, creative synthesis |

**Batching pattern:**
```python
import anthropic

client = anthropic.Anthropic()

def classify_batch(items, categories, batch_size=20):
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i+batch_size]
        # Send multiple items in one prompt to reduce API calls
        prompt = f"Classify each item into one of: {', '.join(categories)}\n\n"
        for j, item in enumerate(batch):
            prompt += f"{j+1}. {item['text'][:500]}\n"
        prompt += "\nRespond with one category per line, numbered to match."
        
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",  # or claude-sonnet-4-6 for complex taxonomies
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        results.extend(parse_classifications(response.content[0].text))
    return results
```

**Rules:**
- Start with Haiku, upgrade only if accuracy on gold set is <85%
- Batch 10-20 items per API call to reduce cost and latency
- Store the model ID and prompt version alongside results — you'll re-run when you refine
- Set `max_tokens` conservatively — classification responses are short
- For >5K items, use the Anthropic Batch API for 50% cost reduction

### Data Visualization

| Library | Use when | Avoid when |
|---|---|---|
| **Recharts** | React dashboards, simple bar/line/pie charts, quick setup | Complex custom visualizations, non-React |
| **Chart.js** | Lightweight, framework-agnostic, canvas-based | Need SVG output, complex interactions |
| **D3.js** | Custom visualizations, maps, force-directed graphs | Simple charts (overkill), tight deadlines |
| **Observable Plot** | Quick exploratory analysis, notebook-style | Production dashboards |

For research dashboards (Step 5A), default to Recharts with Next.js. It handles responsive sizing and SSR without configuration.

---

## Anti-patterns

- **Don't collect first, ask questions later.** Define the question before scraping.
- **Don't skip the manual taxonomy step.** Automated classification without human labels produces confident garbage.
- **Don't present methodology before findings.** Nobody reads past "We collected 1,183 data points using PRAW."
- **Don't re-scrape when you can cache.** Raw data is expensive to collect, cheap to store.
- **Don't publish user PII.** Anonymize usernames in published datasets. Keep raw data private.
- **Don't over-automate one-time research.** If you're doing this once, a Python script + CSV is fine. You don't need a pipeline framework.

---

## Changelog

- **2026-06-16 — v1.2: Updated model IDs to current Claude 4.X family**
  - UPDATED: Model selection table — added Fable 5, updated all model IDs to current versions (claude-haiku-4-5-20251001, claude-sonnet-4-6, claude-opus-4-6, claude-fable-5)
  - Evidence: model IDs were stale; Fable 5 is now available for long-context research analysis
- **2026-06-12 — v1.1: Claude API integration, data visualization**
  - ADDED: Claude API for classification — model selection table (Haiku/Sonnet/Opus by use case), batching pattern, Batch API note
  - ADDED: Data visualization library comparison table (Recharts, Chart.js, D3, Observable Plot)
  - Evidence: classification step referenced LLMs but had no concrete API guidance; dashboard step recommended Recharts without comparing alternatives
- **2026-06-05 — v1: Initial skill based on 4 research repos**
  - Covers: data collection, classification (manual + LLM), analysis, presentation
  - Sources: twitch-community-research, workspace-ai-research, claude-code-insights-dashboard, managed-agents-pulse
  - Addresses CLAUDE.md known issue #5
