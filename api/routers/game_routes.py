from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.db import get_db_connection
from scripts.insertion.ai_generation.insert_nba_lineup_analysis import create_nba_lineup_analysis
from random import randint
from typing import Dict, Optional, Literal

import json

router = APIRouter()

class LineupSubmission(BaseModel):
    mode: Literal["starting5", "rotation"]
    lineup: Dict[str, Optional[str]]  # positions mapped to player names or null
    user_id: str

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
    """
    Takes a lineup submission, generates AI analysis, and inserts into the DB.
    """
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Get numeric user_id from email
        cursor.execute("SELECT user_id FROM users WHERE email = %s", (submission.user_id,))
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user_row["user_id"]

        # Extract player IDs
        player_ids = list(submission.lineup.values())
        placeholders = ",".join(["%s"] * len(player_ids))

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

        if not results:
            raise HTTPException(status_code=404, detail="No players found for lineup")

        # Generate AI analysis
        analysis_json = await create_nba_lineup_analysis(submission.mode, results)
        print(analysis_json)

        # Insert lineup into DB
        insert_sql = """
            INSERT INTO lineups (user_id, mode, players, scouting_report)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(
            insert_sql,
            (
                user_id,
                submission.mode,
                json.dumps(submission.lineup),
                json.dumps(analysis_json),
            ),
        )
        conn.commit()
        lineup_id = cursor.lastrowid

        return {
            "message": "Lineup submitted successfully",
            "lineup_id": lineup_id,
            "scouting_report": analysis_json,
            "players": results,
        }

    finally:
        cursor.close()
        conn.close()
