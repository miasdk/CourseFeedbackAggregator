"""Service for feedback-related business logic."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from ..models import Feedback, Course


class FeedbackService:
    """Business logic for feedback operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_feedback_list(
        self, 
        course_id: Optional[str] = None,
        source: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Feedback]:
        """Get filtered list of feedback entries."""
        query = select(Feedback).where(Feedback.is_active == True)
        
        if course_id:
            query = query.where(Feedback.course_id == course_id)
        if source:
            query = query.where(Feedback.source == source)
        if severity:
            query = query.where(Feedback.severity == severity)
            
        query = query.order_by(Feedback.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_feedback(self, feedback_data: Dict[str, Any]) -> Feedback:
        """Create a new feedback entry."""
        feedback = Feedback(**feedback_data)
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback
    
    async def get_feedback_by_id(self, feedback_id: int) -> Optional[Feedback]:
        """Get feedback by ID."""
        result = await self.db.execute(
            select(Feedback).where(Feedback.id == feedback_id)
        )
        return result.scalar_one_or_none()
    
    async def get_feedback_stats(self) -> Dict[str, Any]:
        """Get feedback statistics."""
        # Total feedback count
        total_result = await self.db.execute(
            select(func.count(Feedback.id)).where(Feedback.is_active == True)
        )
        total_feedback = total_result.scalar()
        
        # Source distribution
        source_result = await self.db.execute(
            select(Feedback.source, func.count(Feedback.id))
            .where(Feedback.is_active == True)
            .group_by(Feedback.source)
        )
        source_distribution = {row[0]: row[1] for row in source_result}
        
        # Severity distribution
        severity_result = await self.db.execute(
            select(Feedback.severity, func.count(Feedback.id))
            .where(Feedback.is_active == True)
            .group_by(Feedback.severity)
        )
        severity_distribution = {row[0]: row[1] for row in severity_result}
        
        # Average rating
        rating_result = await self.db.execute(
            select(func.avg(Feedback.rating))
            .where(and_(Feedback.is_active == True, Feedback.rating.isnot(None)))
        )
        avg_rating = rating_result.scalar()
        
        return {
            "total_feedback": total_feedback,
            "source_distribution": source_distribution,
            "severity_distribution": severity_distribution,
            "average_rating": round(avg_rating, 2) if avg_rating else None
        }
    
    async def get_feedback_by_course(self, course_id: str) -> List[Feedback]:
        """Get all feedback for a specific course."""
        result = await self.db.execute(
            select(Feedback)
            .where(and_(Feedback.course_id == course_id, Feedback.is_active == True))
            .order_by(Feedback.created_at.desc())
        )
        return result.scalars().all()