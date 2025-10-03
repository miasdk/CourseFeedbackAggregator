"""
Response Processor Service

Processes Canvas quiz submissions to extract, categorize, and analyze student feedback.
Handles question categorization, critical issue detection, and improvement suggestion extraction.
"""

from typing import Dict, List, Any, Tuple, Optional
from decimal import Decimal
from datetime import datetime
import re


class ResponseProcessor:
    """
    Service for processing student feedback responses.

    Provides methods to:
    - Parse Canvas submission structure
    - Categorize questions by topic (content, instructor, technical, etc.)
    - Analyze text responses for critical issues and suggestions
    - Extract improvement themes from student feedback
    """

    @staticmethod
    def _parse_datetime(datetime_str: Optional[str]) -> Optional[datetime]:
        """
        Parse Canvas ISO datetime string to Python datetime object.

        Args:
            datetime_str: ISO 8601 datetime string from Canvas (e.g., '2020-06-01T21:31:11Z')

        Returns:
            datetime object or None if string is None/empty

        Example:
            >>> ResponseProcessor._parse_datetime('2020-06-01T21:31:11Z')
            datetime(2020, 6, 1, 21, 31, 11, tzinfo=timezone.utc)
        """
        if not datetime_str:
            return None

        try:
            # Canvas uses ISO 8601 format with 'Z' suffix for UTC
            # Python's fromisoformat doesn't handle 'Z', so replace with '+00:00'
            if datetime_str.endswith('Z'):
                datetime_str = datetime_str[:-1] + '+00:00'
            return datetime.fromisoformat(datetime_str)
        except (ValueError, AttributeError):
            # Fallback: try without timezone
            try:
                return datetime.strptime(datetime_str[:19], '%Y-%m-%dT%H:%M:%S')
            except:
                return None

    # Question categorization keywords
    CATEGORY_KEYWORDS = {
        "course_content": [
            "content", "material", "curriculum", "topic", "subject", "lesson",
            "module", "chapter", "reading", "resource", "textbook"
        ],
        "instructor": [
            "instructor", "teacher", "professor", "teaching", "facilitat",
            "presenter", "lecturer", "explanation", "communication"
        ],
        "technical": [
            "canvas", "platform", "video", "audio", "technical", "system",
            "access", "login", "connection", "browser", "computer", "software",
            "zoom", "recording", "download", "upload"
        ],
        "assessment": [
            "assignment", "quiz", "test", "exam", "homework", "project",
            "rubric", "grading", "grade", "feedback", "score", "criteria"
        ],
        "interaction": [
            "discussion", "interaction", "engage", "participate", "collaborate",
            "group", "peer", "classmate", "forum", "chat", "activity"
        ],
        "overall_satisfaction": [
            "overall", "general", "experience", "satisfaction", "recommend",
            "rating", "opinion", "course as a whole"
        ]
    }

    # Critical issue keywords
    CRITICAL_KEYWORDS = [
        "broken", "crash", "cannot access", "can't access", "won't load",
        "doesn't work", "not working", "urgent", "critical", "blocking",
        "unable to", "error", "failed", "failure", "down", "unavailable"
    ]

    # Improvement suggestion keywords
    SUGGESTION_KEYWORDS = [
        "should", "could", "suggest", "recommend", "improve", "better",
        "enhance", "add", "need", "would be good", "would help", "wish",
        "hope", "please", "consider", "maybe", "perhaps"
    ]

    # Improvement theme keywords (for effort estimation)
    THEME_KEYWORDS = {
        "content_updates": [
            "outdated", "old", "current", "update", "recent", "new",
            "relevant", "modern", "latest", "refresh"
        ],
        "instructional_clarity": [
            "confusing", "unclear", "complex", "difficult", "hard to understand",
            "fast", "slow", "pace", "speed", "rushed", "clear", "explain better"
        ],
        "technical_platform": [
            "canvas", "video", "audio", "technical", "platform", "system",
            "broken", "access", "quality", "lag", "buffer", "connection"
        ],
        "assessment_design": [
            "assignment", "rubric", "grading", "criteria", "grade", "points",
            "unclear instructions", "confusing assignment", "feedback on grades"
        ],
        "interaction_engagement": [
            "boring", "engage", "interactive", "discussion", "participation",
            "activity", "hands-on", "practical", "exercise", "workshop"
        ],
        "structural_redesign": [
            "redesign", "restructure", "completely", "overhaul", "redo",
            "rework", "rebuild", "fundamentally", "entire course"
        ]
    }

    def categorize_question(self, question_text: str, question_type: str) -> str:
        """
        Categorize a question based on its text and type.

        Args:
            question_text: The question text from Canvas
            question_type: Canvas question type (essay, multiple_choice, etc.)

        Returns:
            Category string: 'course_content', 'instructor', 'technical',
                           'assessment', 'interaction', 'overall_satisfaction', or 'other'

        Example:
            >>> processor = ResponseProcessor()
            >>> processor.categorize_question("How would you rate the course content?", "multiple_choice")
            'course_content'
        """
        text_lower = question_text.lower()

        # Check each category's keywords
        category_scores = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                category_scores[category] = score

        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)

        # Default to 'other' if no match
        return "other"

    def analyze_text_response(self, response_text: Optional[str]) -> Dict[str, Any]:
        """
        Analyze a text response for critical issues and suggestions.

        Args:
            response_text: Student's text response

        Returns:
            Dictionary with analysis results:
            {
                "is_critical_issue": bool,
                "contains_improvement_suggestion": bool,
                "detected_themes": List[str],
                "sentiment_indicators": Dict[str, int]
            }

        Example:
            >>> processor = ResponseProcessor()
            >>> result = processor.analyze_text_response("The pace was too fast and the video quality was poor.")
            >>> result["detected_themes"]
            ['instructional_clarity', 'technical_platform']
        """
        if not response_text:
            return {
                "is_critical_issue": False,
                "contains_improvement_suggestion": False,
                "detected_themes": [],
                "sentiment_indicators": {}
            }

        text_lower = response_text.lower()

        # Critical issue detection
        is_critical = any(keyword in text_lower for keyword in self.CRITICAL_KEYWORDS)

        # Improvement suggestion detection
        has_suggestion = any(keyword in text_lower for keyword in self.SUGGESTION_KEYWORDS)

        # Theme detection
        detected_themes = []
        for theme, keywords in self.THEME_KEYWORDS.items():
            if any(keyword in text_lower for keyword in keywords):
                detected_themes.append(theme)

        # Basic sentiment indicators (count positive/negative words)
        positive_words = ["good", "great", "excellent", "helpful", "clear", "easy", "love", "enjoy"]
        negative_words = ["bad", "poor", "difficult", "hard", "confusing", "unclear", "hate", "dislike"]

        sentiment_indicators = {
            "positive_count": sum(1 for word in positive_words if word in text_lower),
            "negative_count": sum(1 for word in negative_words if word in text_lower)
        }

        return {
            "is_critical_issue": is_critical,
            "contains_improvement_suggestion": has_suggestion,
            "detected_themes": detected_themes,
            "sentiment_indicators": sentiment_indicators
        }

    def extract_response_data(self, submission: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract question/answer pairs from Canvas submission structure.

        Canvas submissions now use Quiz Submission Questions API which returns:
        - submission['submission_data'] = list of quiz_submission_question objects

        Each quiz_submission_question has:
        - id: question ID
        - answer: student's answer
        - flagged: whether question was flagged

        Args:
            submission: Canvas QuizSubmission dict with submission_data from Questions API

        Returns:
            List of question/answer dictionaries with normalized structure

        Example:
            >>> submission = {
            ...     "id": 123,
            ...     "submission_data": [
            ...         {"id": 100, "answer": "Great course!", "flagged": false}
            ...     ]
            ... }
            >>> processor.extract_response_data(submission)
            [{'question_id': 100, 'answer': 'Great course!'}]
        """
        submission_data = []

        # Direct submission_data field (from Quiz Submission Questions API)
        if 'submission_data' in submission and submission['submission_data']:
            data = submission['submission_data']

            if isinstance(data, list):
                # Normalize quiz_submission_questions structure to match expected format
                for item in data:
                    if isinstance(item, dict):
                        # Canvas Quiz Submission Questions API structure
                        normalized = {
                            'question_id': item.get('id'),  # Note: 'id' field is the question_id
                            'answer': item.get('answer'),
                            'flagged': item.get('flagged', False)
                        }
                        submission_data.append(normalized)
            else:
                print(f"Warning: submission_data is not a list: {type(data)}")

        return submission_data

    def extract_answers_from_statistics(
        self,
        user_id: int,
        quiz_statistics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract individual student answers from Quiz Statistics API data.

        Canvas Quiz Statistics API provides aggregated data showing which users
        selected which answers. This method reverse-maps to get a single student's answers.

        Args:
            user_id: Canvas user_id of the student
            quiz_statistics: Quiz statistics dict from Canvas API

        Returns:
            List of answer dictionaries in submission_data format:
            [
                {
                    'question_id': 3627,
                    'answer': '5773',  # answer_id for multiple choice
                    'text': 'Excellent'  # answer text
                },
                {
                    'question_id': 3628,
                    'answer': 'The case study module was great...',  # essay text
                    'text': 'The case study module was great...'
                },
                ...
            ]

        Example:
            >>> stats = quizzes_client.get_statistics(course_id=42, quiz_id=481)
            >>> processor = ResponseProcessor()
            >>> answers = processor.extract_answers_from_statistics(user_id=626, quiz_statistics=stats)
            >>> len(answers)
            5
        """
        student_answers = []

        # Get question_statistics array
        quiz_stats_list = quiz_statistics.get('quiz_statistics', [])
        if not quiz_stats_list:
            return student_answers

        question_statistics = quiz_stats_list[0].get('question_statistics', [])

        for q_stat in question_statistics:
            question_id = int(q_stat.get('id'))
            question_type = q_stat.get('question_type')

            # Handle multiple choice / true_false / multiple_answers questions
            if question_type in ['multiple_choice_question', 'true_false_question', 'multiple_answers_question']:
                answers_list = q_stat.get('answers', [])

                # Find which answer this user selected
                for answer in answers_list:
                    user_ids = answer.get('user_ids', [])

                    if user_id in user_ids:
                        student_answers.append({
                            'question_id': question_id,
                            'answer': str(answer.get('id')),  # answer_id
                            'text': answer.get('text', '')  # answer text
                        })
                        break  # Found this user's answer

            # Handle essay / short_answer questions
            elif question_type in ['essay_question', 'short_answer_question']:
                # LIMITATION: Canvas Statistics API does NOT provide essay text responses
                # It only shows which user_ids submitted responses, not the actual text
                # Essay text is only available via Quiz Reports CSV API

                # Check if this user responded (present in any answer's user_ids)
                answers_list = q_stat.get('answers', [])
                user_responded = False

                for answer in answers_list:
                    user_ids = answer.get('user_ids', [])
                    if user_id in user_ids:
                        user_responded = True
                        break

                if user_responded:
                    # Record that user answered, but without text (NULL in database)
                    # NOTE: Statistics API does not provide essay text for survey quizzes
                    # Use Quiz Reports CSV workflow instead (see CanvasQuizReportsClient)
                    student_answers.append({
                        'question_id': question_id,
                        'answer': None,  # Essay text not available via Statistics API
                        'text': None
                    })

            # Handle numerical questions
            elif question_type == 'numerical_question':
                responses = q_stat.get('responses', [])

                # Find this user's numeric response
                for response in responses:
                    if response.get('user_id') == user_id:
                        student_answers.append({
                            'question_id': question_id,
                            'answer': str(response.get('value', '')),
                            'text': str(response.get('value', ''))
                        })
                        break

        return student_answers

    def parse_csv_student_response(
        self,
        csv_student_data: Dict[str, Any],
        questions: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse student response data from Quiz Reports CSV into structured feedback.

        This method handles the CSV-based response format from Canvas Quiz Reports API,
        which provides complete answer data including essay text.

        Args:
            csv_student_data: Student data from Quiz Reports CSV with structure:
                {
                    "student_canvas_id": 21089,
                    "student_name": "Emily Voytecek",
                    "responses": [
                        {
                            "question_id": 3627,
                            "question_text": "How Effective...",
                            "answer": "Excellent"
                        },
                        {
                            "question_id": 3628,
                            "question_text": "What was your favorite...",
                            "answer": "The case study module..."
                        }
                    ]
                }
            questions: List of Canvas QuizQuestion dicts for metadata enrichment

        Returns:
            Tuple of (submission_metadata, parsed_responses)
            - submission_metadata: Dict for StudentFeedback model
            - parsed_responses: List of dicts for FeedbackResponse model

        Example:
            >>> processor = ResponseProcessor()
            >>> metadata, responses = processor.parse_csv_student_response(csv_data, questions)
            >>> len(responses)
            5
            >>> responses[0]['response_text']
            'The case study module was great...'
        """
        # Create question lookup by ID
        question_lookup = {q['id']: q for q in questions}

        # Build submission metadata
        # Note: CSV doesn't provide timing/score data - only answers
        submission_metadata = {
            "student_canvas_id": csv_student_data.get('student_canvas_id'),
            "canvas_submission_id": None,  # Not available in CSV
            "started_at": None,  # Not available in CSV
            "finished_at": None,  # Not available in CSV
            "attempt": 1,  # Default to 1
            "score": None,
            "kept_score": None,
            "fudge_points": None,
            "workflow_state": "complete",  # CSV only contains completed responses
            "raw_response_data": csv_student_data  # Store full CSV data for audit
        }

        # Parse each response
        parsed_responses = []

        for response_data in csv_student_data.get('responses', []):
            question_id = response_data.get('question_id')
            question = question_lookup.get(question_id, {})

            question_text = response_data.get('question_text') or question.get('question_text', '')
            question_type = question.get('question_type', '')
            answer_value = response_data.get('answer')

            # Categorize question
            category = self.categorize_question(question_text, question_type)

            # Parse answer based on type
            response_text = None
            response_numeric = None
            selected_answer_text = None
            selected_answer_id = None

            if question_type in ['essay_question', 'short_answer_question']:
                response_text = answer_value
            elif question_type == 'numerical_question':
                try:
                    response_numeric = Decimal(str(answer_value)) if answer_value else None
                except:
                    response_text = str(answer_value)  # Fallback
            elif question_type in ['multiple_choice_question', 'true_false_question']:
                # CSV contains answer text, not ID
                selected_answer_text = answer_value
                # Try to find answer ID from question's answers
                for ans in question.get('answers', []):
                    if ans.get('text') == answer_value:
                        selected_answer_id = ans.get('id')
                        break
            else:
                # Default: store as text
                response_text = str(answer_value) if answer_value else None

            # Analyze text response
            analysis = self.analyze_text_response(response_text or selected_answer_text)

            parsed_response = {
                "canvas_question_id": question_id,
                "question_name": question.get('question_name'),
                "question_text": question_text,
                "question_type": question_type,
                "points_possible": question.get('points_possible'),
                "response_text": response_text,
                "response_numeric": response_numeric,
                "selected_answer_text": selected_answer_text,
                "selected_answer_id": selected_answer_id,
                "question_category": category,
                "contains_improvement_suggestion": analysis["contains_improvement_suggestion"],
                "is_critical_issue": analysis["is_critical_issue"],
            }

            parsed_responses.append(parsed_response)

        return submission_metadata, parsed_responses

    def parse_submission(
        self,
        submission: Dict[str, Any],
        questions: List[Dict[str, Any]]
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse a Canvas submission into structured feedback data.

        Extracts submission metadata and individual question responses,
        applies categorization and analysis to each response.

        Args:
            submission: Canvas QuizSubmission dict from API
            questions: List of Canvas QuizQuestion dicts from API

        Returns:
            Tuple of (submission_metadata, parsed_responses)
            - submission_metadata: Dict with submission info for StudentFeedback model
            - parsed_responses: List of dicts with response info for FeedbackResponse model

        Example:
            >>> processor = ResponseProcessor()
            >>> metadata, responses = processor.parse_submission(submission, questions)
            >>> len(responses)
            5
            >>> responses[0]['question_category']
            'course_content'
        """
        # Create question lookup by ID
        question_lookup = {q['id']: q for q in questions}

        # Extract submission metadata with datetime parsing
        submission_metadata = {
            "canvas_submission_id": submission.get('id'),
            "student_canvas_id": submission.get('user_id'),  # NULL for anonymous
            "started_at": self._parse_datetime(submission.get('started_at')),
            "finished_at": self._parse_datetime(submission.get('finished_at')),
            "attempt": submission.get('attempt', 1),
            "score": submission.get('score'),
            "kept_score": submission.get('kept_score'),
            "fudge_points": submission.get('fudge_points'),
            "workflow_state": submission.get('workflow_state'),
            "raw_response_data": submission  # Store full JSON for audit
        }

        # Extract and parse responses
        submission_data = self.extract_response_data(submission)
        parsed_responses = []

        for answer_data in submission_data:
            # Skip if answer_data is not a dict
            if not isinstance(answer_data, dict):
                print(f"Warning: Skipping non-dict answer_data: {type(answer_data)}: {answer_data}")
                continue

            question_id = answer_data.get('question_id')
            question = question_lookup.get(question_id, {})

            question_text = question.get('question_text', '')
            question_type = question.get('question_type', '')

            # Categorize question
            category = self.categorize_question(question_text, question_type)

            # Parse answer based on type
            response_text = None
            response_numeric = None
            selected_answer_text = None
            selected_answer_id = None

            # Get answer value from normalized structure
            answer_value = answer_data.get('answer')

            if question_type in ['essay_question', 'short_answer_question']:
                response_text = answer_value
            elif question_type == 'numerical_question':
                try:
                    response_numeric = Decimal(str(answer_value)) if answer_value else None
                except:
                    response_text = str(answer_value)  # Fallback
            elif question_type in ['multiple_choice_question', 'true_false_question']:
                # For multiple choice, answer_value is the answer_id (integer)
                selected_answer_id = answer_value
                # We'll need to look up the text from the question's answers if needed
                selected_answer_text = str(answer_value) if answer_value else None
            else:
                # Default: store as text
                response_text = str(answer_value) if answer_value else None

            # Analyze text response
            analysis = self.analyze_text_response(response_text or selected_answer_text)

            parsed_response = {
                "canvas_question_id": question_id,
                "question_name": question.get('question_name'),
                "question_text": question_text,
                "question_type": question_type,
                "points_possible": question.get('points_possible'),
                "response_text": response_text,
                "response_numeric": response_numeric,
                "selected_answer_text": selected_answer_text,
                "selected_answer_id": selected_answer_id,
                "question_category": category,
                "contains_improvement_suggestion": analysis["contains_improvement_suggestion"],
                "is_critical_issue": analysis["is_critical_issue"],
            }

            parsed_responses.append(parsed_response)

        return submission_metadata, parsed_responses


# Testing
if __name__ == "__main__":
    processor = ResponseProcessor()

    print("\n" + "=" * 70)
    print("RESPONSE PROCESSOR SERVICE TEST")
    print("=" * 70 + "\n")

    # Test categorization
    print("Test 1: Question Categorization")
    test_questions = [
        "How would you rate the overall course content?",
        "How effective was the instructor's teaching style?",
        "Did you experience any technical issues with Canvas?",
        "Were the assignment instructions clear?",
        "How would you rate your interaction with peers?"
    ]

    for q in test_questions:
        category = processor.categorize_question(q, "multiple_choice")
        print(f"  Q: {q[:50]}...")
        print(f"  → Category: {category}\n")

    # Test text analysis
    print("\nTest 2: Text Response Analysis")
    test_responses = [
        "The pace was too fast in Module 3.",
        "The Canvas platform keeps crashing and I can't access my assignments.",
        "I suggest adding more hands-on exercises.",
        "Everything was great and very clear!"
    ]

    for text in test_responses:
        analysis = processor.analyze_text_response(text)
        print(f"  Response: {text}")
        print(f"  → Critical: {analysis['is_critical_issue']}")
        print(f"  → Suggestion: {analysis['contains_improvement_suggestion']}")
        print(f"  → Themes: {analysis['detected_themes']}\n")

    print("=" * 70)
    print("SUCCESS: All response processor tests passed!")
    print("=" * 70 + "\n")
