import asyncio
import json
import random
import re
import string
import hashlib
import traceback
from utils.helpers import USER_AGENT
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


def normalize_list(values):
    return sorted(values) if values else []


def compute_college_player_hash(player_obj):
    fields_to_hash = {
        "name": player_obj.get("name"),
        "years": player_obj.get("years"),
        "position": player_obj.get("position"),
        "height": player_obj.get("height"),
        "weight": player_obj.get("weight"),
        "schools": normalize_list([s["name"] for s in player_obj.get("schools", [])]),
        "awards": normalize_list(player_obj.get("awards", []))
    }
    serialized = json.dumps(fields_to_hash, sort_keys=True)
    return hashlib.md5(serialized.encode()).hexdigest()


async def scrape_player(browser, player_data, timeout=30):
    """Scrape a single player with per-player timeout and safe cleanup."""
    context = None
    page = None
    try:
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_extra_http_headers({"User-Agent": USER_AGENT})

        async def _scrape():
            url = f"https://www.sports-reference.com{player_data['href']}"
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout*1000)

            result = await page.evaluate(r'''() => {
                const data = { position: "", height: "", weight: null, awards: [] };
                const metaDiv = document.querySelector("#meta");
                if (metaDiv) {
                    const pTags = Array.from(metaDiv.querySelectorAll("p"));
                    for (let i=0;i<pTags.length;i++){
                        const strong = pTags[i].querySelector("strong");
                        if (strong && strong.innerText.toLowerCase().startsWith("position")) {
                            const match = /Position:\s*<\/strong>\s*([A-Za-z]+)/.exec(pTags[i].innerHTML);
                            if (match) {
                                const posMap = { "Guard":"G","Forward":"F","Center":"C" };
                                data.position = posMap[match[1].trim()]||match[1].trim();
                            }
                            if (i+1 < pTags.length) {
                                const hw = Array.from(pTags[i+1].querySelectorAll("span")).map(el=>el.innerText.trim());
                                if (hw.length>0) data.height = hw[0];
                                if (hw.length>1) data.weight = parseInt(hw[1].replace("lb","").trim())||null;
                            }
                            break;
                        }
                    }
                }
                const bling = document.querySelectorAll("ul#bling li a");
                data.awards = Array.from(bling).map(a=>a.innerText.trim()).filter(Boolean);
                return data;
            }''')

            player_data.update(result)
            player_data['href'] = f"https://www.sports-reference.com{player_data['href']}"
            print(player_data)
            
            return player_data

        return await asyncio.wait_for(_scrape(), timeout=timeout+5)

    except (PlaywrightTimeoutError, asyncio.TimeoutError):
        print(f"⚠️ Timeout scraping {player_data.get('name')}")
    except Exception:
        print(f"⚠️ Error scraping {player_data.get('name')}:\n{traceback.format_exc()}")
    finally:
        if page:
            try: await page.close()
            except: pass
        if context:
            try: await context.close()
            except: pass
    return player_data


async def fetch_college_players(browser, resume_letter="a", batch_size=3, checkpoint_file="players_checkpoint.json"):
    """Fetch all men's college basketball players with checkpointing and per-letter robustness."""
    players_to_insert = []
    seen_hashes = set()
    letters = string.ascii_lowercase[string.ascii_lowercase.index(resume_letter):]

    for letter in letters:
        print(f"🔍 Fetching letter {letter}")
        context = None
        page = None
        try:
            context = await browser.new_context()
            page = await context.new_page()
            await page.set_extra_http_headers({"User-Agent": USER_AGENT})
            url = f"https://www.sports-reference.com/cbb/players/{letter}-index.html"
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            p_elements = await page.query_selector_all("#content p")
            batch = []

            for p_el in p_elements:
                player_a = await p_el.query_selector("a")
                if not player_a:
                    continue
                name = (await player_a.inner_text()).strip().replace(".", "")
                href = await player_a.get_attribute("href")
                if not href or not re.match(r"^[A-Za-z]", name):
                    continue

                small = await p_el.query_selector("small.note")
                years, schools = "", []
                if small:
                    raw = await small.inner_text()
                    match = re.search(r"\(\d{4}\s*[-–]\s*\d{4}\)", raw)
                    if match: years = match.group(0)
                    for a in await small.query_selector_all("a"):
                        href_s = await a.get_attribute("href")
                        if href_s and "/men/" in href_s:
                            schools.append({"name": (await a.inner_text()).strip(), "href": f"https://www.sports-reference.com{href_s}"})

                if not schools:
                    continue

                batch.append({"name": name, "href": href, "years": years, "schools": schools})

                if len(batch) >= batch_size:
                    for pl in batch:
                        pl_data = await scrape_player(browser, pl)
                        if (pl_data.get("weight") is None or pl_data.get("height") is None) and not pl_data.get("awards"):
                            print(f"⚠️ Skipping {pl_data['name']} because weight/height is None and no awards")
                            continue
                        h = compute_college_player_hash(pl_data)
                        if h not in seen_hashes:
                            seen_hashes.add(h)
                            players_to_insert.append(pl_data)
                    batch = []

            # process remaining
            for pl in batch:
                pl_data = await scrape_player(browser, pl)
                if (pl_data.get("weight") is None or pl_data.get("height") is None) and not pl_data.get("awards"):
                    print(f"⚠️ Skipping {pl_data['name']} because weight/height is None and no awards")
                    continue
                h = compute_college_player_hash(pl_data)
                if h not in seen_hashes:
                    seen_hashes.add(h)
                    players_to_insert.append(pl_data)

            # checkpoint to disk
            with open(checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(players_to_insert, f, indent=2)

            await page.close()
            await context.close()
            await asyncio.sleep(random.uniform(3, 7))

        except Exception as e:
            print(f"💥 Fatal error on letter {letter}: {e}")
            if page:
                try: await page.close()
                except: pass
            if context:
                try: await context.close()
                except: pass
            continue

    return players_to_insert


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            players = await fetch_college_players(browser)
            print(f"✅ Scraped {len(players)} players")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
