from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

from .database import engine, Base, migrate_sqlite_users_columns
from .routes import expenses_router, auth_router, budgets_router
from .utils.logger import logger

# Create tables (dev only)
async def init_db():
    # Base.metadata.create_all(bind=engine)
    logger.info("Database ready")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    migrate_sqlite_users_columns()
    logger.info("Tables created - expenses ready")
    yield


app = FastAPI(
    title="Expense Tracker V2",
    description="AI-powered receipt OCR with EasyOCR (optimized for Indian receipts)",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(expenses_router)
app.include_router(budgets_router)

# Serve static files (uploads directory)
uploads_path = Path("uploads")
uploads_path.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/")
def root():
    return {"message": "ET V2 API - POST /expenses/upload for OCR"}

