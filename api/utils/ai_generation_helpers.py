import re
import json

from core.db import get_db_connection
from datetime import datetime

def fetch_players(select_sql):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(select_sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def hs_ai_report_exists(player_uid, class_year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM ai_generated_high_school_evaluations WHERE player_uid = %s LIMIT 1", (player_uid,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    
    if (exists and int(class_year) <= datetime.now().year):
        return True
    
    return exists

def nba_ai_report_exists(player_uid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM ai_generated_nba_evaluations WHERE player_uid = %s LIMIT 1", (player_uid,))
    exists = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    
    if (exists):
        return True
    
    return exists

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

def insert_report(player_uid, stars, rating, strengths, weaknesses, ai_analysis, insert_sql):
    conn = get_db_connection()
    cursor = conn.cursor()
    strengths_json = json.dumps(strengths)
    weaknesses_json = json.dumps(weaknesses)
    cursor.execute(insert_sql, (player_uid, stars, rating, strengths_json, weaknesses_json, ai_analysis))
    conn.commit()
    cursor.close()
    conn.close()