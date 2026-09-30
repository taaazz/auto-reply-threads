# Threads Sessions & Meta Token Auth

Two separate auth systems get confused with each other. Keep them apart.

**None of the Meta API material below is required by the shipped workflow.**
This distribution replies through a browser session; the token path is documented
only to explain why the official API is a dead end for third-party replies, so it
does not get re-litigated with another tool.

| Path | What it authenticates | Can reply to a *third party's* post? |
|---|---|---|
| Browser `storage_state.json` (session cookie) | A real logged-in human web session | **Yes** — this is the only way |
| Meta Graph / Threads API `access_token` | An authorized app acting for its own account | **No** |

## Why the official API cannot do it

`POST /v1.0/{thread-user-id}/threads` with `reply_to=<post_id>` followed by
`POST /v1.0/{thread-user-id}/threads_publish` is the documented two-step publish
flow. It only accepts posts owned by the token's own account. Against another
user's post id it fails regardless of token validity.

Verified this session: the same token returned HTTP 200 for
`GET /v1.0/me?fields=id,username`, and the *same token* worked when the operator
fired it by hand from Postman / Graph API Explorer — yet the reply to a third
party's post never landed. The token was never the problem; the endpoint scope
is. Do not re-litigate this with another tool.

Practical consequence: tools sold as "reply to any Threads post" via API
(Postiz, Repliz, Zernio and friends) either restrict themselves to your own
posts, or are doing browser automation under the hood and inherit every
anti-bot problem below. Reach for browser automation directly instead of paying
a middleman to hit the same wall.

## Meta token lifetimes

- **Short-lived**: ~1 hour. Default out of the dashboard. Fine for a one-off
  curl, useless for a scheduled agent — it dies mid-run.
- **Long-lived**: ~60 days, and extends on use. Exchange once:

```python
# GET or POST https://graph.facebook.com/v19.0/oauth/access_token
params = {
    "grant_type": "fb_exchange_token",
    "client_id": os.environ["META_APP_ID"],
    "client_secret": os.environ["META_APP_SECRET"],
    "fb_exchange_token": os.environ["THREADS_ACCESS_TOKEN"],
}
```

The App Secret comes from the Meta dashboard (Settings -> Basic -> App Secret);
it cannot be minted from the CLI. Store token, App ID and App Secret in
`/root/.env` (chmod 600) and read them with `python-dotenv` — never inline them
in a script.

## Diagnosing code 190

`{"error": {... "code": 190, "type": "OAuthException"}}` has two very different
causes. Read the message, don't assume:

- `Session has expired on <date>` -> genuine expiry. Mint a new token and
  exchange it for a long-lived one.
- `Invalid OAuth access token - Cannot parse access token` -> the *string* is
  malformed. Usually a browser `sessionid` cookie pasted in as if it were an
  OAuth token, a truncated copy, a stray quote, or a trailing newline. Cookie
  values are never valid here. Print `len(token)` and the first 15 chars to
  confirm what is actually loaded before blaming the token.

A Threads OAuth token starts `THAA...` / `EAA...`; a browser session cookie
starts with a numeric user id followed by `%3A`.

## Session-validity signals

- Page content contains `Continue with Instagram` -> not logged in. The reply
  composer will not render; drop straight to re-exporting the session.
- `navigator.webdriver` is still `true` -> `add_init_script` was not applied
  before the first navigation.
- Always confirm a live session by watching a *write* attempt, not a read.

## Headless runners

Export the state on a machine with a display, copy it to the runner, then run
`headless=True` there. Launching headed on a display-less server fails before
any page loads:

```
Looks like you launched a headed browser without having a XServer running.
```

Minimum working context setup on the runner:

```python
context = await browser.new_context(
    storage_state="/root/storage_state.json",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    viewport={"width": 1280, "height": 800},
)
await context.add_init_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
)
```

Sessions die when the operator logs out or changes the password, and Meta
invalidates them on its own schedule. Expect to re-export periodically and treat
a fresh `storage_state.json` as normal maintenance, not a failure.
