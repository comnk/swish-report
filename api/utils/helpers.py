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
            await page.goto(url, wait_until="load", timeout=60000)
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
    """Compute TS%, PER, USG%, BPM (simplified) per season."""
    FGA = stats.get("FGA", 0)
    FGM = stats.get("FGM", 0)
    FTA = stats.get("FTA", 0)
    FTM = stats.get("FTM", 0)
    PTS = stats.get("PTS", 0)
    REB = stats.get("REB", 0)
    AST = stats.get("AST", 0)
    STL = stats.get("STL", 0)
    BLK = stats.get("BLK", 0)
    TOV = stats.get("TOV", 0)
    MP = stats.get("MP", 0)

    # True Shooting %
    TS = round(PTS / (2 * (FGA + 0.44 * FTA)) * 100, 1) if (FGA + 0.44 * FTA) > 0 else 0

    # Simplified PER
    PER = round((PTS + REB + AST + STL + BLK - (FGA - FGM) - (FTA - FTM) - TOV) / GP, 1) if GP else 0

    # Usage Rate (approx)
    USG = round((FGA + 0.44 * FTA + TOV) / GP, 1) if GP else 0

    # Box Plus/Minus (simplified estimate)
    BPM = round((PTS + REB + AST + STL + BLK - TOV - FGA) / GP, 1) if GP else 0

    return {
        "TS": TS,
        "PER": PER,
        "USG": USG,
        "BPM": BPM
    }