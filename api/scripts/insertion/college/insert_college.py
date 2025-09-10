from core.db import get_db_connection
from scripts.scraping.fetch_college_player_info import fetch_college_players
from utils.helpers import launch_browser, normalize_name
import asyncio
import json
from datetime import datetime
import hashlib

def compute_data_hash(player):
    """Compute a hash for deduplication."""
    fields = {
        "position": player[4] or "",
        "height": player[5] or "",
        "weight": player[6] or 0,
        "schools": player[13] or [],
        "awards": player[12] or []
    }
    serialized = json.dumps(fields, sort_keys=True)
    return hashlib.md5(serialized.encode()).hexdigest()

async def insert_college_players(cursor, player_list):
    """
    Insert players into `players` table if they don't exist.
    Update current_level if previously "HS" -> "COLLEGE".
    Skip if current_level is "NBA".
    Returns a mapping of (full_name, years) -> player_uid
    """
    player_uid_map = {}

    for player in player_list:
        full_name = normalize_name(player[0])
        years = player[3] if player[3] else ""

        cursor.execute("""
            SELECT player_uid, current_level FROM players
            WHERE full_name=%s
        """, (full_name,))
        row = cursor.fetchone()

        if row:
            player_uid, current_level = row
            if current_level == "HS":
                cursor.execute("""
                    UPDATE players SET current_level='COLLEGE', updated_at=NOW()
                    WHERE player_uid=%s
                """, (player_uid,))
            elif current_level == "NBA":
                continue  # skip
        else:
            cursor.execute("""
                INSERT INTO players (full_name, current_level, created_at, updated_at)
                VALUES (%s, 'COLLEGE', NOW(), NOW())
            """, (full_name,))
            player_uid = cursor.lastrowid

        player_uid_map[(full_name, years)] = player_uid

    return player_uid_map


async def insert_college_player_info(cursor, player_uid_map, player_list):
    """
    Insert into `college_player_info` table.
    Deduplicate using UNIQUE (player_uid, years) and data_hash.
    Update row if data_hash changed.
    """
    for player in player_list:
        full_name = normalize_name(player[0])
        years = player[3] if player[3] else ""
        player_uid = player_uid_map.get((full_name, years))
        if not player_uid:
            continue

        player_url = player[1]
        position = player[4] or ""
        height = player[5] or ""
        weight = player[6]
        schools = json.dumps(player[13] or [])
        awards = json.dumps(player[12] or [])
        is_active = 1 if player[15] else 0

        if weight is None:
            continue

        data_hash = compute_data_hash(player)

        # Check if row exists
        cursor.execute("""
            SELECT info_uid, data_hash FROM college_player_info
            WHERE player_uid=%s AND years=%s
        """, (player_uid, years))
        row = cursor.fetchone()

        if row:
            info_uid, existing_hash = row
            if existing_hash != data_hash:
                # Update existing row
                cursor.execute("""
                    UPDATE college_player_info
                    SET player_url=%s, position=%s, height=%s, weight=%s,
                        schools=%s, awards=%s, is_active=%s, data_hash=%s,
                        last_scraped=NOW()
                    WHERE info_uid=%s
                """, (player_url, position, height, weight, schools, awards, is_active, data_hash, info_uid))
        else:
            # Insert new row
            cursor.execute("""
                INSERT INTO college_player_info
                (player_uid, player_url, position, height, weight, years,
                 schools, awards, is_active, data_hash)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (player_uid, player_url, position, height, weight, years, schools, awards, is_active, data_hash))


async def main():
    cnx = get_db_connection()
    cursor = cnx.cursor()

    playwright, browser = await launch_browser(headless=True)
    scraped_players = await fetch_college_players(browser)
    await browser.close()
    await playwright.stop()

    player_uid_map = await insert_college_players(cursor, scraped_players)
    await insert_college_player_info(cursor, player_uid_map, scraped_players)

    cnx.commit()
    cursor.close()
    cnx.close()
    print("Inserted/Updated college players successfully!")


if __name__ == "__main__":
    asyncio.run(main())
