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

        # Convert JSON fields from string to dict
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
