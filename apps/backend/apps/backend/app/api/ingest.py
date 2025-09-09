from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Dict, Any
import logging
from datetime import datetime

from ..database import get_db, Feedback
from ..clients.canvas_client import CanvasClient
from ..clients.zoho_client import ZohoClient
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/ingest/canvas")
async def ingest_canvas_data(
    background_tasks: BackgroundTasks,
    course_id: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger Canvas LMS data ingestion
    """
    try:
        if not settings.canvas_token:
            raise HTTPException(status_code=400, detail="Canvas API token not configured")
        
        # Add background task for data ingestion
        background_tasks.add_task(process_canvas_ingestion, course_id, db)
        
        return {
            "success": True,
            "message": "Canvas data ingestion started",
            "course_id_filter": course_id,
            "status": "processing",
            "estimated_duration": "2-5 minutes"
        }
        
    except Exception as e:
        logger.error(f"Error starting Canvas ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start Canvas data ingestion")

@router.post("/ingest/zoho")
async def ingest_zoho_data(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger Zoho CRM data ingestion
    """
    try:
        if not settings.zoho_access_token:
            raise HTTPException(status_code=400, detail="Zoho API token not configured")
        
        # Add background task for data ingestion
        background_tasks.add_task(process_zoho_ingestion, db)
        
        return {
            "success": True,
            "message": "Zoho CRM data ingestion started", 
            "status": "processing",
            "estimated_duration": "3-8 minutes"
        }
        
    except Exception as e:
        logger.error(f"Error starting Zoho ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start Zoho data ingestion")

@router.post("/ingest/all")
async def ingest_all_data(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger data ingestion from both Canvas and Zoho
    """
    try:
        # Check API tokens
        missing_tokens = []
        if not settings.canvas_token:
            missing_tokens.append("Canvas")
        if not settings.zoho_access_token:
            missing_tokens.append("Zoho")
        
        if missing_tokens:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing API tokens for: {', '.join(missing_tokens)}"
            )
        
        # Add background tasks for both sources
        background_tasks.add_task(process_canvas_ingestion, None, db)
        background_tasks.add_task(process_zoho_ingestion, db)
        
        return {
            "success": True,
            "message": "Full data ingestion started from Canvas and Zoho",
            "status": "processing",
            "estimated_duration": "5-10 minutes",
            "sources": ["Canvas LMS", "Zoho CRM"]
        }
        
    except Exception as e:
        logger.error(f"Error starting full ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start data ingestion")

@router.get("/ingest/status")
async def get_ingestion_status(
    db: AsyncSession = Depends(get_db)
):
    """
    Get status of data ingestion and current data metrics
    """
    try:
        # Get total feedback count
        total_query = select(func.count(Feedback.id)).where(Feedback.is_active == True)
        total_result = await db.execute(total_query)
        total_feedback = total_result.scalar()
        
        # Get count by source
        canvas_query = select(func.count(Feedback.id)).where(
            Feedback.is_active == True, 
            Feedback.source == 'canvas'
        )
        canvas_result = await db.execute(canvas_query)
        canvas_count = canvas_result.scalar()
        
        zoho_query = select(func.count(Feedback.id)).where(
            Feedback.is_active == True,
            Feedback.source == 'zoho'
        )
        zoho_result = await db.execute(zoho_query)
        zoho_count = zoho_result.scalar()
        
        # Get latest ingestion timestamps
        latest_canvas_query = select(func.max(Feedback.created_at)).where(
            Feedback.source == 'canvas'
        )
        latest_canvas_result = await db.execute(latest_canvas_query)
        latest_canvas = latest_canvas_result.scalar()
        
        latest_zoho_query = select(func.max(Feedback.created_at)).where(
            Feedback.source == 'zoho'
        )
        latest_zoho_result = await db.execute(latest_zoho_query)
        latest_zoho = latest_zoho_result.scalar()
        
        # Get unique courses count
        courses_query = select(func.count(func.distinct(Feedback.course_id))).where(
            Feedback.is_active == True
        )
        courses_result = await db.execute(courses_query)
        unique_courses = courses_result.scalar()
        
        return {
            "ingestion_status": "idle",  # In production, track active ingestion jobs
            "data_summary": {
                "total_feedback": total_feedback,
                "by_source": {
                    "canvas": canvas_count,
                    "zoho": zoho_count
                },
                "unique_courses": unique_courses
            },
            "last_ingestion": {
                "canvas": latest_canvas.isoformat() if latest_canvas else None,
                "zoho": latest_zoho.isoformat() if latest_zoho else None
            },
            "api_configuration": {
                "canvas_configured": bool(settings.canvas_token),
                "zoho_configured": bool(settings.zoho_access_token)
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching ingestion status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve ingestion status")

async def process_canvas_ingestion(course_id: str, db: AsyncSession):
    """
    Background task to process Canvas data ingestion
    """
    try:
        logger.info(f"Starting Canvas data ingestion for course_id: {course_id}")
        
        canvas_client = CanvasClient()
        
        # Extract feedback from Canvas
        if course_id:
            raw_feedback = await canvas_client.extract_feedback_from_course(course_id)
        else:
            raw_feedback = await canvas_client.sync_all_feedback()
        
        # Convert to database objects
        feedback_objects = await canvas_client.convert_to_feedback_objects(raw_feedback)
        
        # Save to database
        saved_count = 0
        for feedback in feedback_objects:
            # Check if feedback already exists (avoid duplicates)
            existing_query = select(Feedback).where(
                Feedback.source_id == feedback.source_id,
                Feedback.source == 'canvas'
            )
            existing_result = await db.execute(existing_query)
            existing = existing_result.scalar_one_or_none()
            
            if not existing:
                db.add(feedback)
                saved_count += 1
        
        await db.commit()
        
        logger.info(f"Canvas ingestion completed: {saved_count} new feedback items saved")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Canvas ingestion failed: {str(e)}")

async def process_zoho_ingestion(db: AsyncSession):
    """
    Background task to process Zoho data ingestion
    """
    try:
        logger.info("Starting Zoho CRM data ingestion")
        
        zoho_client = ZohoClient()
        
        # Extract feedback from Zoho CRM
        raw_feedback = await zoho_client.sync_all_feedback()
        
        # Convert to database objects
        feedback_objects = await zoho_client.convert_to_feedback_objects(raw_feedback)
        
        # Save to database
        saved_count = 0
        for feedback in feedback_objects:
            # Check if feedback already exists (avoid duplicates)
            existing_query = select(Feedback).where(
                Feedback.source_id == feedback.source_id,
                Feedback.source == 'zoho'
            )
            existing_result = await db.execute(existing_query)
            existing = existing_result.scalar_one_or_none()
            
            if not existing:
                db.add(feedback)
                saved_count += 1
        
        await db.commit()
        
        logger.info(f"Zoho ingestion completed: {saved_count} new feedback items saved")
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Zoho ingestion failed: {str(e)}")

@router.delete("/ingest/cleanup")
async def cleanup_old_data(
    source: str = None,
    older_than_days: int = 90,
    dry_run: bool = True,
    db: AsyncSession = Depends(get_db)
):
    """
    Clean up old or invalid feedback data
    """
    try:
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=older_than_days)
        
        # Build cleanup query
        cleanup_query = select(Feedback).where(
            Feedback.created_at < cutoff_date,
            Feedback.is_active == True
        )
        
        if source:
            cleanup_query = cleanup_query.where(Feedback.source == source)
        
        result = await db.execute(cleanup_query)
        items_to_cleanup = result.scalars().all()
        
        if dry_run:
            return {
                "dry_run": True,
                "items_found": len(items_to_cleanup),
                "cutoff_date": cutoff_date.isoformat(),
                "source_filter": source,
                "message": f"Would mark {len(items_to_cleanup)} items as inactive"
            }
        else:
            # Mark items as inactive instead of deleting
            for item in items_to_cleanup:
                item.is_active = False
            
            await db.commit()
            
            return {
                "success": True,
                "items_cleaned": len(items_to_cleanup),
                "cutoff_date": cutoff_date.isoformat(),
                "source_filter": source,
                "action": "marked_inactive"
            }
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cleanup old data")