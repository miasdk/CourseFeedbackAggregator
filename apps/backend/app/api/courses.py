"""
Canvas Course API Endpoints

Provides endpoints for syncing and retrieving Canvas courses.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from dateutil import parser as date_parser

from app.core.database import get_db
from app.core.config import get_settings, Settings
from app.models.course import Course
from app.schemas.course import CourseResponse, CourseListResponse
import httpx

router = APIRouter(prefix="/courses", tags=["courses"])


def parse_canvas_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse Canvas date string to datetime object"""
    if not date_str:
        return None
    try:
        return date_parser.parse(date_str)
    except (ValueError, TypeError):
        return None


async def fetch_canvas_courses(settings: Settings) -> List[dict]:
    """
    Fetch all courses from Canvas API with pagination support.

    Canvas API uses Link headers (RFC 5988) for pagination.
    We follow the 'next' links until there are no more pages.
    """
    courses = []
    url = f"{settings.CANVAS_BASE_URL}/api/v1/accounts/{settings.CANVAS_ACCOUNT_ID}/courses"

    params = {
        "per_page": settings.CANVAS_PER_PAGE,
        "include[]": ["total_students", "term"]
    }

    async with httpx.AsyncClient(timeout=settings.CANVAS_API_TIMEOUT) as client:
        while url:
            response = await client.get(
                url,
                headers=settings.canvas_headers,
                params=params if url == f"{settings.CANVAS_BASE_URL}/api/v1/accounts/{settings.CANVAS_ACCOUNT_ID}/courses" else None
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"Canvas API error: {response.status_code}"
                )

            page_courses = response.json()
            courses.extend(page_courses)

            # Parse Link header for next page
            link_header = response.headers.get("Link", "")
            next_url = None

            for link in link_header.split(","):
                if 'rel="next"' in link:
                    next_url = link[link.find("<") + 1:link.find(">")]
                    break

            url = next_url
            params = None  # Don't send params for subsequent requests

    return courses


@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_canvas_courses(
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> dict:
    """
    Sync courses from Canvas API to database.

    Fetches all courses from Canvas and upserts them into the database.
    Returns count of synced courses.
    """
    try:
        # Fetch courses from Canvas
        canvas_courses = await fetch_canvas_courses(settings)

        synced_count = 0

        for canvas_course in canvas_courses:
            # Parse Canvas course data
            course_data = {
                "canvas_id": canvas_course["id"],
                "name": canvas_course.get("name"),
                "course_code": canvas_course.get("course_code"),
                "workflow_state": canvas_course.get("workflow_state"),
                "start_date": parse_canvas_date(canvas_course.get("start_at")),
                "end_date": parse_canvas_date(canvas_course.get("end_at")),
                "total_students": canvas_course.get("total_students", 0),
                "enrollment_term_id": canvas_course.get("enrollment_term_id"),
                "updated_at": datetime.utcnow()
            }

            # Upsert course (insert or update if canvas_id exists)
            stmt = insert(Course).values(**course_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["canvas_id"],
                set_={
                    "name": stmt.excluded.name,
                    "course_code": stmt.excluded.course_code,
                    "workflow_state": stmt.excluded.workflow_state,
                    "start_date": stmt.excluded.start_date,
                    "end_date": stmt.excluded.end_date,
                    "total_students": stmt.excluded.total_students,
                    "enrollment_term_id": stmt.excluded.enrollment_term_id,
                    "updated_at": stmt.excluded.updated_at
                }
            )

            await db.execute(stmt)
            synced_count += 1

        await db.commit()

        return {
            "status": "success",
            "synced_count": synced_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    except httpx.HTTPError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch from Canvas API: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync courses: {str(e)}"
        )


@router.get("/", response_model=CourseListResponse)
async def get_courses(
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get courses from database.

    Args:
        active_only: Filter to only active courses (excludes OLD, CLOSED courses)
        skip: Number of courses to skip (pagination)
        limit: Maximum number of courses to return
    """
    query = select(Course).offset(skip).limit(limit)

    result = await db.execute(query)
    courses = result.scalars().all()

    # Convert to Pydantic models and filter if needed
    course_responses = [CourseResponse.model_validate(course) for course in courses]

    if active_only:
        course_responses = [c for c in course_responses if c.is_active]

    # Get total count
    count_query = select(Course)
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    return CourseListResponse(
        courses=course_responses,
        total=len(course_responses),
        skip=skip,
        limit=limit
    )


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific course by ID.

    Args:
        course_id: Database ID (not Canvas ID)
    """
    query = select(Course).where(Course.id == course_id)
    result = await db.execute(query)
    course = result.scalar_one_or_none()

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )

    return CourseResponse.model_validate(course)
