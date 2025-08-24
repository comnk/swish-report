from datetime import datetime
import hashlib
import json
import asyncio
import string
import re
import random
import traceback

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36"
)

async def safe_goto(page, url, max_retries=3):
    for attempt in range(max_retries):
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=40000)
            return
        except Exception as e:
            print(f"⚠️ Navigation failed (attempt {attempt+1}) for {url}: {e}")
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(5 + random.random()*5)

def normalize_list(value):
    return value if value else []

def compute_player_hash(player_tuple):
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

async def scrape_player(page, data):
    player_url = f"https://www.basketball-reference.com{data['link']}"
    try:
        await safe_goto(page, player_url)

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
        is_active = False

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


async def fetch_nba_players(browser, existing_players=None, batch_size=3, letter_delay_range=(5,10)):
    if existing_players is None:
        existing_players = {}

    players_to_insert = []
    seen_keys = set()
    index_page = await browser.new_page()
    await index_page.set_extra_http_headers({"User-Agent": USER_AGENT})

    for letter in string.ascii_lowercase:
        if letter == "x":
            continue

        url = f"https://www.basketball-reference.com/players/{letter}/"
        await safe_goto(index_page, url)
        await index_page.wait_for_selector("table#players tbody tr", timeout=15000)

        rows_data = await index_page.evaluate('''() => {
            const rows = Array.from(document.querySelectorAll("table#players tbody tr"))
                        .filter(r => !r.classList.contains("thead"));
            return rows.map(row => {
                const playerCell = row.querySelector('th[data-stat="player"] a');
                return {
                    name: playerCell?.innerText.trim() || null,
                    link: playerCell?.getAttribute("href") || null,
                    yearMin: row.querySelector('td[data-stat="year_min"]')?.innerText.trim() || null,
                    yearMax: row.querySelector('td[data-stat="year_max"]')?.innerText.trim() || null,
                    position: row.querySelector('td[data-stat="pos"]')?.innerText.trim() || null,
                    height: row.querySelector('td[data-stat="height"]')?.innerText.trim() || null,
                    weight: row.querySelector('td[data-stat="weight"]')?.innerText.trim() || null,
                    colleges: Array.from(row.querySelectorAll('td[data-stat="colleges"] a'))
                        .map(a => a.innerText.trim())
                };
            });
        }''')

        rows_data = [r for r in rows_data if r["link"]]

        # Process in batches
        for i in range(0, len(rows_data), batch_size):
            batch = rows_data[i:i+batch_size]

            # fresh page for this batch
            page = await browser.new_page()
            await page.set_extra_http_headers({"User-Agent": USER_AGENT})

            for d in batch:
                player_tuple = await scrape_player(page, d)

                # Normalize draft year
                draft_year = player_tuple[10] or (int(player_tuple[3]) if player_tuple[3] else 0)
                key = (player_tuple[0], draft_year)
                if key in seen_keys:
                    continue
                seen_keys.add(key)

                # --- 🚨 filter
                yearMax = player_tuple[3] or 0
                accolades = player_tuple[12] or []
                if yearMax <= 2004 and not accolades:
                    continue
                years_pro = player_tuple[11] or 0
                is_active = player_tuple[15] or 0
                if years_pro <= 1 and not is_active:
                    continue

                player_hash = compute_player_hash(player_tuple)
                existing = existing_players.get(key)
                should_update = (
                    not existing or
                    existing["hash"] != player_hash or
                    (datetime.now() - existing.get("last_scraped", datetime.min)).days > 365
                )

                if should_update:
                    p = list(player_tuple)
                    p[10] = draft_year  # normalized
                    players_to_insert.append(tuple(p))
                    existing_players[key] = {"hash": player_hash, "last_scraped": datetime.now()}

            await page.close()
            await asyncio.sleep(random.uniform(2, 5))  # delay between batches

        await asyncio.sleep(random.uniform(*letter_delay_range))

    await index_page.close()
    return players_to_insert