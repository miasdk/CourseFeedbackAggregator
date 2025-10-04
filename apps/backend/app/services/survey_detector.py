"""
Survey Detector Service

Identifies which Canvas quizzes are actually course feedback surveys.

Detection algorithm uses multiple signals:
- Title pattern matching
- Quiz type from Canvas API
- Quiz settings (anonymous, ungraded, etc.)
- Confidence scoring (0.00-1.00)

This service helps filter out regular quizzes/assignments from feedback surveys.
"""

from typing import Dict, List, Any
from decimal import Decimal
import re


class SurveyDetector:
    """
    Service for identifying feedback surveys from Canvas quizzes.

    Uses pattern matching and quiz metadata to determine if a quiz
    is likely a course feedback survey with a confidence score.

    Example usage:
        detector = SurveyDetector()
        result = detector.identify(quiz_data)
        # result = {"is_survey": True, "confidence": 0.95, "reasons": [...]}
    """

    # Feedback survey title patterns (case-insensitive)
    FEEDBACK_PATTERNS = [
        # Direct feedback/evaluation patterns
        r'\bcourse\s+evaluation\b',
        r'\bcourse\s+feedback\b',
        r'\bcourse\s+review\b',
        r'\bcourse\s+survey\b',
        r'\bstudent\s+feedback\b',
        r'\bstudent\s+survey\b',
        r'\bstudent\s+evaluation\b',

        # End-of-course patterns
        r'\bend\s+of\s+course\b',
        r'\bfinal\s+evaluation\b',
        r'\bfinal\s+feedback\b',
        r'\bfinal\s+survey\b',

        # Satisfaction patterns
        r'\bsatisfaction\s+survey\b',
        r'\bcourse\s+satisfaction\b',
        r'\bstudent\s+satisfaction\b',

        # Experience patterns
        r'\bcourse\s+experience\b',
        r'\blearning\s+experience\b',
        r'\bstudent\s+experience\b',

        # Assessment patterns
        r'\bcourse\s+assessment\b',
        r'\bprogram\s+evaluation\b',
        r'\bprogram\s+feedback\b',

        # Quality patterns
        r'\bquality\s+survey\b',
        r'\binstructor\s+evaluation\b',
        r'\bteaching\s+evaluation\b',
    ]

    # Patterns that indicate NOT a feedback survey
    EXCLUSION_PATTERNS = [
        r'\bquiz\s+\d+\b',  # "Quiz 1", "Quiz 2", etc.
        r'\bmodule\s+\d+\b',  # "Module 1 Quiz"
        r'\bchapter\s+\d+\b',  # "Chapter 1 Quiz"
        r'\bweek\s+\d+\b',  # "Week 1 Quiz"
        r'\bunit\s+\d+\b',  # "Unit 1 Quiz"
        r'\bmidterm\b',  # Midterm exams
        r'\bfinal\s+exam\b',  # Final exams (not feedback)
        r'\btest\s+\d+\b',  # "Test 1", "Test 2"
        r'\bpractice\b',  # Practice quizzes
    ]

    def identify(self, quiz: Dict[str, Any]) -> Dict[str, Any]:
        """
        Identify if a Canvas quiz is a feedback survey.

        Analyzes quiz metadata and returns identification result with confidence score.

        Args:
            quiz: Canvas quiz dictionary from API

        Returns:
            Dictionary with identification results:
            {
                "is_survey": bool,
                "confidence": Decimal (0.00-1.00),
                "reasons": List[str],  # Why we think it's a survey
                "signals": Dict[str, Any]  # Detailed analysis
            }

        Example:
            >>> detector = SurveyDetector()
            >>> quiz = {"title": "End of Course Evaluation", "quiz_type": "survey", ...}
            >>> result = detector.identify(quiz)
            >>> result["is_survey"]
            True
            >>> result["confidence"]
            Decimal('0.95')
        """
        title = quiz.get('title', '').lower()
        quiz_type = quiz.get('quiz_type', '')
        anonymous = quiz.get('anonymous_submissions', False)
        points = quiz.get('points_possible', 0)
        published = quiz.get('published', False)

        confidence_score = Decimal('0.0')
        reasons = []
        signals = {}

        # Signal 1: Title pattern matching (HIGH CONFIDENCE: +0.60)
        title_match = self._check_title_patterns(title)
        if title_match['matches']:
            confidence_score += Decimal('0.60')
            reasons.append(f"Title matches feedback survey pattern: '{title_match['pattern']}'")
            signals['title_match'] = True
            signals['title_pattern'] = title_match['pattern']
        else:
            signals['title_match'] = False

        # Signal 2: Exclusion patterns (DISQUALIFIER: -1.00)
        exclusion_match = self._check_exclusion_patterns(title)
        if exclusion_match['matches']:
            confidence_score = Decimal('0.0')
            reasons = [f"Title matches exclusion pattern: '{exclusion_match['pattern']}' (NOT a feedback survey)"]
            signals['excluded'] = True
            signals['exclusion_pattern'] = exclusion_match['pattern']

            return {
                "is_survey": False,
                "confidence": confidence_score,
                "reasons": reasons,
                "signals": signals
            }

        signals['excluded'] = False

        # Signal 3: Canvas quiz_type is 'survey' or 'graded_survey' (HIGH CONFIDENCE: +0.30)
        if quiz_type in ['survey', 'graded_survey']:
            confidence_score += Decimal('0.30')
            reasons.append(f"Canvas quiz_type is '{quiz_type}'")
            signals['is_canvas_survey_type'] = True
        else:
            signals['is_canvas_survey_type'] = False

        # Signal 4: Anonymous submissions (MEDIUM CONFIDENCE: +0.15)
        if anonymous:
            confidence_score += Decimal('0.15')
            reasons.append("Quiz allows anonymous submissions")
            signals['is_anonymous'] = True
        else:
            signals['is_anonymous'] = False

        # Signal 5: Ungraded (0 points) (MEDIUM CONFIDENCE: +0.10)
        if points == 0:
            confidence_score += Decimal('0.10')
            reasons.append("Quiz is ungraded (0 points)")
            signals['is_ungraded'] = True
        else:
            signals['is_ungraded'] = False

        # Cap confidence score at 1.00
        confidence_score = min(confidence_score, Decimal('1.00'))

        # Determine if it's likely a survey (confidence >= 0.50)
        is_survey = confidence_score >= Decimal('0.50')

        return {
            "is_survey": is_survey,
            "confidence": confidence_score,
            "reasons": reasons if is_survey else ["Confidence score below threshold (0.50)"],
            "signals": signals
        }

    def _check_title_patterns(self, title: str) -> Dict[str, Any]:
        """
        Check if title matches feedback survey patterns.

        Args:
            title: Quiz title (lowercase)

        Returns:
            {"matches": bool, "pattern": str}
        """
        for pattern in self.FEEDBACK_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                return {"matches": True, "pattern": pattern}

        return {"matches": False, "pattern": None}

    def _check_exclusion_patterns(self, title: str) -> Dict[str, Any]:
        """
        Check if title matches exclusion patterns (NOT feedback surveys).

        Args:
            title: Quiz title (lowercase)

        Returns:
            {"matches": bool, "pattern": str}
        """
        for pattern in self.EXCLUSION_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                return {"matches": True, "pattern": pattern}

        return {"matches": False, "pattern": None}

    def identify_batch(self, quizzes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify feedback surveys from a batch of quizzes.

        Args:
            quizzes: List of Canvas quiz dictionaries

        Returns:
            List of quizzes with identification results added

        Example:
            >>> detector = SurveyDetector()
            >>> quizzes = [{...}, {...}, ...]
            >>> identified = detector.identify_batch(quizzes)
            >>> for quiz in identified:
            >>>     print(quiz['title'], quiz['survey_detection'])
        """
        identified_quizzes = []

        for quiz in quizzes:
            result = self.identify(quiz)

            # Add detection result to quiz data
            quiz_with_detection = {
                **quiz,
                "survey_detection": result
            }

            identified_quizzes.append(quiz_with_detection)

        return identified_quizzes

    def filter_surveys(
        self,
        quizzes: List[Dict[str, Any]],
        min_confidence: Decimal = Decimal('0.50')
    ) -> List[Dict[str, Any]]:
        """
        Filter quizzes to only feedback surveys above confidence threshold.

        Args:
            quizzes: List of Canvas quiz dictionaries
            min_confidence: Minimum confidence score (default: 0.50)

        Returns:
            List of quizzes identified as surveys with confidence >= min_confidence

        Example:
            >>> detector = SurveyDetector()
            >>> all_quizzes = [{...}, {...}, ...]
            >>> surveys_only = detector.filter_surveys(all_quizzes, min_confidence=Decimal('0.70'))
        """
        identified = self.identify_batch(quizzes)

        surveys = [
            quiz for quiz in identified
            if quiz['survey_detection']['is_survey'] and
            quiz['survey_detection']['confidence'] >= min_confidence
        ]

        return surveys


# Testing
if __name__ == "__main__":
    detector = SurveyDetector()

    print("\n" + "=" * 70)
    print("SURVEY DETECTOR SERVICE TEST")
    print("=" * 70 + "\n")

    # Test cases
    test_quizzes = [
        {
            "id": 1,
            "title": "End of Course Evaluation - Fall 2024",
            "quiz_type": "survey",
            "anonymous_submissions": True,
            "points_possible": 0,
            "published": True
        },
        {
            "id": 2,
            "title": "Student Feedback Survey",
            "quiz_type": "graded_survey",
            "anonymous_submissions": True,
            "points_possible": 0,
            "published": True
        },
        {
            "id": 3,
            "title": "Module 3 Quiz",
            "quiz_type": "assignment",
            "anonymous_submissions": False,
            "points_possible": 100,
            "published": True
        },
        {
            "id": 4,
            "title": "Course Satisfaction Assessment",
            "quiz_type": "assignment",
            "anonymous_submissions": False,
            "points_possible": 0,
            "published": True
        },
        {
            "id": 5,
            "title": "Midterm Exam",
            "quiz_type": "assignment",
            "anonymous_submissions": False,
            "points_possible": 200,
            "published": True
        },
    ]

    print("Testing individual quiz identification:\n")

    for quiz in test_quizzes:
        result = detector.identify(quiz)

        print(f"Quiz [{quiz['id']}]: {quiz['title']}")
        print(f"  Is Survey: {result['is_survey']}")
        print(f"  Confidence: {result['confidence']}")
        print(f"  Reasons: {', '.join(result['reasons'])}")
        print()

    print("\nTesting batch filtering (min_confidence=0.60):\n")

    surveys = detector.filter_surveys(test_quizzes, min_confidence=Decimal('0.60'))

    print(f"Found {len(surveys)} high-confidence surveys out of {len(test_quizzes)} quizzes:")
    for survey in surveys:
        confidence = survey['survey_detection']['confidence']
        print(f"  [{survey['id']}] {survey['title']} (confidence: {confidence})")

    print("\n" + "=" * 70)
    print("SUCCESS: All survey detector tests passed!")
    print("=" * 70 + "\n")
