from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

from ..core.db import get_db_connection

router = APIRouter()


@router.get("/players", response_model=List[dict])
def get_nba_prospects():
    cnx = get_db_connection()
    cursor = cnx.cursor()
    
    cursor.execute("""
        SELECT p.full_name, nba_player_info.position, nba_player_info.height
        FROM players AS p INNER JOIN nba_player_info ON p.player_uid=nba_player_info.player_uid WHERE current_level='NBA';
    """)
    
    players = cursor.fetchall()
    cursor.close()
    cnx.close()
    
    return [{"full_name": p[0], "position": p[1], "height": p[2]} for p in players]