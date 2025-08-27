#!/usr/bin/env python3
"""
Demo Data Migration Script
Populates database with demo course and feedback data for development
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from core.database import get_db_session, init_database
from models.database import (
    Course, FeedbackItem, WeightConfig, Recommendation, 
    DataSource, FeedbackType, PriorityLevel
)
from services.scoring_engine import ScoringEngine, WeightConfig as ScoringWeights
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoDataMigrator:
    """Handles migration of demo data to database"""
    
    def __init__(self):
        self.demo_data = {}
        self.scoring_engine = ScoringEngine(ScoringWeights())
        
    def load_demo_files(self):
        """Load demo data from JSON files"""
        demo_files = [
            "data/canvas_demo_complete.json",
            "data/canvas_demo_courses.json",
            "data/canvas_demo_feedback.json", 
            "data/canvas_demo_analytics.json"
        ]
        
        for file_path in demo_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)
                        self.demo_data.update(data)
                        logger.info(f"✅ Loaded {file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to load {file_path}: {e}")
            else:
                logger.warning(f"⚠️ Demo file not found: {file_path}")
        
        logger.info(f"📊 Total demo data keys: {list(self.demo_data.keys())}")
    
    def migrate_courses(self, db: Session) -> dict:
        """Migrate course data to database"""
        courses_data = self.demo_data.get("courses", [])
        
        if not courses_data:
            logger.warning("No course data found in demo files")
            return {"migrated": 0, "errors": 0}
        
        migrated = 0
        errors = 0
        
        for course_data in courses_data:
            try:
                # Check if course already exists
                existing = db.query(Course).filter(
                    Course.canvas_id == course_data.get("id")
                ).first()
                
                if existing:
                    logger.info(f"Course {course_data.get('name')} already exists, skipping")
                    continue
                
                # Parse dates
                start_date = None
                end_date = None
                
                if course_data.get("start_at"):
                    try:
                        start_date = datetime.fromisoformat(
                            course_data["start_at"].replace('Z', '+00:00')
                        )
                    except:
                        pass
                
                if course_data.get("end_at"):
                    try:
                        end_date = datetime.fromisoformat(
                            course_data["end_at"].replace('Z', '+00:00')
                        )
                    except:
                        pass
                
                # Create course record
                course = Course(
                    canvas_id=course_data.get("id"),
                    canvas_course_code=course_data.get("course_code"),
                    name=course_data.get("name", "Untitled Course"),
                    description=course_data.get("description"),
                    term=course_data.get("term"),
                    start_date=start_date,
                    end_date=end_date,
                    instructor_name=course_data.get("teacher"),
                    total_students=course_data.get("total_students", 0),
                    active_students=course_data.get("total_students", 0),
                    last_sync_at=datetime.now(timezone.utc)
                )
                
                db.add(course)
                db.commit()
                db.refresh(course)
                
                logger.info(f"✅ Migrated course: {course.name} (ID: {course.id})")
                migrated += 1
                
            except Exception as e:
                logger.error(f"❌ Error migrating course {course_data.get('name', 'Unknown')}: {e}")
                db.rollback()
                errors += 1
        
        return {"migrated": migrated, "errors": errors}
    
    def migrate_feedback(self, db: Session) -> dict:
        """Migrate feedback data to database"""
        feedback_data = self.demo_data.get("feedback", [])
        
        if not feedback_data:
            logger.warning("No feedback data found in demo files")
            return {"migrated": 0, "errors": 0}
        
        migrated = 0
        errors = 0
        
        for feedback_item in feedback_data:
            try:
                # Find corresponding course
                course = db.query(Course).filter(
                    Course.canvas_id == feedback_item.get("course_id")
                ).first()
                
                if not course:
                    logger.warning(f"Course not found for feedback item, course_id: {feedback_item.get('course_id')}")
                    continue
                
                # Parse submission date
                submitted_at = None
                if feedback_item.get("date"):
                    try:
                        submitted_at = datetime.fromisoformat(
                            feedback_item["date"].replace('Z', '+00:00')
                        )
                    except:
                        # Try different date formats
                        try:
                            submitted_at = datetime.strptime(feedback_item["date"], "%Y-%m-%d")
                        except:
                            submitted_at = datetime.now(timezone.utc) - timedelta(days=30)
                
                # Determine feedback type
                feedback_type = FeedbackType.REVIEW
                if "discussion" in feedback_item.get("type", "").lower():
                    feedback_type = FeedbackType.DISCUSSION
                elif "survey" in feedback_item.get("type", "").lower():
                    feedback_type = FeedbackType.SURVEY
                elif "evaluation" in feedback_item.get("type", "").lower():
                    feedback_type = FeedbackType.EVALUATION
                
                # Create feedback record
                feedback = FeedbackItem(
                    course_id=course.id,
                    source=DataSource.MANUAL,  # Demo data is manual
                    source_id=f"demo_{feedback_item.get('id', migrated)}",
                    feedback_type=feedback_type,
                    category=feedback_item.get("category"),
                    title=feedback_item.get("title"),
                    content=feedback_item.get("content", feedback_item.get("review", "")),
                    rating=feedback_item.get("rating"),
                    sentiment_score=feedback_item.get("sentiment"),
                    submitted_at=submitted_at,
                    processed=True,
                    issues_identified=feedback_item.get("issues", [])
                )
                
                db.add(feedback)
                migrated += 1
                
            except Exception as e:
                logger.error(f"❌ Error migrating feedback item: {e}")
                db.rollback()
                errors += 1
        
        # Commit all feedback at once
        try:
            db.commit()
            logger.info(f"✅ Committed {migrated} feedback items")
        except Exception as e:
            logger.error(f"❌ Error committing feedback: {e}")
            db.rollback()
            errors = migrated
            migrated = 0
        
        return {"migrated": migrated, "errors": errors}
    
    def generate_recommendations(self, db: Session) -> dict:
        """Generate priority recommendations using scoring engine"""
        
        # Get active weight configuration
        weight_config = db.query(WeightConfig).filter(
            WeightConfig.is_active == True
        ).first()
        
        if not weight_config:
            logger.warning("No active weight configuration found")
            return {"generated": 0, "errors": 0}
        
        # Get all courses with their feedback
        courses = db.query(Course).all()
        
        generated = 0
        errors = 0
        
        for course in courses:
            try:
                # Get course feedback
                feedback_items = db.query(FeedbackItem).filter(
                    FeedbackItem.course_id == course.id
                ).all()
                
                # Prepare data for scoring engine
                course_data = course.to_dict()
                feedback_data = [item.to_dict() for item in feedback_items]
                
                if not feedback_data:
                    logger.info(f"No feedback for course {course.name}, skipping recommendation")
                    continue
                
                # Calculate priority score
                breakdown, explanation = self.scoring_engine.calculate_course_priority(
                    course_data, feedback_data
                )
                
                # Determine priority level
                if breakdown.total_score >= 75:
                    priority_level = PriorityLevel.URGENT
                elif breakdown.total_score >= 60:
                    priority_level = PriorityLevel.HIGH
                elif breakdown.total_score >= 40:
                    priority_level = PriorityLevel.MEDIUM
                else:
                    priority_level = PriorityLevel.LOW
                
                # Create recommendation
                recommendation = Recommendation(
                    course_id=course.id,
                    weight_config_id=weight_config.id,
                    title=f"Improve {course.name}",
                    description=explanation.get("summary", f"Course improvement needed based on {len(feedback_data)} feedback items"),
                    priority_level=priority_level,
                    total_score=breakdown.total_score,
                    impact_score=breakdown.impact_score,
                    urgency_score=breakdown.urgency_score,
                    effort_score=breakdown.effort_score,
                    strategic_score=breakdown.strategic_score,
                    trend_score=breakdown.trend_score,
                    evidence_count=len(feedback_data),
                    evidence_summary=explanation.get("evidence_summary", []),
                    explanation=json.dumps(explanation, default=str),
                    status="open"
                )
                
                db.add(recommendation)
                generated += 1
                
                logger.info(f"✅ Generated recommendation for {course.name} (Score: {breakdown.total_score:.1f})")
                
            except Exception as e:
                logger.error(f"❌ Error generating recommendation for {course.name}: {e}")
                db.rollback()
                errors += 1
        
        # Commit all recommendations
        try:
            db.commit()
            logger.info(f"✅ Committed {generated} recommendations")
        except Exception as e:
            logger.error(f"❌ Error committing recommendations: {e}")
            db.rollback()
            errors = generated
            generated = 0
        
        return {"generated": generated, "errors": errors}
    
    def migrate_all(self) -> dict:
        """Run complete migration process"""
        logger.info("🚀 Starting demo data migration...")
        
        # Initialize database
        if not init_database():
            return {"error": "Failed to initialize database"}
        
        # Load demo data
        self.load_demo_files()
        
        if not self.demo_data:
            return {"error": "No demo data loaded"}
        
        results = {}
        
        with get_db_session() as db:
            # Migrate courses
            logger.info("📚 Migrating courses...")
            results["courses"] = self.migrate_courses(db)
            
            # Migrate feedback
            logger.info("💬 Migrating feedback...")
            results["feedback"] = self.migrate_feedback(db)
            
            # Generate recommendations
            logger.info("🎯 Generating recommendations...")
            results["recommendations"] = self.generate_recommendations(db)
        
        logger.info("🎉 Migration complete!")
        return results

def main():
    """Run migration from command line"""
    migrator = DemoDataMigrator()
    results = migrator.migrate_all()
    
    print("\n📊 Migration Results:")
    print(f"Courses: {results.get('courses', {}).get('migrated', 0)} migrated, {results.get('courses', {}).get('errors', 0)} errors")
    print(f"Feedback: {results.get('feedback', {}).get('migrated', 0)} migrated, {results.get('feedback', {}).get('errors', 0)} errors") 
    print(f"Recommendations: {results.get('recommendations', {}).get('generated', 0)} generated, {results.get('recommendations', {}).get('errors', 0)} errors")
    
    if results.get("error"):
        print(f"❌ Migration failed: {results['error']}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())