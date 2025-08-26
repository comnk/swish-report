from datetime import datetime
from unidecode import unidecode
import hashlib
import json
import asyncio

from api.core.db import get_db_connection
from api.scripts.scraping.fetch_nba_player_info import fetch_nba_players
from api.utils.helpers import launch_browser

def normalize_name(name):
    """Remove accents and special characters, lowercase, strip spaces."""
    return unidecode(name).strip()

def compute_player_hash(player_tuple):
    """Compute a hash of player info ignoring URL and is_active."""
    relevant_data = player_tuple[:3] + player_tuple[4:15]  # skip link and is_active
    return hashlib.md5(json.dumps(relevant_data, sort_keys=True, default=str).encode()).hexdigest()


async def insert_nba_players(cursor, player_list):
    """
    Insert players into `players` table and return mapping (full_name, draft_year) -> player_uid.
    Checks for existing player to avoid duplicates.
    """
    player_uid_map = {}

    for player in player_list:
        full_name = normalize_name(player[0])
        draft_year = int(player[10] or 0)

        # Check for existing player
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


async def insert_nba_player_details(cursor, player_list, player_uid_map, existing_players):
    """
    Insert or update detailed player info based on hash and draft_year.
    Only updates if data has changed.
    """
    for player in player_list:
        full_name, link, min_year, max_year, position, height, weight, teams, \
        draft_round, draft_pick, draft_year, years_pro, accolades, colleges, \
        high_schools, is_active = player

        player_uid = player_uid_map[(full_name, draft_year)]
        data_hash = compute_player_hash(player)

        key = (player_uid, draft_year)
        existing = existing_players.get(key)

        if existing and existing["hash"] == data_hash:
            continue  # no changes

        cursor.execute("""
            INSERT INTO nba_player_info
            (player_uid, player_url, position, height, weight, teams, min_year, max_year,
            draft_round, draft_pick, draft_year, years_pro, accolades, colleges, high_schools,
            is_active, data_hash, last_scraped)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                position = VALUES(position),
                height = VALUES(height),
                weight = VALUES(weight),
                teams = VALUES(teams),
                min_year = VALUES(min_year),
                max_year = VALUES(max_year),
                draft_round = VALUES(draft_round),
                draft_pick = VALUES(draft_pick),
                years_pro = VALUES(years_pro),
                accolades = VALUES(accolades),
                colleges = VALUES(colleges),
                high_schools = VALUES(high_schools),
                is_active = VALUES(is_active),
                data_hash = VALUES(data_hash),
                last_scraped = VALUES(last_scraped)
        """, (
            player_uid, link, position, height, weight, json.dumps(teams),
            int(min_year) if min_year else None,
            int(max_year) if max_year else None,
            draft_round, draft_pick, draft_year, years_pro,
            json.dumps(accolades), json.dumps(colleges), json.dumps(high_schools),
            is_active, data_hash, datetime.now()
        ))


async def main():
    cnx = get_db_connection()
    cursor = cnx.cursor()

    # Load existing nba_player_info keyed by (player_uid, draft_year)
    cursor.execute("""
        SELECT player_uid, draft_year, data_hash, last_scraped
        FROM nba_player_info
    """)
    existing_players_list = cursor.fetchall()
    existing_players = {
        (row[0], row[1]): {"hash": row[2], "last_scraped": row[3]}
        for row in existing_players_list
    }

    # Launch browser and fetch players
    playwright, browser = await launch_browser(headless=True)
    scraped_players = await fetch_nba_players(browser, existing_players)
    await browser.close()
    await playwright.stop()

    # Deduplicate scraped players by (full_name, draft_year)
    unique_players = {}
    for p in scraped_players:
        draft_year = p[10] or (p[3] if p[3] else 0)
        key = (normalize_name(p[0]), draft_year)
        if key not in unique_players:
            p = list(p)
            p[10] = draft_year
            unique_players[key] = tuple(p)
    players = list(unique_players.values())

    # Insert players
    player_uid_map = await insert_nba_players(cursor, players)
    await insert_nba_player_details(cursor, players, player_uid_map, existing_players)

    cnx.commit()
    cursor.close()
    cnx.close()
    print("Inserted NBA players successfully!")


asyncio.run(main())