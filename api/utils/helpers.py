from playwright.async_api import async_playwright
from unidecode import unidecode

import json
import random
import asyncio

# VARIABLES

USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
)

# SYNCHRONOUS FUNCTIONS

def normalize_name(name):
    """Remove accents and special characters, lowercase, strip spaces."""
    return unidecode(name).strip()

def parse_json_list(field: str):
    if not field:
        return []
    try:
        data = json.loads(field)
        return [str(x).strip().strip('"') for x in data]
    except Exception:
        return [x.strip().strip('"') for x in field.split(",")]

# ASYNC FUNCTIONS

async def launch_browser(headless=True):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless, args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"])
    return playwright, browser

async def safe_goto(browser, page, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=40000)
            return page
        except Exception as e:
            print(f"⚠️ Navigation failed (attempt {attempt+1}) for {url}: {e}")
            try:
                await page.close()
            except:
                pass

            # fresh context+page for retry
            context = await browser.new_context()
            page = await context.new_page()
            await page.set_extra_http_headers({"User-Agent": USER_AGENT})

            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(5 + random.random() * 5)

    return page