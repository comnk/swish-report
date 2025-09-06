from fastapi import APIRouter
from pydantic import BaseModel
from core.db import get_db_connection
from scripts.insertion.ai_generation.insert_nba_lineup_analysis import create_nba_lineup_analysis
from random import randint

router = APIRouter()

class LineupSubmission(BaseModel):
    mode: str
    lineup: dict

@router.get("/poeltl/get-player")
def poeltl_get_daily_player():
    select_sql = """
    SELECT p.full_name, nba.position, nba.height, nba.weight, nba.years_pro, nba.teams, nba.accolades FROM players AS p INNER JOIN nba_player_info AS nba ON p.player_uid=nba.player_uid WHERE current_level='NBA';
    """
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(select_sql)
    
    rows = cursor.fetchall()
    
    random_index = randint(0, len(rows) - 1)
    random_player = rows[random_index]
    print(random_player)
    return random_player


@router.post("/lineup-builder/submit-lineup", response_model=dict)
async def get_lineup_analysis(submission: LineupSubmission):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # return rows as dicts

    # Prepare player_ids
    player_ids = list(submission.lineup.values())
    placeholders = ",".join(["%s"] * len(player_ids))

    # Safe query with aliases
    select_sql = f"""
        SELECT
            p.player_uid,
            p.full_name,
            nba.position,
            nba.height,
            nba.weight,
            nba.years_pro,
            nba.accolades,
            ai.stars,
            ai.rating,
            ai.strengths,
            ai.weaknesses,
            ai.ai_analysis
        FROM players AS p
        INNER JOIN nba_player_info AS nba
            ON p.player_uid = nba.player_uid
        INNER JOIN ai_generated_nba_evaluations AS ai
            ON p.player_uid = ai.player_uid
        WHERE p.player_uid IN ({placeholders})
    """

    cursor.execute(select_sql, player_ids)
    results = cursor.fetchall()

    analysis_info = await create_nba_lineup_analysis(submission.mode, results)
    print(analysis_info)
    
    cursor.close()
    conn.close()

    return {
        "message": "AI analysis placeholder",
        "players_fetched": len(results),
        "players": results,   # now you can return actual player data
    }
