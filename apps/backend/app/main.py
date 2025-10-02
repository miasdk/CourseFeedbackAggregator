from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# Only import the webhook router (the only functional API file)
from .api.webhooks import router as webhooks_router

app = FastAPI(
    title="Course Feedback Aggregator API",
    description="Intelligent course feedback prioritization system",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include webhook router
app.include_router(webhooks_router, tags=["webhooks"])
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
        "message": "Webhook service operational"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Course Feedback Aggregator API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": [
            "/health",
            "/webhooks/zoho-survey"
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    0