import mysql.connector
from playwright.sync_api import sync_playwright

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

def fetch_247_sports_info():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(f'https://247sports.com/season/2027-basketball/recruitrankings/', wait_until='domcontentloaded', timeout=60000)
        page.wait_for_selector("li.rankings-page__list-item")

        wrappers = page.query_selector_all("li.rankings-page__list-item")

        for wrapper in wrappers:
            # player Name & link (using your working approach)
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

            # position
            pos_div = wrapper.query_selector(".position")
            position = pos_div.inner_text().strip() if pos_div else None

            # height / weight
            metrics_div = wrapper.query_selector(".metrics")
            metrics = metrics_div.inner_text().strip() if metrics_div else None

            print({
                "rank": rank,
                "name": player_name,
                "link": player_link,
                "school": school_meta,
                "position": position,
                "metrics": metrics
            })

        browser.close()

fetch_247_sports_info()