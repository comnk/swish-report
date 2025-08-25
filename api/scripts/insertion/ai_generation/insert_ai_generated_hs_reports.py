import time
import json
import re
import concurrent.futures

from datetime import datetime
from ....core.db import get_db_connection
from ....core.config import set_openai
from ....utils.ai_prompts import SYSTEM_PROMPT, user_content

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

def clean_markdown_json(text):
    # Remove ```json ... ``` or ``` ... ``` fences if present
    fenced_code = re.search(r"```json\s*([\s\S]*?)```", text)
    if fenced_code:
        return fenced_code.group(1).strip()
    fenced_code = re.search(r"```[\s\S]*?```", text)
    if fenced_code:
        return fenced_code.group(0).replace("```", "").strip()
    return text.strip()

def fix_ai_analysis_quotes(text):
    key = '"aiAnalysis":'
    idx = text.find(key)
    if idx == -1:
        return text

    start_quote = text.find('"', idx + len(key))
    if start_quote == -1:
        return text

    result = []
    i = start_quote + 1
    while i < len(text):
        ch = text[i]
        if ch == '"' and text[i-1] != '\\':
            # Look ahead to see if this ends the value
            j = i + 1
            while j < len(text) and text[j] in " \n\r\t":
                j += 1
            if j < len(text) and text[j] in ",}":
                break  # closing quote
            result.append('\\"')
            i += 1
            continue
        result.append(ch)
        i += 1

    fixed_value = ''.join(result)
    return text[:start_quote+1] + fixed_value + text[i:]

def parse_json_report(text):
    cleaned = extract_first_json_object(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        fixed = fix_ai_analysis_quotes(cleaned)
        try:
            return json.loads(fixed)
        except Exception as e2:
            print(f"JSON parse error even after cleanup and fix: {e2}\nOriginal text:\n{text}")
            return None

def extract_first_json_object(text):
    # First, try to find a code block
    fenced_code = re.search(r"```json\s*([\s\S]*?)```", text)
    if fenced_code:
        text = fenced_code.group(1).strip()
    else:
        fenced_code = re.search(r"```([\s\S]*?)```", text)
        if fenced_code:
            text = fenced_code.group(1).strip()

    start = text.find('{')
    if start == -1:
        return text
    brace_count = 0
    for i, ch in enumerate(text[start:], start=start):
        if ch == '{':
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
            if brace_count == 0:
                return text[start:i+1]
    return text[start:]
        
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

def insert_report(player_uid, stars, rating, strengths, weaknesses, ai_analysis):
    conn = get_db_connection()
    cursor = conn.cursor()
    strengths_json = json.dumps(strengths)
    weaknesses_json = json.dumps(weaknesses)
    cursor.execute(insert_sql, (player_uid, stars, rating, strengths_json, weaknesses_json, ai_analysis))
    conn.commit()
    cursor.close()
    conn.close()

def ai_report_exists(player_uid, class_year):
    # fix Jacob Wilkins later because why
    
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