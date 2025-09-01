from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.db import get_db_connection
from utils.hs_helpers import get_youtube_videos

router = APIRouter()

@router.get("/poeltl/get-players")
def poeltl_get_players():
    select_sql = """
    SELECT full_name FROM players;
    """
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(select_sql)
    
    
    pass

@router.get("/poeltl/get-player")
def poeltl_get_daily_player():
    pass

@router.get("/lineup-builder")
def get_lineup_analysis():
    pass