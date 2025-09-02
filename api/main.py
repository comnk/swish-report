from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import nba_routes, hs_routes, college_routes, game_routes, auth_routes

app = FastAPI(title="swish report")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nba_routes.router, prefix="/nba", tags=["NBA"])
app.include_router(college_routes.router, prefix="/college", tags=["College"])
app.include_router(hs_routes.router, prefix="/high-school", tags=["High School"])
app.include_router(game_routes.router, prefix="/games", tags=["Games"])
app.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])