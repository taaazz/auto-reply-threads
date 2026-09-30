---
name: threads-automation
description: Automate lead discovery and engagement on Meta Threads.
trigger: Use when researching, scraping, or replying to Threads posts for lead generation (e.g., HKI/Trademark niche).
---

# Threads Automation Workflow

This skill governs the end-to-end process of finding high-intent leads on Threads and engaging them using a mix of scraping and browser automation.

## 1. Lead Discovery (Scraping)
To find users seeking specific services (e.g., trademark registration), use a headless browser (Playwright) to scrape the search results.

### High-Intent Filtering
Do not target all keyword matches. Filter by:
- **Intent Keywords**: Look for "cari jasa", "butuh rekomendasi", "cara daftar", "biaya pendaftaran".
- **Exclude Competitors**: Filter out posts containing "terima jasa", "konsultan hki", "agency", "murah", "dm saya".
- **Exclude non-buyers**: official/government accounts (e.g. `@kemenkum`), accounts teaching people to self-register, and "open order" posts.
- **Guard against false positives**: the keywords are homographs. "HKI" also matches Helsinki airport chatter and Finnish slang; "paten" matches unrelated slang. Require Indonesian sentence context (`saya`, `aku`, `mau`, `butuh`, `cari`, `rekomendasi`, `biaya`) and a caption longer than ~30 chars before treating a hit as a lead.
- **Context**: Ensure the post is a question or a request for help, not a promotional ad.

## 2. Authentication & Session Management
Threads has aggressive bot detection. Standard cookies often expire or are restricted to read-only.

### Session Persistence
The most reliable method for "Write" actions (posting replies) is using a `storage_state.json` file:
1. Run a headed browser session (`headless=False`).
2. Manually login to `threads.net`.
3. Export the state: `context.storage_state(path="storage_state.json")`.
4. Load this state in automated scripts: `browser.new_context(storage_state="storage_state.json")`.

**Do the login/export on a machine that has a display** (the operator's laptop),
then copy the file to the runner and go headless there. A headed launch on a
display-less server dies with "Missing X server or $DISPLAY" /
`TargetClosedError: Target page, context or browser has been closed`; `xvfb-run`
only helps if a human can still finish the login inside the invisible window.

On Windows, printing an emoji with the default cp1252 console raises
`UnicodeEncodeError` *after* the file is written — the export succeeded, don't
redo the login over it.

### Anti-Bot Fingerprinting
To avoid "Login Wall" or "Invalid Token" errors during automation, always apply these stealth settings:
- **User Agent**: Use a modern, realistic Desktop User Agent.
- **WebDriver Flag**: Set `navigator.webdriver` to `undefined` via `add_init_script`.
- **Headless Mode**: If possible, use `headless=True` but with `--disable-blink-features=AutomationControlled`.

## 3. Automated Engagement (Reply)

**Only browser automation can reply to another user's post.** The official Meta
Graph / Threads API cannot do it: `POST /{thread-user-id}/threads` with
`reply_to` only accepts posts owned by the token's own account, so curl/Postman
hits against a third party's post id fail no matter how valid the token is. Do
not burn a session on Postiz/Repliz/Zernio or on the Graph API for third-party
replies — the token mechanics and the evidence are in
`references/session-and-auth.md`. Use the session-based Playwright flow below.

When posting replies to leads:
- **Targeting**: Use the `post_id` and `username` to navigate directly to the post URL.
- **Interacting**: 
    - Target the `div[role='textbox']` or `div[contenteditable='true']` for the reply input.
    - Use `.fill()` for the text and `.click()` on the "Post" button or press "Enter".
- **Safety**: Implement a delay (e.g., 10-30 seconds) between replies to avoid rate-limiting and account bans.

### Reply content rules (brand persona)
- **Tone**: casual Gen-Z Indonesian, warm, helpful. No hard sell, no formal register.
- **CTA — hard rule from the operator**: never invite a DM, never offer
  "konsultasi" or "tanya-tanya dulu". Point to `example.com` and/or mention
  `@yourbrand`. A reply ending in "DM aku ya" is wrong.
- **Substance**: carry 1-3 sentences of product knowledge — registration is done
  digitally, an instant mark check lowers the risk of rejection, and the result
  is legal protection for the brand. Pure praise with no product fact is not
  acceptable.
- **Vary the wording** between replies; identical text across many accounts is
  the clearest spam signal.

## Pitfalls & Troubleshooting
- **Invalid OAuth Token**: `Code 190` often means the token is expired or invalid for the requested action. Use a Long-Lived Token (60 days) generated via Meta App Secret.
- **Strict Mode Violation**: If `locator().fill()` fails due to multiple elements, use `.last` or filter by `aria-placeholder`.
- **Login Wall**: If the "Continue with Instagram" popup appears despite having cookies, it means the fingerprint was detected as a bot or the session is invalid. Re-export `storage_state.json`.
- **Element Not Found**: Threads uses dynamic class names; prefer role-based selectors (`get_by_role`, `get_by_label`) or text-based locators.
- **Claiming success too early**: pressing Enter raises a "Posting..." overlay.
  Wait ~5s, then confirm the reply text is actually rendered in the thread before
  reporting it posted. Never report success off the overlay alone.
- **Read works without a session, write does not**: search and permalink scraping
  return data even with a dead cookie, because the page ships its Relay payload
  server-side. A passing scrape is NOT evidence the session is valid — only the
  write path proves that.

## References
- See `references/playwright_selectors.md` for proven selector patterns.
- See `references/keyword-guide.md` for lead filtering lists.
- See `references/json-pathing.md` for pulling posts out of the Relay payload.
- See `references/session-and-auth.md` for storage_state export, Meta token
  lifetimes, and why the official Graph API cannot reply to other people's posts.

