from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from datetime import datetime
import os

from .config.database import create_tables
from .config.config import settings
from .api.feedback import router as feedback_router
from .api.priorities import router as priorities_router
from .api.ingest import router as ingest_router
from .api.weights import router as weights_router
from .api.mock import router as mock_router

app = FastAPI(
    title="Course Feedback Aggregator API",
    description="Intelligent course feedback prioritization system",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    await create_tables()

# Include API routers
app.include_router(feedback_router, prefix="/api", tags=["feedback"])
app.include_router(priorities_router, prefix="/api", tags=["priorities"])
app.include_router(ingest_router, prefix="/api", tags=["ingestion"])
app.include_router(weights_router, prefix="/api", tags=["weights"])
app.include_router(mock_router, prefix="/api", tags=["mock"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": "connected",
            "canvas_api": "configured" if settings.canvas_token else "missing_token",
            "zoho_api": "configured" if settings.zoho_access_token else "missing_token"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Course Feedback Aggregator API",
        "version": "1.0.0",
        "environment": settings.environment,
        "endpoints": [
            "/health",
            "/api/feedback",
            "/api/priorities", 
            "/api/weights",
            "/api/ingest/canvas",
            "/api/ingest/zoho"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )