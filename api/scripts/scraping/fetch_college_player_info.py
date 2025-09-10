from utils.helpers import safe_goto, USER_AGENT

import string
import re
import traceback

async def scrape_player(browser, _, data):
    player_url = f"https://www.sports-reference.com{data['href']}"
    page = None
    context = None

    try:
        context = await browser.new_context()
        page = await context.new_page()
        await page.set_extra_http_headers({"User-Agent": USER_AGENT})
        
        await safe_goto(browser, page, player_url)

        meta_div = await page.query_selector("#meta")
        if meta_div:
            p_tags = await meta_div.query_selector_all("p")

            for i, p in enumerate(p_tags):
                strong = await p.query_selector("strong")
                if strong:
                    strong_text = (await strong.inner_text()).strip().lower()
                    if strong_text.startswith("position"):
                        # --- Position
                        raw_position_html = await p.inner_html()
                        match = re.search(r"Position:\s*</strong>\s*([A-Za-z]+)", raw_position_html)
                        if match:
                            pos_word = match.group(1).strip()
                            pos_map = {"Guard": "G", "Forward": "F", "Center": "C"}
                            data["position"] = pos_map.get(pos_word, pos_word)
                        else:
                            data["position"] = ""

                        # --- Height/Weight (next <p>)
                        if i + 1 < len(p_tags):
                            raw_hw_html = await p_tags[i + 1].inner_html()
                            hw_matches = re.findall(r"<span>(.*?)</span>", raw_hw_html)
                            if hw_matches:
                                data["height"] = hw_matches[0].strip()
                                if len(hw_matches) > 1:
                                    weight_raw = hw_matches[1].replace("lb", "").strip()
                                    try:
                                        data["weight"] = int(weight_raw)
                                    except ValueError:
                                        data["weight"] = None
                                else:
                                    data["weight"] = None
                            else:
                                data["height"] = ""
                                data["weight"] = None
                        break

    except Exception:
        print(f"⚠️ Error scraping {player_url}:\n{traceback.format_exc()}")
    finally:
        if page:
            await page.close()
        if context:
            await context.close()

    return data


async def fetch_college_players(browser, existing_players=None, batch_size=3, letter_delay_range=(5,10)):
    if existing_players is None:
        existing_players = {}
    
    players_to_insert = []
    seen_keys = set()

    index_page = await browser.new_page()
    await index_page.set_extra_http_headers({"User-Agent": USER_AGENT})
    
    for letter in string.ascii_lowercase:
        url = f"https://www.sports-reference.com/cbb/players/{letter}-index.html"
        try:
            index_page = await safe_goto(browser, index_page, url)

            p_elements = await index_page.query_selector_all("#content p")

            for p in p_elements:
                player_a = await p.query_selector("a")
                if not player_a:
                    continue

                player_name = (await player_a.inner_text()).strip()
                player_href = await player_a.get_attribute("href")

                if not player_href:
                    continue

                if not player_name or player_name.startswith("_"):
                    continue
                if not re.match(r"^[A-Za-z]", player_name):
                    continue

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
                            schools.append({
                                "name": school_name,
                                "href": school_href
                            })

                if not schools:
                    continue

                player_obj = {
                    "name": player_name,
                    "href": player_href,
                    "years": years,
                    "schools": schools
                }

                # ✅ Call scrape_player to enrich with metadata
                player_obj = await scrape_player(browser, None, player_obj)
                print(player_obj)
                players_to_insert.append(player_obj)

            print(f"✅ Found {len(players_to_insert)} men’s players for letter {letter}")

        except Exception as e:
            print(f"⚠️ Failed to load letter {letter}: {e}")
            continue
    
    await index_page.close()
    return players_to_insert
