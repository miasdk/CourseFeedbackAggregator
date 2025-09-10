"""Service for priority-related business logic."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, text
from sqlalchemy.orm import selectinload

from ..models import Priority, Feedback, WeightConfig, Review
from .scoring_service import ScoringService


class PriorityService:
    """Business logic for priority operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.scoring_service = ScoringService(db)
    
    async def get_priority_list(
        self,
        course_id: Optional[str] = None,
        min_score: Optional[int] = None,
        order_by: str = "priority_score"
    ) -> List[Priority]:
        """Get filtered and sorted list of priorities."""
        query = select(Priority).options(selectinload(Priority.reviews))
        
        if course_id:
            query = query.where(Priority.course_id == course_id)
        if min_score:
            query = query.where(Priority.priority_score >= min_score)
        
        # Order by different fields
        if order_by == "created_at":
            query = query.order_by(Priority.created_at.desc())
        elif order_by == "updated_at":
            query = query.order_by(Priority.updated_at.desc())
        else:  # default to priority_score
            query = query.order_by(Priority.priority_score.desc())
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_priority_by_id(self, priority_id: int) -> Optional[Priority]:
        """Get priority by ID with reviews."""
        result = await self.db.execute(
            select(Priority)
            .options(selectinload(Priority.reviews))
            .where(Priority.id == priority_id)
        )
        return result.scalar_one_or_none()
    
    async def create_priority(self, priority_data: Dict[str, Any]) -> Priority:
        """Create a new priority entry."""
        priority = Priority(**priority_data)
        self.db.add(priority)
        await self.db.commit()
        await self.db.refresh(priority)
        return priority
    
    async def recompute_priorities(
        self, 
        course_ids: Optional[List[str]] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """Recompute priority scores for courses."""
        
        # Get active weight configuration
        weight_result = await self.db.execute(
            select(WeightConfig).where(WeightConfig.is_active == True)
            .order_by(WeightConfig.updated_at.desc()).limit(1)
        )
        weights = weight_result.scalar_one_or_none()
        
        if not weights:
            raise ValueError("No active weight configuration found")
        
        # Get courses to process
        if course_ids:
            courses_query = select(func.distinct(Feedback.course_id)).where(
                Feedback.course_id.in_(course_ids)
            )
        else:
            courses_query = select(func.distinct(Feedback.course_id)).where(
                Feedback.is_active == True
            )
        
        courses_result = await self.db.execute(courses_query)
        courses_to_process = [row[0] for row in courses_result]
        
        updated_priorities = []
        
        for course_id in courses_to_process:
            # Get course feedback
            feedback_result = await self.db.execute(
                select(Feedback).where(
                    and_(Feedback.course_id == course_id, Feedback.is_active == True)
                )
            )
            feedback_items = feedback_result.scalars().all()
            
            if not feedback_items:
                continue
            
            # Calculate priority score using scoring service
            priority_data = await self.scoring_service.calculate_priority(
                course_id=course_id,
                feedback_items=feedback_items,
                weights=weights
            )
            
            # Check if priority already exists
            existing_result = await self.db.execute(
                select(Priority).where(Priority.course_id == course_id)
            )
            existing_priority = existing_result.scalar_one_or_none()
            
            if existing_priority:
                # Update existing priority
                for key, value in priority_data.items():
                    setattr(existing_priority, key, value)
                existing_priority.updated_at = func.now()
                updated_priorities.append(existing_priority)
            else:
                # Create new priority
                new_priority = Priority(**priority_data)
                self.db.add(new_priority)
                updated_priorities.append(new_priority)
        
        await self.db.commit()
        
        return {
            "courses_processed": len(courses_to_process),
            "priorities_updated": len(updated_priorities),
            "weight_config_used": {
                "impact": weights.impact_weight,
                "urgency": weights.urgency_weight, 
                "effort": weights.effort_weight,
                "strategic": weights.strategic_weight,
                "trend": weights.trend_weight
            }
        }
    
    async def add_priority_review(
        self, 
        priority_id: int, 
        review_data: Dict[str, Any]
    ) -> Review:
        """Add a review to a priority."""
        review_data["priority_id"] = priority_id
        review = Review(**review_data)
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review