"""Data ingestion API routes for Canvas and Zoho."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from ..config.database import get_db
from ..controllers.ingest_controller import IngestController

router = APIRouter()

@router.post("/ingest/canvas/{course_id}")
async def ingest_canvas_course(
    course_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Ingest feedback data from Canvas for a specific course."""
    controller = IngestController()
    result = await controller.ingest_canvas_feedback(db, course_id)
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error'))
    
    return result

@router.post("/ingest/zoho/{program_id}")
async def ingest_zoho_program(
    program_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Ingest feedback data from Zoho for a specific program."""
    controller = IngestController()
    result = await controller.ingest_zoho_feedback(db, program_id)
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error'))
    
    return result

@router.get("/ingest/status")
async def get_ingestion_status(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get current ingestion status and statistics."""
    from sqlalchemy import select, func
    from ..config.database import Feedback, Course
    
    # Count feedback by source
    feedback_query = select(
        Feedback.source,
        func.count(Feedback.id).label('count')
    ).group_by(Feedback.source)
    
    feedback_result = await db.execute(feedback_query)
    feedback_counts = {row.source: row.count for row in feedback_result}
    
    # Count courses
    course_query = select(func.count(Course.course_id))
    course_result = await db.execute(course_query)
    total_courses = course_result.scalar()
    
    return {
        "success": True,
        "data": {
            "total_courses": total_courses,
            "feedback_by_source": feedback_counts,
            "last_updated": "2025-09-10T18:00:00Z"  # Would track actual timestamps
        }
    }