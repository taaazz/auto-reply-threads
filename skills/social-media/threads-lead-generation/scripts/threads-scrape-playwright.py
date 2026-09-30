#!/usr/bin/env python3
"""Scrape Threads search results for high-intent leads with Playwright.

Discovery stage of the pipeline: find posts whose caption matches a topic
keyword AND an intent keyword, minus competitor/promo accounts.

Usage:
    /root/threads-venv/bin/python threads-scrape-playwright.py
    /root/threads-venv/bin/python threads-scrape-playwright.py --keywords "daftar merek" "paten" --limit 5
    /root/threads-venv/bin/python threads-scrape-playwright.py --out leads.json

The session is read from --state (default /root/storage_state.json) when the file
exists; without it the run continues anonymously, which returns fewer results.
Scraping is read-only, so it works with an expired session - only the reply path
proves a session is alive (see references/session-and-auth.md).

Keywords mirror references/threads-lead-keywords.yml; override with --keywords.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from urllib.parse import quote

TOPIC_KEYWORDS = [
    "daftar merek", "pendaftaran merek", "merek dagang", "hak cipta",
    "paten", "hki", "kekayaan intelektual", "trademark",
]

INTENT_KEYWORDS = [
    "rekomendasi", "spill", "cari jasa", "butuh jasa", "mau daftar",
    "caranya daftar", "bisa bantu", "bantuan", "mohon petunjuknya",
    "boleh saya daftar",
]

EXCLUDE_KEYWORDS = [
    "terima jasa", "promo", "harga murah", "hubungi wa", "dm saya", "dm kakk",
    "dm kami", "konsultan hki", "jasa pendaftaran", "kami menyediakan",
    "buka sesi", "ready stock", "order sekarang", "kontak kami", "minat hubungi",
    # penjual/agensi yang menyamar sebagai pencari jasa
    "chat aku", "chat saya", "bisa chat", "chat yaa", "chat ya kak",
    "konsul dulu", "konsul gratis", "konsultasi gratis", "gratiss",
    "jasa kami", "menerima jasa", "open jasa", "konsul dulu gratisss",
]

EXCLUDE_USERNAMES = [
    "legal", "law", "konsultan", "advokat", "notaris", "kemenkum", "official",
    "patenindo",
]

# Akun sendiri: postingannya TIDAK boleh dianggap lead (kalau tidak, agen akan
# membalas postingannya sendiri). Placeholder - ganti atau pakai --self-accounts.
DEFAULT_SELF_ACCOUNTS = ["yourbrand"]

SEARCH_URL = "https://www.threads.net/search?q={q}&serp_type=default"
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")


def find_posts(obj, out):
    """Recursively collect post nodes from the Relay/JSON payload."""
    if isinstance(obj, dict):
        sr = obj.get("searchResults")
        if isinstance(sr, dict) and isinstance(sr.get("edges"), list):
            for edge in sr["edges"]:
                thread = (edge.get("node") or {}).get("thread") or {}
                for item in thread.get("thread_items") or []:
                    post = item.get("post")
                    if post:
                        out.append(post)
        for value in obj.values():
            find_posts(value, out)
    elif isinstance(obj, list):
        for value in obj:
            find_posts(value, out)


def qualifies(username: str, caption: str, self_accounts=()) -> bool:
    user, cap = username.lower(), caption.lower()
    if any(x in user for x in EXCLUDE_USERNAMES):
        return False
    if any(x and x in user for x in (a.lower().lstrip("@") for a in self_accounts)):
        return False
    if any(x in cap for x in EXCLUDE_KEYWORDS):
        return False
    has_topic = any(x in cap for x in TOPIC_KEYWORDS)
    has_intent = any(x in cap for x in INTENT_KEYWORDS)
    return has_topic and has_intent


async def scrape_keyword(page, keyword: str, limit: int | None, scrolls: int, self_accounts=()):
    await page.goto(SEARCH_URL.format(q=quote(keyword)), wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(3000)
    for _ in range(scrolls):
        await page.evaluate("window.scrollBy(0, window.innerHeight)")
        await page.wait_for_timeout(1500)

    raw = []
    for script in await page.query_selector_all('script[type="application/json"]'):
        text = await script.inner_text()
        if not text or len(text) < 1000:
            continue
        try:
            find_posts(json.loads(text), raw)
        except json.JSONDecodeError:
            continue

    leads = []
    for post in raw:
        caption = post.get("caption")
        text = caption.get("text", "") if isinstance(caption, dict) else str(caption or "")
        username = (post.get("user") or {}).get("username") or ""
        code = post.get("code") or post.get("pk") or ""
        if not text or not username or not code:
            continue
        if not qualifies(username, text, self_accounts):
            continue
        leads.append({
            "post_id": str(code),
            "username": f"@{username}",
            "url": f"https://www.threads.net/@{username}/post/{code}",
            "keyword": keyword,
            "caption": text.strip(),
        })
    return leads[:limit] if limit else leads


async def run(keywords, limit, scrolls, state: Path, headless: bool, self_accounts=()):
    from playwright.async_api import async_playwright

    collected = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=headless, args=["--no-sandbox"])
        kwargs = {"user_agent": USER_AGENT, "viewport": {"width": 1280, "height": 800}}
        if state.exists():
            kwargs["storage_state"] = str(state)
        context = await browser.new_context(**kwargs)
        page = await context.new_page()

        for keyword in keywords:
            try:
                leads = await scrape_keyword(page, keyword, limit, scrolls, self_accounts)
                print(f"{keyword}: {len(leads)} lead", flush=True)
                collected.extend(leads)
            except Exception as exc:  # keep going on a single bad keyword
                print(f"{keyword}: gagal ({exc})", flush=True)

        await browser.close()

    unique = {}
    for lead in collected:
        unique.setdefault(lead["post_id"], lead)
    return list(unique.values())


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keywords", nargs="*", default=TOPIC_KEYWORDS)
    ap.add_argument("--limit", type=int, default=5, help="max leads per keyword (0 = no limit)")
    ap.add_argument("--scrolls", type=int, default=2, help="scroll passes per keyword")
    ap.add_argument("--state", type=Path, default=Path("/root/storage_state.json"))
    ap.add_argument("--self-accounts", nargs="*", default=DEFAULT_SELF_ACCOUNTS,
                    help="handle akun sendiri yang harus diabaikan (tanpa @)")
    ap.add_argument("--no-headless", action="store_true")
    ap.add_argument("--out", type=Path, help="write JSON to a file instead of stdout only")
    args = ap.parse_args()

    leads = asyncio.run(run(args.keywords, args.limit or None, args.scrolls,
                            args.state, not args.no_headless, args.self_accounts))
    payload = json.dumps(leads, indent=2, ensure_ascii=False)
    if args.out:
        args.out.write_text(payload, encoding="utf-8")
        print(f"{len(leads)} lead ditulis ke {args.out}")
    else:
        print(payload)


if __name__ == "__main__":
    main()
