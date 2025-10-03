"""
Canvas Quizzes API Client

Handles all quiz-related Canvas API operations.

Official Canvas API Endpoints:
- GET /api/v1/courses/:course_id/quizzes (list quizzes in course)
- GET /api/v1/courses/:course_id/quizzes/:id (get single quiz)
- GET /api/v1/courses/:course_id/quizzes/:id/questions (get quiz questions)

Documentation:
- Quizzes: https://canvas.instructure.com/doc/api/quizzes.html
- Quiz Questions: https://canvas.instructure.com/doc/api/quiz_questions.html
"""

from typing import List, Dict, Any
from .base import CanvasBaseClient


class CanvasQuizzesClient(CanvasBaseClient):
    """
    Client for Canvas Quizzes API.

    Provides methods to interact with Canvas quizzes:
    - List all quizzes in a course (with pagination)
    - Get single quiz by ID
    - Get quiz questions

    Example usage:
        client = CanvasQuizzesClient()
        quizzes = await client.get_all_for_course(course_id=123)
        quiz = await client.get_by_id(course_id=123, quiz_id=456)
        questions = await client.get_questions(course_id=123, quiz_id=456)
    """

    async def get_all_for_course(self, course_id: int) -> List[Dict[str, Any]]:
        """
        Fetch all quizzes for a specific course.

        Uses pagination to retrieve complete list of quizzes.

        Official API: GET /api/v1/courses/:course_id/quizzes

        Args:
            course_id: Canvas course ID (NOT database ID)

        Returns:
            List of quiz dictionaries from Canvas API

        Example response:
            [
                {
                    "id": 456,
                    "title": "End of Course Evaluation",
                    "quiz_type": "survey",
                    "points_possible": 0,
                    "published": true,
                    "anonymous_submissions": true,
                    "question_count": 15,
                    "description": "Please provide feedback...",
                    "due_at": "2024-12-15T23:59:00Z",
                    "lock_at": null,
                    "unlock_at": "2024-12-01T00:00:00Z"
                },
                ...
            ]

        Canvas API Field Reference:
            - id (int): Canvas quiz identifier
            - title (str): Quiz title
            - quiz_type (str): 'practice_quiz', 'assignment', 'graded_survey', 'survey'
            - points_possible (int): Total points (0 for ungraded surveys)
            - published (bool): Whether quiz is published
            - anonymous_submissions (bool): Whether submissions are anonymous
            - question_count (int): Number of questions
            - description (str): Quiz description/instructions
            - due_at (datetime): Quiz due date
            - lock_at (datetime): When quiz becomes unavailable
            - unlock_at (datetime): When quiz becomes available
        """
        endpoint = f"/api/v1/courses/{course_id}/quizzes"
        return await self._get_paginated(endpoint)

    async def get_by_id(self, course_id: int, quiz_id: int) -> Dict[str, Any]:
        """
        Fetch a single quiz by ID.

        Official API: GET /api/v1/courses/:course_id/quizzes/:id

        Args:
            course_id: Canvas course ID
            quiz_id: Canvas quiz ID

        Returns:
            Single quiz dictionary from Canvas API

        Raises:
            httpx.HTTPStatusError: If quiz not found (404)

        Example response:
            {
                "id": 456,
                "title": "End of Course Evaluation",
                "quiz_type": "survey",
                "points_possible": 0,
                "published": true,
                "anonymous_submissions": true,
                "question_count": 15,
                ...
            }
        """
        endpoint = f"/api/v1/courses/{course_id}/quizzes/{quiz_id}"
        return await self._get_single(endpoint)

    async def get_questions(self, course_id: int, quiz_id: int) -> List[Dict[str, Any]]:
        """
        Fetch all questions for a specific quiz.

        Uses pagination to retrieve complete list of questions.

        Official API: GET /api/v1/courses/:course_id/quizzes/:quiz_id/questions

        Args:
            course_id: Canvas course ID
            quiz_id: Canvas quiz ID

        Returns:
            List of question dictionaries from Canvas API

        Example response:
            [
                {
                    "id": 789,
                    "quiz_id": 456,
                    "question_name": "Overall Satisfaction",
                    "question_text": "How would you rate the course overall?",
                    "question_type": "multiple_choice_question",
                    "points_possible": 0,
                    "position": 1,
                    "answers": [
                        {
                            "id": 1,
                            "text": "Excellent",
                            "weight": 100
                        },
                        {
                            "id": 2,
                            "text": "Good",
                            "weight": 0
                        },
                        ...
                    ]
                },
                {
                    "id": 790,
                    "quiz_id": 456,
                    "question_name": "Improvement Suggestions",
                    "question_text": "What could be improved?",
                    "question_type": "essay_question",
                    "points_possible": 0,
                    "position": 2
                },
                ...
            ]

        Canvas API Field Reference:
            - id (int): Canvas question identifier
            - quiz_id (int): Parent quiz ID
            - question_name (str): Question name/label
            - question_text (str): Full question text
            - question_type (str): Type of question (see below)
            - points_possible (int): Points for correct answer
            - position (int): Display order
            - answers (array): Possible answers (for multiple choice/matching)

        Question Types (from Canvas API):
            - essay_question: Long text response
            - multiple_choice_question: Single selection
            - multiple_answers_question: Multiple selections
            - true_false_question: True/False selection
            - short_answer_question: Brief text response
            - numerical_question: Numeric answer
            - matching_question: Match pairs
            - fill_in_multiple_blanks_question: Fill in blanks
            - text_only_question: Informational text (no answer)
        """
        endpoint = f"/api/v1/courses/{course_id}/quizzes/{quiz_id}/questions"
        return await self._get_paginated(endpoint)

    async def get_statistics(
        self,
        course_id: int,
        quiz_id: int
    ) -> Dict[str, Any]:
        """
        Fetch quiz statistics including answer-level data with user_ids.

        This endpoint provides aggregated statistics showing which students
        selected which answers for each question. This is the PRIMARY method
        for extracting individual student quiz responses from Canvas.

        Official API: GET /api/v1/courses/:course_id/quizzes/:quiz_id/statistics

        Args:
            course_id: Canvas course ID
            quiz_id: Canvas quiz ID

        Returns:
            Quiz statistics dict containing question_statistics array

        Example response structure:
            {
                "quiz_statistics": [{
                    "id": "123",
                    "question_statistics": [
                        {
                            "id": "3627",
                            "question_type": "multiple_choice_question",
                            "question_text": "How would you rate...",
                            "responses": 81,
                            "answers": [
                                {
                                    "id": "5773",
                                    "text": "Excellent",
                                    "correct": true,
                                    "responses": 19,
                                    "user_ids": [21089, 907, 5385, ...],
                                    "user_names": ["Emily Voytecek", "Meg Phillips", ...]
                                },
                                ...
                            ]
                        },
                        {
                            "id": "3628",
                            "question_type": "essay_question",
                            "question_text": "What was your favorite part...",
                            "responses": 81,
                            "answers": [],  # Essay questions don't have predefined answers
                            "answered": [
                                {
                                    "user_id": 21089,
                                    "text": "The case study module. The speaker's anecdotes..."
                                },
                                ...
                            ]
                        }
                    ]
                }]
            }

        Note:
            For multiple choice questions, use the user_ids arrays in each answer
            For essay/text questions, use the answered array with user_id and text
        """
        endpoint = f"/api/v1/courses/{course_id}/quizzes/{quiz_id}/statistics"
        return await self._get_single(endpoint)


# Testing
if __name__ == "__main__":
    import asyncio

    async def test_quizzes_client():
        """Test Canvas Quizzes API client"""
        print("\n" + "=" * 70)
        print("CANVAS QUIZZES API CLIENT TEST")
        print("=" * 70 + "\n")

        client = CanvasQuizzesClient()

        try:
            # Test 1: Get a course to test with
            print("TEST 1: Fetching a test course...")
            from .courses import CanvasCoursesClient
            courses_client = CanvasCoursesClient()
            courses = await courses_client.get_all(account_id=client.settings.CANVAS_ACCOUNT_ID)

            if not courses:
                print("ERROR: No courses found to test with")
                return

            test_course = courses[0]
            course_id = test_course['id']
            course_name = test_course.get('name', 'Unnamed')
            print(f"SUCCESS: Using course [{course_id}] {course_name}\n")

            # Test 2: Fetch quizzes for course
            print(f"TEST 2: Fetching quizzes for course {course_id}...")
            quizzes = await client.get_all_for_course(course_id)
            print(f"SUCCESS: Found {len(quizzes)} quizzes\n")

            if quizzes:
                # Show first 3 quizzes
                print("Sample quizzes:")
                for quiz in quizzes[:3]:
                    quiz_id = quiz.get('id')
                    title = quiz.get('title', 'Untitled')
                    quiz_type = quiz.get('quiz_type', 'unknown')
                    published = quiz.get('published', False)
                    anonymous = quiz.get('anonymous_submissions', False)
                    questions = quiz.get('question_count', 0)

                    print(f"  [{quiz_id}] {title}")
                    print(f"       Type: {quiz_type}, Published: {published}, Anonymous: {anonymous}, Questions: {questions}")

                if len(quizzes) > 3:
                    print(f"  ... and {len(quizzes) - 3} more quizzes\n")

                # Test 3: Get quiz questions
                first_quiz_id = quizzes[0]['id']
                print(f"TEST 3: Fetching questions for quiz {first_quiz_id}...")
                questions = await client.get_questions(course_id, first_quiz_id)
                print(f"SUCCESS: Found {len(questions)} questions\n")

                if questions:
                    print("Sample questions:")
                    for question in questions[:2]:
                        q_id = question.get('id')
                        q_name = question.get('question_name', 'Unnamed')
                        q_type = question.get('question_type', 'unknown')
                        q_text_preview = (question.get('question_text', '')[:60] + "...") if question.get('question_text') else ""

                        print(f"  [{q_id}] {q_name}")
                        print(f"       Type: {q_type}")
                        print(f"       Text: {q_text_preview}")

            print("\n" + "=" * 70)
            print("SUCCESS: All Canvas Quizzes API tests passed!")
            print("=" * 70 + "\n")

        except Exception as e:
            print(f"ERROR: {e}")
            print("\nTroubleshooting:")
            print("1. Verify CANVAS_API_TOKEN in .env")
            print("2. Verify course has quizzes")
            print("3. Check Canvas API token permissions")
            raise

    asyncio.run(test_quizzes_client())
