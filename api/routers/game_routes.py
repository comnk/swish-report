from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..core.db import get_db_connection
from ..utils.hs_helpers import get_youtube_videos

router = APIRouter()