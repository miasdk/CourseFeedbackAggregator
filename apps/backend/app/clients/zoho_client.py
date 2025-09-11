import httpx
import asyncio
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import json
import re

from ..config.config import settings
from ..models import Feedback

logger = logging.getLogger(__name__)

class ZohoClient:
    """Zoho CRM API Client for extracting course feedback data"""
    
    def __init__(self):
        self.access_token = settings.zoho_access_token
        self.api_domain = settings.zoho_api_domain
        self.headers = {
            'Authorization': f'Zoho-oauthtoken {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Survey/feedback related field mappings discovered in dev-kit
        self.feedback_fields = {
            'Contacts': [
                'Feedback_on_Content', 'Feedback_on_Faculty', 'Houston_Review',
                'Completed_Course_Review', 'Board_Member_Rating'
            ],
            'Deals': [
                'Feedback_on_the_Content', 'Feedback_on_the_Faculty', 'Houston_Review',
                'Board_Member_Rating', 'Instructor_Review_Process'
            ],
            'Accounts': [
                'Houston_Review', 'Board_Member_Rating'
            ],
            'Leads': [
                'Houston_Review'
            ]
        }
        
        # Course-related fields
        self.course_fields = [
            'Official_Program_Name', 'Course_Completed', 'Program_Name',
            'Course_Name', 'Course_Title'
        ]
        
        # Rating field patterns
        self.rating_fields = [
            'Board_Member_Rating', 'Rating', 'Score', 'Satisfaction_Rating'
        ]

    async def api_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make async API request with error handling"""
        url = f"{self.api_domain}{endpoint}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(url, headers=self.headers, params=params)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    logger.error("Zoho API authentication failed - check access token")
                    return None
                elif response.status_code == 403:
                    logger.error(f"Zoho API access forbidden for endpoint: {endpoint}")
                    return None
                elif response.status_code == 429:
                    logger.warning("Zoho API rate limit hit - waiting...")
                    await asyncio.sleep(60)  # Zoho has stricter rate limits
                    return await self.api_request(endpoint, params)  # Retry
                else:
                    logger.error(f"Zoho API error {response.status_code}: {response.text}")
                    return None
                    
            except httpx.TimeoutException:
                logger.error(f"Zoho API timeout for endpoint: {endpoint}")
                return None
            except Exception as e:
                logger.error(f"Zoho API request failed: {str(e)}")
                return None

    def extract_rating_from_value(self, value: Any) -> Optional[float]:
        """Extract numerical rating from various field types"""
        if not value:
            return None
            
        if isinstance(value, (int, float)):
            # Normalize ratings to 1-5 scale
            if value <= 5:
                return max(1.0, min(5.0, float(value)))
            elif value <= 10:
                return max(1.0, min(5.0, (float(value) / 10.0) * 5.0))
            elif value <= 100:
                return max(1.0, min(5.0, (float(value) / 100.0) * 5.0))
        
        if isinstance(value, str):
            # Try to extract numbers from text
            numbers = re.findall(r'\d+(?:\.\d+)?', value)
            if numbers:
                rating = float(numbers[0])
                if rating <= 5:
                    return max(1.0, min(5.0, rating))
                elif rating <= 10:
                    return max(1.0, min(5.0, (rating / 10.0) * 5.0))
        
        return None

    def classify_feedback_severity(self, feedback_text: str, rating: Optional[float] = None) -> str:
        """Classify feedback severity based on content and rating"""
        if not feedback_text:
            if rating:
                if rating >= 4.0:
                    return "low"
                elif rating >= 3.0:
                    return "medium"
                else:
                    return "high"
            return "medium"
        
        text_lower = feedback_text.lower()
        
        # Critical indicators
        critical_keywords = ['urgent', 'critical', 'emergency', 'broken', 'not working', 'cannot access']
        if any(keyword in text_lower for keyword in critical_keywords):
            return "critical"
        
        # High severity indicators
        high_keywords = ['confusing', 'unclear', 'difficult', 'struggling', 'problem']
        if any(keyword in text_lower for keyword in high_keywords):
            return "high"
        
        # Positive indicators (low severity)
        positive_keywords = ['great', 'excellent', 'helpful', 'clear', 'good', 'satisfied']
        if any(keyword in text_lower for keyword in positive_keywords):
            return "low"
        
        # Use rating as secondary indicator
        if rating:
            if rating >= 4.0:
                return "low"
            elif rating <= 2.0:
                return "high"
        
        return "medium"

    def extract_course_info(self, record: Dict) -> Dict[str, str]:
        """Extract course information from a record"""
        course_info = {
            'course_id': '',
            'course_name': ''
        }
        
        # Look for course name in various fields
        for field in self.course_fields:
            value = record.get(field)
            if value and isinstance(value, str) and value.strip():
                course_info['course_name'] = value.strip()
                # Use first course field found as basis for course_id
                course_info['course_id'] = f"zoho_{field.lower()}_{record.get('id', 'unknown')}"
                break
        
        # Fallback to record type and ID
        if not course_info['course_name']:
            course_info['course_name'] = f"Course from {record.get('module', 'Unknown')} record"
            course_info['course_id'] = f"zoho_{record.get('module', 'unknown').lower()}_{record.get('id', 'unknown')}"
        
        return course_info

    async def get_module_records(self, module: str, page: int = 1, per_page: int = 200) -> List[Dict]:
        """Get records from a specific Zoho CRM module"""
        endpoint = f"/crm/v2/{module}"
        params = {
            'page': page,
            'per_page': per_page
        }
        
        response = await self.api_request(endpoint, params)
        if response and 'data' in response:
            return response['data']
        return []

    async def extract_feedback_from_module(self, module: str) -> List[Dict]:
        """Extract feedback from a specific CRM module"""
        module_feedback = []
        feedback_field_names = self.feedback_fields.get(module, [])
        
        if not feedback_field_names:
            logger.info(f"No feedback fields defined for module {module}")
            return module_feedback
        
        logger.info(f"Extracting feedback from Zoho {module} module")
        
        # Get records from module
        page = 1
        while True:
            records = await self.get_module_records(module, page)
            if not records:
                break
            
            for record in records:
                record['module'] = module  # Add module info for context
                course_info = self.extract_course_info(record)
                
                # Extract feedback from each feedback field
                for field_name in feedback_field_names:
                    field_value = record.get(field_name)
                    
                    if field_value and isinstance(field_value, str) and len(field_value.strip()) > 5:
                        # Look for rating in the same record
                        rating = None
                        for rating_field in self.rating_fields:
                            rating_value = record.get(rating_field)
                            if rating_value:
                                rating = self.extract_rating_from_value(rating_value)
                                if rating:
                                    break
                        
                        feedback_item = {
                            'course_id': course_info['course_id'],
                            'course_name': course_info['course_name'],
                            'student_email': record.get('Email', ''),
                            'student_name': record.get('Full_Name') or record.get('Name') or record.get('Contact_Name', ''),
                            'feedback_text': field_value.strip(),
                            'rating': rating,
                            'severity': self.classify_feedback_severity(field_value.strip(), rating),
                            'source': 'zoho',
                            'source_id': f'{module.lower()}_{record.get("id")}_{field_name}',
                            'context': {
                                'module': module,
                                'record_id': record.get('id'),
                                'field_name': field_name,
                                'record_type': module
                            }
                        }
                        module_feedback.append(feedback_item)
            
            # Check if there are more pages
            if len(records) < 200:  # Less than full page indicates last page
                break
            page += 1
            
            # Safety limit
            if page > 10:
                logger.warning(f"Stopping at page 10 for module {module}")
                break
        
        logger.info(f"Extracted {len(module_feedback)} feedback items from {module}")
        return module_feedback

    async def sync_all_feedback(self) -> List[Dict]:
        """Sync feedback from all CRM modules"""
        all_feedback = []
        
        # Process each module that contains feedback fields
        for module in self.feedback_fields.keys():
            try:
                module_feedback = await self.extract_feedback_from_module(module)
                all_feedback.extend(module_feedback)
                
                # Add delay between modules to respect rate limits
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error extracting feedback from Zoho module {module}: {str(e)}")
                continue
        
        logger.info(f"Total extracted {len(all_feedback)} feedback items from Zoho CRM")
        return all_feedback

    async def get_specific_records_with_feedback(self, search_term: str) -> List[Dict]:
        """Search for records containing specific feedback terms"""
        all_feedback = []
        
        for module in self.feedback_fields.keys():
            try:
                # Use search API if available, otherwise fallback to getting all records
                endpoint = f"/crm/v2/{module}/search"
                params = {'criteria': f'(Full_Name:starts_with:{search_term})'}
                
                response = await self.api_request(endpoint, params)
                if response and 'data' in response:
                    records = response['data']
                    
                    for record in records:
                        record['module'] = module
                        course_info = self.extract_course_info(record)
                        
                        # Process feedback fields for this record
                        for field_name in self.feedback_fields[module]:
                            field_value = record.get(field_name)
                            if field_value and isinstance(field_value, str) and search_term.lower() in field_value.lower():
                                
                                feedback_item = {
                                    'course_id': course_info['course_id'],
                                    'course_name': course_info['course_name'],
                                    'student_email': record.get('Email', ''),
                                    'student_name': record.get('Full_Name') or record.get('Name', ''),
                                    'feedback_text': field_value.strip(),
                                    'rating': None,  # Would need to extract if available
                                    'severity': self.classify_feedback_severity(field_value.strip()),
                                    'source': 'zoho',
                                    'source_id': f'{module.lower()}_{record.get("id")}_{field_name}',
                                    'context': {
                                        'module': module,
                                        'record_id': record.get('id'),
                                        'field_name': field_name
                                    }
                                }
                                all_feedback.append(feedback_item)
                
            except Exception as e:
                logger.error(f"Error searching {module} for '{search_term}': {str(e)}")
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