"""Feedback controller for handling feedback business logic."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .base_controller import BaseController
from ..models import Feedback


class FeedbackController(BaseController):
    """Controller for feedback operations."""
    
    async def get_all_feedback(
        self,
        db: AsyncSession,
        course_id: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[Feedback]:
        """Get feedback with basic filtering."""
        query = select(Feedback).where(Feedback.is_active == True)
        
        if course_id:
            query = query.where(Feedback.course_id == course_id)
        if source:
            query = query.where(Feedback.source == source)
            
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_feedback_by_id(self, db: AsyncSession, feedback_id: int) -> Optional[Feedback]:
        """Get single feedback item."""
        query = select(Feedback).where(Feedback.id == feedback_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_feedback(self, db: AsyncSession, feedback_data: Dict[str, Any]) -> Feedback:
        """Create new feedback entry."""
        feedback = Feedback(**feedback_data)
        db.add(feedback)
        await db.commit()
        await db.refresh(feedback)
        return feedback