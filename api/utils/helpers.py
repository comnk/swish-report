from playwright.async_api import async_playwright

async def launch_browser(headless=True):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    return playwright, browser