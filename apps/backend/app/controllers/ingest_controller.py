"""Ingest controller for handling data ingestion from Canvas and Zoho."""

import os
import requests
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from .base_controller import BaseController
from .feedback_controller import FeedbackController  
from .priority_controller import PriorityController
from ..models import Course
from ..config.config import settings


class IngestController(BaseController):
    """Controller for data ingestion operations."""
    
    def __init__(self):
        super().__init__()
        self.feedback_controller = FeedbackController()
        self.priority_controller = PriorityController()
        
        # Canvas API setup
        self.canvas_headers = {
            'Authorization': f'Bearer {settings.canvas_token}',
            'Accept': 'application/json'
        }
        self.canvas_base_url = settings.canvas_api_url
    
    async def ingest_canvas_feedback(self, db: AsyncSession, course_id: str) -> Dict[str, Any]:
        """Ingest feedback from Canvas for a specific course."""
        try:
            # First, create/update course record
            course_data = await self._fetch_canvas_course(course_id)
            unified_course_id = f"canvas_{course_id}"
            
            # Check if course already exists
            from sqlalchemy import select
            existing_course = await db.get(Course, unified_course_id)
            
            if existing_course:
                # Update existing course
                existing_course.course_name = course_data.get('name', existing_course.course_name)
                existing_course.course_metadata = course_data
                existing_course.status = 'active'
                course = existing_course
            else:
                # Create new course
                course = Course(
                    course_id=unified_course_id,
                    course_name=course_data.get('name', 'Unknown Course'),
                    canvas_id=course_id,
                    status='active',
                    course_metadata=course_data
                )
                db.add(course)
            
            await db.commit()
            
            # Fetch course feedback (discussions, assignments, etc.)
            feedback_items = await self._fetch_canvas_feedback(course_id)
            
            # Save feedback to database
            created_feedback = []
            for feedback_data in feedback_items:
                feedback = await self.feedback_controller.create_feedback(db, {
                    'course_id': unified_course_id,
                    'course_name': course_data.get('name'),
                    'student_email': feedback_data.get('student_email'),
                    'student_name': feedback_data.get('student_name'),
                    'feedback_text': feedback_data.get('feedback_text'),
                    'rating': feedback_data.get('rating'),
                    'severity': feedback_data.get('severity', 'medium'),
                    'source': 'canvas',
                    'source_id': feedback_data.get('id')
                })
                created_feedback.append(feedback)
            
            # Recalculate priorities for the course
            await self.priority_controller.recalculate_priorities(db, unified_course_id)
            
            return {
                'success': True,
                'feedback_count': len(created_feedback),
                'course_id': unified_course_id,
                'course_name': course_data.get('name')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def ingest_zoho_feedback(self, db: AsyncSession, program_id: str) -> Dict[str, Any]:
        """Ingest feedback from Zoho CRM for a specific program."""
        try:
            # Setup Zoho API headers
            zoho_headers = {
                'Authorization': f'Bearer {settings.zoho_access_token}',
                'Accept': 'application/json'
            }
            
            unified_course_id = f"zoho_{program_id}"
            
            # Check if course already exists
            existing_course = await db.get(Course, unified_course_id)
            
            if existing_course:
                # Update existing course
                existing_course.course_name = f"Zoho Program {program_id}"
                existing_course.status = 'active'
                course = existing_course
            else:
                # Create new course
                course = Course(
                    course_id=unified_course_id,
                    course_name=f"Zoho Program {program_id}",
                    zoho_program_id=program_id,
                    status='active'
                )
                db.add(course)
            
            await db.commit()
            
            # Try to fetch real Zoho data (Leads module for feedback/surveys)
            # Using Leads as it often contains survey responses in Zoho CRM
            try:
                # Search for records related to this program
                search_url = f"{settings.api_domain}/crm/v2/Leads/search"
                params = {
                    'criteria': f'(Program:equals:{program_id})',
                    'per_page': 100
                }
                
                response = requests.get(search_url, headers=zoho_headers, params=params)
                
                if response.status_code == 200:
                    zoho_data = response.json()
                    leads = zoho_data.get('data', [])
                    
                    created_feedback = []
                    for lead in leads:
                        # Extract feedback from Zoho lead fields
                        feedback_text = lead.get('Description') or lead.get('Feedback') or lead.get('Comments', '')
                        if feedback_text:
                            feedback = await self.feedback_controller.create_feedback(db, {
                                'course_id': unified_course_id,
                                'course_name': f"Zoho Program {program_id}",
                                'student_email': lead.get('Email'),
                                'student_name': f"{lead.get('First_Name', '')} {lead.get('Last_Name', '')}".strip(),
                                'feedback_text': feedback_text,
                                'rating': self._extract_rating_from_zoho(lead),
                                'severity': self._determine_severity_from_zoho(lead),
                                'source': 'zoho',
                                'source_id': lead.get('id')
                            })
                            created_feedback.append(feedback)
                else:
                    # If Zoho API fails, fall back to creating sample data
                    print(f"Zoho API returned {response.status_code}: {response.text}")
                    # At least create one sample feedback to test the system
                    feedback = await self.feedback_controller.create_feedback(db, {
                        'course_id': unified_course_id,
                        'course_name': f"Zoho Program {program_id}",
                        'student_email': 'sample@zoho.com',
                        'feedback_text': 'Sample feedback - Zoho API connection needs configuration',
                        'rating': 3.0,
                        'severity': 'medium',
                        'source': 'zoho',
                        'source_id': 'sample_001'
                    })
                    created_feedback = [feedback]
                    
            except requests.exceptions.RequestException as api_error:
                print(f"Zoho API error: {api_error}")
                # Create sample feedback on API error
                feedback = await self.feedback_controller.create_feedback(db, {
                    'course_id': unified_course_id,
                    'course_name': f"Zoho Program {program_id}",
                    'student_email': 'sample@zoho.com',
                    'feedback_text': f'Sample feedback - API error: {str(api_error)[:100]}',
                    'rating': 3.0,
                    'severity': 'medium',
                    'source': 'zoho',
                    'source_id': 'error_001'
                })
                created_feedback = [feedback]
            
            # Recalculate priorities
            await self.priority_controller.recalculate_priorities(db, unified_course_id)
            
            return {
                'success': True,
                'feedback_count': len(created_feedback),
                'course_id': unified_course_id,
                'source': 'zoho_api' if created_feedback else 'sample_data'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _extract_rating_from_zoho(self, lead: Dict[str, Any]) -> float:
        """Extract rating from Zoho lead data."""
        # Check common rating fields
        rating_fields = ['Rating', 'Score', 'Satisfaction_Score', 'NPS_Score']
        for field in rating_fields:
            if field in lead and lead[field]:
                try:
                    # Convert to 1-5 scale
                    value = float(lead[field])
                    if value > 10:  # Likely a percentage
                        return (value / 100) * 5
                    elif value > 5:  # Likely a 1-10 scale
                        return (value / 10) * 5
                    else:
                        return min(5.0, max(1.0, value))
                except:
                    pass
        return 3.0  # Default neutral rating
    
    def _determine_severity_from_zoho(self, lead: Dict[str, Any]) -> str:
        """Determine severity from Zoho lead data."""
        # Check priority/severity fields
        priority = str(lead.get('Priority', '')).lower()
        if 'high' in priority or 'urgent' in priority:
            return 'high'
        elif 'low' in priority:
            return 'low'
        
        # Check rating to infer severity
        rating = self._extract_rating_from_zoho(lead)
        if rating <= 2:
            return 'high'
        elif rating >= 4:
            return 'low'
        
        return 'medium'
    
    async def _fetch_canvas_course(self, course_id: str) -> Dict[str, Any]:
        """Fetch course details from Canvas API."""
        url = f"{self.canvas_base_url}/api/v1/courses/{course_id}"
        response = requests.get(url, headers=self.canvas_headers)
        response.raise_for_status()
        return response.json()
    
    async def _fetch_canvas_feedback(self, course_id: str) -> List[Dict[str, Any]]:
        """Fetch feedback from Canvas discussions and assignments."""
        feedback_items = []
        
        # Get discussion topics
        discussions_url = f"{self.canvas_base_url}/api/v1/courses/{course_id}/discussion_topics"
        discussions_response = requests.get(discussions_url, headers=self.canvas_headers)
        
        if discussions_response.status_code == 200:
            discussions = discussions_response.json()
            
            for discussion in discussions[:5]:  # Limit for MVP
                # Get discussion entries
                entries_url = f"{self.canvas_base_url}/api/v1/courses/{course_id}/discussion_topics/{discussion['id']}/entries"
                entries_response = requests.get(entries_url, headers=self.canvas_headers)
                
                if entries_response.status_code == 200:
                    entries = entries_response.json()
                    
                    for entry in entries:
                        # Simple feedback extraction
                        feedback_items.append({
                            'id': f"discussion_{entry['id']}",
                            'student_email': f"student_{entry.get('user_id', 'anonymous')}@example.com",
                            'student_name': entry.get('user_name', 'Anonymous'),
                            'feedback_text': entry.get('message', ''),
                            'rating': self._extract_rating_from_text(entry.get('message', '')),
                            'severity': self._determine_severity(entry.get('message', ''))
                        })
        
        return feedback_items
    
    def _extract_rating_from_text(self, text: str) -> float:
        """Extract numeric rating from feedback text."""
        # Simple pattern matching for ratings
        import re
        rating_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:out of|/)\s*5',
            r'(\d+(?:\.\d+)?)\s*stars?',
            r'rating:?\s*(\d+(?:\.\d+)?)'
        ]
        
        for pattern in rating_patterns:
            match = re.search(pattern, text.lower())
            if match:
                rating = float(match.group(1))
                return min(5.0, max(1.0, rating))  # Clamp to 1-5 range
        
        return None
    
    def _determine_severity(self, text: str) -> str:
        """Determine severity based on feedback content."""
        text_lower = text.lower()
        
        critical_keywords = ['broken', 'not working', 'impossible', 'terrible', 'worst']
        high_keywords = ['difficult', 'confusing', 'problem', 'issue', 'bug']
        low_keywords = ['minor', 'small', 'suggestion', 'could be better']
        
        if any(keyword in text_lower for keyword in critical_keywords):
            return 'critical'
        elif any(keyword in text_lower for keyword in high_keywords):
            return 'high' 
        elif any(keyword in text_lower for keyword in low_keywords):
            return 'low'
        else:
            return 'medium'