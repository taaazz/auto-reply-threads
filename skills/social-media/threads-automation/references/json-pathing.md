# Threads JSON Pathing Reference

Threads uses Relay (GraphQL) to hydrate the page. Data is usually found in `<script type="application/json">` tags with large `data-content-len`.

### Search Results Path
Inside the JSON object, look for:
`data['require'][...]` -> `searchResults` -> `edges`
- `node` -> `thread` -> `thread_items` -> `post`
- `caption` -> `text`
- `user` -> `username`
- `code` or `pk`: The unique post ID (shortcode).

### Post Detail Path
`data['require'][...]` -> `adp_BarcelonaPostPageTargetQueryRelayPreloader`
- `searchResults` (even on single post pages) or `edges` containing the target post.

### Extraction Snippet
```python
def find_posts(obj):
    posts = []
    if isinstance(obj, dict):
        if "searchResults" in obj and "edges" in obj["searchResults"]:
            for edge in obj["searchResults"]["edges"]:
                items = edge.get("node", {}).get("thread", {}).get("thread_items", [])
                for item in items:
                    if item.get("post"): posts.append(item["post"])
        for v in obj.values(): posts.extend(find_posts(v))
    elif isinstance(obj, list):
        for v in obj: posts.extend(find_posts(v))
    return posts
```
