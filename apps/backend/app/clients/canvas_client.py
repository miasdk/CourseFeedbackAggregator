import httpx
import asyncio
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json

from ..config import settings
from ..database import Feedback

logger = logging.getLogger(__name__)

class CanvasClient:
    """Canvas LMS API Client for extracting feedback data"""
    
    def __init__(self):
        self.access_token = settings.canvas_token
        self.api_url = settings.canvas_base_url
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Accept': 'application/json'
        }
        
        # Feedback detection keywords from dev-kit
        self.feedback_keywords = {
            'confusion': ['confusing', 'confused', 'unclear', "don't understand", 'hard to follow'],
            'difficulty': ['difficult', 'hard', 'challenging', 'struggle', 'struggling'],
            'technical_issues': ['broken', 'not working', 'error', 'crash', "can't access", 'cannot access'],
            'suggestions': ['suggest', 'recommend', 'should', 'could be better', 'improve'],
            'positive': ['great', 'excellent', 'helpful', 'clear', 'good', 'love', 'amazing'],
            'urgent': ['urgent', 'critical', 'immediately', 'asap', 'emergency']
        }
        
    async def api_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make async API request with error handling"""
        url = f"{self.api_url}/api/v1/{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # Rate limiting - Canvas allows 100 requests per 10 seconds
                await asyncio.sleep(0.1)
                
                response = await client.get(url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    logger.error("Canvas API authentication failed - check access token")
                    return None
                elif response.status_code == 403:
                    logger.error(f"Canvas API access forbidden for endpoint: {endpoint}")
                    return None
                elif response.status_code == 429:
                    logger.warning("Canvas API rate limit hit - waiting...")
                    await asyncio.sleep(10)
                    return await self.api_request(endpoint, params)  # Retry
                else:
                    logger.error(f"Canvas API error {response.status_code}: {response.text}")
                    return None
                    
            except httpx.TimeoutException:
                logger.error(f"Canvas API timeout for endpoint: {endpoint}")
                return None
            except Exception as e:
                logger.error(f"Canvas API request failed: {str(e)}")
                return None

    def classify_feedback_severity(self, text: str) -> str:
        """Classify feedback severity based on keywords"""
        if not text:
            return "low"
            
        text_lower = text.lower()
        
        # Check for critical/urgent indicators
        urgent_count = sum(1 for keyword in self.feedback_keywords['urgent'] if keyword in text_lower)
        technical_count = sum(1 for keyword in self.feedback_keywords['technical_issues'] if keyword in text_lower)
        
        if urgent_count >= 1 or technical_count >= 2:
            return "critical"
        
        # Check for high severity indicators
        confusion_count = sum(1 for keyword in self.feedback_keywords['confusion'] if keyword in text_lower)
        difficulty_count = sum(1 for keyword in self.feedback_keywords['difficulty'] if keyword in text_lower)
        
        if confusion_count >= 2 or difficulty_count >= 2:
            return "high"
        elif confusion_count >= 1 or difficulty_count >= 1:
            return "medium"
        
        # Check for positive feedback (lower priority)
        positive_count = sum(1 for keyword in self.feedback_keywords['positive'] if keyword in text_lower)
        if positive_count >= 2:
            return "low"
            
        return "medium"  # Default

    def extract_rating_from_text(self, text: str) -> Optional[float]:
        """Extract numerical rating from feedback text"""
        if not text:
            return None
            
        # Look for patterns like "3/5", "7 out of 10", "rating: 4"
        import re
        
        # Pattern: X/Y or X out of Y
        ratio_match = re.search(r'(\d+)\s*(?:/|out\s+of)\s*(\d+)', text.lower())
        if ratio_match:
            numerator, denominator = float(ratio_match.group(1)), float(ratio_match.group(2))
            if denominator > 0:
                # Normalize to 5-point scale
                return min(5.0, (numerator / denominator) * 5.0)
        
        # Pattern: "rating: X" or "score: X"
        rating_match = re.search(r'(?:rating|score):\s*(\d+(?:\.\d+)?)', text.lower())
        if rating_match:
            rating = float(rating_match.group(1))
            # Assume ratings are typically 1-5 or 1-10
            if rating <= 5:
                return min(5.0, rating)
            elif rating <= 10:
                return min(5.0, (rating / 10.0) * 5.0)
        
        return None

    async def get_courses(self) -> List[Dict]:
        """Get list of courses the user has access to"""
        courses = await self.api_request("courses", {"enrollment_state": "active", "per_page": 100})
        return courses if courses else []

    async def get_course_assignments(self, course_id: str) -> List[Dict]:
        """Get assignments for a course"""
        assignments = await self.api_request(f"courses/{course_id}/assignments", {"per_page": 100})
        return assignments if assignments else []

    async def get_assignment_submissions(self, course_id: str, assignment_id: str) -> List[Dict]:
        """Get submissions for an assignment with comments"""
        submissions = await self.api_request(
            f"courses/{course_id}/assignments/{assignment_id}/submissions",
            {"include[]": ["submission_comments", "user"], "per_page": 100}
        )
        return submissions if submissions else []

    async def get_discussion_topics(self, course_id: str) -> List[Dict]:
        """Get discussion topics for a course"""
        discussions = await self.api_request(f"courses/{course_id}/discussion_topics", {"per_page": 100})
        return discussions if discussions else []

    async def get_discussion_entries(self, course_id: str, topic_id: str) -> List[Dict]:
        """Get entries for a discussion topic"""
        entries = await self.api_request(f"courses/{course_id}/discussion_topics/{topic_id}/entries", {"per_page": 100})
        return entries if entries else []

    async def extract_feedback_from_course(self, course_id: str) -> List[Dict]:
        """Extract all feedback-relevant data from a course"""
        course_feedback = []
        
        logger.info(f"Extracting feedback from Canvas course {course_id}")
        
        # Get course info
        course_info = await self.api_request(f"courses/{course_id}")
        if not course_info:
            return course_feedback
            
        course_name = course_info.get('name', f'Course {course_id}')
        
        # Extract feedback from assignments
        assignments = await self.get_course_assignments(course_id)
        for assignment in assignments:
            assignment_id = assignment['id']
            assignment_name = assignment.get('name', 'Unnamed Assignment')
            
            submissions = await self.get_assignment_submissions(course_id, assignment_id)
            for submission in submissions:
                user = submission.get('user', {})
                student_email = user.get('email', '')
                student_name = user.get('name', '')
                
                # Extract feedback from submission comments
                comments = submission.get('submission_comments', [])
                for comment in comments:
                    comment_text = comment.get('comment', '')
                    if comment_text and len(comment_text.strip()) > 10:  # Filter out very short comments
                        
                        feedback_item = {
                            'course_id': f'canvas_{course_id}',
                            'course_name': course_name,
                            'student_email': student_email,
                            'student_name': student_name,
                            'feedback_text': comment_text,
                            'rating': self.extract_rating_from_text(comment_text),
                            'severity': self.classify_feedback_severity(comment_text),
                            'source': 'canvas',
                            'source_id': f'assignment_{assignment_id}_comment_{comment["id"]}',
                            'context': {
                                'assignment_name': assignment_name,
                                'assignment_id': assignment_id,
                                'comment_id': comment['id']
                            }
                        }
                        course_feedback.append(feedback_item)
        
        # Extract feedback from discussions
        discussions = await self.get_discussion_topics(course_id)
        for discussion in discussions:
            topic_id = discussion['id']
            topic_title = discussion.get('title', 'Unnamed Discussion')
            
            entries = await self.get_discussion_entries(course_id, topic_id)
            for entry in entries:
                message = entry.get('message', '')
                if message and len(message.strip()) > 10:
                    
                    feedback_item = {
                        'course_id': f'canvas_{course_id}',
                        'course_name': course_name,
                        'student_email': entry.get('user_email', ''),
                        'student_name': entry.get('user_name', ''),
                        'feedback_text': message,
                        'rating': self.extract_rating_from_text(message),
                        'severity': self.classify_feedback_severity(message),
                        'source': 'canvas',
                        'source_id': f'discussion_{topic_id}_entry_{entry["id"]}',
                        'context': {
                            'discussion_title': topic_title,
                            'topic_id': topic_id,
                            'entry_id': entry['id']
                        }
                    }
                    course_feedback.append(feedback_item)
        
        logger.info(f"Extracted {len(course_feedback)} feedback items from Canvas course {course_id}")
        return course_feedback

    async def sync_all_feedback(self) -> List[Dict]:
        """Sync feedback from all accessible courses"""
        all_feedback = []
        
        # Get all courses
        courses = await self.get_courses()
        logger.info(f"Found {len(courses)} Canvas courses")
        
        for course in courses[:5]:  # Limit to 5 courses for initial sync
            course_id = course['id']
            try:
                course_feedback = await self.extract_feedback_from_course(str(course_id))
                all_feedback.extend(course_feedback)
            except Exception as e:
                logger.error(f"Error extracting feedback from course {course_id}: {str(e)}")
                continue
        
        return all_feedback

    async def convert_to_feedback_objects(self, raw_feedback: List[Dict]) -> List[Feedback]:
        """Convert raw feedback data to database Feedback objects"""
        feedback_objects = []
        
        for item in raw_feedback:
            feedback = Feedback(
                course_id=item['course_id'],
                course_name=item['course_name'],
                student_email=item.get('student_email'),
                student_name=item.get('student_name'),
                feedback_text=item['feedback_text'],
                rating=item.get('rating'),
                severity=item['severity'],
                source=item['source'],
                source_id=item['source_id'],
                created_at=datetime.utcnow(),
                is_active=True
            )
            feedback_objects.append(feedback)
        
        return feedback_objects