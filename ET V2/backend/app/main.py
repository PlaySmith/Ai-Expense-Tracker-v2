from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine, Base
from .routes import expenses_router
from .utils.error_handlers import add_exception_handlers

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 SmartSpend AI v2 starting...")
    yield
    # Shutdown
    print("👋 SmartSpend AI v2 shutdown")

app = FastAPI(
    title="SmartSpend AI v2",
    description="AI Receipt Tracker - OCR + Analytics",
    version="2.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB tables
Base.metadata.create_all(bind=engine)

# Custom errors
add_exception_handlers(app)

# Routes
app.include_router(expenses_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

