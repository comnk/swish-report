import os
import time
import json
import re
import concurrent.futures
import mysql.connector
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
dotenv_path = '../.env'
load_dotenv(dotenv_path)

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
OPENAI_KEY = os.getenv('OPENAI_KEY')
if not OPENAI_KEY:
    raise ValueError("OPENAI_KEY not found")

client = OpenAI(api_key=OPENAI_KEY)

select_sql = """
SELECT p.player_uid, p.full_name FROM players AS p
INNER JOIN high_school_player_rankings AS hspr ON hspr.player_uid = p.player_uid
WHERE hspr.source = '247sports';
"""

select_sql_per_player = """
SELECT p.full_name, hspr.player_rank, hspr.player_grade, hspr.stars, hspr.source
FROM high_school_player_rankings AS hspr
INNER JOIN players AS p ON hspr.player_uid = p.player_uid
WHERE p.full_name = %s;
"""

insert_sql = """
INSERT INTO ai_generated_high_school_evaluations
    (player_id, strengths, weaknesses, ai_analysis)
VALUES (%s, %s, %s, %s)
ON DUPLICATE KEY UPDATE
    strengths = VALUES(strengths),
    weaknesses = VALUES(weaknesses),
    ai_analysis = VALUES(ai_analysis);
"""

def get_db_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database='swish_report',
        autocommit=True
    )

def fetch_players():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(select_sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def fetch_player_rankings(player_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(select_sql_per_player, (player_name,))
    rankings = cursor.fetchall()
    cursor.close()
    conn.close()
    return rankings

system_prompt = """
You are a basketball recruiting expert that scouts high school, college, and NBA talent.

When the user asks for a scouting report, you must return a valid JSON object in this exact format:

{
    "rating": 85,
    "strengths": ["list", "of", "strengths"] (list where each strength is at most 2 word tags to use in the frontend UI),
    "weaknesses": ["list", "of", "weaknesses"] (list where each strength is at most 2 word tags to use in the frontend UI),
    "aiAnalysis": "your detailed analysis of the player"
}

Output only JSON, no extra text.
"""

def clean_markdown_json(text):
    # Remove ```json ... ``` or ``` ... ``` fences if present
    fenced_code = re.search(r"```json\s*([\s\S]*?)```", text)
    if fenced_code:
        return fenced_code.group(1).strip()
    fenced_code = re.search(r"```[\s\S]*?```", text)
    if fenced_code:
        return fenced_code.group(0).replace("```", "").strip()
    return text.strip()

def parse_json_report(text):
    cleaned_text = clean_markdown_json(text)
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        # Try replacing single quotes and removing trailing commas
        fallback_text = cleaned_text.replace("'", '"')
        if fallback_text.endswith(","):
            fallback_text = fallback_text[:-1]
        try:
            return json.loads(fallback_text)
        except Exception:
            print(f"JSON parse error even after cleanup: {e}\nOriginal text:\n{text}")
            return None

def get_scouting_report_with_retry(player_name, ranking_info, retries=3):
    ranking_info_json = json.dumps(ranking_info, indent=2)
    user_content = f"""Here is the ranking info for {player_name}:

{ranking_info_json}

Please give me a scouting report for {player_name} in the JSON format I requested."""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content}
    ]

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini-search-preview",
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

def insert_report(player_id, strengths, weaknesses, ai_analysis):
    conn = get_db_connection()
    cursor = conn.cursor()
    strengths_json = json.dumps(strengths)
    weaknesses_json = json.dumps(weaknesses)
    cursor.execute(insert_sql, (player_id, strengths_json, weaknesses_json, ai_analysis))
    cursor.close()
    conn.close()

def safe_process_player(player):
    player_id = player['player_uid']
    player_name = player['full_name']

    # Fetch the player's ranking info for context
    ranking_info = fetch_player_rankings(player_name)

    try:
        raw = get_scouting_report_with_retry(player_name, ranking_info)

        parsed = parse_json_report(raw)
        if not parsed:
            print(f"Failed to parse JSON for {player_name}")
            return player_name, False

        insert_report(
            player_id=player_id,
            strengths=parsed.get('strengths', []),
            weaknesses=parsed.get('weaknesses', []),
            ai_analysis=parsed.get('aiAnalysis', '')
        )
        print(f"Inserted report for {player_name}")
        return player_name, True
    except Exception as e:
        print(f"Error processing {player_name}: {e}")
        return player_name, False

def main():
    players = fetch_players()
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