from utils.helpers import safe_goto, USER_AGENT
from datetime import datetime

import hashlib
import json
import asyncio
import string
import re
import random
import traceback


def normalize_list(value):
    return value if value else []

def compute_college_player_hash(player_tuple):
    """Compute a consistent hash of player info, ignoring URL and is_active."""
    fields_to_hash = {
        "full_name": player_tuple[0],
        "years": (player_tuple[2], player_tuple[3]),
        "position": player_tuple[4],
        "height": player_tuple[5],
        "weight": player_tuple[6],
        "teams": normalize_list(player_tuple[7]),
        "draft": player_tuple[8:11],
        "years_pro": player_tuple[11],
        "accolades": normalize_list(player_tuple[12]),
        "colleges": normalize_list(player_tuple[13]),
        "high_schools": normalize_list(player_tuple[14])
    }
    serialized = json.dumps(fields_to_hash, sort_keys=True)
    return hashlib.md5(serialized.encode()).hexdigest()

async def scrape_player(browser, _, data):
    player_url = f"https://www.basketball-reference.com{data['link']}"
    page = None
    try:
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_extra_http_headers({"User-Agent": USER_AGENT})

        await safe_goto(browser, page, player_url)

        # Optional "more info" click
        try:
            await page.click("#meta_more_button", timeout=3000)
            await page.wait_for_selector("div#info p", timeout=5000)
        except:
            pass

        info_paragraphs = await page.evaluate('''() => {
            const infoDiv = document.querySelector("div#info");
            if (!infoDiv) return [];
            return Array.from(infoDiv.querySelectorAll("p"))
                        .map(p => p.innerText.trim())
                        .filter(Boolean);
        }''')

        teams_data = await page.evaluate('''() => {
            const uniDiv = document.querySelector("div.uni_holder");
            if (!uniDiv) return [];
            return Array.from(uniDiv.querySelectorAll("a"))
                        .map(a => a.getAttribute("data-tip"))
                        .filter(Boolean);
        }''')

        team_names = list({tip.split(",",1)[0].strip() for tip in teams_data})

        accolades = await page.evaluate('''() => {
            const blingList = document.querySelector("ul#bling");
            if (!blingList) return [];
            return Array.from(blingList.querySelectorAll("li a"))
                        .map(a => a.textContent.trim())
                        .filter(Boolean);
        }''')

        years_pro = draft_round = draft_pick = draft_year = high_schools = None

        for p_text in info_paragraphs:
            text_lower = p_text.lower()
            if "experience" in text_lower or "career length" in text_lower:
                exp_match = re.search(r'(\d+)', p_text)
                if exp_match:
                    years_pro = int(exp_match.group(1))
                elif "rookie" in text_lower:
                    years_pro = 0
            if "draft" in text_lower:
                round_match = re.search(r'(?:Round\s+(\d+)|(\d+)(?:st|nd|rd|th)\s+round)', p_text, re.IGNORECASE)
                pick_match = re.search(r'(?:Pick\s+(\d+)|(\d+)(?:st|nd|rd|th)\s+pick)', p_text, re.IGNORECASE)
                year_match = re.search(r'(\d{4})', p_text)
                if round_match:
                    draft_round = int(next(g for g in round_match.groups() if g))
                if pick_match:
                    draft_pick = int(next(g for g in pick_match.groups() if g))
                if year_match:
                    draft_year = int(year_match.group(1))
            if text_lower.startswith("high school:") or text_lower.startswith("high schools:"):
                hs_part = p_text.split(":",1)[1].strip()
                matches = re.findall(r'([^,]+?)\s+in\s+[^,]+(?:,\s*[^,]+)?', hs_part)
                high_schools = matches or [hs_part]

        yearMax = int(data["yearMax"]) if data["yearMax"] else 0
        current_year = datetime.now().year
        is_active = yearMax >= current_year

        draft_year = draft_year or (int(data["yearMin"]) if data["yearMin"] else 0)

        player_tuple = (
            data.get("name"),
            player_url,
            int(data.get("yearMin")) if data.get("yearMin") else None,
            yearMax,
            data.get("position"),
            data.get("height"),
            data.get("weight"),
            team_names,
            draft_round,
            draft_pick,
            draft_year,
            years_pro,
            accolades,
            data.get("colleges") or [],
            high_schools or [],
            is_active
        )
        
        print(player_tuple)
        
        return player_tuple

    except Exception:
        print(f"⚠️ Error scraping {player_url}:\n{traceback.format_exc()}")
        return (
            data["name"], player_url, int(data.get("yearMin") or 0),
            int(data.get("yearMax") or 0), data["position"], data.get("height"),
            data.get("weight"), [], None, None, None, None, [], data.get("colleges") or [], [], False
        )
    finally:
        if page:
            await page.close()
        
        if context:
            await context.close()


async def fetch_college_players(browser, existing_players=None, batch_size=3, letter_delay_range=(5,10)):
    if existing_players is None:
        existing_players = {}

    players_to_insert = []
    seen_hashes = set()

    index_page = await browser.new_page()
    await index_page.set_extra_http_headers({"User-Agent": USER_AGENT})

    for letter in string.ascii_lowercase:
        url = f"https://www.sports-reference.com/cbb/players/{letter}-index.html"
        try:
            index_page = await safe_goto(browser, index_page, url)
            p_elements = await index_page.query_selector_all("#content p")
            print(f"🔍 Found {len(p_elements)} p tags for letter {letter}")

            batch = []
            for p in p_elements:
                player_a = await p.query_selector("a")
                if not player_a:
                    continue

                player_name = (await player_a.inner_text()).strip()
                href = await player_a.get_attribute("href")
                if not href or not player_name or player_name.startswith("_") or not re.match(r"^[A-Za-z]", player_name):
                    continue

                # Extract years and schools
                small = await p.query_selector("small.note")
                years = ""
                schools = []
                if small:
                    raw_small_text = await small.inner_text()
                    match = re.search(r"\(\d{4}\s*[-–]\s*\d{4}\)", raw_small_text)
                    if match:
                        years = match.group(0)
                    school_links = await small.query_selector_all("a")
                    for a in school_links:
                        school_href = await a.get_attribute("href")
                        if school_href and "/men/" in school_href:
                            school_name = (await a.inner_text()).strip()
                            schools.append({"name": school_name, "href": school_href})

                if not schools:
                    continue

                player_obj = {
                    "name": player_name,
                    "href": href,
                    "years": years,
                    "schools": schools,
                    "position": "",
                    "height": "",
                    "weight": None,
                    "awards": []
                }

                batch.append(player_obj)

                # Process batch when full
                if len(batch) >= batch_size:
                    await _process_player_batch(browser, batch, players_to_insert, seen_hashes)
                    batch = []

            # Process remaining players in batch
            if batch:
                await _process_player_batch(browser, batch, players_to_insert, seen_hashes)

            print(f"✅ Found {len(players_to_insert)} men’s players for letter {letter}")
            await asyncio.sleep(random.uniform(*letter_delay_range))

        except Exception as e:
            print(f"⚠️ Failed to load letter {letter}: {e}")
            continue

    await index_page.close()
    return players_to_insert

async def _process_player_batch(browser, batch, players_to_insert, seen_hashes):
    """Helper to scrape and deduplicate a batch of players."""
    for player_obj in batch:
        try:
            player_obj = await scrape_player(browser, player_obj)
            player_hash = compute_college_player_hash(player_obj)
            if player_hash in seen_hashes:
                continue
            seen_hashes.add(player_hash)
            players_to_insert.append(player_obj)
        except Exception as e:
            print(f"⚠️ Error scraping {player_obj['name']}: {e}")
            continue
    await asyncio.sleep(random.uniform(2, 5))

