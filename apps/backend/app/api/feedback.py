from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
import logging

from ..database import get_db, Feedback
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/feedback")
async def get_feedback(
    course_id: Optional[str] = Query(None, description="Filter by specific course ID"),
    source: Optional[str] = Query(None, description="Filter by source (canvas/zoho)"),
    severity: Optional[str] = Query(None, description="Filter by severity level"),
    limit: int = Query(100, description="Maximum number of results"),
    offset: int = Query(0, description="Number of results to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregated feedback data with filtering options
    """
    try:
        # Build query with filters
        query = select(Feedback).where(Feedback.is_active == True)
        
        if course_id:
            query = query.where(Feedback.course_id == course_id)
        if source:
            query = query.where(Feedback.source == source)
        if severity:
            query = query.where(Feedback.severity == severity)
        
        # Add pagination
        query = query.offset(offset).limit(limit)
        query = query.order_by(Feedback.created_at.desc())
        
        # Execute query
        result = await db.execute(query)
        feedback_items = result.scalars().all()
        
        # Get total count for pagination info
        count_query = select(func.count(Feedback.id)).where(Feedback.is_active == True)
        if course_id:
            count_query = count_query.where(Feedback.course_id == course_id)
        if source:
            count_query = count_query.where(Feedback.source == source)
        if severity:
            count_query = count_query.where(Feedback.severity == severity)
            
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        # Format response
        feedback_data = []
        for item in feedback_items:
            feedback_data.append({
                "id": item.id,
                "course_id": item.course_id,
                "course_name": item.course_name,
                "student_email": item.student_email,
                "student_name": item.student_name,
                "feedback_text": item.feedback_text,
                "rating": item.rating,
                "severity": item.severity,
                "source": item.source,
                "source_id": item.source_id,
                "created_at": item.created_at.isoformat() if item.created_at else None,
                "last_modified": item.last_modified.isoformat() if item.last_modified else None
            })
        
        return {
            "feedback": feedback_data,
            "pagination": {
                "total": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + len(feedback_items) < total_count
            },
            "filters_applied": {
                "course_id": course_id,
                "source": source,
                "severity": severity
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve feedback data")

@router.get("/feedback/summary")
async def get_feedback_summary(
    course_id: Optional[str] = Query(None, description="Filter by specific course ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary statistics of feedback data
    """
    try:
        # Base query
        base_query = select(Feedback).where(Feedback.is_active == True)
        if course_id:
            base_query = base_query.where(Feedback.course_id == course_id)
        
        # Total feedback count
        count_query = select(func.count(Feedback.id)).where(Feedback.is_active == True)
        if course_id:
            count_query = count_query.where(Feedback.course_id == course_id)
        count_result = await db.execute(count_query)
        total_feedback = count_result.scalar()
        
        # Count by source
        source_query = select(
            Feedback.source,
            func.count(Feedback.id).label('count')
        ).where(Feedback.is_active == True)
        if course_id:
            source_query = source_query.where(Feedback.course_id == course_id)
        source_query = source_query.group_by(Feedback.source)
        
        source_result = await db.execute(source_query)
        source_counts = {row.source: row.count for row in source_result}
        
        # Count by severity
        severity_query = select(
            Feedback.severity,
            func.count(Feedback.id).label('count')
        ).where(Feedback.is_active == True)
        if course_id:
            severity_query = severity_query.where(Feedback.course_id == course_id)
        severity_query = severity_query.group_by(Feedback.severity)
        
        severity_result = await db.execute(severity_query)
        severity_counts = {row.severity: row.count for row in severity_result}
        
        # Average rating
        rating_query = select(func.avg(Feedback.rating)).where(
            Feedback.is_active == True,
            Feedback.rating.isnot(None)
        )
        if course_id:
            rating_query = rating_query.where(Feedback.course_id == course_id)
        rating_result = await db.execute(rating_query)
        avg_rating = rating_result.scalar()
        
        # Unique courses
        courses_query = select(func.count(func.distinct(Feedback.course_id))).where(
            Feedback.is_active == True
        )
        if course_id:
            courses_query = courses_query.where(Feedback.course_id == course_id)
        courses_result = await db.execute(courses_query)
        unique_courses = courses_result.scalar()
        
        # Unique students
        students_query = select(func.count(func.distinct(Feedback.student_email))).where(
            Feedback.is_active == True,
            Feedback.student_email.isnot(None)
        )
        if course_id:
            students_query = students_query.where(Feedback.course_id == course_id)
        students_result = await db.execute(students_query)
        unique_students = students_result.scalar()
        
        return {
            "total_feedback": total_feedback,
            "unique_courses": unique_courses,
            "unique_students": unique_students,
            "average_rating": round(avg_rating, 2) if avg_rating else None,
            "by_source": source_counts,
            "by_severity": severity_counts,
            "filter_applied": {
                "course_id": course_id
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching feedback summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve feedback summary")

@router.get("/feedback/courses")
async def get_courses_with_feedback(
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of courses that have feedback data
    """
    try:
        query = select(
            Feedback.course_id,
            Feedback.course_name,
            func.count(Feedback.id).label('feedback_count'),
            func.count(func.distinct(Feedback.student_email)).label('student_count'),
            func.avg(Feedback.rating).label('avg_rating')
        ).where(
            Feedback.is_active == True
        ).group_by(
            Feedback.course_id,
            Feedback.course_name
        ).order_by(
            func.count(Feedback.id).desc()
        )
        
        result = await db.execute(query)
        courses = result.all()
        
        courses_data = []
        for course in courses:
            courses_data.append({
                "course_id": course.course_id,
                "course_name": course.course_name,
                "feedback_count": course.feedback_count,
                "student_count": course.student_count,
                "average_rating": round(course.avg_rating, 2) if course.avg_rating else None
            })
        
        return {
            "courses": courses_data,
            "total_courses": len(courses_data)
        }
        
    except Exception as e:
        logger.error(f"Error fetching courses: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve courses with feedback")