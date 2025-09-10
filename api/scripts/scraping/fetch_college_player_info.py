from utils.helpers import safe_goto, USER_AGENT
import string
import re
import traceback
import random
import asyncio
import hashlib
import json

def normalize_list(values):
    if not values:
        return []
    return sorted(values)

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


async def scrape_player(browser, page, data):
    """Scrape metadata from a single player's page."""
    player_url = f"https://www.sports-reference.com{data['href']}"
    print(f"📝 Scraping player: {data.get('name')} at {player_url}")

    data["position"] = data.get("position", "")
    data["height"] = data.get("height", "")
    data["weight"] = data.get("weight", None)
    data["awards"] = []

    try:
        await safe_goto(browser, page, player_url)
        meta_div = await page.query_selector("#meta")
        if meta_div:
            p_tags = await meta_div.query_selector_all("p")
            for i, p in enumerate(p_tags):
                strong = await p.query_selector("strong")
                if strong:
                    strong_text = (await strong.inner_text()).strip().lower()
                    if strong_text.startswith("position"):
                        raw_html = await p.inner_html()
                        match = re.search(r"Position:\s*</strong>\s*([A-Za-z]+)", raw_html)
                        if match:
                            pos_map = {"Guard": "G", "Forward": "F", "Center": "C"}
                            data["position"] = pos_map.get(match.group(1).strip(), match.group(1).strip())
                        else:
                            data["position"] = ""
                        # --- Height/Weight next <p>
                        if i + 1 < len(p_tags):
                            hw_html = await p_tags[i+1].inner_html()
                            hw_matches = re.findall(r"<span>(.*?)</span>", hw_html)
                            if hw_matches:
                                data["height"] = hw_matches[0].strip()
                                if len(hw_matches) > 1:
                                    try:
                                        data["weight"] = int(hw_matches[1].replace("lb", "").strip())
                                    except:
                                        data["weight"] = None
                                else:
                                    data["weight"] = None
                            else:
                                data["height"] = ""
                                data["weight"] = None
                        break

        # --- Extract awards from #bling
        bling_ul = await page.query_selector("ul#bling")
        if bling_ul:
            li_elements = await bling_ul.query_selector_all("li")
            for li in li_elements:
                a_tag = await li.query_selector("a")
                if a_tag:
                    award_text = (await a_tag.inner_text()).strip()
                    if award_text:
                        data["awards"].append(award_text)

        print(f"✅ Parsed player: {data.get('name')} | Pos: {data.get('position')} | "
            f"Height: {data.get('height')} | Weight: {data.get('weight')} | Awards: {data.get('awards')}")

    except Exception as e:
        print(f"⚠️ Error scraping {player_url}: {e}\n{traceback.format_exc()}")

    return data


async def fetch_college_players(browser, existing_players=None, batch_size=3, letter_delay_range=(5,10)):
    """Fetch all men's college basketball players with batch processing, deduplication, and awards."""
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

                # --- extract years + schools
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

                player_data = {"name": player_name, "href": href, "years": years, "schools": schools}
                batch.append(player_data)

                # process batch when it reaches batch_size
                if len(batch) >= batch_size:
                    for d in batch:
                        try:
                            print(f"⏳ Scraping player: {d['name']}")
                            player_page = await browser.new_page()
                            await player_page.set_extra_http_headers({"User-Agent": USER_AGENT})
                            player_obj = await scrape_player(browser, player_page, d)
                            await player_page.close()

                            if not player_obj:
                                continue

                            player_hash = compute_college_player_hash(player_obj)
                            if player_hash in seen_hashes:
                                continue
                            seen_hashes.add(player_hash)

                            if (player_obj.get("weight") is None or player_obj.get("height") is None) and len(player_obj.get("awards")) == 0:
                                print(f"⚠️ Skipping {player_obj['name']} because weight is None")
                                continue

                            players_to_insert.append(player_obj)
                        except Exception as e:
                            print(f"⚠️ Error scraping {d['name']}: {e}")
                            continue
                    batch = []
                    await asyncio.sleep(random.uniform(2, 5))

            # process remaining players in batch
            for d in batch:
                try:
                    print(f"⏳ Scraping player: {d['name']}")
                    player_page = await browser.new_page()
                    await player_page.set_extra_http_headers({"User-Agent": USER_AGENT})
                    player_obj = await scrape_player(player_page, d)
                    await player_page.close()

                    if not player_obj:
                        continue

                    player_hash = compute_college_player_hash(player_obj)
                    if player_hash in seen_hashes:
                        continue
                    seen_hashes.add(player_hash)

                    players_to_insert.append(player_obj)
                except Exception as e:
                    print(f"⚠️ Error scraping {d['name']}: {e}")
                    continue

            print(f"✅ Found {len(players_to_insert)} men’s players for letter {letter}")
            await asyncio.sleep(random.uniform(*letter_delay_range))  # delay between letters

        except Exception as e:
            print(f"⚠️ Failed to load letter {letter}: {e}")
            continue

    await index_page.close()
    return players_to_insert

