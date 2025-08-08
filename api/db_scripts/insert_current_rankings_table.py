import asyncio
import mysql.connector
import os
from dotenv import load_dotenv
from celery import shared_task
from fetch_rankings_current_script import fetch_247_sports_info, fetch_espn_info, fetch_rivals_info
from db_script_helper_functions import find_matching_player, launch_browser, clean_player_rank

async def load_current_player_rankings_async():
    dotenv_path = '../.env'
    load_dotenv(dotenv_path)

    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')

    class_years = [2025, 2026, 2027]

    print("🚀 Starting serial data collection...")

    playwright, browser = await launch_browser(headless=True)

    rankings_247_all = await asyncio.gather(
        fetch_247_sports_info(class_years, browser),
    )

    rankings_espn_all, rankings_rivals_all = await asyncio.gather(
        asyncio.gather(*(fetch_espn_info(year, browser) for year in class_years)),
        asyncio.gather(*(fetch_rivals_info(year, browser) for year in class_years))
    )

    await browser.close()
    await playwright.stop()

    data_247 = [record for year_data in rankings_247_all for record in year_data]
    data_espn = [record for year_data in rankings_espn_all for record in year_data]
    data_rivals = [record for year_data in rankings_rivals_all for record in year_data]

    print("✅ Rankings fetched from all sources.")

    all_rankings = data_247 + data_espn + data_rivals

    cnx = mysql.connector.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database='swish_report'
    )
    cursor = cnx.cursor()

    insert_rank_sql = """
    INSERT INTO high_school_player_rankings
    (player_uid, source, class_year, player_rank, player_grade, stars, link, position, height, weight, school_name, city, state, location_type, is_finalized)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    insert_player_sql = """
    INSERT INTO players (full_name, class_year, current_level)
    VALUES (%s, %s, %s)
    """

    # Step 1: Fetch all existing players per class_year (to avoid many DB queries)
    existing_players_by_year = {}
    for year in class_years:
        cursor.execute("SELECT player_uid, full_name FROM players WHERE class_year=%s", (year,))
        existing_players_by_year[year] = cursor.fetchall()

    # Step 2: For each player in all_rankings, find matching player_uid or insert new player
    ranking_rows = []
    for (source, class_year, player_rank, grade, stars, player_name,
        player_link, position, height, weight,
        school_name, city, state, location_type, finalized) in all_rankings:

        player_uid = find_matching_player(existing_players_by_year, int(class_year), player_name)

        if not player_uid:
            cursor.execute(insert_player_sql, (player_name, class_year, 'HS'))
            player_uid = cursor.lastrowid
            # Add newly inserted player to cache for future matches in this run
            existing_players_by_year.setdefault(int(class_year), []).append((player_uid, player_name))

        ranking_rows.append((
            player_uid, source, class_year, clean_player_rank(player_rank),
            grade, stars, player_link, position, height, weight,
            school_name, city, state, location_type, finalized
        ))

    # Step 3: Bulk insert rankings
    if ranking_rows:
        cursor.executemany(insert_rank_sql, ranking_rows)

    cnx.commit()
    cursor.close()
    cnx.close()

    print("✅ All rankings inserted into database.")


async def main():
    result = await load_current_player_rankings_async()
    print(result)

asyncio.run(main())
# @shared_task
# def load_current_player_rankings():
#     asyncio.run(load_current_player_rankings_async())