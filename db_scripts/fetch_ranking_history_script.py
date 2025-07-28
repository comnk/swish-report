import mysql.connector
from playwright.sync_api import sync_playwright

import os

from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST=os.getenv('DB_HOST')

cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, host=DB_HOST, database='swish_report')
cursor = cnx.cursor()

def fetch_players_247_ranking_history(class_year):
    class_year_history = []
    
    select_sql = """
    SELECT name, link FROM player_rankings WHERE class_year=%s AND source=%s
    """
    
    cursor.execute(select_sql, (class_year,'247sports'))
    rows = cursor.fetchall()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for (name, link,) in rows:
            page = browser.new_page()
            page.goto(f'{link}', wait_until='domcontentloaded', timeout=30000)
            
            list_item = page.query_selector("ul.ranks-list li")
            next_link = list_item.query_selector_all("a")[1].get_attribute("href")
            
            page.goto(f'{next_link}', wait_until='domcontentloaded', timeout=30000)
            
            list_items = page.query_selector_all("ul.ranking-history-list li")[1:]
            
            for item in list_items:
                spans = item.query_selector_all("span")
                
                rating = spans[0].inner_text().strip() if len(spans) > 0 else None
                rank = spans[1].inner_text().strip() if len(spans) > 1 else None
                change_date = spans[2].inner_text().strip() if len(spans) > 2 else None
                class_year_history.append((name, class_year, "247sports", rating, rank, change_date))
            
            page.close()
            
        browser.close()
    
    cursor.close()
    cnx.close()
    
    return class_year_history

def fetch_player_rivals_ranking_history(class_year):
    class_year_history = []
    
    select_sql = """
    SELECT name, link FROM player_rankings WHERE class_year=%s AND source=%s
    """
    
    cursor.execute(select_sql, (class_year,'rivals'))
    rows = cursor.fetchall()
    
    return class_year_history

fetch_players_247_ranking_history(2027)
