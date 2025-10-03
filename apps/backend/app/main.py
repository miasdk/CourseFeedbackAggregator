from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime

# Import routers
from .api.zoho.webhooks import router as webhooks_router
from .api.courses import router as courses_router
from .api.quizzes import router as quizzes_router
from .api.feedback import router as feedback_router

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

# Include routers
app.include_router(webhooks_router, tags=["webhooks"])
app.include_router(courses_router)
app.include_router(quizzes_router)
app.include_router(feedback_router)
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
        "message": "API service operational"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Course Feedback Aggregator API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "canvas_courses": {
                "sync": "POST /courses/sync",
                "list": "GET /courses/",
                "detail": "GET /courses/{id}"
            },
            "canvas_quizzes": {
                "sync_all": "POST /quizzes/sync",
                "sync_course": "POST /quizzes/sync/{course_id}",
                "list_surveys": "GET /quizzes/surveys",
                "survey_detail": "GET /quizzes/surveys/{survey_id}"
            },
            "student_feedback": {
                "sync_survey": "POST /feedback/sync/{survey_id}",
                "get_survey_feedback": "GET /feedback/surveys/{survey_id}",
                "course_summary": "GET /feedback/courses/{course_id}/summary",
                "course_detail": "GET /feedback/courses/{course_id}/detail",
                "course_categories": "GET /feedback/courses/{course_id}/categories",
                "course_themes": "GET /feedback/courses/{course_id}/themes"
            },
            "webhooks": {
                "zoho_survey": "POST /webhooks/zoho-survey"
            }
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    0