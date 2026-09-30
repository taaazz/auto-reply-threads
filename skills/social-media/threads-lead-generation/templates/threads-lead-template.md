# Threads Lead Result Template

Use this format when outputting leads for downstream processing (CSV, database, CRM).

## Required Fields

```markdown
---
post_id: <string>          # Threads post ID (e.g., "DaRgErUk1pP")
username: <string>         # With @ prefix (e.g., "@senseibranding")
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
post_id: "DaRgErUk1pP"
username: "@senseibranding"
url: "https://www.threads.net/@senseibranding/post/DaRgErUk1pP"
caption: "Hi threads, pertemukan aku dengan agency yang biasa handle pendaftaran merek atau HAKI"
matched_topic: ["pendaftaran merek", "haki"]
matched_intent: ["rekomendasi", "spill"]
timestamp: "2026-09-28T10:30:00Z"
---
```

## CSV Export Format

```csv
post_id,username,url,caption,matched_topic,matched_intent,timestamp
DaRgErUk1pP,"@senseibranding","https://www.threads.net/@senseibranding/post/DaRgErUk1pP","Hi threads, pertemukan aku dengan agency yang biasa handle pendaftaran merek atau HAKI","[\"pendaftaran merek\", \"haki\"]","[\"rekomendasi\", \"spill\"]","2026-09-28T10:30:00Z"
```

## Validation Rules

1. `post_id` must be alphanumeric with dashes/underscores
2. `username` must start with `@`
3. `url` must match `https://www.threads.net/@<username>/post/<post_id>`
4. `caption` must not be empty
5. At least one `matched_topic` and one `matched_intent` must be present
6. `timestamp` must be valid ISO8601