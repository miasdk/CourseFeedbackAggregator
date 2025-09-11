from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging
from datetime import datetime

from ..config.database import get_db
from ..models import Feedback

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/mock/insert_feedback")
async def insert_mock_feedback(
    feedback_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Insert mock feedback data for demo purposes
    """
    try:
        # Create Feedback object from the provided data
        feedback = Feedback(
            course_id=feedback_data["course_id"],
            course_name=feedback_data["course_name"], 
            student_email=feedback_data.get("student_email"),
            student_name=feedback_data.get("student_name"),
            feedback_text=feedback_data["feedback_text"],
            rating=feedback_data.get("rating"),
            severity=feedback_data["severity"],
            source=feedback_data["source"],
            source_id=feedback_data["source_id"],
            created_at=datetime.fromisoformat(feedback_data["created_at"]) if feedback_data.get("created_at") else datetime.utcnow(),
            last_modified=datetime.fromisoformat(feedback_data["last_modified"]) if feedback_data.get("last_modified") else datetime.utcnow(),
            is_active=feedback_data.get("is_active", True)
        )
        
        db.add(feedback)
        await db.commit()
        
        return {"success": True, "message": "Mock feedback inserted successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error inserting mock feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to insert mock feedback")

@router.delete("/mock/clear_all")
async def clear_all_feedback(db: AsyncSession = Depends(get_db)):
    """
    Clear all feedback data (for demo reset)
    """
    try:
        await db.execute("DELETE FROM feedback")
        await db.commit()
        
        return {"success": True, "message": "All feedback data cleared"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error clearing feedback data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear feedback data")