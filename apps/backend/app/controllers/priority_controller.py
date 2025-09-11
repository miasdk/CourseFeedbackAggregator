"""Priority controller for handling priority scoring and recommendations."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .base_controller import BaseController
from ..config.database import Priority, Feedback, WeightConfig


class PriorityController(BaseController):
    """Controller for priority operations and scoring."""
    
    async def get_all_priorities(
        self,
        db: AsyncSession,
        course_id: Optional[str] = None
    ) -> List[Priority]:
        """Get priorities with optional course filtering."""
        query = select(Priority)
        
        if course_id:
            query = query.where(Priority.course_id == course_id)
            
        query = query.order_by(Priority.priority_score.desc())
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_priority_by_id(self, db: AsyncSession, priority_id: int) -> Optional[Priority]:
        """Get single priority with details."""
        query = select(Priority).where(Priority.id == priority_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def recalculate_priorities(self, db: AsyncSession, course_id: str) -> List[Priority]:
        """Recalculate priority scores for a course."""
        # Get active weight config
        weights_query = select(WeightConfig).where(WeightConfig.is_active == True)
        weights_result = await db.execute(weights_query)
        weights = weights_result.scalar_one()
        
        # Get course feedback
        feedback_query = select(Feedback).where(
            and_(
                Feedback.course_id == course_id,
                Feedback.is_active == True
            )
        )
        feedback_result = await db.execute(feedback_query)
        feedback_items = feedback_result.scalars().all()
        
        # Calculate new priorities (simplified for MVP)
        priorities = []
        if feedback_items:
            # Group feedback by severity and create priority
            severity_groups = {}
            for feedback in feedback_items:
                severity = feedback.severity or 'medium'
                if severity not in severity_groups:
                    severity_groups[severity] = []
                severity_groups[severity].append(feedback)
            
            # Create priority for each severity group
            for severity, feedback_group in severity_groups.items():
                # Simple MVP scoring
                impact_score = len(feedback_group) * 0.5  # More feedback = higher impact
                urgency_score = self._severity_to_urgency(severity)
                effort_score = 3.0  # Default effort
                
                final_score = (
                    impact_score * weights.impact_weight +
                    urgency_score * weights.urgency_weight + 
                    effort_score * weights.effort_weight
                )
                
                priority = Priority(
                    course_id=course_id,
                    issue_summary=f"{severity.title()} issues reported by {len(feedback_group)} students",
                    priority_score=min(5, max(1, int(final_score))),
                    impact_score=min(5.0, impact_score),
                    urgency_score=urgency_score,
                    effort_score=effort_score,
                    students_affected=len(set(f.student_email for f in feedback_group if f.student_email)),
                    feedback_ids=[f.id for f in feedback_group]
                )
                
                db.add(priority)
                priorities.append(priority)
        
        await db.commit()
        return priorities
    
    def _severity_to_urgency(self, severity: str) -> float:
        """Convert severity level to urgency score."""
        severity_map = {
            'critical': 5.0,
            'high': 4.0,
            'medium': 3.0,
            'low': 2.0
        }
        return severity_map.get(severity, 3.0)