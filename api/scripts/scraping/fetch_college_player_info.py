from utils.helpers import safe_goto, USER_AGENT
import string
import re
import traceback
import random
import asyncio
import hashlib
import json

def normalize_list(values):
    return sorted(values) if values else []

def compute_college_player_hash(player_obj):
    """Compute a consistent hash of college player info, ignoring hrefs."""
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


async def scrape_player(browser, data):
    """Scrape metadata from a single player's page efficiently (warning-free)."""
    player_url = f"https://www.sports-reference.com{data['href']}"
    print(f"📝 Scraping player: {data.get('name')} at {player_url}")

    try:
        # Create a new context & page
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_extra_http_headers({"User-Agent": USER_AGENT})
        await safe_goto(browser, page, player_url)

        # Extract meta info in a single evaluate call using raw string
        result = await page.evaluate(r'''() => {
            const data = { position: "", height: "", weight: null, awards: [] };

            const metaDiv = document.querySelector("#meta");
            if (metaDiv) {
                const pTags = Array.from(metaDiv.querySelectorAll("p"));
                for (let i = 0; i < pTags.length; i++) {
                    const strong = pTags[i].querySelector("strong");
                    if (strong && strong.innerText.toLowerCase().startsWith("position")) {
                        const match = /Position:\s*<\/strong>\s*([A-Za-z]+)/.exec(pTags[i].innerHTML);
                        if (match) {
                            const posMap = { "Guard": "G", "Forward": "F", "Center": "C" };
                            data.position = posMap[match[1].trim()] || match[1].trim();
                        }
                        if (i + 1 < pTags.length) {
                            const hwMatches = Array.from(pTags[i+1].querySelectorAll("span"))
                                                .map(el => el.innerText.trim());
                            if (hwMatches.length > 0) data.height = hwMatches[0];
                            if (hwMatches.length > 1) data.weight = parseInt(hwMatches[1].replace("lb","").trim()) || null;
                        }
                        break;
                    }
                }
            }

            const bling = document.querySelectorAll("ul#bling li a");
            data.awards = Array.from(bling).map(a => a.innerText.trim()).filter(Boolean);

            return data;
        }''')

        data.update(result)

        print(
            f"✅ Parsed player: {data.get('name')} | Pos: {data.get('position')} | "
            f"Height: {data.get('height')} | Weight: {data.get('weight')} | Awards: {data.get('awards')}"
        )

    except Exception:
        print(f"⚠️ Error scraping {player_url}:\n{traceback.format_exc()}")
    finally:
        await page.close()
        await context.close()

    return data


async def _process_player_batch(browser, batch, players_to_insert, seen_hashes):
    """Scrape and deduplicate a batch of players."""
    for player_obj in batch:
        try:
            player_obj = await scrape_player(browser, player_obj)
            player_hash = compute_college_player_hash(player_obj)
            if player_hash in seen_hashes:
                continue
            seen_hashes.add(player_hash)

            if (player_obj.get("weight") is None or player_obj.get("height") is None) and len(player_obj.get("awards")) == 0:
                print(f"⚠️ Skipping {player_obj['name']} because weight is None")
                continue

            players_to_insert.append(player_obj)
        except Exception as e:
            print(f"⚠️ Error scraping {player_obj.get('name')}: {e}")
    await asyncio.sleep(random.uniform(2, 5))


async def fetch_college_players(browser, existing_players=None, batch_size=3, letter_delay_range=(5, 10)):
    """Fetch all men's college basketball players efficiently."""
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

                player_name = (await player_a.inner_text()).strip().replace(".", "")
                href = await player_a.get_attribute("href")
                if not href or not player_name or player_name.startswith("_") or not re.match(r"^[A-Za-z]", player_name):
                    continue

                # Extract years + schools
                small = await p.query_selector("small.note")
                years = ""
                schools = []
                if small:
                    raw_small_text = await small.inner_text()
                    match = re.search(r"\(\d{4}\s*[-–]\s*\d{4}\)", raw_small_text)
                    if match: years = match.group(0)
                    school_links = await small.query_selector_all("a")
                    for a in school_links:
                        school_href = await a.get_attribute("href")
                        if school_href and "/men/" in school_href:
                            schools.append({"name": (await a.inner_text()).strip(), "href": school_href})

                if not schools:
                    continue

                player_data = {"name": player_name, "href": href, "years": years, "schools": schools}
                batch.append(player_data)

                if len(batch) >= batch_size:
                    await _process_player_batch(browser, batch, players_to_insert, seen_hashes)
                    batch = []

            if batch:
                await _process_player_batch(browser, batch, players_to_insert, seen_hashes)

            print(f"✅ Found {len(players_to_insert)} men’s players for letter {letter}")
            await asyncio.sleep(random.uniform(*letter_delay_range))

        except Exception as e:
            print(f"⚠️ Failed to load letter {letter}: {e}")
            continue

    await index_page.close()
    return players_to_insert
