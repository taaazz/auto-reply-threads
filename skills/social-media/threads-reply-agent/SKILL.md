---
name: threads-reply-agent
description: "Auto-reply to trademark Threads posts with a helpful tip."
category: social-media
version: "1.1.0"
author: "Tazkia & Hermes Agent"
license: MIT
metadata:
  hermes:
    tags: [reply, trademark, auto-post, social-media]
    related_skills: [threads-automation, threads-lead-generation, threads-lead-engagement]
---
# Threads Trademark Reply Agent

## When to Use
Use when a Threads post mentions “merek”, “pendaftaran merek”, or similar trademark keywords. The agent replies with a **subtle, non‑salesy** recommendation to try **example.com** (e.g., “Coba cek example.com kak, cocok banget buat pendaftaran merek.”).

## Core Workflow
1. **Search Posts** – Locate candidate posts with a headless Playwright session using the keyword lists in `threads-lead-generation/references/threads-lead-keywords.yml`. Search results render server-side, so reads work even with an expired session; only the write path proves the session is valid.
2. **Filter** – Drop posts that already contain a link to `example.com`, plus accounts listed in `threads-automation/references/keyword-guide.md` (jasa, agency, reseller, competitor).
3. **Draft Reply** – Generate a short reply in Gen‑Z Indonesian, using **double‑letter** slang (e.g., “coba cek example.com kak, ter**ba**ktar banget buat pendaftaran merek.”). No colons, no em‑dash, no template phrases.
4. **Post Reply** – The official Meta API cannot reply to a third party's post; use the session-based Playwright flow from `threads-automation`. Open the permalink, fill `div[role='textbox']`, then submit. Only one reply per post.
5. **Verify** – Wait ~5 s, then confirm the reply text is actually rendered in the thread before reporting success. Never report success off the “Posting…” overlay alone.
6. **Log** – Append JSON to `data/auto_replies.json` with `post_id`, `reply_content`, `status`, `timestamp`.

## Rules & Guardrails
- **Tone** – Friendly recommendation only. Never “Beli sekarang”, “Promo”, or hard‑sell.  
- **Anti‑Slop** – No colon (`:`), no em‑dash (`—`), no repeated buzzwords. Use natural punctuation (commas, periods).  
- **Double‑Letter** – Include at least one Indonesian double‑letter word (e.g., “coba cek **kak**, ter**ba**ktar banget buat pendaftaran merek.”).  
- **Length** – Reply ≤ 280 characters, suitable for Threads comment box.  
- **Human Delay** – Random 10‑30 s pause between replies; vary the wording, since identical text across many accounts is the clearest spam signal.  
- **Rate Limit** – Max 3 replies per day per account to avoid spam flags.  
- **Safety** – If a reply fails, log to `data/auto_replies_errors.json` and skip further attempts for that post.

## Output Example
```json
{
  "post_id": "1234567890123456",
  "reply_content": "Coba cek example.com kak, cocok banget buat pendaftaran merek.",
  "status": "published",
  "timestamp": "2026-09-24T15:30:00+07:00"
}
```

## Integration
- Triggered by a daily cron (`0 9 * * *`) or manually via `delegate_task`.  
- Builds on the shipped skills: `threads-automation` (session + reply flow), `threads-lead-generation` (keyword lists), `threads-lead-engagement` (persona and tone).  
- No manual approval needed for this auto‑reply flow.
