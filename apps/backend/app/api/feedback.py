"""
Student Feedback API Endpoints

Provides endpoints for syncing and retrieving student feedback from Canvas quiz submissions.
Integrates response processing, categorization, and aggregation.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.core.config import get_settings, Settings
from app.models.canvas_survey import CanvasSurvey
from app.models.student_feedback import StudentFeedback
from app.models.feedback_response import FeedbackResponse
from app.models.course import Course
from app.schemas.feedback import (
    StudentFeedbackResponse,
    StudentFeedbackList,
    FeedbackResponseCreate,
    CourseFeedbackSummary,
    CourseFeedbackDetail,
    CategoryBreakdown,
    FeedbackSyncResponse
)

from app.services.canvas.submissions import CanvasSubmissionsClient
from app.services.canvas.quizzes import CanvasQuizzesClient
from app.services.canvas.reports import CanvasQuizReportsClient
from app.services.response_processor import ResponseProcessor
from app.services.feedback_aggregation import FeedbackAggregator

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/sync/{survey_id}", status_code=status.HTTP_200_OK)
async def sync_student_feedback(
    survey_id: str,
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings)
) -> FeedbackSyncResponse:
    """
    Sync student feedback submissions for a specific survey.

    This endpoint:
    1. Fetches all quiz submissions from Canvas API
    2. Parses and categorizes each student response
    3. Stores submissions and individual question answers
    4. Updates survey response count

    Args:
        survey_id: Survey UUID

    Returns:
        FeedbackSyncResponse with sync statistics
    """
    try:
        # Get survey from database
        survey_uuid = UUID(survey_id)
        survey_query = select(CanvasSurvey).where(CanvasSurvey.id == survey_uuid)
        survey_result = await db.execute(survey_query)
        survey = survey_result.scalar_one_or_none()

        if not survey:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Survey with id {survey_id} not found"
            )

        # Get course for Canvas IDs
        course_query = select(Course).where(Course.id == survey.course_id)
        course_result = await db.execute(course_query)
        course = course_result.scalar_one_or_none()

        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Course for survey {survey_id} not found"
            )

        # Extract IDs as primitives to avoid SQLAlchemy lazy-loading issues
        course_canvas_id = course.canvas_id
        course_db_id = course.id
        survey_canvas_quiz_id = survey.canvas_quiz_id
        survey_db_id = survey.id

        # Fetch quiz questions for metadata
        quizzes_client = CanvasQuizzesClient()
        questions = await quizzes_client.get_questions(
            course_id=course_canvas_id,
            quiz_id=survey_canvas_quiz_id
        )

        # Fetch student responses via Quiz Reports CSV
        reports_client = CanvasQuizReportsClient()

        try:
            student_responses = await reports_client.get_all_student_responses(
                course_id=course_canvas_id,
                quiz_id=survey_canvas_quiz_id
            )
        except Exception as e:
            print(f"Error fetching quiz reports: {e}")
            return FeedbackSyncResponse(
                status="error",
                survey_id=survey_db_id,
                course_id=course_db_id,
                submissions_found=0,
                submissions_stored=0,
                responses_parsed=0,
                critical_issues_detected=0,
                timestamp=datetime.utcnow()
            )

        if not student_responses:
            return FeedbackSyncResponse(
                status="no_submissions",
                survey_id=survey_db_id,
                course_id=course_db_id,
                submissions_found=0,
                submissions_stored=0,
                responses_parsed=0,
                critical_issues_detected=0,
                timestamp=datetime.utcnow()
            )

        # Process each student's responses
        processor = ResponseProcessor()
        submissions_stored = 0
        responses_parsed = 0
        critical_issues_detected = 0

        for csv_student_data in student_responses:
            try:
                # Parse CSV student response
                submission_metadata, parsed_responses = processor.parse_csv_student_response(
                    csv_student_data, questions
                )

                # Store student feedback
                feedback_data = {
                    "canvas_survey_id": survey_db_id,
                    "course_id": course_db_id,
                    **submission_metadata
                }

                # Upsert student feedback
                # CSV data uses student_canvas_id for uniqueness (no canvas_submission_id available)
                stmt = insert(StudentFeedback).values(**feedback_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=["canvas_survey_id", "student_canvas_id"],
                    set_={
                        "workflow_state": stmt.excluded.workflow_state,
                        "raw_response_data": stmt.excluded.raw_response_data,
                        "processed_at": datetime.utcnow()
                    }
                ).returning(StudentFeedback.id)

                result = await db.execute(stmt)
                student_feedback_id = result.scalar_one()
                submissions_stored += 1

                # Store individual responses
                for response_data in parsed_responses:
                    response_data["student_feedback_id"] = student_feedback_id

                    # Upsert feedback response
                    response_stmt = insert(FeedbackResponse).values(**response_data)
                    response_stmt = response_stmt.on_conflict_do_nothing()
                    await db.execute(response_stmt)
                    responses_parsed += 1

                    if response_data.get("is_critical_issue"):
                        critical_issues_detected += 1

            except Exception as e:
                student_id = csv_student_data.get('student_canvas_id', 'unknown')
                print(f"Error processing CSV student response for student {student_id}: {e}")
                continue

        # Update survey response count using primitive update
        update_stmt = (
            select(CanvasSurvey)
            .where(CanvasSurvey.id == survey_db_id)
        )
        survey_to_update = (await db.execute(update_stmt)).scalar_one()
        survey_to_update.response_count = submissions_stored
        survey_to_update.last_synced = datetime.utcnow()

        await db.commit()

        return FeedbackSyncResponse(
            status="success",
            survey_id=survey_db_id,
            course_id=course_db_id,
            submissions_found=len(student_responses),
            submissions_stored=submissions_stored,
            responses_parsed=responses_parsed,
            critical_issues_detected=critical_issues_detected,
            timestamp=datetime.utcnow()
        )

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync student feedback: {str(e)}"
        )


@router.get("/surveys/{survey_id}", response_model=StudentFeedbackList)
async def get_survey_feedback(
    survey_id: str,
    skip: int = 0,
    limit: int = 100,
    include_responses: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all student feedback submissions for a survey.

    Args:
        survey_id: Survey UUID
        skip: Number of submissions to skip (pagination)
        limit: Maximum number of submissions to return
        include_responses: Include individual question responses

    Returns:
        Paginated list of StudentFeedbackResponse objects
    """
    try:
        survey_uuid = UUID(survey_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid survey ID format"
        )

    query = (
        select(StudentFeedback)
        .where(StudentFeedback.canvas_survey_id == survey_uuid)
        .offset(skip)
        .limit(limit)
        .order_by(StudentFeedback.finished_at.desc())
    )

    result = await db.execute(query)
    submissions = result.scalars().all()

    # Get total count
    count_query = select(StudentFeedback).where(
        StudentFeedback.canvas_survey_id == survey_uuid
    )
    count_result = await db.execute(count_query)
    total = len(count_result.scalars().all())

    # Convert to response schemas
    submission_responses = []
    for submission in submissions:
        response_data = StudentFeedbackResponse.model_validate(submission)

        if include_responses:
            # Load responses if requested
            responses_query = select(FeedbackResponse).where(
                FeedbackResponse.student_feedback_id == submission.id
            )
            responses_result = await db.execute(responses_query)
            response_data.responses = responses_result.scalars().all()

        submission_responses.append(response_data)

    return StudentFeedbackList(
        submissions=submission_responses,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/courses/{course_id}/summary", response_model=CourseFeedbackSummary)
async def get_course_feedback_summary(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get aggregated feedback summary for a course.

    Provides course-level metrics for priority scoring:
    - Response rate
    - Average ratings
    - Critical issue counts
    - Improvement themes

    Args:
        course_id: Database course ID

    Returns:
        CourseFeedbackSummary with aggregated metrics
    """
    aggregator = FeedbackAggregator(db)
    summary = await aggregator.get_course_summary(course_id)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No feedback found for course {course_id}"
        )

    return summary


@router.get("/courses/{course_id}/detail", response_model=CourseFeedbackDetail)
async def get_course_feedback_detail(
    course_id: int,
    include_recent_submissions: bool = Query(True, description="Include recent submissions"),
    recent_limit: int = Query(10, description="Number of recent submissions to include"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed feedback analysis for a course.

    Includes:
    - Aggregated summary metrics
    - Category breakdowns
    - Recent student submissions

    Args:
        course_id: Database course ID
        include_recent_submissions: Include recent submissions
        recent_limit: Number of recent submissions to include

    Returns:
        CourseFeedbackDetail with full analysis
    """
    aggregator = FeedbackAggregator(db)

    # Get summary
    summary = await aggregator.get_course_summary(course_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No feedback found for course {course_id}"
        )

    # Get category breakdowns
    category_breakdowns = await aggregator.get_category_breakdowns(course_id)

    # Get recent submissions if requested
    recent_submissions = []
    if include_recent_submissions:
        recent_query = (
            select(StudentFeedback)
            .where(StudentFeedback.course_id == course_id)
            .order_by(StudentFeedback.finished_at.desc())
            .limit(recent_limit)
        )
        recent_result = await db.execute(recent_query)
        recent_submissions = [
            StudentFeedbackResponse.model_validate(s)
            for s in recent_result.scalars().all()
        ]

    # Build detailed response
    return CourseFeedbackDetail(
        **summary.model_dump(),
        category_breakdowns=category_breakdowns,
        recent_submissions=recent_submissions
    )


@router.get("/courses/{course_id}/categories", response_model=List[CategoryBreakdown])
async def get_course_category_breakdowns(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get category-level breakdown of responses.

    Provides per-category analytics:
    - Question count
    - Response count
    - Average rating
    - Critical issue count

    Args:
        course_id: Database course ID

    Returns:
        List of CategoryBreakdown objects
    """
    aggregator = FeedbackAggregator(db)
    breakdowns = await aggregator.get_category_breakdowns(course_id)

    if not breakdowns:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No category data found for course {course_id}"
        )

    return breakdowns


@router.get("/courses/{course_id}/themes")
async def get_course_improvement_themes(
    course_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get improvement theme counts for a course.

    Returns theme counts needed for priority scoring effort calculation.

    Args:
        course_id: Database course ID

    Returns:
        Dictionary mapping theme names to counts
    """
    aggregator = FeedbackAggregator(db)
    themes = await aggregator.get_improvement_themes_for_course(course_id)

    if not themes:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No theme data found for course {course_id}"
        )

    return themes
