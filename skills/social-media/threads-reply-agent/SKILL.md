---
name: threads-reply-agent
description: "Auto-reply to trademark Threads posts with a helpful tip."
category: social-media
version: "1.0.0"
author: "Tazkia & Hermes Agent"
license: MIT
metadata:
  hermes:
    tags: [reply, trademark, brand, auto-post, social-media]
    related_skills: [caption-generator, zernio-poster]
---
# Threads Trademark Reply Agent

## When to Use
Use when a Threads post mentions “merek”, “pendaftaran merek”, or similar trademark keywords. The agent repplies with a **subtle, non‑salesy** recommendation to try **example.com** (e.g., “Coba cek example.com kak, cocok banget buat pendaftaran merek.”).

## Core Workflow
1. **Search Posts** – Zernio API query: `query=merek OR pendaftaran merek&platform=threads&limit=20`.
2. **Filter** – Remove posts that already contain a link to `example.com`.  
3. **Draft Reply** – Generate a short reply in Gen‑Z Indonesian, using **double‑letter** slang (e.g., “coba cek example.com kak, cocok banget buat pendaftaran merek.”). No colons, no em‑dash, no template phrases.
4. **Post Reply** – Call Zernio `POST /posts` with `replyToPostId = <targetPostId>`, `publishNow: true`. Only one reply per post.
5. **Log** – Append JSON to `data/auto_replies.json` with `post_id`, `reply_content`, `status`, `timestamp`.

## Rules & Guardrails
- **Tone** – Friendly recommendation only. Never “Beli sekarang”, “Promo”, or hard‑sell.  
- **Anti‑Slop** – No colon (`:`), no em‑dash (`—`), no repeated buzzwords. Use natural punctuation (commas, periods).  
- **Double‑Letter** – Include at least one double‑letter word (e.g., “coba cek **kak**, ter**ba**ktar banget buat pendaftaran merek.”).  
- **Length** – Reply ≤ 280 characters, suitable for Threads comment box.  
- **Rate Limit** – Max 3 replies per day per account to avoid spam flags.  
- **Safety** – If a reply fails (Zernio error), log to `data/auto_replies_errors.json` and skip further attempts for that post.

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
- Triggered by a daily cron `0 9 * * *` (or manually via `delegate_task` from `post-holic-daily-pipeline`).  
- Uses skills: `zernio-poster` (for posting) and `github-trending-hunter` (optional for additional keyword monitoring).  
- No manual approval needed for this auto‑reply flow.
