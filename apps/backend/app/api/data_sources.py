"""Data sources API routes for frontend compatibility."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from ..config.database import get_db
from ..controllers.ingest_controller import IngestController

router = APIRouter()

@router.get("/data-sources/status")
async def get_data_source_status(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get data source connection status and sync information."""
    from sqlalchemy import select, func
    from ..models import Feedback, Course
    from datetime import datetime
    
    # Count feedback by source
    feedback_query = select(
        Feedback.source,
        func.count(Feedback.id).label('count')
    ).group_by(Feedback.source)
    
    feedback_result = await db.execute(feedback_query)
    feedback_counts = {row.source: row.count for row in feedback_result}
    
    # Count courses by integration type
    canvas_query = select(func.count(Course.course_id)).where(Course.canvas_id.isnot(None))
    zoho_query = select(func.count(Course.course_id)).where(Course.zoho_program_id.isnot(None))
    
    canvas_result = await db.execute(canvas_query)
    zoho_result = await db.execute(zoho_query)
    
    canvas_courses = canvas_result.scalar()
    zoho_courses = zoho_result.scalar()
    
    return {
        "canvas": {
            "status": "connected" if canvas_courses > 0 else "no_data",
            "last_sync": datetime.utcnow().isoformat(),
            "courses_synced": canvas_courses,
            "feedback_count": feedback_counts.get("canvas", 0),
            "health": "operational"
        },
        "zoho": {
            "status": "connected" if zoho_courses > 0 else "no_data", 
            "last_sync": datetime.utcnow().isoformat(),
            "programs_synced": zoho_courses,
            "feedback_count": feedback_counts.get("zoho", 0),
            "health": "operational"
        },
        "overall_status": "healthy",
        "total_feedback": sum(feedback_counts.values()),
        "last_updated": datetime.utcnow().isoformat()
    }