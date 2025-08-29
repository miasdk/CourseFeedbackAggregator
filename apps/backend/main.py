"""
Course Feedback Aggregator - FastAPI Backend
Enhanced with intelligent scoring and database integration
"""

from fastapi import FastAPI, HTTPException, Depends, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
import json
import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Import new systems
from core.database import get_db, init_database, get_db_stats, check_database_health
from services.canvas_client import CanvasClient
from services.scoring_engine import ScoringEngine, WeightConfig as ScoringWeights
from services.weight_config_service import WeightConfigService
from services.recommendation_engine import RecommendationEngine
from models.database import Course, FeedbackItem, Recommendation, WeightConfig

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Course Feedback Aggregator",
    description="Intelligent priority scoring system for course feedback analysis",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global services
canvas_client = None
scoring_engine = None
demo_data = {}

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global canvas_client, scoring_engine, demo_data
    
    logger.info("🚀 Starting Course Feedback Aggregator...")
    
    # Initialize database
    if not init_database():
        logger.error("❌ Failed to initialize database")
        return
    
    # Initialize Canvas client
    try:
        canvas_client = CanvasClient()
        logger.info("✅ Canvas client initialized")
    except Exception as e:
        logger.warning(f"⚠️ Canvas client unavailable: {e}")
    
    # Initialize scoring engine with default weights
    try:
        default_weights = ScoringWeights()
        scoring_engine = ScoringEngine(default_weights)
        logger.info("✅ Scoring engine initialized")
    except Exception as e:
        logger.error(f"❌ Scoring engine failed: {e}")
        return
    
    # Load demo data as fallback
    try:
        demo_files = ["data/canvas_demo_complete.json"]
        for file_path in demo_files:
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    file_data = json.load(f)
                    demo_data.update(file_data)
                logger.info(f"📊 Loaded demo data from {file_path}")
    except Exception as e:
        logger.warning(f"⚠️ Demo data loading failed: {e}")
    
    logger.info("🎉 System startup complete!")

# Health and Status Endpoints
@app.get("/health")
async def health_check():
    """System health check with detailed status"""
    db_health = check_database_health()
    
    canvas_status = "disconnected"
    if canvas_client:
        try:
            connection_test = canvas_client._make_request("/api/v1/users/self")
            canvas_status = "connected" if connection_test["success"] else "error"
        except:
            canvas_status = "error"
    
    return {
        "status": "healthy" if db_health["healthy"] else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {
            "database": db_health,
            "canvas": canvas_status,
            "scoring_engine": "active" if scoring_engine else "inactive",
            "demo_data": len(demo_data) > 0
        },
        "version": "2.0.0"
    }

@app.get("/api/status")
async def system_status(db: Session = Depends(get_db)):
    """Detailed system status and statistics"""
    stats = get_db_stats()
    
    # Get active weight configuration
    active_weights = db.query(WeightConfig).filter(WeightConfig.is_active == True).first()
    
    return {
        "database": stats,
        "active_weights": {
            "name": active_weights.name if active_weights else "default",
            "weights": {
                "impact": active_weights.impact_weight if active_weights else 0.35,
                "urgency": active_weights.urgency_weight if active_weights else 0.25,
                "effort": active_weights.effort_weight if active_weights else 0.20,
                "strategic": active_weights.strategic_weight if active_weights else 0.15,
                "trend": active_weights.trend_weight if active_weights else 0.05
            }
        } if active_weights else None,
        "canvas_connection": await test_canvas_connection(),
        "demo_mode": len(demo_data) > 0 and not canvas_client
    }

async def test_canvas_connection():
    """Test Canvas API connection"""
    if not canvas_client:
        return {"connected": False, "reason": "Canvas client not initialized"}
    
    try:
        result = canvas_client._make_request("/api/v1/users/self")
        if result["success"]:
            user_data = result["data"]
            courses_result = canvas_client._make_request("/api/v1/courses")
            courses_count = len(courses_result["data"]) if courses_result["success"] else 0
            
            return {
                "connected": True,
                "user": user_data.get("name"),
                "user_id": user_data.get("id"),
                "courses_accessible": courses_count,
                "has_data_access": courses_count > 0
            }
        else:
            return {"connected": False, "error": result["error"]}
    except Exception as e:
        return {"connected": False, "error": str(e)}

# Course Data Endpoints
@app.get("/api/courses")
async def get_courses(
    include_analytics: bool = True,
    limit: Optional[int] = Query(None, gt=0, le=100),
    db: Session = Depends(get_db)
):
    """Get courses with optional analytics data"""
    
    # Try to get from database first
    query = db.query(Course)
    if limit:
        query = query.limit(limit)
    
    db_courses = query.all()
    
    if db_courses:
        logger.info(f"📊 Retrieved {len(db_courses)} courses from database")
        courses_data = [course.to_dict() for course in db_courses]
        
        if include_analytics:
            # Add analytics from recommendations
            for course_data in courses_data:
                recommendations = db.query(Recommendation).filter(
                    Recommendation.course_id == course_data["id"]
                ).order_by(desc(Recommendation.total_score)).all()
                
                if recommendations:
                    top_rec = recommendations[0]
                    course_data.update({
                        "priority_score": round(top_rec.total_score, 1),
                        "priority_level": top_rec.priority_level,
                        "total_recommendations": len(recommendations),
                        "last_analyzed": top_rec.generated_at.isoformat() if top_rec.generated_at else None
                    })
        
        return {
            "source": "database",
            "count": len(courses_data),
            "courses": courses_data
        }
    
    # Fallback to demo data
    demo_courses = demo_data.get("courses", [])
    if limit:
        demo_courses = demo_courses[:limit]
    
    logger.info(f"📊 Using {len(demo_courses)} demo courses")
    return {
        "source": "demo_data",
        "count": len(demo_courses),
        "courses": demo_courses
    }

@app.get("/api/courses/{course_id}")
async def get_course_details(course_id: int, db: Session = Depends(get_db)):
    """Get detailed information for a specific course"""
    
    # Try database first
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if db_course:
        course_data = db_course.to_dict()
        
        # Add feedback count and recent recommendations
        feedback_count = db.query(FeedbackItem).filter(
            FeedbackItem.course_id == course_id
        ).count()
        
        recent_recommendations = db.query(Recommendation).filter(
            Recommendation.course_id == course_id
        ).order_by(desc(Recommendation.generated_at)).limit(3).all()
        
        course_data.update({
            "feedback_count": feedback_count,
            "recent_recommendations": [rec.to_dict() for rec in recent_recommendations]
        })
        
        return course_data
    
    # Fallback to demo data
    demo_courses = demo_data.get("courses", [])
    course = next((c for c in demo_courses if c.get("id") == course_id), None)
    
    if course:
        # Add demo analytics
        analytics = demo_data.get("analytics", {})
        course_analytics = analytics.get(str(course_id), {})
        course.update(course_analytics)
        return course
    
    raise HTTPException(status_code=404, detail="Course not found")

@app.get("/api/courses/{course_id}/feedback")
async def get_course_feedback(course_id: int, db: Session = Depends(get_db)):
    """Get feedback for a specific course"""
    
    # Try database first
    feedback_items = db.query(FeedbackItem).filter(
        FeedbackItem.course_id == course_id
    ).order_by(desc(FeedbackItem.submitted_at)).all()
    
    if feedback_items:
        return {
            "course_id": course_id,
            "source": "database",
            "feedback_count": len(feedback_items),
            "feedback": [item.to_dict() for item in feedback_items]
        }
    
    # Fallback to demo data
    demo_feedback = demo_data.get("feedback", [])
    course_feedback = [f for f in demo_feedback if f.get("course_id") == course_id]
    
    return {
        "course_id": course_id,
        "source": "demo_data", 
        "feedback_count": len(course_feedback),
        "feedback": course_feedback
    }

# Priority and Recommendation Endpoints
@app.get("/api/priorities")
async def get_priorities(
    limit: Optional[int] = Query(20, gt=0, le=100),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    priority_level: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Get prioritized course recommendations"""
    
    query = db.query(Recommendation).join(Course)
    
    if min_score is not None:
        query = query.filter(Recommendation.total_score >= min_score)
    
    if priority_level:
        query = query.filter(Recommendation.priority_level == priority_level)
    
    recommendations = query.order_by(
        desc(Recommendation.total_score)
    ).limit(limit).all()
    
    if recommendations:
        return {
            "source": "database",
            "total_found": len(recommendations),
            "recommendations": [rec.to_dict() for rec in recommendations],
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
    
    # Fallback to demo data with simple scoring
    demo_courses = demo_data.get("courses", [])
    demo_analytics = demo_data.get("analytics", {})
    
    priorities = []
    for course in demo_courses:
        course_id = str(course["id"])
        if course_id in demo_analytics:
            analytics = demo_analytics[course_id]
            priority_score = analytics.get("priority_score", 0)
            
            if min_score is None or priority_score >= min_score:
                priorities.append({
                    "course_id": course["id"],
                    "course_name": course["name"],
                    "instructor": course.get("teacher", "Unknown"),
                    "priority_score": priority_score,
                    "priority_level": "high" if priority_score > 60 else "medium" if priority_score > 30 else "low",
                    "explanation": f"Priority score of {priority_score} based on feedback analysis",
                    "source": "demo_data"
                })
    
    priorities.sort(key=lambda x: x["priority_score"], reverse=True)
    
    return {
        "source": "demo_data",
        "total_found": len(priorities[:limit]),
        "recommendations": priorities[:limit],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/recommendations/{recommendation_id}")
async def get_recommendation_details(recommendation_id: int, db: Session = Depends(get_db)):
    """Get detailed explanation for a specific recommendation"""
    
    recommendation = db.query(Recommendation).filter(
        Recommendation.id == recommendation_id
    ).first()
    
    if not recommendation:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    
    # Get related course and feedback
    course = db.query(Course).filter(Course.id == recommendation.course_id).first()
    feedback_items = db.query(FeedbackItem).filter(
        FeedbackItem.course_id == recommendation.course_id
    ).all()
    
    return {
        "recommendation": recommendation.to_dict(),
        "course": course.to_dict() if course else None,
        "supporting_evidence": [item.to_dict() for item in feedback_items[:5]],
        "evidence_count": len(feedback_items)
    }

# Weight Configuration Endpoints (Enhanced)
@app.get("/api/weights")
async def get_weight_configs(include_inactive: bool = Query(True)):
    """Get all weight configurations with advanced features"""
    try:
        service = WeightConfigService()
        configs = service.list_weight_configs(include_inactive=include_inactive)
        return {
            "success": True,
            "configs": configs,
            "total_count": len(configs)
        }
    except Exception as e:
        logger.error(f"Failed to get weight configs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/weights/active")
async def get_active_weight_config():
    """Get the currently active weight configuration"""
    try:
        service = WeightConfigService()
        config = service.get_active_config()
        
        if not config:
            raise HTTPException(status_code=404, detail="No active weight configuration found")
        
        return {
            "success": True,
            "config": config
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get active config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/weights")
async def create_weight_config(
    config_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Create new weight configuration with full validation"""
    try:
        service = WeightConfigService()
        
        # Extract request data
        name = config_data.get("name")
        description = config_data.get("description", "")
        weights = config_data.get("weights", {})
        created_by = config_data.get("created_by", "api_user")
        make_active = config_data.get("make_active", False)
        recompute = config_data.get("recompute", False)
        
        if not name:
            raise HTTPException(status_code=400, detail="Name is required")
        
        if not weights:
            raise HTTPException(status_code=400, detail="Weights are required")
        
        result = service.create_weight_config(
            name=name,
            description=description,
            weights=weights,
            created_by=created_by,
            make_active=make_active
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Optionally trigger recommendation regeneration
        if recompute:
            background_tasks.add_task(recompute_recommendations_with_new_weights, result["config_id"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create weight config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/weights/{config_id}")
async def update_weight_config(
    config_id: int, 
    config_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Update an existing weight configuration"""
    try:
        service = WeightConfigService()
        
        result = service.update_weight_config(
            config_id=config_id,
            weights=config_data.get("weights"),
            name=config_data.get("name"),
            description=config_data.get("description"),
            make_active=config_data.get("make_active")
        )
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Optionally trigger recommendation regeneration
        if config_data.get("recompute", False):
            background_tasks.add_task(recompute_recommendations_with_new_weights, config_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update weight config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/weights/{config_id}/activate")
async def activate_weight_config(
    config_id: int,
    background_tasks: BackgroundTasks,
    recompute: bool = Query(False)
):
    """Activate a weight configuration"""
    try:
        service = WeightConfigService()
        result = service.activate_config(config_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Optionally trigger recommendation regeneration
        if recompute:
            background_tasks.add_task(recompute_recommendations_with_new_weights, config_id)
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to activate config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/weights/validate")
async def validate_weights(config_data: Dict[str, Any]):
    """Validate weight configuration without saving"""
    try:
        service = WeightConfigService()
        weights = config_data.get("weights", {})
        
        if not weights:
            raise HTTPException(status_code=400, detail="Weights are required")
        
        result = service.validate_weights(weights)
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate weights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/weights/preview")
async def preview_weight_impact(config_data: Dict[str, Any]):
    """Preview how weight changes would affect existing recommendations"""
    try:
        service = WeightConfigService()
        weights = config_data.get("weights", {})
        sample_size = config_data.get("sample_size", 5)
        
        if not weights:
            raise HTTPException(status_code=400, detail="Weights are required")
        
        result = service.get_config_impact_preview(weights, sample_size)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to preview weight impact: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/weights/{config_id}")
async def delete_weight_config(config_id: int):
    """Delete a weight configuration (if not active and not used by recommendations)"""
    try:
        service = WeightConfigService()
        result = service.delete_config(config_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete weight config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def recompute_recommendations_with_new_weights(weight_config_id: int):
    """Background task to regenerate recommendations with new weight configuration"""
    logger.info(f"🔄 Regenerating recommendations with weight config {weight_config_id}")
    
    try:
        # Use the specific weight configuration
        engine = RecommendationEngine(weight_config_id=weight_config_id)
        
        # Add institutional context
        context = {
            "institutional_priorities": [
                {
                    "keywords": ["strategic", "ai", "artificial intelligence"],
                    "weight": 20,
                    "description": "AI and Strategic courses are institutional priorities"
                },
                {
                    "keywords": ["women", "leadership"],
                    "weight": 15,
                    "description": "Leadership development programs"
                }
            ]
        }
        
        result = engine.generate_all_recommendations(
            force_refresh=True,
            context=context
        )
        
        if result["success"]:
            logger.info(f"✅ Generated {result['total_recommendations']} recommendations with new weights")
        else:
            logger.error(f"❌ Failed to regenerate recommendations: {result['error']}")
            
    except Exception as e:
        logger.error(f"❌ Background recommendation generation failed: {e}")

# Canvas Integration Endpoints
@app.get("/api/canvas/status")
async def canvas_status():
    """Check Canvas API connection status"""
    return await test_canvas_connection()

@app.post("/api/canvas/sync")
async def trigger_canvas_sync(background_tasks: BackgroundTasks):
    """Trigger Canvas data synchronization"""
    if not canvas_client:
        raise HTTPException(status_code=503, detail="Canvas client not available")
    
    background_tasks.add_task(sync_canvas_data)
    
    return {
        "success": True,
        "message": "Canvas sync initiated",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

async def sync_canvas_data():
    """Background task to sync data from Canvas"""
    logger.info("🔄 Starting Canvas data sync...")
    # Implementation will be added when Canvas access is available

# Migration and Data Management
@app.post("/api/data/migrate")
async def migrate_demo_data(db: Session = Depends(get_db)):
    """Migrate demo data to database for testing"""
    
    if not demo_data:
        raise HTTPException(status_code=400, detail="No demo data available to migrate")
    
    # This endpoint will be implemented next
    return {"message": "Migration endpoint ready - implementation in progress"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)