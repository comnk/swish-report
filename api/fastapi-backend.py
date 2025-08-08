from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
from pydantic import BaseModel
from typing import List

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database='swish_report'
    )

class Player(BaseModel):
    player_uid: int
    full_name: str
    class_year: int
    position: str
    school_name: str
    height: str

@app.get("/prospects/highschool", response_model=List[Player])
def get_highschool_prospects():
    select_sql = """
    SELECT p.player_uid, p.full_name, p.class_year, hspr.position, hspr.school_name, hspr.height
    FROM players AS p
    INNER JOIN high_school_player_rankings AS hspr ON hspr.player_uid = p.player_uid
    WHERE hspr.source = '247sports';
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