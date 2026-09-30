# Threads Lead Result Template

Use this format when outputting leads for downstream processing (CSV, database, CRM).

All handles and IDs below are placeholders — never paste a real user's handle or a
resulting post into this repository.

## Required Fields

```markdown
---
post_id: <string>          # Threads post ID (e.g., "AbCdEfGhIjK")
username: <string>         # With @ prefix (e.g., "@example_user")
url: <string>              # Full URL to the post
caption: <string>          # Full caption text (trimmed to 500 chars)
matched_topic: <string[]>  # Which topic keywords matched
matched_intent: <string[]> # Which intent keywords matched
timestamp: <ISO8601>       # When the lead was scraped
---
```

## Example Output

```markdown
---
post_id: "AbCdEfGhIjK"
username: "@example_user"
url: "https://www.threads.net/@example_user/post/AbCdEfGhIjK"
caption: "Ada yang bisa bantu daftar merek? Sudah coba sendiri tapi bingung isinya"
matched_topic: ["daftar merek"]
matched_intent: ["bisa bantu"]
timestamp: "2026-09-28T10:30:00Z"
---
```

## CSV Export Format

```csv
post_id,username,url,caption,matched_topic,matched_intent,timestamp
AbCdEfGhIjK,"@example_user","https://www.threads.net/@example_user/post/AbCdEfGhIjK","Ada yang bisa bantu daftar merek? Sudah coba sendiri tapi bingung isinya","[\"daftar merek\"]","[\"bisa bantu\"]","2026-09-28T10:30:00Z"
```

## Validation Rules

1. `post_id` must be alphanumeric with dashes/underscores
2. `username` must start with `@`
3. `url` must match `https://www.threads.net/@<username>/post/<post_id>`
4. `caption` must not be empty
5. At least one `matched_topic` and one `matched_intent` must be present
6. `timestamp` must be valid ISO8601
