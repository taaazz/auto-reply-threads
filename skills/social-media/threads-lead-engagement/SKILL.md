---
name: threads-lead-engagement
description: Use when researching and replying to leads on Meta Threads.
---

# Threads Lead Engagement

Automated workflow for identifying and responding to potential leads on Meta Threads.

## Lead Identification (AwareNest)
1. **Keywords**: Target high-intent phrases (e.g., "daftar merek", "butuh jasa HAKI", "rekomendasi agency trademark").
2. **Filter (brand-relevance filter)**:
   - **INCLUDE**: Questions, frustration with current services, requests for recommendations.
   - **EXCLUDE**: Competitor ads, agency promotions, official government accounts, unrelated slang (e.g., "HKI" as non-legal term).
3. **Lead Capture**: Extract `post_id`, `username`, `url`, and `caption`.

## Interaction (Engagement)
1. **Persona (brand persona)**: Gen Z, friendly, helpful but terse.
2. **CTA Guardrails**:
   - **NO** "DM me" or "Contact for consultation".
   - **YES** "Check example.com" or "Mention @yourbrand".
3. **Drafting Pattern**:
   - Acknowledge pain point $\rightarrow$ Provide a quick tip/value $\rightarrow$ Direct to `example.com` or `@yourbrand`.

## Technical Implementation (Automation)
1. **Auth**: Use `storage_state.json` from a manual login session to bypass login walls.
2. **Bypass Bot Detection**:
   - Set `navigator.webdriver` to `undefined`.
   - Use a realistic `User-Agent`.
   - Implement random delays (8-15s) between posts to avoid rate-limiting.
3. **Selector Strategy**:
   - Use role-based locators (`role='textbox'`, `role='button'`) instead of class-based selectors due to dynamic CSS.
   - Fallback to `aria-label` if text is missing.

## Pitfalls & Solutions
- **Login Wall**: If "Continue with Instagram" popup appears, the session/cookie has expired. Re-authenticate and save `storage_state.json`.
- **API vs UI**: Meta Graph API prohibits replying to posts by other users. Browser automation (Playwright/Puppeteer) is required for external engagement.
- **Post-Failure**: If the "Post" button isn't found, try `Control+Enter` via keyboard emulation.
