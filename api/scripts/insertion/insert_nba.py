from api.core.db import get_db_connection
from api.scripts.scraping.fetch_nba_player_info import fetch_nba_players
from api.utils.helpers import launch_browser

import asyncio

cnx = get_db_connection()
cursor = cnx.cursor()

def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def insert_nba_players():
    # Insert NBA players into the master players table
    insert_sql = """
    INSERT INTO players (full_name, class_year, current_level)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
        full_name = VALUES(full_name),
        current_level = VALUES(current_level)
    """

def insert_nba_player_details():
    pass


async def main():
    playwright, browser = await launch_browser(headless=False)
    players = await fetch_nba_players(browser)
    
    for player in players:
        print(player)
        break
    
    result = insert_nba_player_details()
    print(result)

asyncio.run(main())