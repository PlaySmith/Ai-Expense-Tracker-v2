from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.routes import expenses, auth
from app.database import Base, engine
from app.utils.error_handlers import setup_exception_handlers
from app.utils.logger import setup_logging

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="SmartSpend AI",
    description="AI-powered expense tracking from receipt images",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
setup_exception_handlers(app)

# Include routers
app.include_router(expenses.router, prefix="/api/v1", tags=["expenses"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])

@app.on_event("startup")
async def startup():
    # \"\"\"Create database tables on startup.\"\"\"
    Base.metadata.create_all(bind=engine)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all incoming requests"""
    start_time = time.time()
    
    # Log request
    logger = logging.getLogger("api")
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} | Time: {process_time:.3f}s")
    
    return response

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SmartSpend AI API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "SmartSpend AI API",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
