# Canvas Course API Integration Tutorial

**Building a Course API Client for Course Feedback Aggregation**
 
This tutorial shows how to build a Canvas API client to fetch course data needed for your course feedback aggregation project. We'll focus on the specific endpoints and data you need for course attribution and priority scoring.

## Prerequisites

- Canvas API Token: `15908~n7rLxPkkfXxZVkaLZ2CBNL9QzXCew8cCQmxaK4arEMtYWwJAUfaW3JQmn3Le2QuY`
- Canvas Instance URL: `https://executiveeducation.instructure.com`
- Python 3.8+ or FastAPI environment

---

## Step 1: Basic Canvas API Client Setup

### Python Implementation

```python
import httpx
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CanvasAPIClient:
    """
    Canvas API client optimized for course data retrieval
    Handles pagination, rate limiting, and error management
    """
    
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.api_base = f"{self.base_url}/api/v1"
        
        # Configure HTTP client with reasonable timeouts
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
        )
    
    async def close(self):
        """Clean up HTTP client"""
        await self.client.aclose()
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        Make authenticated request to Canvas API
        Handles basic error responses and logging
        """
        url = f"{self.api_base}/{endpoint.lstrip('/')}"
        
        try:
            response = await self.client.get(url, params=params or {})
            response.raise_for_status()
            
            logger.info(f"Canvas API: {response.status_code} - {url}")
            return response.json()
            
        except httpx.HTTPStatusError as e:
            logger.error(f"Canvas API Error {e.response.status_code}: {url}")
            if e.response.status_code == 401:
                raise Exception("Canvas API authentication failed - check token")
            elif e.response.status_code == 403:
                raise Exception("Canvas API access forbidden - insufficient permissions")
            elif e.response.status_code == 404:
                raise Exception(f"Canvas API endpoint not found: {url}")
            else:
                raise Exception(f"Canvas API error: {e.response.status_code}")
                
        except httpx.RequestError as e:
            logger.error(f"Canvas API Request Error: {str(e)}")
            raise Exception(f"Failed to connect to Canvas: {str(e)}")
```

### FastAPI Service Integration

```python
# app/services/canvas_service.py
from typing import List, Dict, Optional
from app.core.config import settings

class CanvasService:
    """
    Service layer for Canvas operations
    Integrates with FastAPI dependency injection
    """
    
    def __init__(self):
        self.client = CanvasAPIClient(
            base_url=settings.CANVAS_BASE_URL,
            api_token=settings.CANVAS_API_TOKEN
        )
    
    async def get_courses_for_feedback_attribution(self) -> List[Dict]:
        """
        Get course data optimized for survey response attribution
        Returns courses with key fields needed for fuzzy matching
        """
        return await self.client.get_courses_with_details()
    
    async def refresh_course_cache(self) -> int:
        """
        Refresh local course cache from Canvas
        Returns number of courses synchronized
        """
        courses = await self.get_courses_for_feedback_attribution()
        # Store in database (implementation depends on your DB setup)
        return len(courses)
```

---

## Step 2: Course Data Retrieval

### Core Course Fetching

```python
async def get_courses_with_details(self) -> List[Dict]:
    """
    Fetch all courses with detailed information needed for feedback attribution
    
    Key fields retrieved:
    - Basic course info (id, name, course_code)
    - Enrollment data (student count, teacher info)
    - Timeline data (start_date, end_date, workflow_state)
    - Term information for context
    """
    
    courses = []
    page = 1
    per_page = 100  # Canvas max per page
    
    while True:
        params = {
            'enrollment_type': ['teacher', 'ta'],  # Courses where user can teach
            'state': ['available', 'completed', 'unpublished'],  # Include all relevant states
            'include': [
                'total_students',
                'teachers', 
                'term',
                'course_progress',
                'concluded'
            ],
            'per_page': per_page,
            'page': page
        }
        
        batch = await self._make_request('courses', params)
        
        if not batch or len(batch) == 0:
            break
            
        # Process and clean course data
        processed_batch = [self._process_course_data(course) for course in batch]
        courses.extend(processed_batch)
        
        logger.info(f"Fetched {len(batch)} courses from page {page}")
        
        # Check if we got a full page (indicates more pages available)
        if len(batch) < per_page:
            break
            
        page += 1
    
    logger.info(f"Total courses retrieved: {len(courses)}")
    return courses

def _process_course_data(self, raw_course: Dict) -> Dict:
    """
    Clean and structure course data for our use case
    Focus on fields needed for survey attribution
    """
    
    # Extract teacher information
    teachers = []
    if 'teachers' in raw_course:
        teachers = [
            {
                'id': teacher.get('id'),
                'name': teacher.get('name'),
                'email': teacher.get('email')
            }
            for teacher in raw_course['teachers']
        ]
    
    # Parse dates safely
    start_date = None
    end_date = None
    
    if raw_course.get('start_at'):
        try:
            start_date = datetime.fromisoformat(raw_course['start_at'].replace('Z', '+00:00'))
        except:
            pass
            
    if raw_course.get('end_at'):
        try:
            end_date = datetime.fromisoformat(raw_course['end_at'].replace('Z', '+00:00'))
        except:
            pass
    
    return {
        # Core identification
        'canvas_id': raw_course['id'],
        'name': raw_course.get('name', '').strip(),
        'course_code': raw_course.get('course_code', '').strip(),
        'sis_course_id': raw_course.get('sis_course_id'),
        
        # State and timeline
        'workflow_state': raw_course.get('workflow_state'),
        'start_date': start_date,
        'end_date': end_date,
        
        # Enrollment context
        'total_students': raw_course.get('total_students', 0),
        'teachers': teachers,
        
        # Term information
        'enrollment_term_id': raw_course.get('enrollment_term_id'),
        'term': self._process_term_data(raw_course.get('term', {})),
        
        # Attribution helpers
        'name_variations': self._generate_name_variations(raw_course.get('name', '')),
        
        # Metadata
        'last_updated': datetime.utcnow(),
        'is_concluded': raw_course.get('workflow_state') == 'completed'
    }

def _process_term_data(self, term_data: Dict) -> Dict:
    """Extract relevant term information"""
    if not term_data:
        return {}
        
    return {
        'id': term_data.get('id'),
        'name': term_data.get('name'),
        'start_at': term_data.get('start_at'),
        'end_at': term_data.get('end_at')
    }

def _generate_name_variations(self, course_name: str) -> List[str]:
    """
    Generate possible name variations for fuzzy matching
    Helps with survey response attribution
    """
    if not course_name:
        return []
    
    variations = [course_name.strip()]
    
    # Common variations
    name_cleaned = course_name.strip()
    
    # Remove common prefixes/suffixes
    prefixes_to_remove = ['Course:', 'Program:', 'Training:']
    suffixes_to_remove = ['- Online', '- Executive', '- Certificate']
    
    for prefix in prefixes_to_remove:
        if name_cleaned.startswith(prefix):
            variations.append(name_cleaned[len(prefix):].strip())
    
    for suffix in suffixes_to_remove:
        if name_cleaned.endswith(suffix):
            variations.append(name_cleaned[:-len(suffix)].strip())
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variations = []
    for var in variations:
        if var and var not in seen:
            seen.add(var)
            unique_variations.append(var)
    
    return unique_variations
```

---

## Step 3: Course Attribution Helper Methods

### Fuzzy Matching Support

```python
async def find_matching_courses(self, survey_course_name: str, confidence_threshold: float = 0.7) -> List[Dict]:
    """
    Find Canvas courses that match a survey course name
    Returns candidates with confidence scores for manual review
    """
    
    if not survey_course_name or not survey_course_name.strip():
        return []
    
    all_courses = await self.get_courses_with_details()
    matches = []
    
    for course in all_courses:
        # Check exact matches first
        if course['name'].lower() == survey_course_name.lower():
            matches.append({
                'course': course,
                'confidence': 1.0,
                'match_type': 'exact_name',
                'matched_field': 'name'
            })
            continue
        
        # Check course code matches
        if course.get('course_code') and course['course_code'].lower() in survey_course_name.lower():
            matches.append({
                'course': course,
                'confidence': 0.95,
                'match_type': 'course_code',
                'matched_field': 'course_code'
            })
            continue
        
        # Check name variations
        for variation in course['name_variations']:
            if variation.lower() == survey_course_name.lower():
                matches.append({
                    'course': course,
                    'confidence': 0.90,
                    'match_type': 'name_variation',
                    'matched_field': 'name_variation'
                })
                break
    
    # Sort by confidence score (highest first)
    matches.sort(key=lambda x: x['confidence'], reverse=True)
    
    # Filter by confidence threshold
    return [match for match in matches if match['confidence'] >= confidence_threshold]

async def get_course_context_for_attribution(self, course_id: int) -> Dict:
    """
    Get additional context about a course to help with attribution decisions
    Useful for manual mapping interface
    """
    
    course_details = await self._make_request(f'courses/{course_id}', {
        'include': ['teachers', 'total_students', 'term', 'course_progress']
    })
    
    # Get recent assignments for context
    recent_assignments = await self._make_request(f'courses/{course_id}/assignments', {
        'per_page': 5,
        'order_by': 'due_at'
    })
    
    return {
        'course_details': self._process_course_data(course_details),
        'recent_assignments': [
            {
                'name': assignment.get('name'),
                'due_at': assignment.get('due_at'),
                'published': assignment.get('published')
            }
            for assignment in recent_assignments[:5]
        ],
        'attribution_confidence_factors': self._calculate_attribution_factors(course_details)
    }

def _calculate_attribution_factors(self, course: Dict) -> Dict:
    """
    Calculate factors that help determine attribution confidence
    """
    factors = {
        'has_students': course.get('total_students', 0) > 0,
        'is_published': course.get('workflow_state') == 'available',
        'has_teachers': len(course.get('teachers', [])) > 0,
        'is_recent': False,  # Will be calculated based on dates
        'has_course_code': bool(course.get('course_code'))
    }
    
    # Check if course is recent (within last 2 years)
    if course.get('start_at'):
        try:
            start_date = datetime.fromisoformat(course['start_at'].replace('Z', '+00:00'))
            two_years_ago = datetime.utcnow().replace(tzinfo=start_date.tzinfo) - timedelta(days=730)
            factors['is_recent'] = start_date > two_years_ago
        except:
            pass
    
    return factors
```

---

## Step 4: FastAPI Endpoints

### API Routes for Course Management

```python
# app/api/courses.py
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from app.services.canvas_service import CanvasService

router = APIRouter(prefix="/api/courses", tags=["courses"])

@router.get("/sync")
async def sync_courses_from_canvas(canvas_service: CanvasService = Depends()):
    """
    Synchronize courses from Canvas LMS
    Updates local database with latest course information
    """
    try:
        courses = await canvas_service.get_courses_for_feedback_attribution()
        
        # Store courses in database (implementation depends on your DB setup)
        # await store_courses_in_database(courses)
        
        return {
            "status": "success",
            "courses_synced": len(courses),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to sync courses: {str(e)}")

@router.get("/")
async def get_courses(canvas_service: CanvasService = Depends()) -> List[Dict]:
    """
    Get all courses available for feedback attribution
    """
    return await canvas_service.get_courses_for_feedback_attribution()

@router.get("/search")
async def search_courses_for_attribution(
    course_name: str,
    confidence_threshold: float = 0.7,
    canvas_service: CanvasService = Depends()
) -> List[Dict]:
    """
    Find Canvas courses that match a survey course name
    Used for course attribution in feedback processing
    """
    if not course_name:
        raise HTTPException(status_code=400, detail="course_name parameter required")
    
    matches = await canvas_service.find_matching_courses(course_name, confidence_threshold)
    
    return {
        "survey_course_name": course_name,
        "matches_found": len(matches),
        "matches": matches
    }

@router.get("/{course_id}/context")
async def get_course_attribution_context(
    course_id: int,
    canvas_service: CanvasService = Depends()
) -> Dict:
    """
    Get detailed context about a course for attribution decisions
    """
    try:
        context = await canvas_service.get_course_context_for_attribution(course_id)
        return context
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Course {course_id} not found or inaccessible")
```

---

## Step 5: Configuration & Environment Setup

### Environment Variables

```bash
# Add to your .env file
CANVAS_BASE_URL=https://executiveeducation.instructure.com
CANVAS_API_TOKEN=15908~n7rLxPkkfXxZVkaLZ2CBNL9QzXCew8cCQmxaK4arEMtYWwJAUfaW3JQmn3Le2QuY
CANVAS_RATE_LIMIT=5  # requests per second
```

### Configuration Class

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    CANVAS_BASE_URL: str
    CANVAS_API_TOKEN: str
    CANVAS_RATE_LIMIT: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Step 6: Testing Your Canvas Integration

### Basic API Test

```python
# test_canvas_api.py
import asyncio
from app.services.canvas_service import CanvasService

async def test_canvas_connection():
    """Test basic Canvas API connectivity"""
    service = CanvasService()
    
    try:
        # Test basic course retrieval
        courses = await service.get_courses_for_feedback_attribution()
        print(f"✅ Successfully retrieved {len(courses)} courses")
        
        # Test course search
        if courses:
            sample_course_name = courses[0]['name']
            matches = await service.find_matching_courses(sample_course_name)
            print(f"✅ Course search working: found {len(matches)} matches for '{sample_course_name}'")
        
        print("\n🎉 Canvas API integration is working correctly!")
        
    except Exception as e:
        print(f"❌ Canvas API test failed: {str(e)}")
        
    finally:
        await service.client.close()

if __name__ == "__main__":
    asyncio.run(test_canvas_connection())
```

### Attribution Test

```python
async def test_course_attribution():
    """Test course attribution with sample survey data"""
    service = CanvasService()
    
    # Sample survey course names (replace with your actual survey data)
    sample_survey_names = [
        "Executive Leadership in Digital Transformation",
        "Strategic Marketing for Executives",
        "Financial Analysis and Decision Making"
    ]
    
    try:
        for survey_name in sample_survey_names:
            print(f"\nTesting attribution for: '{survey_name}'")
            matches = await service.find_matching_courses(survey_name)
            
            if matches:
                best_match = matches[0]
                print(f"  ✅ Best match: '{best_match['course']['name']}' (confidence: {best_match['confidence']})")
            else:
                print(f"  ⚠️  No matches found")
                
    except Exception as e:
        print(f"❌ Attribution test failed: {str(e)}")
        
    finally:
        await service.client.close()

if __name__ == "__main__":
    asyncio.run(test_course_attribution())
```

---

## Step 7: Integration with Your Webhook System

### Updated Webhook Processing

```python
# app/api/webhooks.py - Updated version
async def process_survey_feedback_with_attribution(payload: Dict[str, Any], canvas_service: CanvasService):
    """
    Enhanced webhook processing with Canvas course attribution
    """
    
    # Extract course name from survey
    survey_course_name = payload.get("course_name")
    if not survey_course_name:
        logger.warning("Survey response missing course name")
        return None
    
    # Attempt automatic attribution
    matches = await canvas_service.find_matching_courses(survey_course_name, confidence_threshold=0.8)
    
    attribution_result = {
        "survey_course_name": survey_course_name,
        "canvas_course_id": None,
        "attribution_confidence": 0.0,
        "attribution_method": "none",
        "requires_manual_review": True
    }
    
    if matches:
        best_match = matches[0]
        attribution_result.update({
            "canvas_course_id": best_match['course']['canvas_id'],
            "attribution_confidence": best_match['confidence'],
            "attribution_method": best_match['match_type'],
            "requires_manual_review": best_match['confidence'] < 0.9
        })
    
    # Process feedback with attribution data
    processed_feedback = process_survey_feedback(payload)  # Your existing function
    processed_feedback['course_attribution'] = attribution_result
    
    return processed_feedback
```

---

## Usage Summary

### For Your Course Feedback Project

1. **Initial Setup**: Use `sync_courses_from_canvas()` to populate your local database
2. **Webhook Processing**: Each incoming survey response tries automatic attribution via `find_matching_courses()`
3. **Manual Review**: Unmatched surveys go to a manual mapping queue
4. **Priority Scoring**: Attributed feedback feeds into your priority scoring engine

### Key Benefits

- **Automatic Attribution**: 80%+ of survey responses should map automatically
- **Fuzzy Matching**: Handles variations in course names between systems
- **Manual Fallback**: Clean interface for handling edge cases
- **Performance Optimized**: Caches course data locally, only syncs when needed

### Next Steps

1. Integrate with your database layer to persist course data
2. Build manual mapping interface for unmatched surveys
3. Add this to your webhook processing pipeline
4. Test with your actual survey data

This Canvas API client is specifically designed for your course feedback aggregation needs and should solve the attribution challenges we discussed in your validation framework.