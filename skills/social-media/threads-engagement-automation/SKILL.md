---
name: threads-engagement-automation
description: Use when automating lead discovery and replies on Threads.
---

# Threads Engagement Automation

This skill governs the process of identifying high-intent leads on Meta Threads and automating friendly, brand-aligned replies.

## Lead Discovery & Filtering
1. **Search Strategy**: Use keyword-based searches for high-intent phrases (e.g., "mau daftar merek", "rekomendasi jasa HKI", "cara urus paten").
2. **Lead Qualification**:
   - **Include**: Users asking for help, seeking recommendations, or expressing frustration with current services.
   - **Exclude**: Competitors, agencies, "open order" posts, and official government accounts.
   - **Contextual Check**: Verify the post is a genuine query, not a promotional advertisement.
3. **Data Extraction**: Use Playwright to extract `post_id`, `username`, `url`, and `caption`.

## Engagement & Reply Strategy
1. **Persona**: Use the brand persona: Gen Z, friendly, and helpful, but credible.
2. **CTA Rules**: 
   - NEVER direct users to DM for initial contact.
   - ALWAYS direct users to the official website (e.g., `example.com`) or mention the official handle (e.g., `@yourbrand`).
   - Do not offer "free consultations" via personal chat; refer them to the platform's solution.
3. **Value Proposition**: Embed 1-3 sentences of product value (e.g., "process cepat berbasis digital", "proteksi hukum anti-plagiasi", or "fitur cek merek instan yang meminimalisir penolakan").

## Technical Implementation (Anti-Bot)
1. **Authentication**: Use `storage_state.json` containing `sessionid` and `ds_user_id` to avoid login walls.
2. **Stealth Mode**:
   - Disable `navigator.webdriver` flag.
   - Use realistic User-Agents.
   - Implement random delays between interactions to mimic human behavior.
3. **Selectors**: Use role-based locators (e.g., `get_by_role('button', name='Reply')`) rather than volatile CSS classes.

## Verification
- Verify that the reply was actually posted by checking for the presence of the reply text on the page after submission.
