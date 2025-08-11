from fastapi import APIRouter
from typing import List
from pydantic import BaseModel

import mysql.connector

router = APIRouter()

@router.get("/players", response_model=List[dict])
def get_nba_prospects():
    pass