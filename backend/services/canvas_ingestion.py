"""
Canvas Data Ingestion Service
Converts real Canvas API data into our unified database schema
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from models.database import (
    Course, FeedbackItem, DataSource, FeedbackType, 
    SyncLog, Base
)
from core.database import get_db_session
from services.canvas_client import CanvasClient

logger = logging.getLogger(__name__)


class CanvasIngestionService:
    """Service for importing Canvas course data into our unified schema"""
    
    def __init__(self, canvas_client: CanvasClient):
        self.canvas_client = canvas_client
        
    def ingest_comprehensive_data(self, data_file: str = "canvas_comprehensive_data.json") -> Dict:
        """Ingest the comprehensive Canvas data we extracted"""
        
        with get_db_session() as db:
            sync_log = SyncLog(
                source=DataSource.CANVAS,
                status="running"
            )
            db.add(sync_log)
            db.commit()
            
            try:
                # Load comprehensive data
                with open(data_file, 'r') as f:
                    canvas_data = json.load(f)
                
                total_processed = 0
                total_inserted = 0
                total_updated = 0
                
                for course_id_str, course_data in canvas_data.items():
                    logger.info(f"Processing course: {course_data['course_info']['name']}")
                    
                    # Process course
                    course_result = self._process_course(db, course_data)
                    total_processed += 1
                    
                    if course_result['inserted']:
                        total_inserted += 1
                    else:
                        total_updated += 1
                    
                    # Process feedback sources
                    feedback_result = self._process_feedback_sources(
                        db, course_result['course'], course_data
                    )
                    
                    total_processed += feedback_result['processed']
                    total_inserted += feedback_result['inserted']
                
                # Update sync log
                sync_log.status = "success"
                sync_log.completed_at = datetime.utcnow()
                sync_log.records_processed = total_processed
                sync_log.records_inserted = total_inserted
                sync_log.records_updated = total_updated
                
                db.commit()
                
                logger.info(f"Canvas ingestion completed successfully")
                
                return {
                    "success": True,
                    "processed": total_processed,
                    "inserted": total_inserted,
                    "updated": total_updated,
                    "sync_log_id": sync_log.id
                }
                
            except Exception as e:
                sync_log.status = "failed"
                sync_log.completed_at = datetime.utcnow()
                sync_log.error_message = str(e)
                sync_log.errors_count = 1
                
                db.commit()
                
                logger.error(f"Canvas ingestion failed: {e}")
                
                return {
                    "success": False,
                    "error": str(e),
                    "sync_log_id": sync_log.id
                }
    
    def _process_course(self, db: Session, course_data: Dict) -> Dict:
        """Process a single course and return course object"""
        
        course_info = course_data['course_info']
        canvas_id = course_info['id']
        
        # Check if course already exists
        existing_course = db.query(Course).filter(
            Course.canvas_id == canvas_id
        ).first()
        
        if existing_course:
            # Update existing course
            existing_course.name = course_info['name'].strip()
            existing_course.canvas_course_code = course_info.get('course_code')
            existing_course.total_students = len(course_data.get('students', []))
            existing_course.last_sync_at = datetime.utcnow()
            
            # Update instructor info if available
            teachers = course_info.get('teachers', [])
            if teachers:
                existing_course.instructor_name = teachers[0].get('display_name')
                existing_course.instructor_email = teachers[0].get('email')
            
            db.commit()
            
            return {
                "course": existing_course,
                "inserted": False
            }
        
        else:
            # Create new course
            new_course = Course(
                canvas_id=canvas_id,
                name=course_info['name'].strip(),
                canvas_course_code=course_info.get('course_code'),
                total_students=len(course_data.get('students', [])),
                term=course_info.get('term', {}).get('name'),
                last_sync_at=datetime.utcnow()
            )
            
            # Add instructor info if available
            teachers = course_info.get('teachers', [])
            if teachers:
                new_course.instructor_name = teachers[0].get('display_name')
                new_course.instructor_email = teachers[0].get('email')
            
            # Parse dates if available
            if course_info.get('created_at'):
                try:
                    new_course.start_date = datetime.fromisoformat(
                        course_info['created_at'].replace('Z', '+00:00')
                    )
                except:
                    pass
            
            db.add(new_course)
            db.commit()
            
            return {
                "course": new_course,
                "inserted": True
            }
    
    def _process_feedback_sources(self, db: Session, course: Course, course_data: Dict) -> Dict:
        """Process feedback sources for a course"""
        
        processed = 0
        inserted = 0
        
        # Process discussion feedback
        for feedback_item in course_data.get('feedback_sources', []):
            try:
                # Check if feedback already exists
                existing = db.query(FeedbackItem).filter(
                    FeedbackItem.course_id == course.id,
                    FeedbackItem.source == DataSource.CANVAS,
                    FeedbackItem.source_id == str(feedback_item.get('source_id'))
                ).first()
                
                if existing:
                    processed += 1
                    continue
                
                # Create new feedback item
                feedback_type = self._map_feedback_type(feedback_item['type'])
                
                new_feedback = FeedbackItem(
                    course_id=course.id,
                    source=DataSource.CANVAS,
                    source_id=str(feedback_item.get('source_id')),
                    source_url=self._build_canvas_url(course, feedback_item),
                    feedback_type=feedback_type,
                    title=feedback_item.get('discussion_topic') or feedback_item.get('assignment_name'),
                    content=feedback_item.get('content', ''),
                    category=self._categorize_feedback(feedback_item.get('content', '')),
                    processed=False
                )
                
                # Parse submission date
                if feedback_item.get('created_at'):
                    try:
                        new_feedback.submitted_at = datetime.fromisoformat(
                            feedback_item['created_at'].replace('Z', '+00:00')
                        )
                    except:
                        pass
                
                db.add(new_feedback)
                processed += 1
                inserted += 1
                
            except Exception as e:
                logger.error(f"Error processing feedback item: {e}")
                continue
        
        db.commit()
        
        return {
            "processed": processed,
            "inserted": inserted
        }
    
    def _map_feedback_type(self, canvas_type: str) -> FeedbackType:
        """Map Canvas feedback types to our schema"""
        type_mapping = {
            'discussion': FeedbackType.DISCUSSION,
            'assignment_comment': FeedbackType.EVALUATION,
            'quiz_response': FeedbackType.SURVEY
        }
        return type_mapping.get(canvas_type, FeedbackType.REVIEW)
    
    def _categorize_feedback(self, content: str) -> str:
        """Basic categorization of feedback content"""
        content_lower = content.lower()
        
        # Simple keyword-based categorization
        if any(word in content_lower for word in ['difficult', 'hard', 'confusing', 'unclear']):
            return 'content_difficulty'
        elif any(word in content_lower for word in ['instructor', 'teacher', 'professor']):
            return 'instruction_quality'
        elif any(word in content_lower for word in ['technology', 'platform', 'system', 'canvas']):
            return 'technology_issues'
        elif any(word in content_lower for word in ['time', 'pace', 'schedule']):
            return 'pacing_issues'
        else:
            return 'general_feedback'
    
    def _build_canvas_url(self, course: Course, feedback_item: Dict) -> str:
        """Build Canvas URL for traceability"""
        base_url = "https://executiveeducation.instructure.com"
        course_id = course.canvas_id
        
        if feedback_item['type'] == 'discussion':
            return f"{base_url}/courses/{course_id}/discussion_topics/{feedback_item['source_id']}"
        elif feedback_item['type'] == 'assignment_comment':
            return f"{base_url}/courses/{course_id}/assignments/{feedback_item['source_id']}"
        else:
            return f"{base_url}/courses/{course_id}"
    
    def get_ingestion_stats(self) -> Dict:
        """Get statistics about ingested data"""
        
        with get_db_session() as db:
            # Course stats
            total_courses = db.query(Course).filter(Course.canvas_id.isnot(None)).count()
            
            # Feedback stats
            total_feedback = db.query(FeedbackItem).filter(
                FeedbackItem.source == DataSource.CANVAS
            ).count()
            
            from sqlalchemy import func
            
            feedback_by_type = db.query(
                FeedbackItem.feedback_type, 
                func.count(FeedbackItem.id).label('count')
            ).filter(
                FeedbackItem.source == DataSource.CANVAS
            ).group_by(FeedbackItem.feedback_type).all()
            
            # Recent sync logs
            recent_syncs = db.query(SyncLog).filter(
                SyncLog.source == DataSource.CANVAS
            ).order_by(SyncLog.started_at.desc()).limit(5).all()
            
            return {
                "courses": {
                    "total": total_courses,
                    "with_canvas_data": total_courses
                },
                "feedback": {
                    "total": total_feedback,
                    "by_type": {ftype: count for ftype, count in feedback_by_type}
                },
                "recent_syncs": [sync.to_dict() for sync in recent_syncs]
            }


def run_canvas_ingestion():
    """Standalone function to run Canvas data ingestion"""
    
    try:
        canvas_client = CanvasClient()
        ingestion_service = CanvasIngestionService(canvas_client)
        
        logger.info("Starting Canvas data ingestion...")
        result = ingestion_service.ingest_comprehensive_data()
        
        if result['success']:
            logger.info(f"✅ Ingestion completed: {result['processed']} processed, {result['inserted']} inserted")
            
            # Show stats
            stats = ingestion_service.get_ingestion_stats()
            logger.info(f"📊 Current database stats: {stats}")
            
        else:
            logger.error(f"❌ Ingestion failed: {result['error']}")
            
        return result
        
    except Exception as e:
        logger.error(f"❌ Ingestion service failed: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Run ingestion
    result = run_canvas_ingestion()
    
    if result['success']:
        print("🎉 Canvas data ingestion completed successfully!")
    else:
        print(f"❌ Ingestion failed: {result['error']}")