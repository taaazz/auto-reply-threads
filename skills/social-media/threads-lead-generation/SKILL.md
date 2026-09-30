---
name: threads-lead-generation
description: Extract high-intent Threads leads
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [threads, lead-generation, social-media, scraper]
    related_skills: []
---

# Threads Lead Generation

## When to Use
Use when you need to extract high-intent leads from Threads based on specific keywords like "daftar merek", "hki", "paten" while filtering out promotional content and competitor posts. Ideal for automated lead generation campaigns.

## Description
Automated discovery of potential customers/leads on Threads by searching for high‑intent keywords and filtering out competitors/promotions.

## Workflow

1. **Search Strategy**: Use `https://www.threads.net/search?q=<keyword>&serp_type=default`.
2. **Auth Handling**: Requires a valid `sessionid` and `ds_user_id` cookie to bypass the login wall.
3. **Extraction Method**:
   - Use Playwright to load the page and perform scrolling to load more results.
   - Extract post data from `window.__NEXT_DATA__` JSON for higher reliability than DOM parsing.
4. **Strict Filtering**:
   - **Topic Match**: Caption must contain target keywords (e.g., "daftar merek", "hki").
   - **Intent Match**: Caption must contain "intent" keywords (e.g., "rekomendasi", "mau daftar", "bisa bantu").
   - **Competitor Filter**: Exclude posts containing "promo", "terima jasa", "dm saya", "harga murah".
   - **User Filter**: Exclude usernames containing "legal", "konsultan", "advokat", "official".

## Pitfalls & Solutions

- **Login Wall**: Threads redirects to login for non‑authenticated requests. Always inject active session cookies.
- **False Positives**: Keywords like "HKI" can be Finnish slang. Always combine with intent keywords (e.g., "HKI" + "rekomendasi") to ensure the lead is seeking a service.
- **DOM Drift**: Standard HTML selectors change often. Prefer parsing the `__NEXT_DATA__` JSON script tag.

## Verification

- Lead is valid if: (Topic Match AND Intent Match) AND (NOT Competitor Filter).
- Output must include `post_id`, `username`, and `url` (https://www.threads.net/@username/post/post_id).

### Support Files
- `references/threads-lead-keywords.yml`: Canonical keyword list.  
- `scripts/threads-scrape-verify.js`: Self‑check script that validates JSON extraction before publishing.  
- `templates/threads-lead-template.md`: Boilerplate result format for downstream processing.