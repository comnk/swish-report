from playwright.sync_api import sync_playwright

from db_script_helper_functions import parse_school, parse_247_metrics, normalize_espn_height, get_espn_star_count, is_rankings_finalized

years = range(2020, 2028)

def fetch_247_sports_info(class_year, browser):
    rankings_247 = []
    page = browser.new_page()

    try:
        page.goto(
            f'https://247sports.com/season/{class_year}-basketball/recruitrankings/',
            wait_until='domcontentloaded',
            timeout=60000
        )
        page.wait_for_selector("li.rankings-page__list-item")

        wrappers = page.query_selector_all("li.rankings-page__list-item")

        for wrapper in wrappers:
            a_tag = wrapper.query_selector("a")
            player_name = a_tag.inner_text().strip() if a_tag else None
            player_link = a_tag.get_attribute("href") if a_tag else None
            if player_link and player_link.startswith("/"):
                player_link = "https://247sports.com" + player_link

            rank_div = wrapper.query_selector(".rank-column .primary")
            player_rank = rank_div.inner_text().strip() if rank_div else None

            rating_div = wrapper.query_selector(".rating")
            stars = len(rating_div.query_selector_all(".rankings-page__star-and-score span.icon-starsolid.yellow"))
            grade = int(rating_div.query_selector(".score").inner_text().strip())

            meta_span = wrapper.query_selector(".meta")
            school_meta = meta_span.inner_text().strip() if meta_span else None
            school_name, city, state = parse_school(source='247sports', high_school_raw=school_meta)

            pos_div = wrapper.query_selector(".position")
            position = pos_div.inner_text().strip() if pos_div else None

            metrics_div = wrapper.query_selector(".metrics")
            metrics = metrics_div.inner_text().strip() if metrics_div else None
            height, weight = parse_247_metrics(metrics)

            rankings_247.append((
                "247sports",
                str(class_year),
                player_rank,
                grade,
                stars,
                player_name,
                player_link,
                position,
                height,
                weight,
                school_name,
                city,
                state,
                "schooltown",
                is_rankings_finalized(class_year)
            ))

    except Exception as e:
        print(f"⚠️ Error scraping 247sports {class_year}: {e}")
    finally:
        page.close()

    return rankings_247


def fetch_espn_info(class_year, browser):
    espn_rankings = []
    page = browser.new_page()

    try:
        page.goto(
            f'https://www.espn.com/college-sports/basketball/recruiting/rankings/scnext300boys/_/class/{class_year}/order/true',
            wait_until='domcontentloaded',
            timeout=60000
        )
        page.wait_for_selector("tr.oddrow")

        wrappers = page.query_selector_all("tr.oddrow, tr.evenrow")

        for wrapper in wrappers:
            tds = wrapper.query_selector_all("td")
            if len(tds) < 8:
                continue

            player_rank = tds[0].inner_text().strip()

            # Player name & profile link
            a_tag = tds[1].query_selector("a")
            player_name = a_tag.inner_text().strip() if a_tag else None
            player_link = a_tag.get_attribute("href") if a_tag else None
            if player_link and player_link.startswith("/"):
                player_link = "https://www.espn.com" + player_link

            position = tds[2].inner_text().strip()

            school_raw = tds[3].inner_text().strip()
            school_name, city, state = parse_school(source='espn', high_school_raw=school_raw)

            height = normalize_espn_height(tds[4].inner_text().strip())
            weight = tds[5].inner_text().strip()

            star_li = tds[6].query_selector("li.star")
            star_class = star_li.get_attribute("class") if star_li else ""
            stars = get_espn_star_count(star_class)

            grade = tds[7].inner_text().strip()

            espn_rankings.append((
                "espn",
                str(class_year),
                player_rank,
                grade,
                stars,
                player_name,
                player_link,
                position,
                height,
                weight,
                school_name,
                city,
                state,
                "hometown",
                is_rankings_finalized(class_year)
            ))

    except Exception as e:
        print(f"⚠️ Error scraping ESPN {class_year}: {e}")
    finally:
        page.close()

    return espn_rankings

def fetch_rivals_info(class_year, browser):
    rivals_players = []
    page = browser.new_page()

    try:
        page.goto(
            f"https://www.on3.com/rivals/rankings/player/basketball/{class_year}/",
            wait_until='domcontentloaded',
            timeout=60000
        )

        wrappers = page.query_selector_all(".PlayerRankingsItem_block__kuO8v")

        for wrapper in wrappers:
            a_tag = wrapper.query_selector("a")
            player_name = a_tag.inner_text().strip() if a_tag else None
            player_link = a_tag.get_attribute("href") if a_tag else None
            if player_link and player_link.startswith("/"):
                player_link = "https://www.on3.com" + player_link

            # Rank
            player_rank = wrapper.query_selector('dl[aria-labelledby="rank"] dd').inner_text().strip()

            # Rating & Stars
            rating = wrapper.query_selector('div[aria-labelledby="rating"]')
            grade = int(rating.query_selector('span[data-ui="player-rating"]').inner_text().strip())
            stars_span = rating.query_selector('span[data-ui="player-stars"]')
            stars = len(stars_span.query_selector_all('svg:has(path[fill="#F2C94C"])')) if stars_span else 0

            # Position
            position = wrapper.query_selector('div[aria-labelledby="position"]').inner_text().strip()

            # High school + hometown → parse into city/state/school
            location_dl = wrapper.query_selector('dl.PlayerRankingsItem_homeContainer__CLv44')
            high_school_text = ""
            hometown_text = ""
            if location_dl:
                dts = location_dl.query_selector_all("dt")
                dds = location_dl.query_selector_all("dd")
                for dt, dd in zip(dts, dds):
                    label = dt.inner_text().strip()
                    if label == "High School":
                        hs_a = dd.query_selector("a")
                        high_school_text = hs_a.inner_text().strip() if hs_a else dd.inner_text().strip()
                    elif label == "Hometown":
                        hometown_text = dd.inner_text().strip()

            school_name, city, state = parse_school(
                source="rivals",
                high_school_raw=high_school_text,
                hometown_raw=hometown_text
            )

            # Vitals (height, weight)
            vitals_dl = wrapper.query_selector('dl.PlayerRankingsItem_vitalsContainer__XYfbI')
            height = weight = None
            if vitals_dl:
                dt_elements = vitals_dl.query_selector_all('dt')
                dd_elements = vitals_dl.query_selector_all('dd')
                for i, dt_el in enumerate(dt_elements):
                    label = dt_el.inner_text().strip().lower()
                    value = dd_elements[i].inner_text().strip() if i < len(dd_elements) else ""
                    if "height" in label:
                        height = value
                    elif "weight" in label:
                        weight = value

            # Append data
            rivals_players.append((
                "rivals",
                str(class_year),
                player_rank,
                grade,
                stars,
                player_name,
                player_link,
                position,
                height,
                weight,
                school_name,
                city,
                state,
                "hometown",
                is_rankings_finalized(class_year)
            ))

    except Exception as e:
        print(f"⚠️ Error scraping Rivals {class_year}: {e}")
    finally:
        page.close()

    return rivals_players