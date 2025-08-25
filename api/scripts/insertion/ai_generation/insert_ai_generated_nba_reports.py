import json
import time
import concurrent.futures

from api.core.config import set_gemini_key
from ....utils.ai_prompts import SYSTEM_PROMPT, nba_player_content
from ....utils.ai_generation_helpers import fetch_players, nba_ai_report_exists, parse_json_report, insert_report

client = set_gemini_key()

select_sql = """
SELECT * FROM players INNER JOIN nba_player_info AS nba ON players.player_uid=nba.player_uid WHERE current_level="NBA" AND is_active=1
"""

insert_sql = """
INSERT INTO ai_generated_nba_evaluations
    (player_uid, stars, rating, strengths, weaknesses, ai_analysis)
VALUES (%s, %s, %s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    stars = VALUES(stars),
    rating = VALUES(rating),
    strengths = VALUES(strengths),
    weaknesses = VALUES(weaknesses),
    ai_analysis = VALUES(ai_analysis);
"""

def get_scouting_report_with_retry(player_name, retries=3):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": nba_player_content(player_name)}
    ]

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gemini-2.5-flash",
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

def safe_process_player(player):
    player_uid = player['player_uid']
    player_name = player['full_name']

    # Skip if AI report already exists for this player
    if nba_ai_report_exists(player_uid):
        print(f"Skipping {player_name}, AI report already exists.")
        return player_name, True

    try:
        raw = get_scouting_report_with_retry(player_name)

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