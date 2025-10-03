"""
Canvas Quiz Submissions API Client

Handles all quiz submission-related Canvas API operations for extracting student responses.

Official Canvas API Endpoints:
- GET /api/v1/courses/:course_id/quizzes/:quiz_id/submissions (list all submissions)
- GET /api/v1/courses/:course_id/quizzes/:quiz_id/submissions/:id (get single submission with answers)

Documentation:
- Quiz Submissions: https://canvas.instructure.com/doc/api/quiz_submissions.html
"""

from typing import List, Dict, Any, Optional
from .base import CanvasBaseClient


class CanvasSubmissionsClient(CanvasBaseClient):
    """
    Client for Canvas Quiz Submissions API.

    Provides methods to extract student responses from quiz submissions:
    - List all submissions for a quiz
    - Get detailed submission with student answers
    - Extract submission data for analysis

    Example usage:
        client = CanvasSubmissionsClient()
        submissions = await client.get_all_for_quiz(course_id=123, quiz_id=456)
        submission_detail = await client.get_by_id(course_id=123, quiz_id=456, submission_id=789)
    """

    async def get_all_for_quiz(
        self,
        course_id: int,
        quiz_id: int,
        include_submission_history: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch all quiz submissions for a specific quiz.

        Uses pagination to retrieve complete list of submissions.

        Official API: GET /api/v1/courses/:course_id/quizzes/:quiz_id/submissions

        Args:
            course_id: Canvas course ID
            quiz_id: Canvas quiz ID
            include_submission_history: Include detailed submission data (recommended: True)

        Returns:
            List of quiz submission dictionaries from Canvas API

        Example response:
            [
                {
                    "id": 789,
                    "quiz_id": 456,
                    "user_id": null,  # Anonymous submission
                    "submission_id": 1234,
                    "started_at": "2024-12-10T14:30:00Z",
                    "finished_at": "2024-12-10T14:45:00Z",
                    "end_at": "2024-12-15T23:59:00Z",
                    "attempt": 1,
                    "score": null,  # Ungraded survey
                    "kept_score": null,
                    "fudge_points": 0,
                    "workflow_state": "complete",
                    "submission_data": [  # Only present if include_submission_history=True
                        {
                            "question_id": 100,
                            "answer": "The course content was excellent...",
                            "text": "The course content was excellent..."
                        },
                        {
                            "question_id": 101,
                            "answer": "4",
                            "text": "Very Good"
                        },
                        ...
                    ]
                },
                ...
            ]

        Canvas API Field Reference:
            - id (int): Canvas quiz submission identifier
            - quiz_id (int): Parent quiz ID
            - user_id (int): Student's Canvas ID (null for anonymous)
            - submission_id (int): Associated submission record
            - started_at (datetime): When student started quiz
            - finished_at (datetime): When student submitted quiz
            - attempt (int): Attempt number (for multiple attempts)
            - score (float): Quiz score
            - kept_score (float): Final recorded score
            - workflow_state (str): 'untaken', 'pending_review', 'complete', 'settings_only', 'preview'
            - submission_data (array): Student's answers (requires include[]=submission_history)
        """
        endpoint = f"/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions"

        params = {}
        if include_submission_history:
            params["include[]"] = ["submission_history"]

        # Canvas quiz submissions endpoint returns {"quiz_submissions": [...]}
        # _get_paginated will return a list of these response objects
        response_pages = await self._get_paginated(endpoint, params)

        # Extract quiz_submissions arrays from each page and flatten
        all_submissions = []
        for page_data in response_pages:
            if isinstance(page_data, dict) and "quiz_submissions" in page_data:
                all_submissions.extend(page_data["quiz_submissions"])

        return all_submissions

    async def get_by_id(
        self,
        course_id: int,
        quiz_id: int,
        submission_id: int
    ) -> Dict[str, Any]:
        """
        Fetch a single quiz submission with detailed answers.

        Official API: GET /api/v1/courses/:course_id/quizzes/:quiz_id/submissions/:id
                      ?include[]=submission_history

        Args:
            course_id: Canvas course ID
            quiz_id: Canvas quiz ID
            submission_id: Canvas quiz submission ID

        Returns:
            Single quiz submission dictionary with detailed answers

        Raises:
            httpx.HTTPStatusError: If submission not found (404)

        Example response:
            {
                "id": 789,
                "quiz_id": 456,
                "user_id": null,
                "started_at": "2024-12-10T14:30:00Z",
                "finished_at": "2024-12-10T14:45:00Z",
                "attempt": 1,
                "workflow_state": "complete",
                "submission_data": [
                    {
                        "question_id": 100,
                        "answer": "The course content was excellent...",
                        "text": "The course content was excellent..."
                    },
                    ...
                ]
            }
        """
        endpoint = f"/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{submission_id}"

        params = {
            "include[]": ["submission_history"]
        }

        return await self._get_single(endpoint, params)

    async def get_submission_questions(
        self,
        quiz_submission_id: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch student answers for a quiz submission.

        Official API: GET /api/v1/quiz_submissions/:quiz_submission_id/questions

        This is the correct Canvas API endpoint for retrieving student answers.
        Returns the actual answers provided by students for each question.

        Args:
            quiz_submission_id: Canvas quiz submission ID

        Returns:
            List of question/answer dictionaries

        Example response:
            [
                {
                    "id": 100,
                    "flagged": false,
                    "answer": "The course content was excellent...",
                    "answers": null
                },
                {
                    "id": 101,
                    "flagged": false,
                    "answer": 4,
                    "answers": null
                }
            ]
        """
        endpoint = f"/api/v1/quiz_submissions/{quiz_submission_id}/questions"

        params = {
            "include[]": ["quiz_question"]
        }

        response = await self._get_single(endpoint, params)

        # Canvas returns {"quiz_submission_questions": [...]}
        return response.get("quiz_submission_questions", [])

    def extract_answers_from_submission(
        self,
        submission: Dict[str, Any],
        questions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract and format student answers from a quiz submission.

        Combines submission_data with question metadata for easier processing.

        Args:
            submission: Canvas quiz submission dict (with submission_data)
            questions: List of quiz questions from Canvas Quizzes API

        Returns:
            List of formatted answer dictionaries

        Example return:
            [
                {
                    "question_id": 100,
                    "question_name": "Overall Satisfaction",
                    "question_text": "How would you rate the course overall?",
                    "question_type": "multiple_choice_question",
                    "points_possible": 0,
                    "student_answer": "4",
                    "student_answer_text": "Very Good",
                    "student_answer_id": 456
                },
                {
                    "question_id": 101,
                    "question_name": "Improvements",
                    "question_text": "What could be improved?",
                    "question_type": "essay_question",
                    "points_possible": 0,
                    "student_answer": "The course content was excellent, but the pacing was too fast in Module 3.",
                    "student_answer_text": "The course content was excellent, but the pacing was too fast in Module 3.",
                    "student_answer_id": null
                },
                ...
            ]
        """
        # Create question lookup by ID
        question_lookup = {q['id']: q for q in questions}

        # Extract submission_data (answers)
        submission_data = []

        # Check if submission has submission_history with submission_data
        if 'submission_history' in submission and submission['submission_history']:
            # Get the most recent submission attempt
            latest_attempt = submission['submission_history'][-1]
            submission_data = latest_attempt.get('submission_data', [])
        elif 'submission_data' in submission:
            # Direct submission_data field
            submission_data = submission['submission_data']

        # Format answers with question metadata
        formatted_answers = []

        for answer_data in submission_data:
            question_id = answer_data.get('question_id')
            question = question_lookup.get(question_id, {})

            formatted_answer = {
                # Question metadata
                "question_id": question_id,
                "question_name": question.get('question_name', ''),
                "question_text": question.get('question_text', ''),
                "question_type": question.get('question_type', ''),
                "points_possible": question.get('points_possible', 0),

                # Student's answer
                "student_answer": answer_data.get('answer'),
                "student_answer_text": answer_data.get('text'),
                "student_answer_id": answer_data.get('answer_id')
            }

            formatted_answers.append(formatted_answer)

        return formatted_answers


# Testing
if __name__ == "__main__":
    import asyncio

    async def test_submissions_client():
        """Test Canvas Submissions API client"""
        print("\n" + "=" * 70)
        print("CANVAS SUBMISSIONS API CLIENT TEST")
        print("=" * 70 + "\n")

        client = CanvasSubmissionsClient()

        try:
            # Test 1: Get a quiz to test with
            print("TEST 1: Finding a quiz with submissions...")
            from .courses import CanvasCoursesClient
            from .quizzes import CanvasQuizzesClient

            courses_client = CanvasCoursesClient()
            quizzes_client = CanvasQuizzesClient()

            # Get first course
            courses = await courses_client.get_all(account_id=client.settings.CANVAS_ACCOUNT_ID)
            if not courses:
                print("ERROR: No courses found")
                return

            # Find a course with quizzes
            test_course = None
            test_quiz = None

            for course in courses[:10]:  # Check first 10 courses
                course_id = course['id']
                quizzes = await quizzes_client.get_all_for_course(course_id)

                if quizzes:
                    test_course = course
                    test_quiz = quizzes[0]  # Use first quiz
                    break

            if not test_quiz:
                print("ERROR: No quizzes found in first 10 courses")
                return

            course_id = test_course['id']
            course_name = test_course.get('name', 'Unnamed')
            quiz_id = test_quiz['id']
            quiz_title = test_quiz.get('title', 'Untitled')

            print(f"SUCCESS: Using quiz [{quiz_id}] {quiz_title}")
            print(f"         in course [{course_id}] {course_name}\n")

            # Test 2: Fetch quiz submissions
            print(f"TEST 2: Fetching submissions for quiz {quiz_id}...")
            submissions = await client.get_all_for_quiz(course_id, quiz_id, include_submission_history=True)
            print(f"SUCCESS: Found {len(submissions)} submissions\n")

            if submissions:
                # Show first 2 submissions
                print("Sample submissions:")
                for submission in submissions[:2]:
                    sub_id = submission.get('id')
                    user_id = submission.get('user_id', 'anonymous')
                    state = submission.get('workflow_state', 'unknown')
                    attempt = submission.get('attempt', 1)
                    score = submission.get('score', 'N/A')

                    print(f"  [{sub_id}] User: {user_id}, State: {state}, Attempt: {attempt}, Score: {score}")

                    # Check for submission_data
                    has_data = 'submission_data' in submission or \
                               ('submission_history' in submission and submission.get('submission_history'))
                    print(f"       Has answer data: {has_data}")

                # Test 3: Extract and format answers
                if len(submissions) > 0:
                    print("\nTEST 3: Extracting formatted answers from first submission...")
                    first_submission = submissions[0]

                    # Get quiz questions
                    questions = await quizzes_client.get_questions(course_id, quiz_id)

                    # Extract answers
                    formatted_answers = client.extract_answers_from_submission(first_submission, questions)

                    print(f"SUCCESS: Extracted {len(formatted_answers)} answers\n")

                    if formatted_answers:
                        print("Sample answers:")
                        for answer in formatted_answers[:2]:
                            q_id = answer.get('question_id')
                            q_name = answer.get('question_name', 'Unnamed')
                            q_type = answer.get('question_type', 'unknown')
                            student_answer = str(answer.get('student_answer', ''))[:60]

                            print(f"  Question [{q_id}] {q_name} ({q_type})")
                            print(f"       Answer: {student_answer}...")

            print("\n" + "=" * 70)
            print("SUCCESS: All Canvas Submissions API tests passed!")
            print("=" * 70 + "\n")

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            print("\nTroubleshooting:")
            print("1. Verify CANVAS_API_TOKEN in .env")
            print("2. Verify quiz has submissions")
            print("3. Check Canvas API token permissions")
            raise

    asyncio.run(test_submissions_client())
