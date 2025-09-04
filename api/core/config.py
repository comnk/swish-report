from openai import OpenAI
from googleapiclient.discovery import build
from dotenv import load_dotenv
from authlib.integrations.starlette_client import OAuth

import os

load_dotenv()

def set_google_oauth():
    # ----- Google OAuth -----
    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    
    return oauth

def set_openai():
    OPENAI_KEY = os.getenv('OPENAI_KEY')
    if not OPENAI_KEY:
        raise ValueError("OPENAI_KEY not found")
    
    client = OpenAI(api_key=OPENAI_KEY)
    return client

def set_youtube_key():
    YOUTUBE_KEY = os.getenv("YOUTUBE_KEY")
    youtube = build('youtube', 'v3', developerKey=YOUTUBE_KEY)
    return youtube

def set_gemini_key():
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    client = OpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    return client