from api.core.db import get_db_connection
from api.scripts.scraping.fetch_individual_hs_player import fetch_247_data, fetch_espn_data, fetch_rivals_data
from api.scripts.insertion.insert_ai_generated_hs_reports import ai_report_exists, parse_json_report, fetch_player_rankings, insert_report

from api.core.config import set_openai
from api.utils.ai_prompts import SYSTEM_PROMPT, user_content

import asyncio
import json

async def insert_hs_player(full_name, sports247_link, espn_link, rivals_link):
    cnx = get_db_connection()
    cursor = cnx.cursor()

    insert_rank_sql = """
    INSERT INTO high_school_player_rankings
    (player_uid, source, class_year, player_rank, player_grade, stars, link, position, height, weight,
    school_name, city, state, location_type, is_finalized)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        player_rank   = VALUES(player_rank),
        player_grade  = VALUES(player_grade),
        stars         = VALUES(stars),
        link          = VALUES(link),
        position      = VALUES(position),
        height        = VALUES(height),
        weight        = VALUES(weight),
        school_name   = VALUES(school_name),
        city          = VALUES(city),
        state         = VALUES(state),
        location_type = VALUES(location_type),
        is_finalized  = VALUES(is_finalized),
        last_updated  = CURRENT_TIMESTAMP;
    """

    insert_player_sql = """
    INSERT INTO players (full_name, class_year, current_level)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE current_level = VALUES(current_level), class_year = VALUES(class_year);
    """

    # Fetch ranking data concurrently
    ranking_247, ranking_espn, ranking_rivals = await asyncio.gather(
        fetch_247_data(sports247_link),
        fetch_espn_data(espn_link),
        fetch_rivals_data(rivals_link)
    )

    # Insert/update player first
    class_year = ranking_247[1] or ranking_espn[1] or ranking_rivals[1]  # pick whichever is available
    cursor.execute(insert_player_sql, (full_name, class_year, "HS"))

    # Get the player_uid (assuming it's AUTO_INCREMENT primary key)
    cursor.execute("SELECT player_uid FROM players WHERE full_name = %s AND class_year = %s", (full_name,class_year))
    player_uid = cursor.fetchone()[0]

    # Insert/update each ranking (prepend player_uid)
    for ranking in [ranking_247, ranking_espn, ranking_rivals]:
        if ranking:  # only insert if data exists
            cursor.execute(insert_rank_sql, (player_uid, *ranking))

    cnx.commit()
    cursor.close()
    cnx.close()

    return {"status": "success", "player": full_name, "player_uid": player_uid}

async def create_hs_player_analysis(player_uid):
    client = set_openai()
    cnx = get_db_connection()
    cursor = cnx.cursor()
    
    select_sql = """
    SELECT p.player_uid, p.full_name, hspr.class_year, hspr.school_name FROM players AS p
    INNER JOIN high_school_player_rankings AS hspr ON hspr.player_uid = p.player_uid
    WHERE p.player_uid=%s AND p.class_year IS NOT NULL LIMIT 1;
    """
    
    cursor.execute(select_sql, (player_uid,))
    player = cursor.fetchone()
    
    player_name = player[1]
    class_year = player[2]
    high_school = player[3]
    
    if (ai_report_exists(player_uid, class_year)):
        return {"status": "fail", "player": player_name, "player_uid": player_uid}
    
    ranking_info = fetch_player_rankings(player_name)
    ranking_info_json = json.dumps(ranking_info, indent=2)
    
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content(ranking_info_json, player_name, high_school, class_year)}
    ]
    
    response = client.chat.completions.create(
        model="gpt-4o-search-preview",
        messages=messages,
    )
    
    print(response.choices[0].message.content)
    
    parsed = parse_json_report(response.choices[0].message.content)
    if not parsed:
        return {"status": "fail", "reason": "failed to parse AI response", "player": player_name}

    insert_report(
        player_uid=player_uid,
        stars=parsed.get('stars', None),
        rating=parsed.get('rating', None),
        strengths=parsed.get('strengths', []),
        weaknesses=parsed.get('weaknesses', []),
        ai_analysis=parsed.get('aiAnalysis', '')
    )
    
    print(f"Inserted report for {player_name}")
    
    cnx.commit()
    cursor.close()
    cnx.close()
    
    return {"status": "success", "player": player_name, "player_uid": player_uid}