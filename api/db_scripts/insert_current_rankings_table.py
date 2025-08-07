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

    rankings_247_all = []
    rankings_espn_all = []
    rankings_rivals_all = []

    for year in class_years:
        rankings_247_all.append(await fetch_247_sports_info(year, browser))
        rankings_espn_all.append(await fetch_espn_info(year, browser))
        rankings_rivals_all.append(await fetch_rivals_info(year, browser))

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

    for record in all_rankings:
        (source, class_year, player_rank, grade, stars, player_name,
        player_link, position, height, weight,
        school_name, city, state, location_type, finalized) = record

        player_uid = find_matching_player(cursor, class_year, player_name)
        player_rank = clean_player_rank(player_rank)

        if not player_uid:
            cursor.execute(insert_player_sql, (player_name, class_year, 'HS'))
            player_uid = cursor.lastrowid

        cursor.execute(insert_rank_sql, (
            player_uid, source, class_year, player_rank, grade, stars,
            player_link, position, height, weight,
            school_name, city, state, location_type, finalized
        ))

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