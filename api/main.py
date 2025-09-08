from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from routers import nba_routes, hs_routes, college_routes, game_routes, auth_routes, community_routes, user_routes

app = FastAPI(title="swish report")

# Add session middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY"),  # keep secret in production
    session_cookie="swish_session",
    https_only=True  # set False if testing locally without HTTPS
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(nba_routes.router, prefix="/nba", tags=["NBA"])
app.include_router(college_routes.router, prefix="/college", tags=["College"])
app.include_router(hs_routes.router, prefix="/high-school", tags=["High School"])
app.include_router(game_routes.router, prefix="/games", tags=["Games"])
app.include_router(community_routes.router, prefix="/community", tags=["Community"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
app.include_router(user_routes.router, prefix="/user",tags=["User"] )
