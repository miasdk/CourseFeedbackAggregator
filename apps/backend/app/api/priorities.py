from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List, Optional
import logging

from ..config.database import get_db, Priority, WeightConfig, get_active_weights
from ..scoring.engine import PriorityScoring, group_similar_feedback, generate_issue_summary
from ..config.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/priorities")
async def get_priorities(
    course_id: Optional[str] = Query(None, description="Filter by specific course ID"),
    priority_level: Optional[int] = Query(None, description="Filter by priority level (1-5)"),
    limit: int = Query(50, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get computed priority recommendations
    """
    try:
        # Build query with filters
        query = select(Priority)
        
        if course_id:
            query = query.where(Priority.course_id == course_id)
        if priority_level:
            query = query.where(Priority.priority_score == priority_level)
        
        # Add pagination and ordering
        query = query.order_by(Priority.priority_score.desc(), Priority.students_affected.desc())
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        priorities = result.scalars().all()
        
        # Get total count
        count_query = select(func.count(Priority.id))
        if course_id:
            count_query = count_query.where(Priority.course_id == course_id)
        if priority_level:
            count_query = count_query.where(Priority.priority_score == priority_level)
            
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        # Get current weights for context
        current_weights = await get_active_weights()
        
        # Format response
        priorities_data = []
        for priority in priorities:
            priorities_data.append({
                "id": priority.id,
                "course_id": priority.course_id,
                "issue_summary": priority.issue_summary,
                "priority_score": priority.priority_score,
                "priority_label": PriorityScoring.PRIORITY_LABELS[priority.priority_score]["label"],
                "priority_action": PriorityScoring.PRIORITY_LABELS[priority.priority_score]["action"],
                "priority_color": PriorityScoring.PRIORITY_LABELS[priority.priority_score]["color"],
                "students_affected": priority.students_affected,
                "factor_scores": {
                    "impact": priority.impact_score,
                    "urgency": priority.urgency_score,
                    "effort": priority.effort_score,
                    "strategic": priority.strategic_score,
                    "trend": priority.trend_score
                },
                "evidence": priority.evidence,
                "feedback_ids": priority.feedback_ids,
                "created_at": priority.created_at.isoformat() if priority.created_at else None,
                "updated_at": priority.updated_at.isoformat() if priority.updated_at else None
            })
        
        return {
            "priorities": priorities_data,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(priorities) < total_count
            },
            "current_weights": {
                "impact": current_weights.impact_weight,
                "urgency": current_weights.urgency_weight,
                "effort": current_weights.effort_weight,
                "strategic": current_weights.strategic_weight,
                "trend": current_weights.trend_weight
            },
            "filters_applied": {
                "course_id": course_id,
                "priority_level": priority_level
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching priorities: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve priority recommendations")

@router.get("/priorities/summary")
async def get_priorities_summary(
    course_id: Optional[str] = Query(None, description="Filter by specific course ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary statistics of priority recommendations
    """
    try:
        # Base query
        base_query = select(Priority)
        if course_id:
            base_query = base_query.where(Priority.course_id == course_id)
        
        # Total priorities count
        count_query = select(func.count(Priority.id))
        if course_id:
            count_query = count_query.where(Priority.course_id == course_id)
        count_result = await db.execute(count_query)
        total_priorities = count_result.scalar()
        
        # Count by priority level
        level_query = select(
            Priority.priority_score,
            func.count(Priority.id).label('count')
        )
        if course_id:
            level_query = level_query.where(Priority.course_id == course_id)
        level_query = level_query.group_by(Priority.priority_score)
        
        level_result = await db.execute(level_query)
        level_counts = {}
        for row in level_result:
            label = PriorityScoring.PRIORITY_LABELS[row.priority_score]["label"]
            level_counts[label] = row.count
        
        # Critical issues count (priority 5)
        critical_query = select(func.count(Priority.id)).where(Priority.priority_score == 5)
        if course_id:
            critical_query = critical_query.where(Priority.course_id == course_id)
        critical_result = await db.execute(critical_query)
        critical_count = critical_result.scalar()
        
        # Average priority score
        avg_query = select(func.avg(Priority.priority_score))
        if course_id:
            avg_query = avg_query.where(Priority.course_id == course_id)
        avg_result = await db.execute(avg_query)
        avg_priority = avg_result.scalar()
        
        # Total students affected
        students_query = select(func.sum(Priority.students_affected))
        if course_id:
            students_query = students_query.where(Priority.course_id == course_id)
        students_result = await db.execute(students_query)
        total_students_affected = students_result.scalar() or 0
        
        return {
            "total_recommendations": total_priorities,
            "critical_issues": critical_count,
            "average_priority_score": round(avg_priority, 1) if avg_priority else 0,
            "total_students_affected": total_students_affected,
            "by_priority_level": level_counts,
            "filter_applied": {
                "course_id": course_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching priorities summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve priorities summary")

@router.post("/priorities/recompute")
async def recompute_priorities(
    course_id: Optional[str] = Query(None, description="Recompute for specific course only"),
    db: AsyncSession = Depends(get_db)
):
    """
    Recompute priority scores using current weight configuration
    """
    try:
        logger.info(f"Starting priority recomputation for course_id: {course_id}")
        
        # Get current weights
        current_weights = await get_active_weights()
        scoring_engine = PriorityScoring(current_weights)
        
        # Clear existing priorities (for the specified course or all)
        delete_query = delete(Priority)
        if course_id:
            delete_query = delete_query.where(Priority.course_id == course_id)
        await db.execute(delete_query)
        
        # Group similar feedback for processing
        feedback_groups = await group_similar_feedback(db, course_id)
        
        new_priorities = []
        processed_count = 0
        
        for feedback_group in feedback_groups:
            if not feedback_group:
                continue
                
            # Generate issue summary
            issue_summary = await generate_issue_summary(feedback_group)
            course_id_for_group = feedback_group[0].course_id
            
            # Calculate priority score
            score_result = scoring_engine.calculate_priority_score(
                feedback_group, issue_summary, course_id_for_group
            )
            
            # Create new Priority record
            priority = Priority(
                course_id=course_id_for_group,
                issue_summary=issue_summary,
                priority_score=score_result["priority_score"],
                impact_score=score_result["factor_scores"]["impact"],
                urgency_score=score_result["factor_scores"]["urgency"],
                effort_score=score_result["factor_scores"]["effort"],
                strategic_score=score_result["factor_scores"]["strategic"],
                trend_score=score_result["factor_scores"]["trend"],
                students_affected=score_result["students_affected"],
                feedback_ids=score_result["feedback_ids"],
                evidence=score_result["evidence"]
            )
            
            db.add(priority)
            new_priorities.append(priority)
            processed_count += 1
        
        await db.commit()
        
        logger.info(f"Completed priority recomputation: {processed_count} priorities created")
        
        return {
            "success": True,
            "message": f"Successfully recomputed {processed_count} priority recommendations",
            "priorities_created": processed_count,
            "course_id_filter": course_id,
            "weights_used": {
                "impact": current_weights.impact_weight,
                "urgency": current_weights.urgency_weight,
                "effort": current_weights.effort_weight,
                "strategic": current_weights.strategic_weight,
                "trend": current_weights.trend_weight
            },
            "recomputation_timestamp": current_weights.updated_at.isoformat() if current_weights.updated_at else None
        }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error recomputing priorities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to recompute priorities: {str(e)}")

@router.get("/priorities/{priority_id}")
async def get_priority_details(
    priority_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a specific priority recommendation
    """
    try:
        query = select(Priority).where(Priority.id == priority_id)
        result = await db.execute(query)
        priority = result.scalar_one_or_none()
        
        if not priority:
            raise HTTPException(status_code=404, detail="Priority recommendation not found")
        
        # Get current weights to show how score was calculated
        current_weights = await get_active_weights()
        
        return {
            "id": priority.id,
            "course_id": priority.course_id,
            "issue_summary": priority.issue_summary,
            "priority_score": priority.priority_score,
            "priority_label": PriorityScoring.PRIORITY_LABELS[priority.priority_score]["label"],
            "priority_action": PriorityScoring.PRIORITY_LABELS[priority.priority_score]["action"],
            "priority_color": PriorityScoring.PRIORITY_LABELS[priority.priority_score]["color"],
            "students_affected": priority.students_affected,
            "factor_scores": {
                "impact": priority.impact_score,
                "urgency": priority.urgency_score,
                "effort": priority.effort_score,
                "strategic": priority.strategic_score,
                "trend": priority.trend_score
            },
            "score_calculation": {
                "formula": "impact×weight + urgency×weight + effort×weight + strategic×weight + trend×weight",
                "breakdown": {
                    "impact_contribution": priority.impact_score * current_weights.impact_weight,
                    "urgency_contribution": priority.urgency_score * current_weights.urgency_weight,
                    "effort_contribution": priority.effort_score * current_weights.effort_weight,
                    "strategic_contribution": priority.strategic_score * current_weights.strategic_weight,
                    "trend_contribution": priority.trend_score * current_weights.trend_weight
                },
                "weights_used": {
                    "impact": current_weights.impact_weight,
                    "urgency": current_weights.urgency_weight,
                    "effort": current_weights.effort_weight,
                    "strategic": current_weights.strategic_weight,
                    "trend": current_weights.trend_weight
                }
            },
            "evidence": priority.evidence,
            "feedback_ids": priority.feedback_ids,
            "created_at": priority.created_at.isoformat() if priority.created_at else None,
            "updated_at": priority.updated_at.isoformat() if priority.updated_at else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching priority details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve priority details")