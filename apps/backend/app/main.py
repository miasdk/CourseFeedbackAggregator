from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

from .config.config import settings
from .api.webhooks import router as webhooks_router

app = FastAPI(
    title="Course Feedback Aggregator API",
    description="Intelligent course feedback prioritization system",
    version="1.0.1"
)

# CORS middleware for frontend - must be first middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include webhook router (MVP focus)
app.include_router(webhooks_router, prefix="/api", tags=["webhooks"])
# CORS preflight handler
@app.options("/{path:path}")
async def options_handler(path: str):
    return {"message": "OK"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "phase": "webhook_mvp",
        "services": {
            "webhook_endpoint": "active",
            "zoho_oauth": "configured" if settings.zoho_client_id else "missing_config"
        }
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Course Feedback Aggregator API - Webhook MVP",
        "version": "1.0.1",
        "phase": "webhook_development",
        "environment": settings.environment,
        "active_endpoints": [
            "/health",
            "/api/webhooks/zoho-survey"
        ],
        "status": "Ready for Zoho webhook integration"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )