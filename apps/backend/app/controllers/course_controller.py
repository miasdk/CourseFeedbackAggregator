"""Course controller for handling course operations and Canvas/Zoho synchronization."""

import requests
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from datetime import datetime

from .base_controller import BaseController
from ..models import Course
from ..config.config import settings
from ..services.zoho_auth import ZohoAuthService


class CourseController(BaseController):
    """Controller for course operations and Canvas/Zoho integration."""
    
    def __init__(self):
        super().__init__()
        # Canvas API setup
        self.canvas_headers = {
            'Authorization': f'Bearer {settings.canvas_access_token}',
            'Accept': 'application/json'
        }
        self.canvas_base_url = settings.canvas_api_url
        
        # Zoho API setup with token management
        self.zoho_auth = ZohoAuthService()
        self.zoho_api_domain = settings.zoho_api_domain
    
    async def get_all_courses(
        self,
        db: AsyncSession,
        status: Optional[str] = None,
        source: Optional[str] = None
    ) -> List[Course]:
        """Get courses with optional filtering."""
        query = select(Course)
        
        conditions = []
        if status:
            conditions.append(Course.status == status)
        if source == 'canvas':
            conditions.append(Course.canvas_id.isnot(None))
        elif source == 'zoho':
            conditions.append(Course.zoho_program_id.isnot(None))
        
        if conditions:
            query = query.where(and_(*conditions))
            
        query = query.order_by(Course.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_course_by_id(self, db: AsyncSession, course_id: str) -> Optional[Course]:
        """Get single course by unified course_id."""
        query = select(Course).where(Course.course_id == course_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_course_by_canvas_id(self, db: AsyncSession, canvas_id: str) -> Optional[Course]:
        """Get course by Canvas ID."""
        query = select(Course).where(Course.canvas_id == canvas_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_course_by_zoho_id(self, db: AsyncSession, zoho_id: str) -> Optional[Course]:
        """Get course by Zoho program ID."""
        query = select(Course).where(Course.zoho_program_id == zoho_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def sync_canvas_courses(self, db: AsyncSession) -> Dict[str, Any]:
        """Fetch and sync all Canvas courses using dev-kit approach."""
        try:
            print("🔄 Syncing Canvas courses...")
            
            all_courses = []
            
            # Try multiple approaches based on dev-kit patterns
            # Start with the simplest approach first
            approaches = [
                {
                    'name': 'All Courses (No Filter)',
                    'params': {
                        'per_page': 100
                    }
                },
                {
                    'name': 'With Enrollment State',
                    'params': {
                        'enrollment_state': 'active',
                        'per_page': 100
                    }
                },
                {
                    'name': 'Include Teachers and Students',
                    'params': {
                        'include[]': ['teachers', 'total_students', 'term'],
                        'per_page': 100
                    }
                },
                {
                    'name': 'Published and Unpublished',
                    'params': {
                        'state[]': ['available', 'unpublished', 'completed'],
                        'per_page': 100
                    }
                }
            ]
            
            # First try to get courses from the account API (gets ALL courses)
            account_url = f"{self.canvas_base_url}/api/v1/accounts/1/courses"
            print(f"   Trying: Account API (All Courses)")
            print(f"   URL: {account_url}")
            
            try:
                response = requests.get(account_url, headers=self.canvas_headers, params={'per_page': 200}, timeout=10)
                print(f"   Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    courses = response.json()
                    print(f"   ✅ Found {len(courses)} courses from account API")
                    all_courses.extend(courses)
                    
                    # Log first few course names for debugging
                    for course in courses[:5]:
                        print(f"      - {course.get('name', 'Unnamed')} (ID: {course.get('id')})")
                else:
                    print(f"   ⚠️  Account API failed: {response.status_code}, falling back to user courses")
            except Exception as e:
                print(f"   ⚠️  Account API exception: {str(e)}, falling back to user courses")
            
            # If account API didn't work or returned nothing, try user enrollment approaches
            if not all_courses:
                courses_url = f"{self.canvas_base_url}/api/v1/courses"
                
                for approach in approaches:
                    print(f"   Trying: {approach['name']}")
                    print(f"   URL: {courses_url}")
                    print(f"   Params: {approach['params']}")
                    
                    try:
                        response = requests.get(courses_url, headers=self.canvas_headers, params=approach['params'], timeout=10)
                        print(f"   Response Status: {response.status_code}")
                        
                        if response.status_code == 200:
                            courses = response.json()
                            print(f"   ✅ Found {len(courses)} courses")
                            
                            if courses:
                                all_courses.extend(courses)
                                # Log first few course names for debugging
                                for course in courses[:3]:
                                    print(f"      - {course.get('name', 'Unnamed')} (ID: {course.get('id')})")
                            else:
                                print(f"   ⚠️  Empty response for {approach['name']}")
                        else:
                            print(f"   ❌ {approach['name']} failed: {response.status_code}")
                            print(f"   Error: {response.text[:200]}")
                    except requests.exceptions.Timeout:
                        print(f"   ⏱️  {approach['name']} timed out")
                    except Exception as e:
                        print(f"   ❌ {approach['name']} exception: {str(e)}")
            
            # Get unique courses
            unique_courses = {c['id']: c for c in all_courses if isinstance(c, dict) and 'id' in c}.values()
            canvas_courses = list(unique_courses)
            print(f"   Total unique Canvas courses: {len(canvas_courses)}")
            
            synced_courses = []
            updated_count = 0
            created_count = 0
            
            for canvas_course in canvas_courses:
                canvas_id = str(canvas_course['id'])
                unified_course_id = f"canvas_{canvas_id}"
                
                # Check if course exists
                existing_course = await self.get_course_by_canvas_id(db, canvas_id)
                
                if existing_course:
                    # Update existing course
                    existing_course.course_name = canvas_course.get('name', existing_course.course_name)
                    existing_course.status = self._map_canvas_status(canvas_course.get('workflow_state'))
                    existing_course.course_metadata = canvas_course
                    existing_course.updated_at = datetime.utcnow()
                    
                    # Parse dates if available
                    if canvas_course.get('start_at'):
                        existing_course.start_date = self._parse_canvas_date(canvas_course['start_at'])
                    if canvas_course.get('end_at'):
                        existing_course.end_date = self._parse_canvas_date(canvas_course['end_at'])
                    
                    synced_courses.append(existing_course)
                    updated_count += 1
                else:
                    # Create new course
                    new_course = Course(
                        course_id=unified_course_id,
                        course_name=canvas_course.get('name', 'Unnamed Course'),
                        canvas_id=canvas_id,
                        status=self._map_canvas_status(canvas_course.get('workflow_state')),
                        start_date=self._parse_canvas_date(canvas_course.get('start_at')),
                        end_date=self._parse_canvas_date(canvas_course.get('end_at')),
                        course_metadata=canvas_course
                    )
                    
                    db.add(new_course)
                    synced_courses.append(new_course)
                    created_count += 1
            
            await db.commit()
            
            print(f"   ✅ Canvas sync complete: {created_count} created, {updated_count} updated")
            
            return {
                'success': True,
                'courses_synced': len(synced_courses),
                'created': created_count,
                'updated': updated_count,
                'courses': [{'course_id': c.course_id, 'name': c.course_name} for c in synced_courses]
            }
            
        except Exception as e:
            print(f"   ❌ Canvas sync failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def sync_zoho_surveys_and_programs(self, db: AsyncSession) -> Dict[str, Any]:
        """Fetch and sync Zoho survey data using enhanced auth service."""
        try:
            print("🔄 Syncing Zoho surveys and programs...")
            
            # Use the enhanced Zoho auth service to get all survey data
            all_survey_data = self.zoho_auth.get_all_survey_data()
            
            if not all_survey_data.get('total_survey_records'):
                return {
                    'success': True,
                    'message': 'No survey data found in Zoho CRM',
                    'modules_checked': all_survey_data.get('modules_checked', []),
                    'errors': all_survey_data.get('errors', [])
                }
            
            # Process survey data and extract course programs
            programs_found = []
            survey_records_processed = 0
            
            for module_name, module_data in all_survey_data.get('survey_data', {}).items():
                print(f"   Processing {module_name} survey data...")
                
                for record in module_data.get('data', []):
                    survey_records_processed += 1
                    
                    # Extract course/program names from various fields
                    for field_name in ['Course_Name', 'Program_Name', 'Official_Program_Name', 'Programs', 'Program', 'Custom_Program_Group', 'Workshop']:
                        field_value = record.get(field_name)
                        if field_value and isinstance(field_value, str):
                            programs_found.append(field_value)
            
            # Remove duplicates while preserving order
            unique_programs = list(dict.fromkeys(programs_found))
            
            print(f"   📊 Processed {survey_records_processed} survey records")
            print(f"   📚 Found {len(unique_programs)} unique programs from survey data")
            
            # Create/update courses based on survey data
            synced_courses = []
            created_count = 0
            updated_count = 0
            
            for program_name in unique_programs:
                if not program_name or program_name.strip() == '':
                    continue
                    
                zoho_program_id = self._create_program_id(program_name)
                unified_course_id = f"zoho_{zoho_program_id}"
                
                # Check if course exists
                existing_course = await self.get_course_by_zoho_id(db, zoho_program_id)
                
                if existing_course:
                    # Update existing course
                    existing_course.course_name = program_name
                    existing_course.updated_at = datetime.utcnow()
                    
                    # Store survey metadata
                    if not existing_course.course_metadata:
                        existing_course.course_metadata = {}
                    existing_course.course_metadata.update({
                        'program_name': program_name,
                        'source': 'zoho_crm_surveys',
                        'survey_data_available': True,
                        'last_survey_sync': datetime.utcnow().isoformat()
                    })
                    
                    synced_courses.append(existing_course)
                    updated_count += 1
                else:
                    # Create new course
                    new_course = Course(
                        course_id=unified_course_id,
                        course_name=program_name,
                        zoho_program_id=zoho_program_id,
                        status='active',
                        course_metadata={
                            'program_name': program_name,
                            'source': 'zoho_crm_surveys',
                            'survey_data_available': True,
                            'last_survey_sync': datetime.utcnow().isoformat()
                        }
                    )
                    
                    db.add(new_course)
                    synced_courses.append(new_course)
                    created_count += 1
            
            await db.commit()
            
            print(f"   ✅ Zoho survey sync complete: {created_count} created, {updated_count} updated")
            
            return {
                'success': True,
                'survey_records_processed': survey_records_processed,
                'programs_synced': len(synced_courses),
                'created': created_count,
                'updated': updated_count,
                'modules_with_data': all_survey_data.get('modules_with_data', []),
                'programs': [{'course_id': c.course_id, 'name': c.course_name} for c in synced_courses],
                'survey_data_summary': {
                    'total_records': all_survey_data.get('total_survey_records', 0),
                    'modules_checked': all_survey_data.get('modules_checked', []),
                    'modules_with_data': all_survey_data.get('modules_with_data', [])
                }
            }
            
        except Exception as e:
            print(f"   ❌ Zoho survey sync failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def map_canvas_to_zoho(self, db: AsyncSession, canvas_id: str, zoho_program_id: str) -> Dict[str, Any]:
        """Manually map a Canvas course to a Zoho program by updating the Canvas course."""
        try:
            # Get Canvas course
            canvas_course = await self.get_course_by_canvas_id(db, canvas_id)
            if not canvas_course:
                return {'success': False, 'error': 'Canvas course not found'}
            
            # Get Zoho program
            zoho_course = await self.get_course_by_zoho_id(db, zoho_program_id)
            if not zoho_course:
                return {'success': False, 'error': 'Zoho program not found'}
            
            # Check if Canvas course already has a Zoho mapping
            if canvas_course.zoho_program_id:
                return {'success': False, 'error': f'Canvas course already mapped to Zoho program: {canvas_course.zoho_program_id}'}
            
            # Update Canvas course with Zoho program mapping
            canvas_course.zoho_program_id = zoho_program_id
            canvas_course.updated_at = datetime.utcnow()
            
            # Merge metadata
            if not canvas_course.course_metadata:
                canvas_course.course_metadata = {}
            canvas_course.course_metadata['zoho_mapping'] = {
                'zoho_program_id': zoho_program_id,
                'zoho_program_name': zoho_course.course_name,
                'mapping_type': 'manual',
                'mapped_at': datetime.utcnow().isoformat()
            }
            
            # Archive the separate Zoho course record since it's now unified
            zoho_course.status = 'archived'
            zoho_course.updated_at = datetime.utcnow()
            
            await db.commit()
            
            return {
                'success': True,
                'unified_course_id': canvas_course.course_id,
                'canvas_course': canvas_course.course_name,
                'zoho_program': zoho_course.course_name,
                'mapping_type': 'unified'
            }
            
        except Exception as e:
            await db.rollback()
            return {'success': False, 'error': str(e)}
    
    def _map_canvas_status(self, workflow_state: str) -> str:
        """Map Canvas workflow state to our status."""
        status_map = {
            'available': 'active',
            'completed': 'completed',
            'deleted': 'archived',
            'unpublished': 'draft'
        }
        return status_map.get(workflow_state, 'active')
    
    def _parse_canvas_date(self, date_str: str) -> Optional[datetime]:
        """Parse Canvas API date string."""
        if not date_str:
            return None
        try:
            # Canvas uses ISO format: 2023-08-15T10:30:00Z
            # Convert to naive datetime (remove timezone info) for database storage
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.replace(tzinfo=None)  # Remove timezone info for database
        except:
            return None
    
    def _create_program_id(self, program_name: str) -> str:
        """Create a clean program ID from program name."""
        import re
        import hashlib
        
        # Remove special characters and spaces, convert to lowercase
        clean_id = re.sub(r'[^a-zA-Z0-9\s]', '', program_name)
        clean_id = re.sub(r'\s+', '_', clean_id.strip()).lower()
        
        # If the clean ID is too long, create a shorter version with a hash
        if len(clean_id) > 40:  # Leave room for hash suffix
            # Take first 32 characters and add 8-character hash
            short_name = clean_id[:32]
            hash_suffix = hashlib.md5(program_name.encode()).hexdigest()[:8]
            clean_id = f"{short_name}_{hash_suffix}"
        
        return clean_id[:50]  # Ensure it's within database limit