"""
Recommendation Engine Service
Generates intelligent priority recommendations using real Canvas data
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.database import (
    Course, FeedbackItem, Recommendation, WeightConfig, 
    DataSource, PriorityLevel, SyncLog
)
from services.scoring_engine import ScoringEngine, WeightConfig as ScoringWeights
from core.database import get_db_session

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Service for generating and managing course improvement recommendations"""
    
    def __init__(self, weight_config_id: Optional[int] = None):
        self.weight_config_id = weight_config_id
        self._scoring_engine = None
        
    def get_scoring_engine(self, db: Session) -> ScoringEngine:
        """Get configured scoring engine with active weights"""
        if self._scoring_engine is None:
            # Get active weight configuration
            if self.weight_config_id:
                weight_config = db.query(WeightConfig).filter(
                    WeightConfig.id == self.weight_config_id
                ).first()
            else:
                weight_config = db.query(WeightConfig).filter(
                    WeightConfig.is_active == True
                ).first()
            
            if not weight_config:
                logger.warning("No weight configuration found, using defaults")
                weights = ScoringWeights()
            else:
                weights = ScoringWeights(
                    impact_weight=weight_config.impact_weight,
                    urgency_weight=weight_config.urgency_weight,
                    effort_weight=weight_config.effort_weight,
                    strategic_weight=weight_config.strategic_weight,
                    trend_weight=weight_config.trend_weight
                )
            
            self._scoring_engine = ScoringEngine(weights)
            
        return self._scoring_engine
    
    def generate_all_recommendations(
        self, 
        force_refresh: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate recommendations for all courses with Canvas data"""
        
        with get_db_session() as db:
            # Get all courses with Canvas data
            courses = db.query(Course).filter(
                Course.canvas_id.isnot(None)
            ).all()
            
            if not courses:
                return {
                    "success": False,
                    "error": "No Canvas courses found",
                    "recommendations": []
                }
            
            scoring_engine = self.get_scoring_engine(db)
            
            # Get active weight config for tracking
            weight_config = db.query(WeightConfig).filter(
                WeightConfig.is_active == True
            ).first()
            
            if not weight_config:
                return {
                    "success": False,
                    "error": "No active weight configuration found",
                    "recommendations": []
                }
            
            recommendations = []
            processed_count = 0
            
            for course in courses:
                try:
                    logger.info(f"Processing recommendations for: {course.name}")
                    
                    # Check if we already have recent recommendations
                    if not force_refresh:
                        existing = db.query(Recommendation).filter(
                            Recommendation.course_id == course.id,
                            Recommendation.weight_config_id == weight_config.id
                        ).order_by(desc(Recommendation.generated_at)).first()
                        
                        if existing:
                            # Check if recommendation is less than 1 hour old
                            hours_old = (datetime.now(timezone.utc) - existing.generated_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600
                            
                            if hours_old < 1:
                                logger.info(f"Using existing recommendation for {course.name}")
                                recommendations.append(existing.to_dict())
                                continue
                    
                    # Generate new recommendation
                    recommendation = self.generate_course_recommendation(
                        course_id=course.id,
                        db=db,
                        context=context
                    )
                    
                    if recommendation:
                        recommendations.append(recommendation)
                        processed_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing {course.name}: {e}")
                    continue
            
            # Sort by total score
            recommendations.sort(key=lambda x: x.get("total_score", 0), reverse=True)
            
            return {
                "success": True,
                "processed_courses": processed_count,
                "total_recommendations": len(recommendations),
                "weight_config_id": weight_config.id,
                "recommendations": recommendations,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
    
    def generate_course_recommendation(
        self,
        course_id: int,
        db: Session,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Generate recommendation for a specific course"""
        
        # Get course data
        course = db.query(Course).filter(Course.id == course_id).first()
        if not course:
            logger.error(f"Course {course_id} not found")
            return None
        
        # Get feedback data for course
        feedback_items = db.query(FeedbackItem).filter(
            FeedbackItem.course_id == course_id,
            FeedbackItem.source == DataSource.CANVAS
        ).all()
        
        if not feedback_items:
            logger.info(f"No feedback found for course {course.name}")
            return None
        
        # Convert to scoring engine format
        course_data = self._format_course_data(course)
        feedback_data = [self._format_feedback_data(item) for item in feedback_items]
        
        # Get scoring engine and calculate priority
        scoring_engine = self.get_scoring_engine(db)
        
        try:
            score_breakdown, explanation = scoring_engine.calculate_course_priority(
                course_data, feedback_data, context or {}
            )
            
            # Get active weight config
            weight_config = db.query(WeightConfig).filter(
                WeightConfig.is_active == True
            ).first()
            
            if not weight_config:
                logger.error("No active weight configuration found")
                return None
            
            # Create recommendation record
            recommendation = Recommendation(
                course_id=course.id,
                weight_config_id=weight_config.id,
                title=self._generate_recommendation_title(course, explanation),
                description=explanation.get("summary", ""),
                priority_level=self._map_priority_level(explanation.get("priority_level")),
                total_score=score_breakdown.total_score,
                impact_score=score_breakdown.impact_score,
                urgency_score=score_breakdown.urgency_score,
                effort_score=score_breakdown.effort_score,
                strategic_score=score_breakdown.strategic_score,
                trend_score=score_breakdown.trend_score,
                evidence_count=len(feedback_items),
                evidence_summary=explanation.get("evidence_summary", []),
                explanation=explanation.get("primary_reason", ""),
                status="open"
            )
            
            # Save to database
            db.add(recommendation)
            db.commit()
            db.refresh(recommendation)
            
            # Return formatted result
            result = recommendation.to_dict()
            result.update({
                "course_name": course.name,
                "course_code": course.canvas_course_code,
                "explanation_details": explanation,
                "feedback_sources": [
                    {
                        "id": item.id,
                        "type": item.feedback_type.value,
                        "source_url": item.source_url,
                        "title": item.title,
                        "content_preview": item.content[:100] + "..." if len(item.content) > 100 else item.content,
                        "submitted_at": item.submitted_at.isoformat() if item.submitted_at else None
                    }
                    for item in feedback_items
                ]
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating recommendation for {course.name}: {e}")
            return None
    
    def _format_course_data(self, course: Course) -> Dict[str, Any]:
        """Format course data for scoring engine"""
        return {
            "id": course.id,
            "canvas_id": course.canvas_id,
            "name": course.name,
            "course_code": course.canvas_course_code,
            "total_students": course.total_students or 0,
            "instructor_name": course.instructor_name,
            "term": course.term,
            "start_date": course.start_date.isoformat() if course.start_date else None,
            "end_date": course.end_date.isoformat() if course.end_date else None,
            "created_at": course.created_at.isoformat() if course.created_at else None
        }
    
    def _format_feedback_data(self, feedback: FeedbackItem) -> Dict[str, Any]:
        """Format feedback data for scoring engine"""
        return {
            "id": feedback.id,
            "source": feedback.source.value,
            "source_id": feedback.source_id,
            "source_url": feedback.source_url,
            "feedback_type": feedback.feedback_type.value,
            "category": feedback.category,
            "title": feedback.title,
            "content": feedback.content,
            "rating": feedback.rating,
            "sentiment_score": feedback.sentiment_score,
            "submitted_at": feedback.submitted_at.isoformat() if feedback.submitted_at else None,
            "issues_identified": feedback.issues_identified or [],
            "processed": feedback.processed
        }
    
    def _generate_recommendation_title(
        self, 
        course: Course, 
        explanation: Dict[str, Any]
    ) -> str:
        """Generate a concise recommendation title"""
        
        priority = explanation.get("priority_level", "medium")
        course_name = course.name
        
        # Truncate long course names
        if len(course_name) > 50:
            course_name = course_name[:47] + "..."
        
        if priority == "urgent":
            return f"🔴 Urgent: {course_name}"
        elif priority == "high":
            return f"🟡 High Priority: {course_name}"
        elif priority == "medium":
            return f"🔵 Medium Priority: {course_name}"
        else:
            return f"🟢 Low Priority: {course_name}"
    
    def _map_priority_level(self, priority_str: str) -> PriorityLevel:
        """Map priority string to enum"""
        mapping = {
            "urgent": PriorityLevel.URGENT,
            "high": PriorityLevel.HIGH,
            "medium": PriorityLevel.MEDIUM,
            "low": PriorityLevel.LOW
        }
        return mapping.get(priority_str, PriorityLevel.MEDIUM)
    
    def validate_recommendation(
        self, 
        recommendation_id: int, 
        reviewer: str,
        notes: Optional[str] = None,
        status: str = "reviewed"
    ) -> Dict[str, Any]:
        """Mark a recommendation as validated/reviewed"""
        
        with get_db_session() as db:
            recommendation = db.query(Recommendation).filter(
                Recommendation.id == recommendation_id
            ).first()
            
            if not recommendation:
                return {
                    "success": False,
                    "error": "Recommendation not found"
                }
            
            # Update recommendation
            recommendation.status = status
            recommendation.reviewed_by = reviewer
            recommendation.reviewed_at = datetime.now(timezone.utc)
            
            if notes:
                recommendation.notes = notes
            
            db.commit()
            
            return {
                "success": True,
                "recommendation_id": recommendation_id,
                "status": status,
                "reviewed_by": reviewer,
                "reviewed_at": recommendation.reviewed_at.isoformat()
            }
    
    def get_recommendations_summary(self) -> Dict[str, Any]:
        """Get summary of all recommendations"""
        
        with get_db_session() as db:
            # Count by priority level
            from sqlalchemy import func
            
            priority_counts = db.query(
                Recommendation.priority_level,
                func.count(Recommendation.id).label('count')
            ).group_by(Recommendation.priority_level).all()
            
            # Count by status
            status_counts = db.query(
                Recommendation.status,
                func.count(Recommendation.id).label('count')
            ).group_by(Recommendation.status).all()
            
            # Recent recommendations
            recent_recommendations = db.query(Recommendation).order_by(
                desc(Recommendation.generated_at)
            ).limit(5).all()
            
            # Top scoring recommendations
            top_recommendations = db.query(Recommendation).order_by(
                desc(Recommendation.total_score)
            ).limit(10).all()
            
            return {
                "total_recommendations": db.query(Recommendation).count(),
                "priority_breakdown": {
                    level.value: count for level, count in priority_counts
                },
                "status_breakdown": {
                    status: count for status, count in status_counts
                },
                "recent_recommendations": [
                    {
                        "id": rec.id,
                        "title": rec.title,
                        "priority_level": rec.priority_level.value,
                        "total_score": rec.total_score,
                        "generated_at": rec.generated_at.isoformat() if rec.generated_at else None
                    }
                    for rec in recent_recommendations
                ],
                "top_recommendations": [
                    {
                        "id": rec.id,
                        "title": rec.title,
                        "total_score": rec.total_score,
                        "priority_level": rec.priority_level.value
                    }
                    for rec in top_recommendations
                ]
            }


def run_recommendation_generation():
    """Standalone function to generate all recommendations"""
    
    logger.info("🔄 Starting recommendation generation...")
    
    try:
        engine = RecommendationEngine()
        
        # Add some context for strategic scoring
        context = {
            "institutional_priorities": [
                {
                    "keywords": ["strategic", "ai", "artificial intelligence"],
                    "weight": 20,
                    "description": "AI and Strategic courses are institutional priorities"
                },
                {
                    "keywords": ["women", "leadership"],
                    "weight": 15,
                    "description": "Leadership development programs"
                }
            ]
        }
        
        result = engine.generate_all_recommendations(
            force_refresh=True,
            context=context
        )
        
        if result["success"]:
            logger.info(f"✅ Generated {result['total_recommendations']} recommendations")
            
            # Show summary
            summary = engine.get_recommendations_summary()
            logger.info(f"📊 Priority breakdown: {summary['priority_breakdown']}")
            logger.info(f"📊 Status breakdown: {summary['status_breakdown']}")
            
            return result
        else:
            logger.error(f"❌ Recommendation generation failed: {result['error']}")
            return result
            
    except Exception as e:
        logger.error(f"❌ Recommendation engine failed: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Generate recommendations
    result = run_recommendation_generation()
    
    if result["success"]:
        print("🎉 Recommendations generated successfully!")
        
        # Print top recommendations
        print("\\n🏆 TOP RECOMMENDATIONS:")
        for i, rec in enumerate(result["recommendations"][:3], 1):
            print(f"{i}. {rec['title']} (Score: {rec['total_score']:.1f})")
            print(f"   {rec['explanation']}")
    else:
        print(f"❌ Generation failed: {result['error']}")