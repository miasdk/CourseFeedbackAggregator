"""
Canvas LMS API Client
Handles authentication and data retrieval from Canvas
"""

import requests
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class CanvasClient:
    """Client for interacting with Canvas LMS API"""
    
    def __init__(self):
        self.api_token = os.getenv('CANVAS_API_TOKEN')
        self.api_url = os.getenv('CANVAS_API_URL', 'https://usfca.instructure.com')
        
        if not self.api_token:
            raise ValueError("Canvas API token not configured")
        
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Accept': 'application/json+canvas-string-ids'
        }
        
        logger.info(f"Canvas client initialized for {self.api_url}")
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """Make authenticated request to Canvas API"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            return {
                "success": True,
                "data": response.json(),
                "headers": dict(response.headers)
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Canvas API error: {e}")
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None)
            }
    
    def test_connection(self) -> Dict:
        """Test Canvas API connection and permissions"""
        result = self._make_request("/api/v1/users/self")
        
        if result["success"]:
            user_data = result["data"]
            
            # Get accessible courses
            courses_result = self._make_request("/api/v1/courses", {
                "enrollment_type": ["teacher", "ta", "designer"],
                "include": ["term", "total_students"],
                "per_page": 100
            })
            
            return {
                "connected": True,
                "user": {
                    "name": user_data.get("name"),
                    "id": user_data.get("id"),
                    "email": user_data.get("primary_email") or user_data.get("login_id")
                },
                "permissions": {
                    "courses_accessible": len(courses_result.get("data", [])) if courses_result["success"] else 0,
                    "can_read_courses": courses_result["success"],
                    "roles": user_data.get("enrollments", []) if isinstance(user_data.get("enrollments"), list) else []
                }
            }
        
        return {
            "connected": False,
            "error": result.get("error", "Unknown error")
        }
    
    def get_courses(self, include_concluded: bool = False) -> List[Dict]:
        """Get all accessible courses"""
        params = {
            "enrollment_type": ["teacher", "ta", "designer", "observer"],
            "include": ["term", "total_students", "course_progress"],
            "per_page": 100
        }
        
        if not include_concluded:
            params["state"] = ["available", "completed"]
        
        result = self._make_request("/api/v1/courses", params)
        
        if result["success"]:
            courses = result["data"]
            
            # Process and enrich course data
            processed_courses = []
            for course in courses:
                if course.get("name") and course.get("id"):
                    processed_courses.append({
                        "canvas_id": course["id"],
                        "name": course["name"],
                        "course_code": course.get("course_code", ""),
                        "term": course.get("term", {}).get("name", "Unknown"),
                        "enrollment_count": course.get("total_students", 0),
                        "workflow_state": course.get("workflow_state", ""),
                        "start_at": course.get("start_at"),
                        "end_at": course.get("end_at"),
                        "created_at": course.get("created_at")
                    })
            
            return processed_courses
        
        return []
    
    def get_course_details(self, course_id: str) -> Optional[Dict]:
        """Get detailed information for a specific course"""
        result = self._make_request(f"/api/v1/courses/{course_id}", {
            "include": ["term", "teachers", "total_students", "course_progress", "syllabus_body"]
        })
        
        if result["success"]:
            course = result["data"]
            
            # Get additional course analytics if available
            analytics = self.get_course_analytics(course_id)
            
            return {
                "canvas_id": course["id"],
                "name": course["name"],
                "course_code": course.get("course_code", ""),
                "term": course.get("term", {}).get("name", "Unknown"),
                "teachers": [
                    {"name": t.get("display_name"), "id": t.get("id")}
                    for t in course.get("teachers", [])
                ],
                "enrollment_count": course.get("total_students", 0),
                "workflow_state": course.get("workflow_state", ""),
                "start_at": course.get("start_at"),
                "end_at": course.get("end_at"),
                "created_at": course.get("created_at"),
                "analytics": analytics
            }
        
        return None
    
    def get_course_analytics(self, course_id: str) -> Dict:
        """Get course analytics and participation data"""
        analytics_data = {
            "participation": {},
            "grades": {},
            "assignments": {}
        }
        
        # Try to get participation data
        participation_result = self._make_request(
            f"/api/v1/courses/{course_id}/analytics/activity"
        )
        if participation_result["success"]:
            analytics_data["participation"] = participation_result["data"]
        
        # Try to get assignment data
        assignments_result = self._make_request(
            f"/api/v1/courses/{course_id}/analytics/assignments"
        )
        if assignments_result["success"]:
            analytics_data["assignments"] = assignments_result["data"]
        
        return analytics_data
    
    def get_course_feedback(self, course_id: str) -> List[Dict]:
        """
        Get feedback data from various Canvas sources:
        - Course evaluations (if available)
        - Discussion posts about the course
        - Assignment comments
        """
        feedback_items = []
        
        # Get course discussions
        discussions_result = self._make_request(
            f"/api/v1/courses/{course_id}/discussion_topics",
            {"per_page": 50}
        )
        
        if discussions_result["success"]:
            for discussion in discussions_result["data"]:
                # Look for feedback-related discussions
                if any(keyword in discussion.get("title", "").lower() 
                       for keyword in ["feedback", "evaluation", "review", "improve"]):
                    
                    # Get discussion entries
                    entries_result = self._make_request(
                        f"/api/v1/courses/{course_id}/discussion_topics/{discussion['id']}/entries"
                    )
                    
                    if entries_result["success"]:
                        for entry in entries_result["data"]:
                            feedback_items.append({
                                "source": "discussion",
                                "canvas_id": entry.get("id"),
                                "course_id": course_id,
                                "content": entry.get("message", ""),
                                "created_at": entry.get("created_at"),
                                "user_id": entry.get("user_id"),
                                "discussion_topic": discussion.get("title")
                            })
        
        # Get quiz responses that might be course evaluations
        quizzes_result = self._make_request(
            f"/api/v1/courses/{course_id}/quizzes",
            {"per_page": 50}
        )
        
        if quizzes_result["success"]:
            for quiz in quizzes_result["data"]:
                # Look for evaluation/survey quizzes
                if any(keyword in quiz.get("title", "").lower() 
                       for keyword in ["evaluation", "survey", "feedback", "assessment"]):
                    
                    # Note: Getting quiz submissions requires additional permissions
                    # Store the quiz as potential feedback source
                    feedback_items.append({
                        "source": "quiz",
                        "canvas_id": quiz.get("id"),
                        "course_id": course_id,
                        "title": quiz.get("title"),
                        "description": quiz.get("description", ""),
                        "quiz_type": quiz.get("quiz_type"),
                        "created_at": quiz.get("created_at")
                    })
        
        return feedback_items
    
    def get_all_feedback(self, limit: Optional[int] = None) -> Dict:
        """Get feedback from all accessible courses"""
        courses = self.get_courses()
        
        all_feedback = []
        courses_processed = 0
        
        for course in courses[:limit] if limit else courses:
            logger.info(f"Processing feedback for course: {course['name']}")
            
            course_feedback = self.get_course_feedback(course["canvas_id"])
            
            for feedback in course_feedback:
                feedback["course_name"] = course["name"]
                feedback["course_code"] = course["course_code"]
                all_feedback.append(feedback)
            
            courses_processed += 1
        
        return {
            "total_courses": len(courses),
            "courses_processed": courses_processed,
            "feedback_count": len(all_feedback),
            "feedback": all_feedback,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def search_courses(self, search_term: str) -> List[Dict]:
        """Search for courses by name or code"""
        all_courses = self.get_courses(include_concluded=True)
        
        search_lower = search_term.lower()
        matched_courses = [
            course for course in all_courses
            if search_lower in course["name"].lower() or 
               search_lower in course.get("course_code", "").lower()
        ]
        
        return matched_courses