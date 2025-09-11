from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
from collections import Counter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models import Feedback, Priority, WeightConfig
from ..config.config import settings

class PriorityScoring:
    """5-Point Priority Scoring Engine with Tunable Weights"""
    
    PRIORITY_LABELS = {
        5: {"label": "CRITICAL", "action": "Fix immediately", "color": "red"},
        4: {"label": "HIGH", "action": "Fix this week", "color": "orange"},
        3: {"label": "MEDIUM", "action": "Fix this month", "color": "yellow"},
        2: {"label": "LOW", "action": "Consider fixing", "color": "blue"},
        1: {"label": "MINIMAL", "action": "Monitor only", "color": "gray"}
    }
    
    SEVERITY_WEIGHTS = {
        "critical": 5.0,
        "high": 4.0,
        "medium": 3.0,
        "low": 2.0,
        "minimal": 1.0
    }
    
    def __init__(self, weights: WeightConfig = None):
        self.weights = weights or WeightConfig()
    
    def calculate_impact_score(self, feedback_group: List[Feedback]) -> Tuple[float, Dict]:
        """
        Calculate impact score (1-5) based on student count and severity
        """
        if not feedback_group:
            return 1.0, {"students_affected": 0, "avg_severity": "minimal"}
        
        # Count unique students affected
        unique_students = len(set(f.student_email for f in feedback_group if f.student_email))
        
        # Calculate average severity weight
        severity_scores = [self.SEVERITY_WEIGHTS.get(f.severity, 3.0) for f in feedback_group]
        avg_severity_score = sum(severity_scores) / len(severity_scores) if severity_scores else 3.0
        
        # Impact calculation: combine student count and severity
        # Scale student count (1-5 students = 1, 6-15 = 2, 16-30 = 3, 31-50 = 4, 50+ = 5)
        if unique_students <= 1:
            student_factor = 1.0
        elif unique_students <= 5:
            student_factor = 2.0
        elif unique_students <= 15:
            student_factor = 3.0
        elif unique_students <= 30:
            student_factor = 4.0
        else:
            student_factor = 5.0
        
        # Combine student count and severity (weighted average)
        impact_score = (student_factor * 0.6) + (avg_severity_score * 0.4)
        impact_score = max(1.0, min(5.0, impact_score))
        
        return impact_score, {
            "students_affected": unique_students,
            "avg_severity_score": avg_severity_score,
            "student_factor": student_factor
        }
    
    def calculate_urgency_score(self, feedback_group: List[Feedback]) -> Tuple[float, Dict]:
        """
        Calculate urgency score (1-5) based on critical issues and recency
        """
        if not feedback_group:
            return 1.0, {"has_critical": False, "avg_days_old": 0}
        
        # Check for critical/high severity issues
        critical_count = sum(1 for f in feedback_group if f.severity in ["critical", "high"])
        has_critical = critical_count > 0
        
        # Calculate recency (how recent are the complaints?)
        now = datetime.utcnow()
        days_old = [(now - f.created_at).days for f in feedback_group if f.created_at]
        avg_days_old = sum(days_old) / len(days_old) if days_old else 30
        
        # Urgency scoring
        urgency_score = 1.0
        
        # Critical issues boost urgency significantly
        if has_critical:
            urgency_score += 2.0
        
        # Recent issues are more urgent
        if avg_days_old <= 3:
            urgency_score += 1.5  # Very recent
        elif avg_days_old <= 7:
            urgency_score += 1.0  # Recent
        elif avg_days_old <= 14:
            urgency_score += 0.5  # Somewhat recent
        
        # Multiple reports increase urgency
        if len(feedback_group) >= 5:
            urgency_score += 1.0
        elif len(feedback_group) >= 3:
            urgency_score += 0.5
        
        urgency_score = max(1.0, min(5.0, urgency_score))
        
        return urgency_score, {
            "has_critical": has_critical,
            "critical_count": critical_count,
            "avg_days_old": avg_days_old,
            "feedback_count": len(feedback_group)
        }
    
    def calculate_effort_score(self, feedback_group: List[Feedback], issue_summary: str) -> Tuple[float, Dict]:
        """
        Calculate effort score (1-5) - INVERTED: higher score = less effort (quick wins)
        """
        if not feedback_group:
            return 3.0, {"complexity": "medium"}
        
        # Analyze issue complexity based on feedback content and summary
        complexity_indicators = {
            "low": ["typo", "spelling", "link", "broken link", "404", "missing link"],
            "medium": ["video", "image", "content", "example", "instruction", "unclear"],
            "high": ["design", "restructure", "rebuild", "architecture", "fundamental"]
        }
        
        # Combine all text to analyze
        all_text = (issue_summary + " " + " ".join(f.feedback_text or "" for f in feedback_group)).lower()
        
        complexity_score = 3.0  # Default medium
        
        # Check for low-effort indicators (quick fixes)
        low_effort_matches = sum(1 for indicator in complexity_indicators["low"] if indicator in all_text)
        if low_effort_matches >= 2:
            complexity_score = 5.0  # Very easy to fix
        elif low_effort_matches >= 1:
            complexity_score = 4.0  # Easy to fix
        
        # Check for high-effort indicators (complex fixes)
        high_effort_matches = sum(1 for indicator in complexity_indicators["high"] if indicator in all_text)
        if high_effort_matches >= 2:
            complexity_score = 1.0  # Very hard to fix
        elif high_effort_matches >= 1:
            complexity_score = 2.0  # Hard to fix
        
        # Medium effort indicators
        medium_effort_matches = sum(1 for indicator in complexity_indicators["medium"] if indicator in all_text)
        if medium_effort_matches >= 2 and complexity_score == 3.0:
            complexity_score = 3.0  # Medium effort
        
        complexity_label = "low" if complexity_score >= 4 else "high" if complexity_score <= 2 else "medium"
        
        return complexity_score, {
            "complexity": complexity_label,
            "low_effort_matches": low_effort_matches,
            "high_effort_matches": high_effort_matches,
            "medium_effort_matches": medium_effort_matches
        }
    
    def calculate_strategic_score(self, feedback_group: List[Feedback], course_id: str) -> Tuple[float, Dict]:
        """
        Calculate strategic score (1-5) based on course importance and learning objectives
        """
        # For now, use course characteristics and feedback patterns
        # In future, could integrate with course metadata
        
        strategic_indicators = {
            "high": ["learning objective", "core concept", "fundamental", "essential", "key skill"],
            "medium": ["assignment", "assessment", "grade", "completion", "understanding"],
            "low": ["cosmetic", "nice to have", "optional", "bonus", "extra"]
        }
        
        all_text = " ".join(f.feedback_text or "" for f in feedback_group).lower()
        
        strategic_score = 3.0  # Default medium strategic value
        
        # Check strategic importance indicators
        high_strategic = sum(1 for indicator in strategic_indicators["high"] if indicator in all_text)
        medium_strategic = sum(1 for indicator in strategic_indicators["medium"] if indicator in all_text)
        low_strategic = sum(1 for indicator in strategic_indicators["low"] if indicator in all_text)
        
        if high_strategic >= 2:
            strategic_score = 5.0
        elif high_strategic >= 1:
            strategic_score = 4.0
        elif low_strategic >= 2:
            strategic_score = 1.0
        elif low_strategic >= 1:
            strategic_score = 2.0
        elif medium_strategic >= 2:
            strategic_score = 3.5
        
        return strategic_score, {
            "strategic_level": "high" if strategic_score >= 4 else "low" if strategic_score <= 2 else "medium",
            "high_indicators": high_strategic,
            "medium_indicators": medium_strategic,
            "low_indicators": low_strategic
        }
    
    def calculate_trend_score(self, feedback_group: List[Feedback]) -> Tuple[float, Dict]:
        """
        Calculate trend score (1-5) based on feedback frequency over time
        """
        if len(feedback_group) <= 1:
            return 2.0, {"trend": "single_report", "feedback_frequency": "low"}
        
        # Group feedback by time periods
        now = datetime.utcnow()
        recent_week = [f for f in feedback_group if f.created_at and (now - f.created_at).days <= 7]
        recent_month = [f for f in feedback_group if f.created_at and (now - f.created_at).days <= 30]
        older = [f for f in feedback_group if f.created_at and (now - f.created_at).days > 30]
        
        trend_score = 3.0  # Default stable trend
        
        # Increasing trend (more recent reports)
        if len(recent_week) >= 2 and len(recent_week) > len(older):
            trend_score = 5.0  # Rapidly increasing
        elif len(recent_month) > len(older) * 1.5:
            trend_score = 4.0  # Increasing
        elif len(recent_week) == 0 and len(older) >= 2:
            trend_score = 1.0  # Decreasing/resolved
        elif len(recent_month) < len(older):
            trend_score = 2.0  # Stable/decreasing
        
        frequency_label = "high" if len(feedback_group) >= 5 else "medium" if len(feedback_group) >= 3 else "low"
        trend_label = "increasing" if trend_score >= 4 else "decreasing" if trend_score <= 2 else "stable"
        
        return trend_score, {
            "trend": trend_label,
            "feedback_frequency": frequency_label,
            "recent_week": len(recent_week),
            "recent_month": len(recent_month),
            "older": len(older)
        }
    
    def calculate_priority_score(self, feedback_group: List[Feedback], issue_summary: str, course_id: str) -> Dict[str, Any]:
        """
        Calculate final priority score using weighted factors
        """
        # Calculate individual factor scores
        impact_score, impact_details = self.calculate_impact_score(feedback_group)
        urgency_score, urgency_details = self.calculate_urgency_score(feedback_group)
        effort_score, effort_details = self.calculate_effort_score(feedback_group, issue_summary)
        strategic_score, strategic_details = self.calculate_strategic_score(feedback_group, course_id)
        trend_score, trend_details = self.calculate_trend_score(feedback_group)
        
        # Apply weights to calculate final score
        weighted_score = (
            impact_score * self.weights.impact_weight +
            urgency_score * self.weights.urgency_weight +
            effort_score * self.weights.effort_weight +
            strategic_score * self.weights.strategic_weight +
            trend_score * self.weights.trend_weight
        )
        
        # Round to 1-5 scale
        final_score = max(1, min(5, round(weighted_score)))
        
        # Prepare evidence from feedback
        evidence = []
        for feedback in feedback_group[:5]:  # Limit to 5 pieces of evidence
            if feedback.feedback_text:
                evidence.append({
                    "quote": feedback.feedback_text[:200] + "..." if len(feedback.feedback_text) > 200 else feedback.feedback_text,
                    "source": feedback.source,
                    "source_id": feedback.source_id,
                    "rating": feedback.rating,
                    "severity": feedback.severity
                })
        
        return {
            "priority_score": final_score,
            "priority_label": self.PRIORITY_LABELS[final_score]["label"],
            "priority_action": self.PRIORITY_LABELS[final_score]["action"],
            "priority_color": self.PRIORITY_LABELS[final_score]["color"],
            "factor_scores": {
                "impact": impact_score,
                "urgency": urgency_score, 
                "effort": effort_score,
                "strategic": strategic_score,
                "trend": trend_score
            },
            "factor_details": {
                "impact": impact_details,
                "urgency": urgency_details,
                "effort": effort_details,
                "strategic": strategic_details,
                "trend": trend_details
            },
            "weights_used": {
                "impact": self.weights.impact_weight,
                "urgency": self.weights.urgency_weight,
                "effort": self.weights.effort_weight,
                "strategic": self.weights.strategic_weight,
                "trend": self.weights.trend_weight
            },
            "evidence": evidence,
            "students_affected": impact_details.get("students_affected", 0),
            "feedback_ids": [f.id for f in feedback_group],
            "calculation_timestamp": datetime.utcnow().isoformat()
        }

async def group_similar_feedback(session: AsyncSession, course_id: str = None) -> List[List[Feedback]]:
    """
    Group similar feedback items together for priority calculation
    Simple grouping by course and keywords for now
    """
    query = select(Feedback).where(Feedback.is_active == True)
    if course_id:
        query = query.where(Feedback.course_id == course_id)
    
    result = await session.execute(query)
    all_feedback = result.scalars().all()
    
    if not all_feedback:
        return []
    
    # Simple grouping by course_id for now
    # In production, could use more sophisticated similarity matching
    groups = {}
    for feedback in all_feedback:
        course_key = feedback.course_id
        if course_key not in groups:
            groups[course_key] = []
        groups[course_key].append(feedback)
    
    return list(groups.values())

async def generate_issue_summary(feedback_group: List[Feedback]) -> str:
    """
    Generate a human-readable summary of the issue from feedback
    """
    if not feedback_group:
        return "No feedback available"
    
    # Count common keywords
    all_text = " ".join(f.feedback_text or "" for f in feedback_group).lower()
    
    # Simple keyword extraction for summary
    issue_keywords = []
    if "video" in all_text:
        issue_keywords.append("video content")
    if "assignment" in all_text:
        issue_keywords.append("assignment instructions")
    if "unclear" in all_text or "confusing" in all_text:
        issue_keywords.append("clarity issues")
    if "broken" in all_text or "not working" in all_text:
        issue_keywords.append("technical problems")
    if "missing" in all_text:
        issue_keywords.append("missing content")
    
    course_name = feedback_group[0].course_name
    student_count = len(set(f.student_email for f in feedback_group if f.student_email))
    
    if issue_keywords:
        summary = f"{', '.join(issue_keywords[:2])} in {course_name}"
    else:
        summary = f"Course feedback issues in {course_name}"
    
    return summary