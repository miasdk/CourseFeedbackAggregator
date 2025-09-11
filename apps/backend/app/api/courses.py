"""Course API routes for course management and synchronization."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional

from ..config.database import get_db
from ..controllers.course_controller import CourseController
from ..models import Course

router = APIRouter()

@router.get("/courses")
async def get_courses(
    status: Optional[str] = Query(None, description="Filter by status: active, completed, archived"),
    source: Optional[str] = Query(None, description="Filter by source: canvas, zoho"),
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get all courses with optional filtering."""
    controller = CourseController()
    courses = await controller.get_all_courses(db, status=status, source=source)
    
    return {
        "success": True,
        "count": len(courses),
        "courses": [
            {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "instructor_name": course.instructor_name,
                "canvas_id": course.canvas_id,
                "zoho_program_id": course.zoho_program_id,
                "start_date": course.start_date.isoformat() if course.start_date else None,
                "end_date": course.end_date.isoformat() if course.end_date else None,
                "status": course.status,
                "created_at": course.created_at.isoformat(),
                "updated_at": course.updated_at.isoformat(),
                "has_canvas_integration": course.canvas_id is not None,
                "has_zoho_integration": course.zoho_program_id is not None,
                "is_unified": course.canvas_id is not None and course.zoho_program_id is not None
            } for course in courses
        ]
    }

@router.get("/courses/{course_id}")
async def get_course_details(
    course_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get detailed information for a specific course."""
    controller = CourseController()
    course = await controller.get_course_by_id(db, course_id)
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {
        "success": True,
        "course": {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "instructor_name": course.instructor_name,
            "canvas_id": course.canvas_id,
            "zoho_program_id": course.zoho_program_id,
            "start_date": course.start_date.isoformat() if course.start_date else None,
            "end_date": course.end_date.isoformat() if course.end_date else None,
            "status": course.status,
            "course_metadata": course.course_metadata,
            "created_at": course.created_at.isoformat(),
            "updated_at": course.updated_at.isoformat(),
            "integration_status": {
                "canvas": "connected" if course.canvas_id else "not_connected",
                "zoho": "connected" if course.zoho_program_id else "not_connected",
                "unified": course.canvas_id is not None and course.zoho_program_id is not None
            }
        }
    }

@router.post("/courses/sync/canvas")
async def sync_canvas_courses(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Sync all Canvas courses into the database."""
    controller = CourseController()
    result = await controller.sync_canvas_courses(db)
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error'))
    
    return result

@router.post("/courses/sync/zoho")
async def sync_zoho_surveys(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Sync Zoho survey data and programs into the database."""
    controller = CourseController()
    result = await controller.sync_zoho_surveys_and_programs(db)
    
    if not result.get('success'):
        raise HTTPException(status_code=500, detail=result.get('error'))
    
    return result

@router.post("/courses/sync/all")
async def sync_all_courses(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Sync both Canvas courses and Zoho programs."""
    controller = CourseController()
    
    # Sync Canvas courses
    canvas_result = await controller.sync_canvas_courses(db)
    
    # Sync Zoho programs
    zoho_result = await controller.sync_zoho_programs(db)
    
    return {
        "success": True,
        "canvas_sync": canvas_result,
        "zoho_sync": zoho_result,
        "summary": {
            "canvas_courses": canvas_result.get('courses_synced', 0) if canvas_result.get('success') else 0,
            "zoho_programs": zoho_result.get('programs_synced', 0) if zoho_result.get('success') else 0,
            "total_synced": (
                (canvas_result.get('courses_synced', 0) if canvas_result.get('success') else 0) +
                (zoho_result.get('programs_synced', 0) if zoho_result.get('success') else 0)
            )
        }
    }

@router.post("/courses/map")
async def map_canvas_to_zoho(
    canvas_id: str,
    zoho_program_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Manually map a Canvas course to a Zoho program."""
    controller = CourseController()
    result = await controller.map_canvas_to_zoho(db, canvas_id, zoho_program_id)
    
    if not result.get('success'):
        raise HTTPException(status_code=400, detail=result.get('error'))
    
    return result

@router.get("/courses/canvas/{canvas_id}")
async def get_course_by_canvas_id(
    canvas_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get course by Canvas ID."""
    controller = CourseController()
    course = await controller.get_course_by_canvas_id(db, canvas_id)
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    return {
        "success": True,
        "course": {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "canvas_id": course.canvas_id,
            "status": course.status
        }
    }

@router.get("/courses/zoho/{zoho_program_id}")
async def get_course_by_zoho_id(
    zoho_program_id: str,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get course by Zoho program ID."""
    controller = CourseController()
    course = await controller.get_course_by_zoho_id(db, zoho_program_id)
    
    if not course:
        raise HTTPException(status_code=404, detail="Program not found")
    
    return {
        "success": True,
        "course": {
            "course_id": course.course_id,
            "course_name": course.course_name,
            "zoho_program_id": course.zoho_program_id,
            "status": course.status
        }
    }

@router.get("/courses/statistics")
async def get_course_statistics(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Get course statistics and integration status."""
    controller = CourseController()
    
    # Get all courses
    all_courses = await controller.get_all_courses(db)
    
    canvas_courses = [c for c in all_courses if c.canvas_id]
    zoho_courses = [c for c in all_courses if c.zoho_program_id]
    unified_courses = [c for c in all_courses if c.canvas_id and c.zoho_program_id]
    
    return {
        "success": True,
        "statistics": {
            "total_courses": len(all_courses),
            "canvas_courses": len(canvas_courses),
            "zoho_programs": len(zoho_courses),
            "unified_courses": len(unified_courses),
            "integration_rate": round(len(unified_courses) / len(all_courses) * 100, 1) if all_courses else 0,
            "status_breakdown": {
                "active": len([c for c in all_courses if c.status == 'active']),
                "completed": len([c for c in all_courses if c.status == 'completed']),
                "archived": len([c for c in all_courses if c.status == 'archived'])
            }
        }
    }

@router.post("/courses/test/zoho-auth")
async def test_zoho_authentication() -> Dict[str, Any]:
    """Test and refresh Zoho authentication."""
    controller = CourseController()
    result = controller.zoho_auth.test_api_access()
    return result