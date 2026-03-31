from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import engine, Base
from .routes import expenses_router
from .utils.logger import logger

# Create tables (dev only)
async def init_db():
    # Base.metadata.create_all(bind=engine)
    logger.info("Database ready")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created - expenses ready")
    yield


app = FastAPI(
    title="Expense Tracker V2",
    description="AI-powered receipt OCR with EasyOCR (optimized for Indian receipts)",
    version="2.0.0",
    lifespan=lifespan
)

app.include_router(expenses_router)
# app.include_router(auth_router)  # Optional

@app.get("/")
def root():
    return {"message": "ET V2 API - POST /expenses/upload for OCR"}

