import time
import json
import re
import concurrent.futures

from datetime import datetime
from ....core.db import get_db_connection
from ....core.config import set_openai
from ....utils.ai_prompts import SYSTEM_PROMPT, user_content
from ....utils.ai_generation_helpers import fetch_players, parse_json_report, insert_report

client = set_openai()

select_sql = """
SELECT p.player_uid, p.full_name, hspr.class_year, hspr.school_name FROM players AS p
INNER JOIN high_school_player_rankings AS hspr ON hspr.player_uid = p.player_uid
WHERE p.class_year IS NOT NULL
AND hspr.source = (
    SELECT source
    FROM high_school_player_rankings h2
    WHERE h2.player_uid = p.player_uid
    ORDER BY FIELD(h2.source, '247sports', 'espn', 'rivals')  -- priority order
    LIMIT 1
);
"""

select_sql_per_player = """
SELECT p.full_name, hspr.player_rank, hspr.player_grade, hspr.stars, hspr.source
FROM high_school_player_rankings AS hspr
INNER JOIN players AS p ON hspr.player_uid = p.player_uid
WHERE p.full_name = %s AND p.class_year IS NOT NULL;
"""

insert_sql = """
INSERT INTO ai_generated_high_school_evaluations
    (player_uid, stars, rating, strengths, weaknesses, ai_analysis)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    stars = VALUES(stars),
    rating = VALUES(rating),
    strengths = VALUES(strengths),
    weaknesses = VALUES(weaknesses),
    ai_analysis = VALUES(ai_analysis);
"""

def fetch_player_rankings(player_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(select_sql_per_player, (player_name,))
    rankings = cursor.fetchall()
    cursor.close()
    conn.close()
    return rankings
        
def get_scouting_report_with_retry(player_name, class_year, high_school, ranking_info, retries=3):
    ranking_info_json = json.dumps(ranking_info, indent=2)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content(ranking_info_json, player_name, high_school, class_year)}
    ]

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-search-preview",
                messages=messages,
            )
            return response.choices[0].message.content
        except Exception as e:
            err_str = str(e).lower()
            if ("rate limit" in err_str or "429" in err_str) and attempt < retries - 1:
                wait = 2 ** attempt
                print(f"Rate limited. Retrying {player_name} in {wait}s...")
                time.sleep(wait)
            else:
                raise

def ai_report_exists(player_uid, class_year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM ai_generated_high_school_evaluations WHERE player_uid = %s LIMIT 1", (player_uid,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    
    if (exists and int(class_year) <= datetime.now().year):
        return True
    
    return exists

def safe_process_player(player):
    player_uid = player['player_uid']
    class_year = player['class_year']
    high_school = player['school_name']
    player_name = player['full_name']

    # Skip if AI report already exists for this player
    if ai_report_exists(player_uid, class_year):
        print(f"Skipping {player_name}, AI report already exists.")
        return player_name, True

    # Fetch the player's ranking info for context
    ranking_info = fetch_player_rankings(player_name)

    try:
        raw = get_scouting_report_with_retry(player_name, class_year, high_school, ranking_info)

        parsed = parse_json_report(raw)
        if not parsed:
            print(f"Failed to parse JSON for {player_name}")
            return player_name, False

        insert_report(
            player_uid=player_uid,
            stars=parsed.get('stars', None),
            rating=parsed.get('rating', None),
            strengths=parsed.get('strengths', []),
            weaknesses=parsed.get('weaknesses', []),
            ai_analysis=parsed.get('aiAnalysis', ''),
            insert_sql=insert_sql
        )
        print(f"Inserted report for {player_name}")
        return player_name, True
    except Exception as e:
        print(f"Error processing {player_name}: {e}")
        return player_name, False

def main():
    players = fetch_players(select_sql)
    print(f"Fetched {len(players)} players from DB")

    MAX_WORKERS = 5
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(safe_process_player, player) for player in players]

        for future in concurrent.futures.as_completed(futures):
            player_name, success = future.result()
            if not success:
                print(f"Failed for player: {player_name}")

if __name__ == "__main__":
    main()