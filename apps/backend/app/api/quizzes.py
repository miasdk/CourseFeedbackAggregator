"""
Canvas Quiz/Survey API Endpoints

Provides endpoints for syncing and retrieving Canvas quizzes/surveys.
Integrates with survey detection to identify feedback surveys.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from decimal import Decimal

from app.core.database import get_db
from app.core.config import get_settings, Settings
from app.models.canvas_survey import CanvasSurvey
from app.models.course import Course
from app.schemas.quiz import CanvasSurveyResponse, CanvasSurveyList

from app.services.canvas.quizzes import CanvasQuizzesClient
from app.services.survey_detector import SurveyDetector

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.post("/sync", status_code=status.HTTP_200_OK)
async def sync_quizzes_for_all_courses(
    min_confidence: float = 0.50,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> dict:
    """
    Sync quizzes from Canvas for all synced courses and identify feedback surveys.

    This endpoint:
    1. Fetches all courses from database
    2. For each course, fetches quizzes from Canvas API
    3. Uses survey detector to identify feedback surveys
    4. Stores identified surveys in database with confidence scores

    Args:
        min_confidence: Minimum confidence score to store survey (default: 0.50)

    Returns:
        {
            "status": "success",
            "total_courses_checked": int,
            "total_quizzes_found": int,
            "surveys_identified": int,
            "high_confidence_surveys": int,
            "timestamp": str
        }
    """
    try:
        # Get all active courses from database
        courses_query = select(Course)
        courses_result = await db.execute(courses_query)
        courses = courses_result.scalars().all()

        if not courses:
            return {
                "status": "no_courses",
                "message": "No courses found in database. Run POST /courses/sync first.",
                "surveys_identified": 0
            }

        quizzes_client = CanvasQuizzesClient()
        detector = SurveyDetector()

        total_quizzes = 0
        surveys_identified = 0
        high_confidence = 0

        # Process each course
        for course in courses:
            try:
                # Fetch quizzes for this course from Canvas
                canvas_quizzes = await quizzes_client.get_all_for_course(course.canvas_id)
                total_quizzes += len(canvas_quizzes)

                if not canvas_quizzes:
                    continue

                # Identify surveys using detector
                identified = detector.identify_batch(canvas_quizzes)

                # Filter to surveys meeting confidence threshold
                surveys = [
                    q for q in identified
                    if q['survey_detection']['is_survey'] and
                    q['survey_detection']['confidence'] >= Decimal(str(min_confidence))
                ]

                # Store each identified survey
                for survey_data in surveys:
                    detection = survey_data['survey_detection']

                    survey_db_data = {
                        "course_id": course.id,  # Database course ID
                        "canvas_quiz_id": survey_data['id'],
                        "title": survey_data.get('title'),
                        "description": survey_data.get('description'),
                        "quiz_type": survey_data.get('quiz_type'),
                        "points_possible": survey_data.get('points_possible', 0),
                        "question_count": survey_data.get('question_count'),
                        "published": survey_data.get('published', False),
                        "anonymous_submissions": survey_data.get('anonymous_submissions', False),
                        "due_at": survey_data.get('due_at'),
                        "lock_at": survey_data.get('lock_at'),
                        "unlock_at": survey_data.get('unlock_at'),
                        "identification_confidence": detection['confidence'],
                        "last_synced": datetime.utcnow()
                    }

                    # Upsert survey
                    stmt = insert(CanvasSurvey).values(**survey_db_data)
                    stmt = stmt.on_conflict_do_update(
                        index_elements=["course_id", "canvas_quiz_id"],
                        set_={
                            "title": stmt.excluded.title,
                            "description": stmt.excluded.description,
                            "quiz_type": stmt.excluded.quiz_type,
                            "points_possible": stmt.excluded.points_possible,
                            "question_count": stmt.excluded.question_count,
                            "published": stmt.excluded.published,
                            "anonymous_submissions": stmt.excluded.anonymous_submissions,
                            "due_at": stmt.excluded.due_at,
                            "lock_at": stmt.excluded.lock_at,
                            "unlock_at": stmt.excluded.unlock_at,
                            "identification_confidence": stmt.excluded.identification_confidence,
                            "last_synced": stmt.excluded.last_synced
                        }
                    )

                    await db.execute(stmt)
                    surveys_identified += 1

                    if detection['confidence'] >= Decimal('0.80'):
                        high_confidence += 1

                # Commit after each course to avoid long-running transactions
                await db.commit()

            except Exception as e:
                # Log error but continue with other courses
                print(f"Error processing course {course.canvas_id}: {e}")
                await db.rollback()
                continue

        return {
            "status": "success",
            "total_courses_checked": len(courses),
            "total_quizzes_found": total_quizzes,
            "surveys_identified": surveys_identified,
            "high_confidence_surveys": high_confidence,
            "min_confidence_threshold": min_confidence,
            "timestamp": datetime.utcnow().isoformat()
        }

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync quizzes: {str(e)}"
        )


@router.post("/sync/{course_id}", status_code=status.HTTP_200_OK)
async def sync_quizzes_for_course(
    course_id: int,
    min_confidence: float = 0.50,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> dict:
    """
    Sync quizzes for a specific course and identify feedback surveys.

    Args:
        course_id: Database course ID (NOT Canvas ID)
        min_confidence: Minimum confidence score to store survey

    Returns:
        {
            "status": "success",
            "course_id": int,
            "course_name": str,
            "quizzes_found": int,
            "surveys_identified": int,
            "timestamp": str
        }
    """
    try:
        # Get course from database
        course_query = select(Course).where(Course.id == course_id)
        course_result = await db.execute(course_query)
        course = course_result.scalar_one_or_none()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course with id {course_id} not found"
            )

        # Fetch quizzes from Canvas
        quizzes_client = CanvasQuizzesClient()
        canvas_quizzes = await quizzes_client.get_all_for_course(course.canvas_id)

        if not canvas_quizzes:
            return {
                "status": "no_quizzes",
                "course_id": course_id,
                "course_name": course.name,
                "quizzes_found": 0,
                "surveys_identified": 0
            }

        # Identify surveys
        detector = SurveyDetector()
        identified = detector.identify_batch(canvas_quizzes)

        surveys = [
            q for q in identified
            if q['survey_detection']['is_survey'] and
            q['survey_detection']['confidence'] >= Decimal(str(min_confidence))
        ]

        surveys_count = 0

        # Store surveys
        for survey_data in surveys:
            detection = survey_data['survey_detection']

            survey_db_data = {
                "course_id": course.id,
                "canvas_quiz_id": survey_data['id'],
                "title": survey_data.get('title'),
                "description": survey_data.get('description'),
                "quiz_type": survey_data.get('quiz_type'),
                "points_possible": survey_data.get('points_possible', 0),
                "question_count": survey_data.get('question_count'),
                "published": survey_data.get('published', False),
                "anonymous_submissions": survey_data.get('anonymous_submissions', False),
                "due_at": survey_data.get('due_at'),
                "lock_at": survey_data.get('lock_at'),
                "unlock_at": survey_data.get('unlock_at'),
                "identification_confidence": detection['confidence'],
                "last_synced": datetime.utcnow()
            }

            stmt = insert(CanvasSurvey).values(**survey_db_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=["course_id", "canvas_quiz_id"],
                set_={k: v for k, v in survey_db_data.items() if k not in ['course_id', 'canvas_quiz_id']}
            )

            await db.execute(stmt)
            surveys_count += 1

        await db.commit()

        return {
            "status": "success",
            "course_id": course_id,
            "course_name": course.name,
            "quizzes_found": len(canvas_quizzes),
            "surveys_identified": surveys_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync quizzes for course: {str(e)}"
        )


@router.get("/surveys", response_model=CanvasSurveyList)
async def get_surveys(
    min_confidence: float = 0.50,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all identified feedback surveys.

    Args:
        min_confidence: Minimum confidence score to include (default: 0.50)
        skip: Number of surveys to skip (pagination)
        limit: Maximum number of surveys to return

    Returns:
        Paginated list of CanvasSurveyResponse objects
    """
    query = (
        select(CanvasSurvey)
        .where(CanvasSurvey.identification_confidence >= Decimal(str(min_confidence)))
        .offset(skip)
        .limit(limit)
        .order_by(CanvasSurvey.identification_confidence.desc())
    )

    result = await db.execute(query)
    surveys = result.scalars().all()

    # Get total count
    count_query = select(CanvasSurvey).where(
        CanvasSurvey.identification_confidence >= Decimal(str(min_confidence))
    )
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    survey_responses = [CanvasSurveyResponse.model_validate(s) for s in surveys]

    return CanvasSurveyList(
        surveys=survey_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/surveys/{survey_id}", response_model=CanvasSurveyResponse)
async def get_survey(
    survey_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific survey by ID.

    Args:
        survey_id: Survey UUID

    Returns:
        CanvasSurveyResponse
    """
    from uuid import UUID

    try:
        survey_uuid = UUID(survey_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid survey ID format"
        )

    query = select(CanvasSurvey).where(CanvasSurvey.id == survey_uuid)
    result = await db.execute(query)
    survey = result.scalar_one_or_none()

    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Survey with id {survey_id} not found"
        )

    return CanvasSurveyResponse.model_validate(survey)
