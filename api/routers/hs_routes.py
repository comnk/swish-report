from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..core.db import get_db_connection
from ..utils.hs_helpers import get_youtube_videos
from ..scripts.insertion.insert_missing_hs_player import insert_hs_player, create_hs_player_analysis
from typing import List, Dict, Optional
import json

router = APIRouter()

class PlayerSubmission(BaseModel):
    name: str
    espn_link: Optional[str] = None
    sports247_link: Optional[str] = None
    rivals_link: Optional[str] = None

@router.get("/prospects", response_model=List[Dict])
def get_highschool_prospects():
    select_sql = """
    SELECT
        p.player_uid,
        p.full_name,
        p.class_year,
        hspr.position,
        hspr.school_name,
        hspr.height,
        COALESCE(ai.stars, 4) AS stars,
        COALESCE(ai.rating, 85) AS overallRating,
        COALESCE(ai.strengths, JSON_ARRAY('Scoring', 'Athleticism', 'Court Vision')) AS strengths,
        COALESCE(ai.weaknesses, JSON_ARRAY('Defense', 'Consistency')) AS weaknesses,
        COALESCE(ai.ai_analysis, 'A highly talented high school prospect with excellent scoring ability and strong athletic traits.') AS aiAnalysis
    FROM players AS p
    INNER JOIN high_school_player_rankings AS hspr
        ON hspr.player_uid = p.player_uid
    LEFT JOIN ai_generated_high_school_evaluations AS ai
        ON ai.player_uid = p.player_uid
    WHERE p.class_year IS NOT NULL
    AND hspr.source = (
        SELECT source
        FROM high_school_player_rankings h2
        WHERE h2.player_uid = p.player_uid
        ORDER BY FIELD(h2.source, '247sports', 'espn', 'rivals')  -- priority order
        LIMIT 1
    );
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(select_sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Parse JSON fields
        for row in rows:
            for field, default in [("strengths", ["Scoring", "Athleticism", "Court Vision"]),
                ("weaknesses", ["Defense", "Consistency"])]:
                if isinstance(row[field], str):
                    try:
                        row[field] = json.loads(row[field])
                    except json.JSONDecodeError:
                        row[field] = default

            # Rename player_uid to id for frontend compatibility
            row["id"] = row.pop("player_uid")

        return rows

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prospects/{player_id}", response_model=Dict)
def get_highschool_player(player_id: int):
    select_sql = """
    SELECT
        p.player_uid,
        p.full_name,
        p.class_year,
        hspr.position,
        hspr.school_name,
        hspr.height,
        hspr.weight,
        COALESCE(ai.stars, 4) AS stars,
        COALESCE(ai.rating, 85) AS overallRating,
        COALESCE(ai.strengths, JSON_ARRAY('Scoring', 'Athleticism', 'Court Vision')) AS strengths,
        COALESCE(ai.weaknesses, JSON_ARRAY('Defense', 'Consistency')) AS weaknesses,
        COALESCE(ai.ai_analysis, 'A highly talented high school prospect with excellent scoring ability and strong athletic traits.') AS aiAnalysis
    FROM players AS p
    INNER JOIN high_school_player_rankings AS hspr ON hspr.player_uid = p.player_uid
    LEFT JOIN ai_generated_high_school_evaluations AS ai ON ai.player_uid = p.player_uid
    WHERE p.player_uid = %s AND p.class_year IS NOT NULL;
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)  # <-- key fix
        cursor.execute(select_sql, (player_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Player not found")

        # Ensure JSON fields are Python lists
        for field, default in [
            ("strengths", ["Scoring", "Athleticism", "Court Vision"]),
            ("weaknesses", ["Defense", "Consistency"])
        ]:
            value = row.get(field)
            if isinstance(value, str):
                try:
                    row[field] = json.loads(value)
                except json.JSONDecodeError:
                    row[field] = default
            elif value is None:
                row[field] = default

        # Rename player_uid to id
        row["id"] = row.pop("player_uid")
        row["school"] = row.pop("school_name")
        row["class"] = row.pop("class_year")
        
        return row

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@router.get("/prospects/{player_id}/videos", response_model=List[str])
def get_high_school_player_videos(player_id: int):
    select_sql = """
    SELECT full_name, class_year
    FROM players
    WHERE player_uid = %s
    AND class_year IS NOT NULL;
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(select_sql, (player_id,))
        row = cursor.fetchone()
        
        youtube_videos = get_youtube_videos(row["full_name"], row["class_year"])
        return youtube_videos
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@router.post("/prospects/submit-player", response_model=Dict)
async def submit_high_school_player(submission: PlayerSubmission):
    try:
        player_info = await insert_hs_player(
            submission.name,
            submission.sports247_link,
            submission.espn_link,
            submission.rivals_link
        )
        
        analysis_info = await create_hs_player_analysis(player_info["player_uid"])
        
        if analysis_info.get("status") != "success":
            return {
                "status": "fail",
                "message": f"Player analysis failed for {submission.name}.",
                "player_uid": player_info["player_uid"]
            }
        
        return {
            "status": "success",
            "message": f"{submission.name} submitted successfully.",
            "player_uid": player_info["player_uid"]
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())  # log full error
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")