# Threads Selectors (Playwright)

These selectors were validated during a Threads lead engagement session.

## Reply Flow
1. **Open Post**: Navigate directly to `https://www.threads.net/@{username}/post/{post_id}`
2. **Inline Reply Box**: Already visible on page load.
   - Locator: `page.locator("div[role='textbox']").first`
3. **Fill Reply**: 
   - `await box.fill(DRAFT_REPLY)`
   - `await box.press("Enter")`  // Works reliably to submit
   - Alternative: `await page.locator("div[role='button']:has-text('Post')").first.click()`
4. **Wait for Overlay**: `await page.wait_for_timeout(5000)` to allow "Posting..." overlay to clear.

## Anti-Bot Initialization Script
```python
await context.add_init_script("""
    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
""")
```

## Storage State Usage
```python
context = await browser.new_context(
    storage_state="/root/storage_state.json",
    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    viewport={"width": 1280, "height": 800}
)
```
