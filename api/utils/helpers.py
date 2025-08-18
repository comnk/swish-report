from playwright.async_api import async_playwright

import json

async def launch_browser(headless=True):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    return playwright, browser


def parse_json_list(field: str):
    if not field:
        return []
    try:
        # Sometimes DB stores it as '["Duke"]' or similar
        data = json.loads(field)
        # Ensure each element is stripped of extra quotes/spaces
        return [str(x).strip().strip('"') for x in data]
    except Exception:
        # fallback if not JSON
        return [x.strip().strip('"') for x in field.split(",")]