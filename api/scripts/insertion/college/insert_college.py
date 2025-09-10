from core.db import get_db_connection
from scripts.scraping.fetch_college_player_info import fetch_college_players
from utils.helpers import launch_browser, normalize_name

import asyncio

async def insert_college_players(cursor, player_list):
    """
    Insert players into `players` table and return mapping (full_name, draft_year) -> player_uid.
    Checks for existing player to avoid duplicates.
    """
    player_uid_map = {}

    for player in player_list:
        full_name = normalize_name(player[0])
        draft_year = int(player[10] or 0)

        cursor.execute("""
            SELECT player_uid FROM players
            WHERE full_name=%s AND draft_year=%s
        """, (full_name, draft_year))
        row = cursor.fetchone()

        if row:
            player_uid = row[0]
        else:
            cursor.execute("""
                INSERT INTO players (full_name, draft_year, current_level)
                VALUES (%s, %s, 'NBA')
            """, (full_name, draft_year))
            player_uid = cursor.lastrowid

        player_uid_map[(full_name, draft_year)] = player_uid

    return player_uid_map

async def main():
    cnx = get_db_connection()
    cursor = cnx.cursor()
    
    cursor.execute("""
        SELECT player_uid, data_hash, last_scraped
        FROM college_player_info
    """)
    
    existing_players_list = cursor.fetchall()
    existing_players = {
        (row[0], row[1]): {"hash": row[2], "last_scraped": row[3]}
        for row in existing_players_list
    }
    
    playwright, browser = await launch_browser(headless=True)
    scraped_players = await fetch_college_players(browser, existing_players)
    await browser.close()
    await playwright.stop()
    
    unique_players = {}
    for p in scraped_players:
        draft_year = p[10] or (p[3] if p[3] else 0)
        key = (normalize_name(p[0]), draft_year)
        if key not in unique_players:
            p = list(p)
            p[10] = draft_year
            unique_players[key] = tuple(p)
    players = list(unique_players.values())
    
    cnx.commit()
    cursor.close()
    cnx.close()
    print("Inserted college players successfully!")

asyncio.run(main())