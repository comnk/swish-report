from api.core.db import get_db_connection
from api.scripts.scraping.fetch_nba_player_info import fetch_nba_players
from api.utils.helpers import launch_browser

import asyncio
import json

cnx = get_db_connection()
cursor = cnx.cursor()

async def insert_nba_players(cursor, player_list):
    """
    Inserts multiple players into the 'players' table.
    Returns a dict mapping full_name + class_year -> player_uid.
    """
    player_uid_map = {}

    for player in player_list:
        (
            full_name, link, min_year, max_year, position, height, weight, teams,
            draft_round, draft_pick, draft_year, years_pro, accolades, colleges,
            high_schools, is_active
        ) = player

        cursor.execute("""
            INSERT INTO players (full_name, class_year, current_level)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                full_name = VALUES(full_name),
                current_level = VALUES(current_level)
        """, (full_name, draft_year, 'NBA'))

        player_uid = cursor.lastrowid
        if player_uid == 0:
            cursor.execute("""
                SELECT player_uid FROM players
                WHERE full_name = %s AND class_year = %s
            """, (full_name, draft_year))
            player_uid = cursor.fetchone()[0]

        player_uid_map[(full_name, draft_year)] = player_uid

    return player_uid_map


async def insert_nba_player_details(cursor, player_list, player_uid_map):
    """
    Inserts or updates NBA player details for multiple players.
    Uses player_uid_map returned from insert_nba_players().
    """
    for player in player_list:
        (
            full_name, link, min_year, max_year, position, height, weight, teams,
            draft_round, draft_pick, draft_year, years_pro, accolades, colleges,
            high_schools, is_active
        ) = player

        player_uid = player_uid_map[(full_name, draft_year)]

        cursor.execute("""
            INSERT INTO nba_player_info
            (player_uid, link, position, height, weight, teams, min_year, max_year, draft_round,
            draft_pick, draft_year, years_pro, accolades, colleges, high_schools, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                position = VALUES(position),
                height = VALUES(height),
                weight = VALUES(weight),
                teams = VALUES(teams),
                min_year = VALUES(min_year),
                max_year = VALUES(max_year),
                draft_round = VALUES(draft_round),
                draft_pick = VALUES(draft_pick),
                draft_year = VALUES(draft_year),
                years_pro = VALUES(years_pro),
                accolades = VALUES(accolades),
                colleges = VALUES(colleges),
                high_schools = VALUES(high_schools),
                is_active = VALUES(is_active)
        """, (
            player_uid, link, position, height, weight, json.dumps(teams),
            int(min_year), int(max_year), draft_round, draft_pick, draft_year,
            years_pro, json.dumps(accolades), json.dumps(colleges),
            json.dumps(high_schools), is_active
        ))


async def main():
    playwright, browser = await launch_browser(headless=True)
    players = await asyncio.gather(fetch_nba_players(browser))
    
    await browser.close()
    await playwright.stop()
    
    player_uid_map = await insert_nba_players(cursor, players)

    await insert_nba_player_details(cursor, players, player_uid_map)

    cnx.commit()
    cursor.close()
    cnx.close()
    
    print("Inserted NBA players successfully!")

asyncio.run(main())