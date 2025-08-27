"""
Intelligent Priority Scoring Engine
Multi-factor algorithm with full explainability for course improvement recommendations
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import math
import json
from dataclasses import dataclass
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

@dataclass
class ScoreBreakdown:
    """Detailed score breakdown for explainability"""
    impact_score: float
    urgency_score: float
    effort_score: float
    strategic_score: float
    trend_score: float
    total_score: float
    confidence: float
    
    def to_dict(self) -> Dict[str, float]:
        return {
            "impact": round(self.impact_score, 2),
            "urgency": round(self.urgency_score, 2),
            "effort": round(self.effort_score, 2),
            "strategic": round(self.strategic_score, 2),
            "trend": round(self.trend_score, 2),
            "total": round(self.total_score, 2),
            "confidence": round(self.confidence, 2)
        }

@dataclass
class WeightConfig:
    """Scoring weights configuration"""
    impact_weight: float = 0.35
    urgency_weight: float = 0.25
    effort_weight: float = 0.20
    strategic_weight: float = 0.15
    trend_weight: float = 0.05
    
    def validate(self) -> bool:
        """Ensure weights sum to 1.0"""
        total = (self.impact_weight + self.urgency_weight + 
                self.effort_weight + self.strategic_weight + self.trend_weight)
        return abs(total - 1.0) < 0.01

class ScoringEngine:
    """
    Intelligent scoring engine that calculates priority scores based on:
    1. IMPACT: How many students are affected (frequency & severity)
    2. URGENCY: Time-sensitivity and course timeline factors
    3. EFFORT: Implementation difficulty and resource requirements
    4. STRATEGIC: Alignment with institutional priorities
    5. TREND: Issue trajectory and momentum
    """
    
    def __init__(self, weights: Optional[WeightConfig] = None):
        self.weights = weights or WeightConfig()
        if not self.weights.validate():
            raise ValueError("Scoring weights must sum to 1.0")
    
    def calculate_course_priority(
        self,
        course_data: Dict[str, Any],
        feedback_data: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[ScoreBreakdown, Dict[str, Any]]:
        """
        Calculate priority score for a course with full explanation
        
        Args:
            course_data: Course information (enrollment, dates, etc.)
            feedback_data: All feedback items for the course
            context: Additional context (institutional priorities, etc.)
            
        Returns:
            Tuple of (ScoreBreakdown, explanation_dict)
        """
        context = context or {}
        
        # Calculate individual factor scores
        impact_score = self._calculate_impact_score(course_data, feedback_data)
        urgency_score = self._calculate_urgency_score(course_data, feedback_data, context)
        effort_score = self._calculate_effort_score(course_data, feedback_data)
        strategic_score = self._calculate_strategic_score(course_data, context)
        trend_score = self._calculate_trend_score(feedback_data)
        
        # Calculate weighted total
        total_score = (
            impact_score * self.weights.impact_weight +
            urgency_score * self.weights.urgency_weight +
            effort_score * self.weights.effort_weight +
            strategic_score * self.weights.strategic_weight +
            trend_score * self.weights.trend_weight
        )
        
        # Calculate confidence based on data availability
        confidence = self._calculate_confidence(course_data, feedback_data)
        
        breakdown = ScoreBreakdown(
            impact_score=impact_score,
            urgency_score=urgency_score,
            effort_score=effort_score,
            strategic_score=strategic_score,
            trend_score=trend_score,
            total_score=total_score,
            confidence=confidence
        )
        
        # Generate human-readable explanation
        explanation = self._generate_explanation(
            course_data, feedback_data, breakdown, context
        )
        
        return breakdown, explanation
    
    def _calculate_impact_score(
        self,
        course_data: Dict[str, Any],
        feedback_data: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate impact score (0-100) based on:
        - Number of students affected
        - Severity of reported issues
        - Frequency of complaints
        """
        total_students = course_data.get("total_students", 0)
        if total_students == 0:
            return 0
        
        # Count negative feedback
        negative_feedback = [
            f for f in feedback_data 
            if f.get("sentiment_score", 0) < -0.2 or f.get("rating", 3) < 2.5
        ]
        
        # Calculate base impact from affected student ratio
        affected_ratio = len(negative_feedback) / max(len(feedback_data), 1)
        base_impact = min(affected_ratio * 100, 100)
        
        # Severity multiplier based on issue types
        severity_multiplier = 1.0
        for feedback in negative_feedback:
            issues = feedback.get("issues_identified", [])
            for issue in issues:
                if issue.get("severity") == "high":
                    severity_multiplier += 0.2
                elif issue.get("category") in ["accessibility", "technical"]:
                    severity_multiplier += 0.15
        
        # Scale factor based on course size
        scale_factor = min(math.log10(total_students + 1) / 2, 1.5)
        
        impact_score = min(base_impact * severity_multiplier * scale_factor, 100)
        
        logger.debug(f"Impact calculation: base={base_impact:.1f}, "
                    f"severity={severity_multiplier:.2f}, scale={scale_factor:.2f}")
        
        return impact_score
    
    def _calculate_urgency_score(
        self,
        course_data: Dict[str, Any],
        feedback_data: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate urgency score (0-100) based on:
        - Time remaining in course
        - Assessment deadlines
        - Issue recency
        """
        now = datetime.now()
        
        # Course timeline urgency
        course_end = course_data.get("end_date")
        timeline_urgency = 50  # Default moderate urgency
        
        if course_end:
            try:
                if isinstance(course_end, str):
                    end_date = datetime.fromisoformat(course_end.replace('Z', '+00:00'))
                else:
                    end_date = course_end
                
                days_remaining = (end_date - now).days
                
                if days_remaining < 7:
                    timeline_urgency = 100  # Critical
                elif days_remaining < 30:
                    timeline_urgency = 80   # High
                elif days_remaining < 60:
                    timeline_urgency = 60   # Moderate-high
                else:
                    timeline_urgency = 30   # Low
                    
            except (ValueError, TypeError):
                pass
        
        # Recent feedback urgency
        recent_feedback = []
        for feedback in feedback_data:
            submitted_at = feedback.get("submitted_at")
            if submitted_at:
                try:
                    if isinstance(submitted_at, str):
                        sub_date = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                    else:
                        sub_date = submitted_at
                    
                    days_ago = (now - sub_date).days
                    if days_ago <= 7:
                        recent_feedback.append(feedback)
                except (ValueError, TypeError):
                    continue
        
        # Boost urgency if recent complaints
        recent_urgency = min(len(recent_feedback) * 10, 40)
        
        # Critical issue urgency
        critical_urgency = 0
        for feedback in feedback_data:
            issues = feedback.get("issues_identified", [])
            for issue in issues:
                if issue.get("category") in ["accessibility", "technical", "grading"]:
                    critical_urgency += 15
        
        critical_urgency = min(critical_urgency, 50)
        
        total_urgency = min(timeline_urgency + recent_urgency + critical_urgency, 100)
        
        logger.debug(f"Urgency calculation: timeline={timeline_urgency}, "
                    f"recent={recent_urgency}, critical={critical_urgency}")
        
        return total_urgency
    
    def _calculate_effort_score(
        self,
        course_data: Dict[str, Any],
        feedback_data: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate effort score (0-100, higher = easier to fix) based on:
        - Issue complexity
        - Required resources
        - Quick wins potential
        """
        if not feedback_data:
            return 50  # Default moderate effort
        
        effort_scores = []
        
        for feedback in feedback_data:
            issues = feedback.get("issues_identified", [])
            
            for issue in issues:
                category = issue.get("category", "").lower()
                
                # Effort mapping based on issue type
                if category in ["content", "clarity", "communication"]:
                    effort_scores.append(80)  # Easy to fix
                elif category in ["instruction", "assignment"]:
                    effort_scores.append(60)  # Moderate effort
                elif category in ["technical", "platform"]:
                    effort_scores.append(40)  # Harder to fix
                elif category in ["curriculum", "structure"]:
                    effort_scores.append(20)  # Major effort
                else:
                    effort_scores.append(50)  # Unknown effort
        
        if not effort_scores:
            return 50
        
        # Higher score = easier to implement (more likely to be prioritized)
        average_effort = sum(effort_scores) / len(effort_scores)
        
        # Boost for quick wins (many easy fixes)
        quick_wins_boost = min(len([s for s in effort_scores if s > 70]) * 5, 20)
        
        return min(average_effort + quick_wins_boost, 100)
    
    def _calculate_strategic_score(
        self,
        course_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate strategic alignment score (0-100) based on:
        - Course importance/visibility
        - Institutional priorities
        - Student enrollment size
        """
        base_score = 50
        
        # High-enrollment courses get priority
        total_students = course_data.get("total_students", 0)
        if total_students > 200:
            base_score += 30
        elif total_students > 100:
            base_score += 20
        elif total_students > 50:
            base_score += 10
        
        # Strategic course indicators
        course_name = course_data.get("name", "").lower()
        course_code = course_data.get("course_code", "").lower()
        
        strategic_keywords = [
            "introduction", "101", "foundational", "required", 
            "prerequisite", "general education", "core"
        ]
        
        for keyword in strategic_keywords:
            if keyword in course_name or keyword in course_code:
                base_score += 15
                break
        
        # Context-based priorities
        priorities = context.get("institutional_priorities", [])
        for priority in priorities:
            if any(keyword in course_name for keyword in priority.get("keywords", [])):
                base_score += priority.get("weight", 10)
        
        return min(base_score, 100)
    
    def _calculate_trend_score(self, feedback_data: List[Dict[str, Any]]) -> float:
        """
        Calculate trend score (0-100) based on:
        - Issue trajectory (getting worse/better)
        - Feedback volume changes
        - Sentiment trends
        """
        if len(feedback_data) < 2:
            return 50  # Neutral trend
        
        # Sort by submission date
        dated_feedback = []
        for feedback in feedback_data:
            submitted_at = feedback.get("submitted_at")
            if submitted_at:
                try:
                    if isinstance(submitted_at, str):
                        date = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                    else:
                        date = submitted_at
                    dated_feedback.append((date, feedback))
                except (ValueError, TypeError):
                    continue
        
        if len(dated_feedback) < 2:
            return 50
        
        dated_feedback.sort()
        
        # Split into recent vs older feedback
        mid_point = len(dated_feedback) // 2
        older_feedback = dated_feedback[:mid_point]
        recent_feedback = dated_feedback[mid_point:]
        
        # Calculate average sentiment for each period
        def avg_sentiment(feedback_list):
            sentiments = [
                f[1].get("sentiment_score", 0) for f in feedback_list
                if f[1].get("sentiment_score") is not None
            ]
            return sum(sentiments) / len(sentiments) if sentiments else 0
        
        older_sentiment = avg_sentiment(older_feedback)
        recent_sentiment = avg_sentiment(recent_feedback)
        
        # Trend calculation (lower sentiment = higher urgency)
        sentiment_trend = older_sentiment - recent_sentiment
        
        # Volume trend
        older_volume = len(older_feedback)
        recent_volume = len(recent_feedback)
        volume_trend = (recent_volume - older_volume) / max(older_volume, 1)
        
        # Combine trends (negative sentiment + increasing volume = urgent)
        trend_score = 50 + (sentiment_trend * 30) + (volume_trend * 20)
        
        return max(0, min(trend_score, 100))
    
    def _calculate_confidence(
        self,
        course_data: Dict[str, Any],
        feedback_data: List[Dict[str, Any]]
    ) -> float:
        """Calculate confidence in the scoring based on data availability"""
        confidence_factors = []
        
        # Course data completeness
        course_fields = ["total_students", "start_date", "end_date", "instructor_name"]
        course_completeness = sum(1 for field in course_fields 
                                if course_data.get(field) is not None) / len(course_fields)
        confidence_factors.append(course_completeness)
        
        # Feedback volume adequacy
        feedback_count = len(feedback_data)
        total_students = course_data.get("total_students", 0)
        
        if total_students > 0:
            response_rate = feedback_count / total_students
            volume_confidence = min(response_rate * 10, 1.0)  # Cap at 10% response rate
        else:
            volume_confidence = min(feedback_count / 10, 1.0)  # Cap at 10 pieces of feedback
        
        confidence_factors.append(volume_confidence)
        
        # Feedback quality (processed vs raw)
        processed_feedback = sum(1 for f in feedback_data if f.get("processed", False))
        if feedback_data:
            processing_confidence = processed_feedback / len(feedback_data)
        else:
            processing_confidence = 0.5
        
        confidence_factors.append(processing_confidence)
        
        # Overall confidence
        return sum(confidence_factors) / len(confidence_factors) * 100
    
    def _generate_explanation(
        self,
        course_data: Dict[str, Any],
        feedback_data: List[Dict[str, Any]],
        breakdown: ScoreBreakdown,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate human-readable explanation for the scoring"""
        
        # Determine priority level
        total_score = breakdown.total_score
        if total_score >= 75:
            priority_level = "urgent"
            urgency_phrase = "requires immediate attention"
        elif total_score >= 60:
            priority_level = "high"
            urgency_phrase = "should be prioritized"
        elif total_score >= 40:
            priority_level = "medium"
            urgency_phrase = "needs attention"
        else:
            priority_level = "low"
            urgency_phrase = "can be addressed later"
        
        # Find top contributing factors
        factors = [
            ("impact", breakdown.impact_score * self.weights.impact_weight),
            ("urgency", breakdown.urgency_score * self.weights.urgency_weight),
            ("effort", breakdown.effort_score * self.weights.effort_weight),
            ("strategic", breakdown.strategic_score * self.weights.strategic_weight),
            ("trend", breakdown.trend_score * self.weights.trend_weight)
        ]
        factors.sort(key=lambda x: x[1], reverse=True)
        
        top_factors = [f[0] for f in factors[:2]]
        
        # Build explanation
        course_name = course_data.get("name", "This course")
        total_students = course_data.get("total_students", 0)
        negative_feedback_count = len([
            f for f in feedback_data 
            if f.get("sentiment_score", 0) < -0.2 or f.get("rating", 3) < 2.5
        ])
        
        explanation = {
            "priority_level": priority_level,
            "summary": f"{course_name} {urgency_phrase} based on our analysis.",
            "primary_reason": self._get_primary_reason(top_factors[0], breakdown, course_data, feedback_data),
            "supporting_factors": [
                self._get_factor_explanation(factor, breakdown, course_data, feedback_data)
                for factor in top_factors[1:]
            ],
            "key_metrics": {
                "total_students": total_students,
                "feedback_items": len(feedback_data),
                "negative_feedback": negative_feedback_count,
                "confidence_level": round(breakdown.confidence, 1)
            },
            "recommended_actions": self._get_recommended_actions(feedback_data, breakdown),
            "evidence_summary": self._get_evidence_summary(feedback_data)
        }
        
        return explanation
    
    def _get_primary_reason(
        self, 
        factor: str, 
        breakdown: ScoreBreakdown, 
        course_data: Dict[str, Any], 
        feedback_data: List[Dict[str, Any]]
    ) -> str:
        """Get primary reason explanation for top contributing factor"""
        
        if factor == "impact":
            affected_count = len([f for f in feedback_data if f.get("sentiment_score", 0) < -0.2])
            total_students = course_data.get("total_students", 0)
            if total_students > 0:
                return f"High impact: {affected_count} students affected out of {total_students} enrolled"
            else:
                return f"High impact: {affected_count} negative feedback items identified"
                
        elif factor == "urgency":
            return "Time-sensitive issues that need immediate resolution"
            
        elif factor == "effort":
            if breakdown.effort_score > 70:
                return "Contains multiple quick-win opportunities that can be easily addressed"
            else:
                return "Issues require significant effort but are important to address"
                
        elif factor == "strategic":
            return "High strategic importance due to course visibility and enrollment"
            
        elif factor == "trend":
            if breakdown.trend_score > 60:
                return "Issues are increasing in frequency and severity"
            else:
                return "Positive trend but still requires attention"
                
        return "Multiple factors contribute to this priority ranking"
    
    def _get_factor_explanation(
        self, 
        factor: str, 
        breakdown: ScoreBreakdown, 
        course_data: Dict[str, Any], 
        feedback_data: List[Dict[str, Any]]
    ) -> str:
        """Get explanation for supporting factors"""
        
        explanations = {
            "impact": f"Impact score: {breakdown.impact_score:.1f}/100",
            "urgency": f"Urgency score: {breakdown.urgency_score:.1f}/100",
            "effort": f"Implementation effort: {breakdown.effort_score:.1f}/100",
            "strategic": f"Strategic importance: {breakdown.strategic_score:.1f}/100",
            "trend": f"Issue trend: {breakdown.trend_score:.1f}/100"
        }
        
        return explanations.get(factor, f"Factor score: {factor}")
    
    def _get_recommended_actions(
        self, 
        feedback_data: List[Dict[str, Any]], 
        breakdown: ScoreBreakdown
    ) -> List[str]:
        """Generate recommended actions based on feedback analysis"""
        
        actions = []
        
        # Analyze feedback for common issues
        issue_categories = {}
        for feedback in feedback_data:
            issues = feedback.get("issues_identified", [])
            for issue in issues:
                category = issue.get("category", "general")
                issue_categories[category] = issue_categories.get(category, 0) + 1
        
        # Generate actions based on most common issues
        sorted_issues = sorted(issue_categories.items(), key=lambda x: x[1], reverse=True)
        
        for category, count in sorted_issues[:3]:
            if category == "content":
                actions.append("Review and update course content based on student feedback")
            elif category == "instruction":
                actions.append("Consider adjusting teaching methods or providing additional support")
            elif category == "technical":
                actions.append("Address technical issues with learning platform or materials")
            elif category == "communication":
                actions.append("Improve communication clarity and response times")
            else:
                actions.append(f"Address {category}-related concerns ({count} reports)")
        
        # Add urgency-based actions
        if breakdown.urgency_score > 75:
            actions.insert(0, "Schedule immediate review meeting with course instructor")
        
        return actions[:4]  # Limit to top 4 actions
    
    def _get_evidence_summary(self, feedback_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Summarize key evidence supporting the priority score"""
        
        evidence = []
        
        # Most critical feedback items
        critical_feedback = sorted(
            feedback_data,
            key=lambda x: x.get("sentiment_score", 0)
        )[:3]
        
        for feedback in critical_feedback:
            evidence.append({
                "type": feedback.get("feedback_type", "review"),
                "source": feedback.get("source", "unknown"),
                "snippet": feedback.get("content", "")[:100] + "...",
                "sentiment": feedback.get("sentiment_score"),
                "date": feedback.get("submitted_at")
            })
        
        return evidence