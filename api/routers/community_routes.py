from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel

from core.db import get_db_connection

import json

router = APIRouter()

class Lineup(BaseModel):
    lineup_id: int
    user_id: int
    mode: str
    players: Dict[str, Any]
    scouting_report: Dict[str, Any]


class CommentCreate(BaseModel):
    take_id: int
    username: str
    content: str
    parent_comment_id: Optional[int] = None

class Comment(BaseModel):
    comment_id: int
    take_id: int
    username: str
    content: str
    parent_comment_id: Optional[int]
    created_at: str
    replies: list


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

@router.get("/hot-takes/{take_id}/comments", response_model=List[Comment])
def get_comments(take_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT c.comment_id, c.take_id, u.username, c.content, "
        "c.parent_comment_id, c.created_at "
        "FROM comments c JOIN users u ON c.user_id = u.user_id "
        "WHERE c.take_id=%s ORDER BY c.created_at ASC",
        (take_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert datetime to string
    for row in rows:
        if isinstance(row['created_at'], datetime):
            row['created_at'] = row['created_at'].isoformat()

    # Build threaded structure
    comment_dict = {row['comment_id']: {**row, 'replies': []} for row in rows}
    root_comments = []

    for comment in comment_dict.values():
        parent_id = comment['parent_comment_id']
        if parent_id is not None and parent_id in comment_dict:
            comment_dict[parent_id]['replies'].append(comment)
        else:
            root_comments.append(comment)

    return root_comments


@router.post("/hot-takes/{take_id}/comments", response_model=Comment)
def create_comment(take_id: int, comment: CommentCreate):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Get user_id and username from username
        cursor.execute(
            "SELECT user_id, username FROM users WHERE username=%s",
            (comment.username,)
        )
        user_row = cursor.fetchone()
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
        user_id = user_row["user_id"]

        # Insert comment
        cursor.execute(
            "INSERT INTO comments (take_id, user_id, content, parent_comment_id) VALUES (%s, %s, %s, %s)",
            (take_id, user_id, comment.content, comment.parent_comment_id)
        )
        conn.commit()
        comment_id = cursor.lastrowid

        # Fetch inserted comment
        cursor.execute(
            "SELECT c.comment_id, c.take_id, c.content, c.parent_comment_id, c.created_at, u.username "
            "FROM comments c JOIN users u ON c.user_id = u.user_id "
            "WHERE c.comment_id=%s",
            (comment_id,)
        )
        new_comment = cursor.fetchone()
        new_comment["replies"] = []

        # Convert datetime to string to match Pydantic model
        if new_comment.get("created_at"):
            new_comment["created_at"] = new_comment["created_at"].isoformat()

        return new_comment

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()