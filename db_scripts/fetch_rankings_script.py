import mysql.connector
from playwright.sync_api import sync_playwright

from db_script_helper_functions import parse_school, parse_247_metrics

import os

from dotenv import load_dotenv

dotenv_path = '../.env'

# Load the .env file
load_dotenv(dotenv_path)

# Access environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')

cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST)
cursorObject = cnx.cursor()

years = range(2020, 2028)

def fetch_247_sports_info(class_year):
    rankings_247 = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
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
            rank = rank_div.inner_text().strip() if rank_div else None

            # school / metadata
            meta_span = wrapper.query_selector(".meta")
            school_meta = meta_span.inner_text().strip() if meta_span else None
            school_name, school_city, school_state = parse_school(source='247sports', high_school_raw=school_meta)
            
            # position
            pos_div = wrapper.query_selector(".position")
            position = pos_div.inner_text().strip() if pos_div else None

            # height / weight
            metrics_div = wrapper.query_selector(".metrics")
            metrics = metrics_div.inner_text().strip() if metrics_div else None
            height, weight = parse_247_metrics(metrics)

            rankings_247({
                "source": "247sports",
                "rank": rank,
                "name": player_name,
                "link": player_link,
                "position": position,
                "school_name": school_name,
                "school_city": school_city,
                "school_state": school_state,
                "location_type": "schooltown",
                "height": height,
                "weight": weight
            })

        browser.close()
    
    return rankings_247

def fetch_espn_info(class_year):
    espn_rankings = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f'https://www.espn.com/college-sports/basketball/recruiting/rankings/scnext300boys/_/class/{class_year}/order/true', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_selector("tr.oddrow")
        
        wrappers = page.query_selector_all("tr.oddrow, tr.evenrow")

        for wrapper in wrappers:
            tds = wrapper.query_selector_all("td")
            
            if len(tds) < 6:
                continue

            rank = tds[0].inner_text().strip()

            a_tag = tds[1].query_selector("a")
            player_name = a_tag.inner_text().strip() if a_tag else None
            player_link = a_tag.get_attribute("href") if a_tag else None
            if player_link and player_link.startswith("/"):
                player_link = "https://www.espn.com" + player_link

            position = tds[2].inner_text().strip()

            school_city_text = tds[3].inner_text().strip()
            school_name, school_city, school_state = parse_school(source='espn', high_school_raw=school_city_text)
            height = tds[4].inner_text().strip()

            weight = tds[5].inner_text().strip()

            espn_rankings.append({
                "source": "espn",
                "rank": rank,
                "name": player_name,
                "link": player_link,
                "position": position,
                "school_name": school_name,
                "school_city": school_city,
                "school_state": school_state,
                "location_type": "schooltown",
                "height": height,
                "weight": weight
            })
        
        browser.close()
        
    return espn_rankings


def fetch_rivals_info(class_year):
    rivals_players = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f"https://www.on3.com/rivals/rankings/player/basketball/{class_year}/", wait_until='domcontentloaded', timeout=60000)
        
        wrappers = page.query_selector_all(".PlayerRankingsItem_block__kuO8v")
        
        for wrapper in wrappers:
            a_tag = wrapper.query_selector("a")
            player_name = a_tag.inner_text().strip() if a_tag else None
            player_link = a_tag.get_attribute("href") if a_tag else None
            
            rank = wrapper.query_selector('dl[aria-labelledby="rank"]').query_selector("dd").inner_text()
            position = wrapper.query_selector('div[aria-labelledby="position"]').inner_text().strip()
            
            if player_link and player_link.startswith("/"):
                player_link = "https://www.on3.com/" + player_link

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

                school_name, school_city, school_state = parse_school(
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
            
            rivals_players.append({
                "source": "rivals",
                "rank": rank,
                "name": player_name,
                "link": player_link,
                "position": position,
                "school_name": school_name,
                "school_city": school_city,
                "school_state": school_state,
                "location_type": "hometown",
                "height": height,
                "weight": weight
            })
            
        browser.close()
    
    return rivals_players


rankings_247 = fetch_247_sports_info(2027)
espn_rankings = fetch_espn_info(2027)
rivals_rankings = fetch_rivals_info(2027)