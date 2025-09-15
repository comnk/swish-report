from playwright.async_api import async_playwright
from unidecode import unidecode

import json, random, asyncio

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
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            return page
        except Exception as e:
            print(f"⚠️ Navigation failed (attempt {attempt+1}) for {url}: {e}")
            try:
                ctx = page.context
                await page.close()
                await ctx.close()
            except:
                pass

            context = await browser.new_context(java_script_enabled=False)
            page = await context.new_page()
            await page.set_extra_http_headers({"User-Agent": USER_AGENT})

            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(5 + random.random() * 5)

    return page

# FUNCTIONS FOR SCOUTING REPORTS

def calculate_advanced_stats(GP, stats):
    """Compute TS%, FG%, eFG%, 3P%, and FT% per season."""
    # Ensure numeric defaults
    FGA = stats.get("FGA") or 0
    FGM = stats.get("FGM") or 0
    FTA = stats.get("FTA") or 0
    FTM = stats.get("FTM") or 0
    PTS = stats.get("PTS") or 0
    THREES_MADE = stats.get("3PM") or 0
    THREES_ATT = stats.get("3PA") or 0

    # True Shooting %
    TS = round(PTS / (2 * (FGA + 0.44 * FTA)) * 100, 1) if (FGA + 0.44 * FTA) > 0 else 0

    # Field Goal %
    FG_PCT = round(FGM / FGA * 100, 1) if FGA > 0 else 0

    # Effective Field Goal %
    EFG_PCT = round((FGM + 0.5 * THREES_MADE) / FGA * 100, 1) if FGA > 0 else 0

    # Three Point %
    TP_PCT = round(THREES_MADE / THREES_ATT * 100, 1) if THREES_ATT > 0 else 0

    # Free Throw %
    FT_PCT = round(FTM / FTA * 100, 1) if FTA > 0 else 0

    return {
        "TS": TS,
        "FG": FG_PCT,
        "eFG": EFG_PCT,
        "3P": TP_PCT,
        "FT": FT_PCT
    }

