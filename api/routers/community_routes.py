from fastapi import APIRouter, HTTPException
from core.db import get_db_connection
from typing import List, Dict, Any
from pydantic import BaseModel

import json

router = APIRouter()

class Lineup(BaseModel):
    lineup_id: int
    user_id: int
    mode: str
    players: Dict[str, Any]   # JSON field
    scouting_report: Dict[str, Any]  # JSON field

@router.get("/lineups", response_model=List[Lineup])
def get_player_lineups():
    select_sql = "SELECT * FROM lineups;"
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(select_sql)
        rows = cursor.fetchall()

        for row in rows:
            if isinstance(row.get("players"), str):
                row["players"] = json.loads(row["players"])
            if isinstance(row.get("scouting_report"), str):
                row["scouting_report"] = json.loads(row["scouting_report"])

        return rows

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
        

@router.get("/lineups/{lineup_id}", response_model=Dict)
def get_player_lineup(lineup_id: int):
    select_sql = """
        SELECT * FROM lineups WHERE lineup_id = %s;
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(select_sql, (lineup_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Lineup not found")

        # Deserialize JSON
        if "players" in row and row["players"]:
            row["players"] = json.loads(row["players"])
        if "scouting_report" in row and row["scouting_report"]:
            row["scouting_report"] = json.loads(row["scouting_report"])

        # Replace player IDs with full_name from players table
        player_ids = [int(pid) for pid in row["players"].values()]
        if player_ids:
            format_strings = ",".join(["%s"] * len(player_ids))
            cursor.execute(
                f"SELECT player_uid, full_name FROM players WHERE player_uid IN ({format_strings})",
                tuple(player_ids),
            )
            results = cursor.fetchall()
            id_to_name = {r["player_uid"]: r["full_name"] for r in results}

            row["players"] = {
                pos: id_to_name.get(int(pid), f"Unknown Player {pid}")
                for pos, pid in row["players"].items()
            }

        return row

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()

@router.get("/hot-takes")
def get_hot_takes():
    """
    Fetch all hot takes with user info attached.
    """
    select_sql = """
        SELECT
            ht.take_id,
            ht.content,
            ht.truthfulness_score,
            ht.ai_insight,
            ht.created_at,
            u.username,
            u.email
        FROM hot_takes ht
        JOIN users u ON ht.user_id = u.user_id
        ORDER BY ht.created_at DESC;
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(select_sql)
        rows = cursor.fetchall()

        return {"hot_takes": rows}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hot takes: {str(e)}")
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()


@router.get("/hot-takes/{take_id}", response_model=Dict)
def get_hot_take(take_id: int):
    """
    Fetch a single hot take by ID, with user info.
    """
    select_sql = """
        SELECT
            ht.take_id,
            ht.content,
            ht.truthfulness_score,
            ht.ai_insight,
            ht.created_at,
            u.username,
            u.email
        FROM hot_takes ht
        JOIN users u ON ht.user_id = u.user_id
        WHERE ht.take_id = %s;
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        cursor.execute(select_sql, (take_id,))
        row = cursor.fetchone()

        if not row:
            raise HTTPException(status_code=404, detail="Hot take not found")

        return row
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hot take: {str(e)}")
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()