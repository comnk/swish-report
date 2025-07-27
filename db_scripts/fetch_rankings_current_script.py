from playwright.sync_api import sync_playwright

from db_script_helper_functions import parse_school, parse_247_metrics, normalize_espn_height, get_espn_star_count, is_rankings_finalized

years = range(2020, 2028)

def fetch_247_sports_info(class_year):
    rankings_247 = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f'https://247sports.com/season/{class_year}-basketball/recruitrankings/', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_selector("li.rankings-page__list-item")

        wrappers = page.query_selector_all("li.rankings-page__list-item")

        for wrapper in wrappers:
            # player name & link
            a_tag = wrapper.query_selector("a")
            player_name = a_tag.inner_text().strip() if a_tag else None
            player_link = a_tag.get_attribute("href") if a_tag else None
            if player_link and player_link.startswith("/"):
                player_link = "https://247sports.com" + player_link

            # rank
            rank_div = wrapper.query_selector(".rank-column .primary")
            player_rank = rank_div.inner_text().strip() if rank_div else None

            # player grade and stars
            rating_div = wrapper.query_selector(".rating")
            stars = len(rating_div.query_selector_all(".rankings-page__star-and-score span.icon-starsolid.yellow"))
            grade = int(rating_div.query_selector(".score").inner_text().strip())

            # school / metadata
            meta_span = wrapper.query_selector(".meta")
            school_meta = meta_span.inner_text().strip() if meta_span else None
            school_name, city, state = parse_school(source='247sports', high_school_raw=school_meta)
            
            # position
            pos_div = wrapper.query_selector(".position")
            position = pos_div.inner_text().strip() if pos_div else None

            # height / weight
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

        browser.close()
    
    return rankings_247

def fetch_espn_info(class_year):
    espn_rankings = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f'https://www.espn.com/college-sports/basketball/recruiting/rankings/scnext300boys/_/class/{class_year}/order/true', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_selector("tr.oddrow")
        
        wrappers = page.query_selector_all("tr.oddrow, tr.evenrow")

        for wrapper in wrappers:
            tds = wrapper.query_selector_all("td")
            
            if len(tds) < 6:
                continue

            player_rank = tds[0].inner_text().strip()

            a_tag = tds[1].query_selector("a")
            player_name = a_tag.inner_text().strip() if a_tag else None
            player_link = a_tag.get_attribute("href") if a_tag else None
            if player_link and player_link.startswith("/"):
                player_link = "https://www.espn.com" + player_link

            position = tds[2].inner_text().strip()

            city_text = tds[3].inner_text().strip()
            school_name, city, state = parse_school(source='espn', high_school_raw=city_text)
            height = tds[4].inner_text().strip()
            height = normalize_espn_height(height)

            weight = tds[5].inner_text().strip()
            
            stars = tds[6].query_selector("li.star")
            stars = get_espn_star_count(stars.get_attribute("class") or "")
            
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
        
        browser.close()
        
    return espn_rankings


def fetch_rivals_info(class_year):
    rivals_players = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"https://www.on3.com/rivals/rankings/player/basketball/{class_year}/", wait_until='domcontentloaded', timeout=60000)
        
        wrappers = page.query_selector_all(".PlayerRankingsItem_block__kuO8v")
        
        for wrapper in wrappers:
            a_tag = wrapper.query_selector("a")
            player_name = a_tag.inner_text().strip() if a_tag else None
            player_link = a_tag.get_attribute("href") if a_tag else None
            
            player_rank = wrapper.query_selector('dl[aria-labelledby="rank"]').query_selector("dd").inner_text()
            
            rating = wrapper.query_selector('div[aria-labelledby="rating"]')
            grade = int(rating.query_selector('span[data-ui="player-rating"]').inner_text())
            
            stars = rating.query_selector('span[data-ui="player-stars"]')
            stars = len(stars.query_selector_all('svg:has(path[fill="#F2C94C"])'))

            position = wrapper.query_selector('div[aria-labelledby="position"]').inner_text().strip()
            
            if player_link and player_link.startswith("/"):
                player_link = "https://www.on3.com" + player_link

            location_dl = wrapper.query_selector('dl.PlayerRankingsItem_homeContainer__CLv44')
            
            if location_dl:
                high_school_text = ""
                hometown_text = ""
                dts = location_dl.query_selector_all("dt")
                dds = location_dl.query_selector_all("dd")
                for dt, dd in zip(dts, dds):
                    label = dt.inner_text().strip()
                    if label == "High School":
                        a_tag = dd.query_selector("a")
                        high_school_text = a_tag.inner_text().strip() if a_tag else dd.inner_text().strip()
                    elif label == "Hometown":
                        hometown_text = dd.inner_text().strip()

                school_name, city, state = parse_school(
                    source="rivals",
                    high_school_raw=high_school_text,
                    hometown_raw=hometown_text
                )
            
            vitals_dl = wrapper.query_selector('dl.PlayerRankingsItem_vitalsContainer__XYfbI')

            height = None
            weight = None

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
            
        browser.close()
    
    return rivals_players