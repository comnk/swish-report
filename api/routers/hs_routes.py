from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from core.db import get_db_connection
from utils.hs_helpers import get_youtube_videos, high_school_highlights
from utils.highlight_reel_helpers import download_youtube_video, extract_highlight_clips, save_highlight_clips, make_final_reel, cleanup_files
from scripts.insertion.high_school.insert_missing_hs_player import insert_hs_player, create_hs_player_analysis
from typing import List, Dict, Optional

import json, os

router = APIRouter()

CACHE_EXPIRY_HOURS = 6

DOWNLOAD_DIR = "downloads"
TEMP_CLIP_DIR = "highlights"
FINAL_DIR = "final_reels"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_CLIP_DIR, exist_ok=True)
os.makedirs(FINAL_DIR, exist_ok=True)

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

@router.get("/prospects/{player_id}/videos")
def get_high_school_player_videos(player_id: int):
    select_sql = """
        SELECT full_name, class_year
        FROM players
        WHERE player_uid = %s
        AND class_year IS NOT NULL;
    """
    select_cache_sql = "SELECT videos_json, last_updated FROM player_videos_cache WHERE player_uid = %s"
    upsert_cache_sql = """
        INSERT INTO player_videos_cache (player_uid, videos_json)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE videos_json = VALUES(videos_json)
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
            videos = cached["videos_json"]
            if isinstance(videos, str):
                try:
                    videos = json.loads(videos)
                except json.JSONDecodeError:
                    videos = []
            return videos
        
        # Step 3: No cache -> fetch now
        youtube_videos = get_youtube_videos(
            full_name=row["full_name"],
            class_year=row["class_year"]
        )

        # Step 4: Save to cache
        cursor.execute(upsert_cache_sql, (player_id, json.dumps(youtube_videos)))
        conn.commit()

        return youtube_videos
        
    except Exception as e:
        # safer: log the real error internally, but keep response generic
        print(f"Error fetching videos for player {player_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            

@router.get("/prospects/{player_id}/reel")
def get_high_school_player_reel(player_id: int, background_tasks: BackgroundTasks):
    select_sql = """
        SELECT full_name, class_year
        FROM players
        WHERE player_uid = %s
        AND class_year IS NOT NULL;
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Step 1: Get player info
        cursor.execute(select_sql, (player_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Player not found")

        full_name = row["full_name"]
        class_year = row["class_year"]

        # Step 2: Fetch YouTube videos
        urls = high_school_highlights(full_name, class_year)
        if not urls:
            raise HTTPException(status_code=404, detail="No videos found for this player.")

        intermediate_clips = []

        # Step 3: Process each video
        for url in urls:
            video_path = download_youtube_video(url, output_dir=DOWNLOAD_DIR)
            segments = extract_highlight_clips(video_path, top_k=3)
            clips = save_highlight_clips(video_path, segments, output_dir=TEMP_CLIP_DIR)
            intermediate_clips.extend(clips)

            # Cleanup full downloaded video in background
            background_tasks.add_task(cleanup_files, [video_path])

        if not intermediate_clips:
            raise HTTPException(status_code=404, detail="No highlight clips could be generated.")

        # Step 4: Create final highlight reel
        final_filename = f"{full_name.replace(' ', '_')}_highlight.mp4"
        final_path = os.path.join(FINAL_DIR, final_filename)
        make_final_reel(intermediate_clips, output_path=final_path, cleanup=True)

        # Step 5: Return final video
        return FileResponse(final_path, filename=final_filename, media_type="video/mp4")

    except Exception as e:
        import traceback
        print("🔥 Highlight reel error:", str(e))
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error generating highlight reel")

    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()


def refresh_player_videos(player_id: int, full_name: str, class_year: int):
    """Background task to refresh YouTube videos cache."""
    upsert_cache_sql = """
        INSERT INTO player_videos_cache (player_uid, videos_json)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE videos_json = VALUES(videos_json)
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        youtube_videos = get_youtube_videos(full_name=full_name, class_year=class_year)

        cursor.execute(upsert_cache_sql, (player_id, json.dumps(youtube_videos)))
        conn.commit()

    except Exception as e:
        print(f"Error refreshing player {player_id} videos: {e}")

    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()


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
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")