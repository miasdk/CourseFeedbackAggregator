from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel, field_validator
from typing import Optional
import logging
from datetime import datetime

from ..config.database import get_db, get_active_weights
from ..models import WeightConfig
from ..config.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

class WeightUpdate(BaseModel):
    impact_weight: Optional[float] = None
    urgency_weight: Optional[float] = None
    effort_weight: Optional[float] = None
    strategic_weight: Optional[float] = None
    trend_weight: Optional[float] = None
    updated_by: str = "admin"
    
    @field_validator('impact_weight', 'urgency_weight', 'effort_weight', 'strategic_weight', 'trend_weight')
    @classmethod
    def validate_weight_range(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('Weight must be between 0.0 and 1.0')
        return v
    
    def validate_total_weights(self):
        """Validate that all weights sum to 1.0"""
        weights = [
            self.impact_weight,
            self.urgency_weight, 
            self.effort_weight,
            self.strategic_weight,
            self.trend_weight
        ]
        
        # Filter out None values
        defined_weights = [w for w in weights if w is not None]
        
        if len(defined_weights) == 5:  # All weights provided
            total = sum(defined_weights)
            if abs(total - 1.0) > 0.001:  # Allow small floating point errors
                raise ValueError(f'All weights must sum to 1.0, current sum: {total:.3f}')
        
        return True

@router.get("/weights")
async def get_current_weights(
    db: AsyncSession = Depends(get_db)
):
    """
    Get the currently active weight configuration
    """
    try:
        weights = await get_active_weights()
        
        return {
            "weights": {
                "impact": weights.impact_weight,
                "urgency": weights.urgency_weight,
                "effort": weights.effort_weight,
                "strategic": weights.strategic_weight,
                "trend": weights.trend_weight
            },
            "weight_details": {
                "impact": {
                    "value": weights.impact_weight,
                    "description": "How many students are affected and severity of impact",
                    "examples": ["23 students can't complete assignment", "8 students confused about content"]
                },
                "urgency": {
                    "value": weights.urgency_weight,
                    "description": "Time sensitivity and course flow disruption",
                    "examples": ["Assignment due tomorrow but broken", "Video needs updating before next semester"]
                },
                "effort": {
                    "value": weights.effort_weight,
                    "description": "How easy/hard it is to fix (quick wins score higher)",
                    "examples": ["Fix typo (2 minutes)", "Update video (2 hours)", "Redesign module (2 weeks)"]
                },
                "strategic": {
                    "value": weights.strategic_weight,
                    "description": "Alignment with course goals and institutional priorities",
                    "examples": ["Core learning objective not met", "Assessment doesn't align with goals"]
                },
                "trend": {
                    "value": weights.trend_weight,
                    "description": "Whether the issue is getting worse or better over time",
                    "examples": ["Complaints increasing each week", "Consistent feedback over time"]
                }
            },
            "updated_at": weights.updated_at.isoformat() if weights.updated_at else None,
            "updated_by": weights.updated_by,
            "total": weights.impact_weight + weights.urgency_weight + weights.effort_weight + 
                     weights.strategic_weight + weights.trend_weight
        }
        
    except Exception as e:
        logger.error(f"Error fetching current weights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve weight configuration")

@router.put("/weights")
async def update_weights(
    weight_update: WeightUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update the weight configuration for priority scoring
    """
    try:
        # Validate that weights sum to 1.0 if all are provided
        weight_update.validate_total_weights()
        
        # Get current weights
        current_weights = await get_active_weights()
        
        # Create new weight configuration
        new_weights = WeightConfig(
            impact_weight=weight_update.impact_weight or current_weights.impact_weight,
            urgency_weight=weight_update.urgency_weight or current_weights.urgency_weight,
            effort_weight=weight_update.effort_weight or current_weights.effort_weight,
            strategic_weight=weight_update.strategic_weight or current_weights.strategic_weight,
            trend_weight=weight_update.trend_weight or current_weights.trend_weight,
            updated_by=weight_update.updated_by,
            updated_at=datetime.utcnow(),
            is_active=True
        )
        
        # Validate final weights sum to 1.0
        total_weight = (new_weights.impact_weight + new_weights.urgency_weight + 
                       new_weights.effort_weight + new_weights.strategic_weight + 
                       new_weights.trend_weight)
        
        if abs(total_weight - 1.0) > 0.001:
            raise HTTPException(
                status_code=400, 
                detail=f"All weights must sum to 1.0, current sum: {total_weight:.3f}"
            )
        
        # Deactivate current weights
        await db.execute(
            update(WeightConfig).where(WeightConfig.is_active == True).values(is_active=False)
        )
        
        # Save new weights
        db.add(new_weights)
        await db.commit()
        
        logger.info(f"Weight configuration updated by {weight_update.updated_by}")
        
        return {
            "success": True,
            "message": "Weight configuration updated successfully",
            "new_weights": {
                "impact": new_weights.impact_weight,
                "urgency": new_weights.urgency_weight,
                "effort": new_weights.effort_weight,
                "strategic": new_weights.strategic_weight,
                "trend": new_weights.trend_weight
            },
            "changes_made": {
                "impact": weight_update.impact_weight is not None,
                "urgency": weight_update.urgency_weight is not None,
                "effort": weight_update.effort_weight is not None,
                "strategic": weight_update.strategic_weight is not None,
                "trend": weight_update.trend_weight is not None
            },
            "updated_by": weight_update.updated_by,
            "updated_at": new_weights.updated_at.isoformat(),
            "total_weight": total_weight,
            "recommendation": "Run /api/priorities/recompute to apply new weights to existing recommendations"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating weights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update weight configuration: {str(e)}")

@router.get("/weights/presets")
async def get_weight_presets():
    """
    Get predefined weight presets for common scenarios
    """
    return {
        "presets": {
            "crisis_mode": {
                "name": "Crisis Mode",
                "description": "Semester starting soon - prioritize urgent fixes regardless of effort",
                "weights": {
                    "impact": 0.35,
                    "urgency": 0.45,
                    "effort": 0.10,
                    "strategic": 0.05,
                    "trend": 0.05
                },
                "use_case": "When you need to fix show-stoppers immediately before semester starts"
            },
            "strategic_planning": {
                "name": "Strategic Planning",
                "description": "Between semesters - focus on strategic improvements with good ROI",
                "weights": {
                    "impact": 0.25,
                    "urgency": 0.10,
                    "effort": 0.30,
                    "strategic": 0.25,
                    "trend": 0.10
                },
                "use_case": "When you have time to plan long-term course improvements"
            },
            "quick_wins": {
                "name": "Quick Wins",
                "description": "Focus on easy fixes that make students happy",
                "weights": {
                    "impact": 0.35,
                    "urgency": 0.15,
                    "effort": 0.40,
                    "strategic": 0.05,
                    "trend": 0.05
                },
                "use_case": "When team needs morale boost from visible improvements"
            },
            "balanced": {
                "name": "Balanced Approach",
                "description": "Default balanced scoring across all factors",
                "weights": {
                    "impact": 0.30,
                    "urgency": 0.25,
                    "effort": 0.25,
                    "strategic": 0.15,
                    "trend": 0.05
                },
                "use_case": "General purpose prioritization for ongoing course management"
            },
            "trend_focused": {
                "name": "Trend Focused",
                "description": "Prioritize issues that are growing or recurring",
                "weights": {
                    "impact": 0.25,
                    "urgency": 0.20,
                    "effort": 0.20,
                    "strategic": 0.15,
                    "trend": 0.20
                },
                "use_case": "When you want to address systemic issues before they grow"
            }
        }
    }

@router.post("/weights/apply-preset")
async def apply_weight_preset(
    preset_name: str,
    updated_by: str = "admin",
    db: AsyncSession = Depends(get_db)
):
    """
    Apply a predefined weight preset
    """
    try:
        presets = await get_weight_presets()
        preset = presets["presets"].get(preset_name)
        
        if not preset:
            available_presets = list(presets["presets"].keys())
            raise HTTPException(
                status_code=400, 
                detail=f"Unknown preset '{preset_name}'. Available: {available_presets}"
            )
        
        # Apply the preset weights
        weight_update = WeightUpdate(
            impact_weight=preset["weights"]["impact"],
            urgency_weight=preset["weights"]["urgency"],
            effort_weight=preset["weights"]["effort"],
            strategic_weight=preset["weights"]["strategic"],
            trend_weight=preset["weights"]["trend"],
            updated_by=f"{updated_by} (preset: {preset_name})"
        )
        
        # Use the existing update weights function
        return await update_weights(weight_update, db)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying preset {preset_name}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to apply weight preset: {str(e)}")

@router.get("/weights/history")
async def get_weights_history(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Get history of weight configuration changes
    """
    try:
        query = select(WeightConfig).order_by(WeightConfig.updated_at.desc()).limit(limit)
        result = await db.execute(query)
        weight_configs = result.scalars().all()
        
        history = []
        for config in weight_configs:
            history.append({
                "id": config.id,
                "weights": {
                    "impact": config.impact_weight,
                    "urgency": config.urgency_weight,
                    "effort": config.effort_weight,
                    "strategic": config.strategic_weight,
                    "trend": config.trend_weight
                },
                "updated_at": config.updated_at.isoformat() if config.updated_at else None,
                "updated_by": config.updated_by,
                "is_active": config.is_active,
                "total_weight": config.impact_weight + config.urgency_weight + 
                              config.effort_weight + config.strategic_weight + config.trend_weight
            })
        
        return {
            "weight_history": history,
            "total_records": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error fetching weights history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to retrieve weight configuration history")

@router.post("/weights/reset")
async def reset_weights_to_default(
    updated_by: str = "admin",
    db: AsyncSession = Depends(get_db)
):
    """
    Reset weight configuration to default balanced values
    """
    try:
        # Default balanced weights (must sum to 1.0)
        default_weights = {
            "impact": 0.35,
            "urgency": 0.30,
            "effort": 0.20,
            "strategic": 0.10,
            "trend": 0.05
        }
        
        # Apply default weights
        weight_update = WeightUpdate(
            impact_weight=default_weights["impact"],
            urgency_weight=default_weights["urgency"],
            effort_weight=default_weights["effort"],
            strategic_weight=default_weights["strategic"],
            trend_weight=default_weights["trend"],
            updated_by=f"{updated_by} (reset to defaults)"
        )
        
        # Use the existing update weights function
        result = await update_weights(weight_update, db)
        
        return {
            "impact": default_weights["impact"],
            "urgency": default_weights["urgency"],
            "effort": default_weights["effort"],
            "strategic": default_weights["strategic"],
            "trend": default_weights["trend"]
        }
        
    except Exception as e:
        logger.error(f"Error resetting weights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to reset weights: {str(e)}")