"""
Weight Configuration Management Service
Provides tunable weight configuration for the scoring engine with version control
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from models.database import WeightConfig
from core.database import get_db_session

logger = logging.getLogger(__name__)


class WeightConfigService:
    """Service for managing tunable scoring weights with validation and versioning"""
    
    def create_weight_config(
        self,
        name: str,
        description: str,
        weights: Dict[str, float],
        created_by: str,
        make_active: bool = False
    ) -> Dict[str, Any]:
        """Create a new weight configuration with validation"""
        
        # Validate weights sum to 1.0 (within tolerance)
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.001:
            return {
                "success": False,
                "error": f"Weights must sum to 1.0, got {total_weight:.3f}",
                "weights_sum": total_weight
            }
        
        # Validate all weights are positive
        if any(weight < 0 for weight in weights.values()):
            return {
                "success": False,
                "error": "All weights must be positive",
                "weights": weights
            }
        
        with get_db_session() as db:
            # Check if name already exists
            existing = db.query(WeightConfig).filter(
                WeightConfig.name == name
            ).first()
            
            if existing:
                return {
                    "success": False,
                    "error": f"Weight configuration '{name}' already exists"
                }
            
            # If making this active, deactivate others
            if make_active:
                db.query(WeightConfig).filter(
                    WeightConfig.is_active == True
                ).update({"is_active": False})
            
            # Create new configuration
            config = WeightConfig(
                name=name,
                description=description,
                impact_weight=weights.get("impact", 0.35),
                urgency_weight=weights.get("urgency", 0.25),
                effort_weight=weights.get("effort", 0.20),
                strategic_weight=weights.get("strategic", 0.15),
                trend_weight=weights.get("trend", 0.05),
                is_active=make_active,
                created_by=created_by
            )
            
            db.add(config)
            db.commit()
            db.refresh(config)
            
            logger.info(f"Created weight configuration: {name}")
            
            return {
                "success": True,
                "config_id": config.id,
                "config": self._format_config(config),
                "is_active": make_active
            }
    
    def update_weight_config(
        self,
        config_id: int,
        weights: Optional[Dict[str, float]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        make_active: Optional[bool] = None
    ) -> Dict[str, Any]:
        """Update an existing weight configuration"""
        
        with get_db_session() as db:
            config = db.query(WeightConfig).filter(
                WeightConfig.id == config_id
            ).first()
            
            if not config:
                return {
                    "success": False,
                    "error": f"Weight configuration {config_id} not found"
                }
            
            # Validate weights if provided
            if weights:
                total_weight = sum(weights.values())
                if abs(total_weight - 1.0) > 0.001:
                    return {
                        "success": False,
                        "error": f"Weights must sum to 1.0, got {total_weight:.3f}",
                        "weights_sum": total_weight
                    }
                
                if any(weight < 0 for weight in weights.values()):
                    return {
                        "success": False,
                        "error": "All weights must be positive",
                        "weights": weights
                    }
                
                # Update weights
                config.impact_weight = weights.get("impact", config.impact_weight)
                config.urgency_weight = weights.get("urgency", config.urgency_weight)
                config.effort_weight = weights.get("effort", config.effort_weight)
                config.strategic_weight = weights.get("strategic", config.strategic_weight)
                config.trend_weight = weights.get("trend", config.trend_weight)
            
            # Update other fields
            if name is not None:
                # Check name uniqueness
                existing = db.query(WeightConfig).filter(
                    WeightConfig.name == name,
                    WeightConfig.id != config_id
                ).first()
                
                if existing:
                    return {
                        "success": False,
                        "error": f"Weight configuration '{name}' already exists"
                    }
                
                config.name = name
            
            if description is not None:
                config.description = description
            
            # Handle activation
            if make_active is not None:
                if make_active:
                    # Deactivate other configurations
                    db.query(WeightConfig).filter(
                        WeightConfig.is_active == True,
                        WeightConfig.id != config_id
                    ).update({"is_active": False})
                
                config.is_active = make_active
            
            db.commit()
            db.refresh(config)
            
            logger.info(f"Updated weight configuration: {config.name}")
            
            return {
                "success": True,
                "config_id": config.id,
                "config": self._format_config(config)
            }
    
    def get_weight_config(self, config_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific weight configuration"""
        
        with get_db_session() as db:
            config = db.query(WeightConfig).filter(
                WeightConfig.id == config_id
            ).first()
            
            if not config:
                return None
            
            return self._format_config(config)
    
    def get_active_config(self) -> Optional[Dict[str, Any]]:
        """Get the currently active weight configuration"""
        
        with get_db_session() as db:
            config = db.query(WeightConfig).filter(
                WeightConfig.is_active == True
            ).first()
            
            if not config:
                return None
            
            return self._format_config(config)
    
    def list_weight_configs(self, include_inactive: bool = True) -> List[Dict[str, Any]]:
        """List all weight configurations"""
        
        with get_db_session() as db:
            query = db.query(WeightConfig)
            
            if not include_inactive:
                query = query.filter(WeightConfig.is_active == True)
            
            configs = query.order_by(desc(WeightConfig.created_at)).all()
            
            return [self._format_config(config) for config in configs]
    
    def activate_config(self, config_id: int) -> Dict[str, Any]:
        """Make a configuration active (deactivating others)"""
        
        with get_db_session() as db:
            config = db.query(WeightConfig).filter(
                WeightConfig.id == config_id
            ).first()
            
            if not config:
                return {
                    "success": False,
                    "error": f"Weight configuration {config_id} not found"
                }
            
            # Deactivate all configurations
            db.query(WeightConfig).update({"is_active": False})
            
            # Activate the target configuration
            config.is_active = True
            
            db.commit()
            
            logger.info(f"Activated weight configuration: {config.name}")
            
            return {
                "success": True,
                "config_id": config.id,
                "config_name": config.name,
                "message": f"Configuration '{config.name}' is now active"
            }
    
    def delete_config(self, config_id: int) -> Dict[str, Any]:
        """Delete a weight configuration (if not active)"""
        
        with get_db_session() as db:
            config = db.query(WeightConfig).filter(
                WeightConfig.id == config_id
            ).first()
            
            if not config:
                return {
                    "success": False,
                    "error": f"Weight configuration {config_id} not found"
                }
            
            if config.is_active:
                return {
                    "success": False,
                    "error": "Cannot delete active configuration. Activate another configuration first."
                }
            
            # Check if used by recommendations
            from models.database import Recommendation
            recommendations_count = db.query(Recommendation).filter(
                Recommendation.weight_config_id == config_id
            ).count()
            
            if recommendations_count > 0:
                return {
                    "success": False,
                    "error": f"Cannot delete configuration used by {recommendations_count} recommendations"
                }
            
            config_name = config.name
            db.delete(config)
            db.commit()
            
            logger.info(f"Deleted weight configuration: {config_name}")
            
            return {
                "success": True,
                "message": f"Configuration '{config_name}' deleted successfully"
            }
    
    def validate_weights(self, weights: Dict[str, float]) -> Dict[str, Any]:
        """Validate weight values without saving"""
        
        required_factors = {"impact", "urgency", "effort", "strategic", "trend"}
        provided_factors = set(weights.keys())
        
        # Check for missing factors
        missing_factors = required_factors - provided_factors
        if missing_factors:
            return {
                "valid": False,
                "error": f"Missing required factors: {list(missing_factors)}",
                "required_factors": list(required_factors)
            }
        
        # Check for extra factors
        extra_factors = provided_factors - required_factors
        if extra_factors:
            return {
                "valid": False,
                "error": f"Unknown factors provided: {list(extra_factors)}",
                "allowed_factors": list(required_factors)
            }
        
        # Check sum
        total_weight = sum(weights.values())
        if abs(total_weight - 1.0) > 0.001:
            return {
                "valid": False,
                "error": f"Weights must sum to 1.0, got {total_weight:.3f}",
                "weights_sum": total_weight,
                "suggested_adjustment": {
                    factor: round(weight / total_weight, 3) 
                    for factor, weight in weights.items()
                }
            }
        
        # Check for negative values
        negative_factors = [factor for factor, weight in weights.items() if weight < 0]
        if negative_factors:
            return {
                "valid": False,
                "error": f"Negative weights not allowed: {negative_factors}"
            }
        
        return {
            "valid": True,
            "weights": weights,
            "weights_sum": total_weight
        }
    
    def get_config_impact_preview(
        self,
        weights: Dict[str, float],
        sample_size: int = 5
    ) -> Dict[str, Any]:
        """Preview how weight changes would affect current recommendations"""
        
        # Validate weights first
        validation = self.validate_weights(weights)
        if not validation["valid"]:
            return {
                "success": False,
                "error": validation["error"]
            }
        
        with get_db_session() as db:
            from models.database import Recommendation
            from services.scoring_engine import ScoringEngine, WeightConfig as ScoringWeights
            
            # Get recent recommendations for comparison
            recent_recs = db.query(Recommendation).order_by(
                desc(Recommendation.generated_at)
            ).limit(sample_size).all()
            
            if not recent_recs:
                return {
                    "success": False,
                    "error": "No recommendations available for preview"
                }
            
            # Create scoring engine with new weights
            scoring_weights = ScoringWeights(
                impact_weight=weights["impact"],
                urgency_weight=weights["urgency"],
                effort_weight=weights["effort"],
                strategic_weight=weights["strategic"],
                trend_weight=weights["trend"]
            )
            
            preview_results = []
            
            for rec in recent_recs:
                # Recalculate scores with new weights
                current_scores = {
                    "impact": rec.impact_score,
                    "urgency": rec.urgency_score,
                    "effort": rec.effort_score,
                    "strategic": rec.strategic_score,
                    "trend": rec.trend_score
                }
                
                new_total_score = (
                    current_scores["impact"] * weights["impact"] +
                    current_scores["urgency"] * weights["urgency"] +
                    current_scores["effort"] * weights["effort"] +
                    current_scores["strategic"] * weights["strategic"] +
                    current_scores["trend"] * weights["trend"]
                )
                
                score_change = new_total_score - rec.total_score
                
                preview_results.append({
                    "recommendation_id": rec.id,
                    "title": rec.title,
                    "current_score": round(rec.total_score, 2),
                    "new_score": round(new_total_score, 2),
                    "score_change": round(score_change, 2),
                    "rank_change": "TBD"  # Would require full re-ranking
                })
            
            # Sort by new scores to show ranking changes
            preview_results.sort(key=lambda x: x["new_score"], reverse=True)
            
            return {
                "success": True,
                "preview_results": preview_results,
                "summary": {
                    "sample_size": len(preview_results),
                    "avg_score_change": round(
                        sum(r["score_change"] for r in preview_results) / len(preview_results), 3
                    ),
                    "score_increases": sum(1 for r in preview_results if r["score_change"] > 0),
                    "score_decreases": sum(1 for r in preview_results if r["score_change"] < 0)
                }
            }
    
    def _format_config(self, config: WeightConfig) -> Dict[str, Any]:
        """Format weight configuration for API response"""
        return {
            "id": config.id,
            "name": config.name,
            "description": config.description,
            "weights": {
                "impact": config.impact_weight,
                "urgency": config.urgency_weight,
                "effort": config.effort_weight,
                "strategic": config.strategic_weight,
                "trend": config.trend_weight
            },
            "weights_sum": round(
                config.impact_weight + config.urgency_weight + 
                config.effort_weight + config.strategic_weight + 
                config.trend_weight, 3
            ),
            "is_active": config.is_active,
            "created_by": config.created_by,
            "created_at": config.created_at.isoformat() if config.created_at else None
        }


def create_experimental_configs():
    """Create some experimental weight configurations for testing"""
    
    logger.info("🧪 Creating experimental weight configurations...")
    
    service = WeightConfigService()
    
    # High Impact Configuration
    high_impact_result = service.create_weight_config(
        name="high_impact",
        description="Prioritizes widespread student impact issues",
        weights={
            "impact": 0.50,
            "urgency": 0.20,
            "effort": 0.15,
            "strategic": 0.10,
            "trend": 0.05
        },
        created_by="system"
    )
    
    # Quick Wins Configuration
    quick_wins_result = service.create_weight_config(
        name="quick_wins",
        description="Focuses on low-effort, high-impact improvements",
        weights={
            "impact": 0.30,
            "urgency": 0.15,
            "effort": 0.40,  # Higher weight = lower effort preferred
            "strategic": 0.10,
            "trend": 0.05
        },
        created_by="system"
    )
    
    # Strategic Focus Configuration
    strategic_result = service.create_weight_config(
        name="strategic_focus",
        description="Aligns with institutional priorities and long-term goals",
        weights={
            "impact": 0.25,
            "urgency": 0.15,
            "effort": 0.15,
            "strategic": 0.35,
            "trend": 0.10
        },
        created_by="system"
    )
    
    results = {
        "high_impact": high_impact_result,
        "quick_wins": quick_wins_result,
        "strategic_focus": strategic_result
    }
    
    successful_configs = [name for name, result in results.items() if result["success"]]
    
    logger.info(f"✅ Created {len(successful_configs)} experimental configurations: {successful_configs}")
    
    return results


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create experimental configurations
    results = create_experimental_configs()
    
    # List all configurations
    service = WeightConfigService()
    all_configs = service.list_weight_configs()
    
    print("📊 Available Weight Configurations:")
    for config in all_configs:
        status = "🟢 ACTIVE" if config["is_active"] else "⚪ Inactive"
        print(f"{status} {config['name']}: {config['description']}")
        print(f"   Weights: Impact={config['weights']['impact']}, Urgency={config['weights']['urgency']}, "
              f"Effort={config['weights']['effort']}, Strategic={config['weights']['strategic']}, "
              f"Trend={config['weights']['trend']}")
        print()