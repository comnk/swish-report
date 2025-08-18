from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

from ..core.db import get_db_connection
from ..utils.helpers import parse_json_list
import json

router = APIRouter()


@router.get("/players", response_model=List[dict])
def get_nba_prospects():
    cnx = get_db_connection()
    cursor = cnx.cursor()

    # Fixed SQL (removed trailing comma) and selected all relevant fields
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
            nba.accolades
        FROM players AS p
        INNER JOIN nba_player_info AS nba ON p.player_uid = nba.player_uid
        WHERE p.current_level = 'NBA';
    """)

    players = cursor.fetchall()
    cursor.close()
    cnx.close()

    # Map SQL result to frontend expected keys
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
        })
    
    print(result[0]["team_names"])

    return result