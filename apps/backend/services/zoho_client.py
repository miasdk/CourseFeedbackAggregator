"""
Zoho CRM Client for Course Feedback Integration
Quick MVP implementation for demo
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ZohoCRMClient:
    """Client for interacting with Zoho CRM API"""
    
    def __init__(self):
        self.api_key = os.getenv('ZOHO_CRM_API_KEY')
        self.base_url = "https://www.zohoapis.com/crm/v2"
        self.headers = {
            "Authorization": f"Zoho-oauthtoken {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def test_connection(self) -> Dict[str, Any]:
        """Test Zoho CRM connection"""
        try:
            # For MVP, return mock success
            return {
                "status": "connected",
                "service": "Zoho CRM",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Zoho connection error: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_survey_responses(self) -> List[Dict[str, Any]]:
        """Get survey responses from Zoho CRM"""
        # For MVP demo, return sample data
        return [
            {
                "id": "zoho_001",
                "course_name": "Strategic AI for HR Professionals",
                "rating": 4.2,
                "feedback": "Great content but needs more practical examples",
                "date": "2025-08-15",
                "source": "zoho_survey",
                "respondent_role": "HR Manager"
            },
            {
                "id": "zoho_002", 
                "course_name": "Transformative Leadership",
                "rating": 4.8,
                "feedback": "Excellent program, very insightful",
                "date": "2025-08-20",
                "source": "zoho_survey",
                "respondent_role": "Executive"
            },
            {
                "id": "zoho_003",
                "course_name": "Customer Experience Program",
                "rating": 3.5,
                "feedback": "Content was too theoretical, needed more case studies",
                "date": "2025-08-22",
                "source": "zoho_survey",
                "respondent_role": "Product Manager"
            }
        ]
    
    def get_course_feedback(self, course_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get course feedback from Zoho CRM"""
        responses = self.get_survey_responses()
        if course_id:
            return [r for r in responses if r.get('course_id') == course_id]
        return responses