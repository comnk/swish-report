import json

from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime, timedelta
from typing import List

from core.db import get_db_connection
from utils.nba_helpers import get_nba_youtube_videos
from utils.helpers import parse_json_list

router = APIRouter()

CACHE_EXPIRY_HOURS = 6

@router.get("/players", response_model=List[dict])
def get_nba_prospects():
    # Fixed SQL (removed trailing comma) and selected all relevant fields
    cnx = get_db_connection()
    cursor = cnx.cursor()
    cursor.execute("""
        SELECT
            p.player_uid,
            p.full_name,
            nba.position,
            nba.height,
            nba.weight,
            nba.years_pro,
            nba.teams,
            nba.draft_year,
            nba.draft_round,
            nba.draft_pick,
            nba.colleges,
            nba.high_schools,
            nba.is_active,
            nba.accolades,
            COALESCE(ai.stars, 4) AS stars,
            COALESCE(ai.rating, 85) AS overallRating,
            COALESCE(ai.strengths, JSON_ARRAY('Scoring', 'Athleticism', 'Court Vision')) AS strengths,
            COALESCE(ai.weaknesses, JSON_ARRAY('Defense', 'Consistency')) AS weaknesses,
            COALESCE(ai.ai_analysis, 'A highly talented high school prospect with excellent scoring ability and strong athletic traits.') AS aiAnalysis
        FROM players AS p
        INNER JOIN nba_player_info AS nba ON p.player_uid = nba.player_uid
        LEFT JOIN ai_generated_nba_evaluations AS ai ON ai.player_uid = p.player_uid
        WHERE p.current_level = 'NBA';
    """)

    players = cursor.fetchall()
    cursor.close()
    cnx.close()

    result = []
    for p in players:
        result.append({
            "player_uid": p[0] if p[0] is not None else -1,
            "full_name": p[1],
            "position": p[2],
            "height": p[3],
            "weight": p[4],
            "years_pro": p[5] or 0,
            "team_names": parse_json_list(p[6]),
            "draft_year": p[7],
            "draft_round": p[8],
            "draft_pick": p[9],
            "colleges": parse_json_list(p[10]),
            "high_schools": parse_json_list(p[11]),
            "is_active": bool(p[12]),
            "accolades": parse_json_list(p[13]),
            "stars": p[14],
            "overallRating": p[15],
            "strengths": parse_json_list(p[16]),
            "weaknesses": parse_json_list(p[17]),
            "aiAnalysis": p[18],
        })

    return result

@router.get("/players/{player_id}")
def get_nba_player(player_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)  # <-- key fix
        cursor.execute("""
            SELECT
                p.player_uid,
                p.full_name,
                nba.position,
                nba.height,
                nba.weight,
                nba.years_pro,
                nba.teams,
                nba.draft_year,
                nba.draft_round,
                nba.draft_pick,
                nba.colleges,
                nba.high_schools,
                nba.is_active,
                nba.accolades,
                COALESCE(ai.stars, 4) AS stars,
                COALESCE(ai.rating, 85) AS overallRating,
                COALESCE(ai.strengths, JSON_ARRAY('Scoring', 'Athleticism', 'Court Vision')) AS strengths,
                COALESCE(ai.weaknesses, JSON_ARRAY('Defense', 'Consistency')) AS weaknesses,
                COALESCE(ai.ai_analysis, 'A highly talented high school prospect with excellent scoring ability and strong athletic traits.') AS aiAnalysis
            FROM players AS p
            INNER JOIN nba_player_info AS nba ON p.player_uid = nba.player_uid
            LEFT JOIN ai_generated_nba_evaluations AS ai ON ai.player_uid = p.player_uid
            WHERE p.current_level = 'NBA' AND p.player_uid=%s;
        """, (player_id,))
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
        row["team_names"] = parse_json_list(row.pop("teams"))
        
        return row

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

@router.get("/players/{player_id}/videos")
def get_nba_player_videos(player_id: int, background_tasks: BackgroundTasks):
    # SQL to get player info
    select_sql = """
    SELECT full_name, draft_year
    FROM players
    WHERE player_uid = %s
    """
    # SQL to get cached videos
    select_cache_sql = """
    SELECT videos_json, last_updated
    FROM player_videos_cache
    WHERE player_uid = %s
    """
    # SQL to insert/update cache
    upsert_cache_sql = """
    REPLACE INTO player_videos_cache (player_uid, videos_json, last_updated)
    VALUES (%s, %s, NOW())
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 1: Get player info
        cursor.execute(select_sql, (player_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Player not found")

        # Step 2: Check cache
        cursor.execute(select_cache_sql, (player_id,))
        cached = cursor.fetchone()

        if cached:
            last_updated = cached["last_updated"]
            is_stale = (datetime.now() - last_updated) > timedelta(hours=CACHE_EXPIRY_HOURS)

            # If stale, refresh in background but return cached data immediately
            if is_stale:
                background_tasks.add_task(
                    refresh_player_videos, player_id, row["full_name"], row["draft_year"]
                )

            return json.loads(cached["videos_json"])

        # Step 3: No cache -> fetch now (blocking)
        youtube_videos = get_nba_youtube_videos(
            full_name=row["full_name"],
            start_year=row["draft_year"]
        )

        # Step 4: Save to cache
        cursor.execute(upsert_cache_sql, (player_id, json.dumps(youtube_videos)))
        conn.commit()

        return youtube_videos

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


def refresh_player_videos(player_id: int, full_name: str, draft_year: int):
    """Background task to refresh YouTube videos cache."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        youtube_videos = get_nba_youtube_videos(full_name=full_name, start_year=draft_year)

        cursor.execute(
            "REPLACE INTO player_videos_cache (player_uid, videos_json, last_updated) VALUES (%s, %s, NOW())",
            (player_id, json.dumps(youtube_videos))
        )
        conn.commit()
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()