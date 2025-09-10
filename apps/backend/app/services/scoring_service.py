"""Service for priority scoring calculations."""

from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
import json
from datetime import datetime, timedelta

from ..models import Feedback, WeightConfig


class ScoringService:
    """Business logic for calculating explainable priority scores."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def calculate_priority(
        self, 
        course_id: str,
        feedback_items: List[Feedback],
        weights: WeightConfig
    ) -> Dict[str, Any]:
        """Calculate explainable priority score for a course."""
        
        if not feedback_items:
            return self._create_empty_priority(course_id)
        
        # Calculate individual factor scores
        impact_score = self._calculate_impact_score(feedback_items)
        urgency_score = self._calculate_urgency_score(feedback_items)
        effort_score = self._calculate_effort_score(feedback_items)
        strategic_score = self._calculate_strategic_score(feedback_items)
        trend_score = self._calculate_trend_score(feedback_items)
        
        # Calculate weighted final score
        final_score = (
            impact_score * weights.impact_weight +
            urgency_score * weights.urgency_weight +
            effort_score * weights.effort_weight +
            strategic_score * weights.strategic_weight +
            trend_score * weights.trend_weight
        )
        
        # Round to nearest integer (1-5 scale)
        priority_score = min(5, max(1, round(final_score)))
        
        # Generate issue summary
        issue_summary = self._generate_issue_summary(feedback_items)
        
        # Extract evidence
        evidence = self._extract_evidence(feedback_items)
        
        # Count affected students
        students_affected = len(set(item.student_email for item in feedback_items if item.student_email))
        
        return {
            "course_id": course_id,
            "issue_summary": issue_summary,
            "priority_score": priority_score,
            "impact_score": round(impact_score, 2),
            "urgency_score": round(urgency_score, 2), 
            "effort_score": round(effort_score, 2),
            "strategic_score": round(strategic_score, 2),
            "trend_score": round(trend_score, 2),
            "students_affected": students_affected,
            "feedback_ids": [item.id for item in feedback_items],
            "evidence": evidence
        }
    
    def _calculate_impact_score(self, feedback_items: List[Feedback]) -> float:
        """Calculate impact score based on severity and frequency."""
        if not feedback_items:
            return 1.0
        
        severity_weights = {"critical": 5, "high": 4, "medium": 3, "low": 2}
        total_impact = 0
        
        for item in feedback_items:
            severity_score = severity_weights.get(item.severity, 2)
            rating_impact = (6 - item.rating) if item.rating else 3  # Lower rating = higher impact
            total_impact += (severity_score + rating_impact) / 2
        
        # Average and normalize to 1-5 scale
        avg_impact = total_impact / len(feedback_items)
        return min(5.0, max(1.0, avg_impact))
    
    def _calculate_urgency_score(self, feedback_items: List[Feedback]) -> float:
        """Calculate urgency based on recency and issue type."""
        if not feedback_items:
            return 1.0
        
        now = datetime.utcnow()
        urgency_total = 0
        
        for item in feedback_items:
            # Recent feedback is more urgent
            days_old = (now - item.created_at).days
            recency_score = max(1, 5 - (days_old / 7))  # Decreases over weeks
            
            # Technical issues are more urgent
            urgency_keywords = ["broken", "error", "not working", "crash", "urgent"]
            keyword_boost = 1.5 if any(keyword in item.feedback_text.lower() 
                                     for keyword in urgency_keywords
                                     if item.feedback_text) else 1.0
            
            urgency_total += recency_score * keyword_boost
        
        avg_urgency = urgency_total / len(feedback_items)
        return min(5.0, max(1.0, avg_urgency))
    
    def _calculate_effort_score(self, feedback_items: List[Feedback]) -> float:
        """Calculate effort score (higher = easier to fix)."""
        if not feedback_items:
            return 3.0
        
        # Quick fix indicators
        quick_fix_keywords = ["typo", "spelling", "link", "color", "font", "text"]
        complex_keywords = ["redesign", "rebuild", "architecture", "database", "integration"]
        
        effort_total = 0
        
        for item in feedback_items:
            base_effort = 3.0  # Medium effort by default
            
            if item.feedback_text:
                text_lower = item.feedback_text.lower()
                
                if any(keyword in text_lower for keyword in quick_fix_keywords):
                    effort_total += 4.5  # Easy to fix
                elif any(keyword in text_lower for keyword in complex_keywords):
                    effort_total += 1.5  # Hard to fix
                else:
                    effort_total += base_effort
            else:
                effort_total += base_effort
        
        avg_effort = effort_total / len(feedback_items)
        return min(5.0, max(1.0, avg_effort))
    
    def _calculate_strategic_score(self, feedback_items: List[Feedback]) -> float:
        """Calculate strategic alignment score."""
        # For now, return a moderate score - this could be enhanced with course metadata
        return 3.0
    
    def _calculate_trend_score(self, feedback_items: List[Feedback]) -> float:
        """Calculate trend score based on feedback frequency over time."""
        if len(feedback_items) < 2:
            return 3.0
        
        # Sort by date
        sorted_items = sorted(feedback_items, key=lambda x: x.created_at)
        
        # Compare recent vs older feedback
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        recent_count = len([item for item in sorted_items if item.created_at > cutoff_date])
        total_count = len(sorted_items)
        
        # If more than half the feedback is recent, it's a growing trend
        trend_ratio = recent_count / total_count
        
        if trend_ratio > 0.6:
            return 4.5  # Growing issue
        elif trend_ratio < 0.2:
            return 2.0  # Declining issue
        else:
            return 3.0  # Stable
    
    def _generate_issue_summary(self, feedback_items: List[Feedback]) -> str:
        """Generate a summary of the main issues."""
        if not feedback_items:
            return "No feedback available"
        
        # Get most common words/themes
        common_issues = []
        severity_counts = {}
        
        for item in feedback_items:
            if item.severity:
                severity_counts[item.severity] = severity_counts.get(item.severity, 0) + 1
        
        # Find most severe issues
        if severity_counts:
            top_severity = max(severity_counts.items(), key=lambda x: x[1])
            severity_text = f"{top_severity[0]} issues" if top_severity[1] > 1 else f"{top_severity[0]} issue"
            common_issues.append(f"{top_severity[1]} {severity_text}")
        
        # Add course context
        course_name = feedback_items[0].course_name
        issue_summary = f"{course_name}: {', '.join(common_issues)} reported by students"
        
        return issue_summary[:500]  # Limit length
    
    def _extract_evidence(self, feedback_items: List[Feedback]) -> Dict[str, Any]:
        """Extract evidence including quotes and source links."""
        student_quotes = []
        source_links = []
        
        for item in feedback_items[:5]:  # Limit to top 5 for evidence
            if item.feedback_text:
                quote_data = {
                    "feedback_id": item.id,
                    "quote": item.feedback_text[:200] + "..." if len(item.feedback_text) > 200 else item.feedback_text,
                    "source": item.source,
                    "source_id": item.source_id,
                    "severity": item.severity
                }
                student_quotes.append(quote_data)
                
                # Add source links (would need actual URLs in production)
                if item.source == "canvas" and item.source_id:
                    source_links.append({
                        "platform": "canvas",
                        "url": f"https://canvas.../discussion/{item.source_id}",
                        "description": "Original Canvas discussion"
                    })
                elif item.source == "zoho" and item.source_id:
                    source_links.append({
                        "platform": "zoho", 
                        "url": f"https://zoho.../survey/{item.source_id}",
                        "description": "Original Zoho survey response"
                    })
        
        return {
            "student_quotes": student_quotes,
            "source_links": source_links,
            "affected_students": len(set(item.student_email for item in feedback_items if item.student_email)),
            "confidence_score": min(1.0, len(feedback_items) / 10)  # Higher with more feedback
        }
    
    def _create_empty_priority(self, course_id: str) -> Dict[str, Any]:
        """Create empty priority for courses with no feedback."""
        return {
            "course_id": course_id,
            "issue_summary": "No feedback available for this course",
            "priority_score": 1,
            "impact_score": 1.0,
            "urgency_score": 1.0,
            "effort_score": 5.0,
            "strategic_score": 3.0,
            "trend_score": 3.0,
            "students_affected": 0,
            "feedback_ids": [],
            "evidence": {"student_quotes": [], "source_links": [], "affected_students": 0, "confidence_score": 0.0}
        }