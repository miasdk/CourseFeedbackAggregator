"""
Feedback Aggregation Service

Aggregates student feedback responses into course-level metrics for priority scoring.
Calculates ratings, counts critical issues, extracts themes, and generates summaries.
"""

from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from collections import Counter

from app.models.student_feedback import StudentFeedback
from app.models.feedback_response import FeedbackResponse
from app.models.canvas_survey import CanvasSurvey
from app.models.course import Course
from app.schemas.feedback import CourseFeedbackSummary, ImprovementTheme, CategoryBreakdown


class FeedbackAggregator:
    """
    Service for aggregating student feedback data.

    Provides methods to calculate course-level metrics from individual
    student feedback responses for use in priority scoring.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_course_summary(self, course_id: int) -> Optional[CourseFeedbackSummary]:
        """
        Generate comprehensive feedback summary for a course.

        Aggregates all student responses for the course into metrics
        needed for priority score calculation.

        Args:
            course_id: Database course ID

        Returns:
            CourseFeedbackSummary with all aggregated metrics,
            or None if no feedback data exists

        Example:
            >>> aggregator = FeedbackAggregator(db)
            >>> summary = await aggregator.get_course_summary(5)
            >>> summary.total_responses
            45
            >>> summary.average_course_rating
            Decimal('3.4')
        """
        # Get course info
        course_query = select(Course).where(Course.id == course_id)
        course_result = await self.db.execute(course_query)
        course = course_result.scalar_one_or_none()

        if not course:
            return None

        # Get all feedback for this course
        feedback_query = select(StudentFeedback).where(
            StudentFeedback.course_id == course_id
        )
        feedback_result = await self.db.execute(feedback_query)
        feedbacks = feedback_result.scalars().all()

        if not feedbacks:
            # Return empty summary with course info
            return CourseFeedbackSummary(
                course_id=course_id,
                course_name=course.name,
                total_students=course.total_students or 0,
                total_responses=0,
                response_rate=Decimal('0'),
                average_course_rating=None,
                rating_count=0,
                critical_issues_count=0,
                improvement_suggestions_count=0,
                top_improvement_themes=[],
                last_feedback_date=None,
                content_responses=0,
                instructor_responses=0,
                technical_responses=0,
                assessment_responses=0,
                interaction_responses=0
            )

        # Calculate participation metrics
        total_responses = len(feedbacks)
        total_students = course.total_students or total_responses
        response_rate = Decimal(str(total_responses / max(total_students, 1)))

        # Get last feedback date
        last_feedback_date = max(
            (f.finished_at for f in feedbacks if f.finished_at),
            default=None
        )

        # Aggregate response-level metrics
        rating_metrics = await self._calculate_rating_metrics(course_id)
        issue_metrics = await self._calculate_issue_metrics(course_id)
        theme_metrics = await self._calculate_theme_metrics(course_id)
        category_metrics = await self._calculate_category_metrics(course_id)

        return CourseFeedbackSummary(
            course_id=course_id,
            course_name=course.name,
            total_students=total_students,
            total_responses=total_responses,
            response_rate=response_rate,
            average_course_rating=rating_metrics["average_rating"],
            rating_count=rating_metrics["rating_count"],
            critical_issues_count=issue_metrics["critical_count"],
            improvement_suggestions_count=issue_metrics["suggestion_count"],
            top_improvement_themes=theme_metrics,
            last_feedback_date=last_feedback_date,
            content_responses=category_metrics.get("course_content", 0),
            instructor_responses=category_metrics.get("instructor", 0),
            technical_responses=category_metrics.get("technical", 0),
            assessment_responses=category_metrics.get("assessment", 0),
            interaction_responses=category_metrics.get("interaction", 0)
        )

    async def _calculate_rating_metrics(self, course_id: int) -> Dict:
        """Calculate average rating and count from numeric responses."""
        # Get all numeric responses for this course
        query = select(FeedbackResponse).join(
            StudentFeedback,
            FeedbackResponse.student_feedback_id == StudentFeedback.id
        ).where(
            and_(
                StudentFeedback.course_id == course_id,
                FeedbackResponse.response_numeric.is_not(None)
            )
        )

        result = await self.db.execute(query)
        responses = result.scalars().all()

        if not responses:
            return {"average_rating": None, "rating_count": 0}

        ratings = [float(r.response_numeric) for r in responses if r.response_numeric]
        average_rating = Decimal(str(sum(ratings) / len(ratings))) if ratings else None

        return {
            "average_rating": average_rating,
            "rating_count": len(ratings)
        }

    async def _calculate_issue_metrics(self, course_id: int) -> Dict:
        """Count critical issues and improvement suggestions."""
        # Get all responses for this course
        query = select(FeedbackResponse).join(
            StudentFeedback,
            FeedbackResponse.student_feedback_id == StudentFeedback.id
        ).where(
            StudentFeedback.course_id == course_id
        )

        result = await self.db.execute(query)
        responses = result.scalars().all()

        critical_count = sum(1 for r in responses if r.is_critical_issue)
        suggestion_count = sum(1 for r in responses if r.contains_improvement_suggestion)

        return {
            "critical_count": critical_count,
            "suggestion_count": suggestion_count
        }

    async def _calculate_theme_metrics(self, course_id: int) -> List[ImprovementTheme]:
        """
        Extract improvement themes from text responses.

        Analyzes text responses to identify common improvement themes
        (content_updates, instructional_clarity, technical_platform, etc.)
        """
        from app.services.response_processor import ResponseProcessor

        processor = ResponseProcessor()

        # Get all text responses for this course
        query = select(FeedbackResponse).join(
            StudentFeedback,
            FeedbackResponse.student_feedback_id == StudentFeedback.id
        ).where(
            and_(
                StudentFeedback.course_id == course_id,
                FeedbackResponse.response_text.is_not(None)
            )
        )

        result = await self.db.execute(query)
        responses = result.scalars().all()

        # Extract themes from each response
        all_themes = []
        for response in responses:
            if response.response_text:
                analysis = processor.analyze_text_response(response.response_text)
                all_themes.extend(analysis["detected_themes"])

        # Count theme frequencies
        theme_counts = Counter(all_themes)
        total_themes = sum(theme_counts.values())

        # Convert to ImprovementTheme objects
        improvement_themes = [
            ImprovementTheme(
                theme=theme,
                count=count,
                percentage=round((count / total_themes) * 100, 1) if total_themes > 0 else 0
            )
            for theme, count in theme_counts.most_common()
        ]

        return improvement_themes

    async def _calculate_category_metrics(self, course_id: int) -> Dict[str, int]:
        """Count responses by question category."""
        # Get all responses grouped by category
        query = select(FeedbackResponse).join(
            StudentFeedback,
            FeedbackResponse.student_feedback_id == StudentFeedback.id
        ).where(
            StudentFeedback.course_id == course_id
        )

        result = await self.db.execute(query)
        responses = result.scalars().all()

        # Count by category
        category_counts = Counter(r.question_category for r in responses if r.question_category)

        return dict(category_counts)

    async def get_category_breakdowns(self, course_id: int) -> List[CategoryBreakdown]:
        """
        Get detailed breakdown of responses by category.

        Provides per-category analytics including question count,
        response count, average rating, and critical issue count.

        Args:
            course_id: Database course ID

        Returns:
            List of CategoryBreakdown objects

        Example:
            >>> breakdowns = await aggregator.get_category_breakdowns(5)
            >>> content_breakdown = next(b for b in breakdowns if b.category == "course_content")
            >>> content_breakdown.average_rating
            Decimal('3.8')
        """
        # Get all responses with their feedback data
        query = select(FeedbackResponse).join(
            StudentFeedback,
            FeedbackResponse.student_feedback_id == StudentFeedback.id
        ).where(
            StudentFeedback.course_id == course_id
        )

        result = await self.db.execute(query)
        responses = result.scalars().all()

        # Group responses by category
        category_data = {}
        for response in responses:
            category = response.question_category or "other"

            if category not in category_data:
                category_data[category] = {
                    "questions": set(),
                    "responses": [],
                    "ratings": [],
                    "critical_issues": 0
                }

            category_data[category]["questions"].add(response.canvas_question_id)
            category_data[category]["responses"].append(response)

            if response.response_numeric:
                category_data[category]["ratings"].append(float(response.response_numeric))

            if response.is_critical_issue:
                category_data[category]["critical_issues"] += 1

        # Build CategoryBreakdown objects
        breakdowns = []
        for category, data in category_data.items():
            average_rating = None
            if data["ratings"]:
                average_rating = Decimal(str(sum(data["ratings"]) / len(data["ratings"])))

            breakdowns.append(CategoryBreakdown(
                category=category,
                question_count=len(data["questions"]),
                response_count=len(data["responses"]),
                average_rating=average_rating,
                critical_issues=data["critical_issues"]
            ))

        return breakdowns

    async def get_improvement_themes_for_course(self, course_id: int) -> Dict[str, int]:
        """
        Get improvement theme counts for effort estimation.

        Returns theme counts needed for the priority scoring effort calculation.

        Args:
            course_id: Database course ID

        Returns:
            Dictionary mapping theme names to counts

        Example:
            >>> themes = await aggregator.get_improvement_themes_for_course(5)
            >>> themes
            {
                "instructional_clarity": 12,
                "technical_platform": 8,
                "content_updates": 5,
                ...
            }
        """
        theme_metrics = await self._calculate_theme_metrics(course_id)

        # Convert to simple dict for priority scoring
        return {theme.theme: theme.count for theme in theme_metrics}


# Testing
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("FEEDBACK AGGREGATION SERVICE")
    print("=" * 70)
    print("\nThis service requires database connection and data.")
    print("Run after Phase 2 implementation is complete to test with real data.")
    print("\nKey methods:")
    print("  - get_course_summary(course_id) → CourseFeedbackSummary")
    print("  - get_category_breakdowns(course_id) → List[CategoryBreakdown]")
    print("  - get_improvement_themes_for_course(course_id) → Dict[str, int]")
    print("\n" + "=" * 70 + "\n")
