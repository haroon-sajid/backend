import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.database import create_db_and_tables
from routes.auth import router as auth_router
from routes.team import router as team_router  
from routes.project import router as project_router

app = FastAPI(title="Team Collaboration App Backend")

# -------------------------------
# Create tables on startup
# -------------------------------
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# -------------------------------
# CORS (Allow frontend to connect)
# -------------------------------
# cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in cors_origins if origin.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Routes
# -------------------------------
#  Same style as signup/login — no prefix, just simple routes
app.include_router(auth_router)
app.include_router(team_router)
app.include_router(project_router)

# -------------------------------
# Health Check
# -------------------------------
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}
