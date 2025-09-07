from fastapi import APIRouter, HTTPException
from core.db import get_db_connection
from typing import List, Dict

router = APIRouter()

@router.get("/lineups", response_model=List[Dict])
def get_player_lineups():
    select_sql = """
    SELECT * FROM lineups;
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(select_sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return rows

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lineups/{id}", response_model=Dict)
def get_player_lineup(lineup_id):
    select_sql = """
    SELECT * FROM lineups WHERE lineup_id=%s;
    """
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)  # <-- key fix
        cursor.execute(select_sql, (lineup_id,))
        row = cursor.fetchone()
        
        return row

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()