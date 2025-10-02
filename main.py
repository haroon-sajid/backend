# from fastapi import FastAPI, HTTPException
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware

# from sqlmodel import SQLModel, Field, select
# from typing import Optional
# from pydantic import EmailStr
# from sqlmodel import Session
# from core.database import engine, create_db_and_tables
# from routes.auth import router as auth_router


# # -----------------------
# # Models for submissions
# # -----------------------
# class Items(SQLModel):
#     name: str
#     email: EmailStr
#     book: str
#     description: Optional[str] = None
#     price: float

# class Submission(Items, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)

# # Create FastAPI app
# app = FastAPI()

# # Create tables at startup (will include User and Submission)
# @app.on_event("startup")
# def on_startup():
#     create_db_and_tables()

# # CORS allow our React server to fetch and get data from the backend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Submission endpoints (same logic as you had)
# @app.post("/submissions", response_model=Submission)
# def create_submission(item: Items):
#     try:
#         with Session(engine) as session:
#             db_items = Submission(**item.model_dump() if hasattr(item, "model_dump") else item.dict())
#             session.add(db_items)
#             session.commit()
#             session.refresh(db_items)

#             return JSONResponse(
#                 content={
#                     "message": "Your Data Submitted Successfully!",
#                     "data": db_items.model_dump() if hasattr(db_items, "model_dump") else db_items.dict()
#                 },
#                 status_code=201
#             )

#     except Exception as e:
#         raise HTTPException(
#             status_code=400,
#             detail=f"Failed to Submit data. Error: {str(e)}"
#         )

# @app.get("/submissions", response_model=list[Submission])
# def list_submission():
#     with Session(engine) as session:
#         rows = session.exec(select(Submission)).all()
#         return rows

# # Include authentication routes from app/routes/auth.py
# app.include_router(auth_router)

# @app.get("/health")
# def health_check():
#     return {"status": "ok", "message": "Backend running"}




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
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
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
