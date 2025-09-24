from fastapi import APIRouter, HTTPException, Depends
from core.db import get_db_connection
from routers.auth_routes import get_current_user
from typing import List

router = APIRouter()

@router.get("/lineup-builder/{user_email}", response_model=List[dict])
def get_user_lineups(user_email: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT user_id FROM users WHERE email = %s", (user_email,))
    user_id = cursor.fetchone()["user_id"]

    cursor.execute(
        "SELECT lineup_id, mode, scouting_report FROM lineups WHERE user_id = %s",
        (user_id,),
    )
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return results

@router.get("/hot-takes/{user_email}", response_model=List[dict])
def get_user_hot_takes(user_email: str):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT user_id FROM users WHERE email = %s", (user_email,))
    user_id = cursor.fetchone()["user_id"]
    
    cursor.execute(
        "SELECT take_id, content, truthfulness_score FROM hot_takes WHERE user_id = %s",
        (user_id,),
    )
    
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return results

@router.get("/get-username/{email}")
def get_username(email: str):
    select_sql = """SELECT username FROM users WHERE email=%s"""
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(select_sql, (email,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="User not found")

    return {"username": row["username"]}

@router.get("/user-info")
def get_user_info(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"], "email": current_user["email"], "password": current_user["password_hash"]}