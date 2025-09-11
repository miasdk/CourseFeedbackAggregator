"""Feedback API routes - thin layer delegating to controllers."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from ..config.database import get_db
from ..controllers.feedback_controller import FeedbackController

router = APIRouter()

@router.get("/feedback")
async def get_feedback(
    course_id: Optional[str] = Query(None, description="Filter by specific course ID"),
    source: Optional[str] = Query(None, description="Filter by source (canvas/zoho)"),
    db: AsyncSession = Depends(get_db)
):
    """Get aggregated feedback data with filtering options."""
    controller = FeedbackController()
    return await controller.get_all_feedback(db, course_id, source)

@router.get("/feedback/{feedback_id}")
async def get_feedback_by_id(
    feedback_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific feedback item by ID."""
    controller = FeedbackController()
    feedback = await controller.get_feedback_by_id(db, feedback_id)
    
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    
    return feedback

@router.post("/feedback")
async def create_feedback(
    feedback_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Create new feedback entry."""
    controller = FeedbackController()
    return await controller.create_feedback(db, feedback_data)