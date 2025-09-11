"""Weight controller for managing scoring configuration."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from .base_controller import BaseController
from ..models import WeightConfig


class WeightController(BaseController):
    """Controller for weight configuration operations."""
    
    async def get_active_weights(self, db: AsyncSession) -> Optional[WeightConfig]:
        """Get current active weight configuration."""
        query = select(WeightConfig).where(WeightConfig.is_active == True)
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    async def update_weights(
        self, 
        db: AsyncSession, 
        weight_data: Dict[str, float],
        updated_by: str
    ) -> WeightConfig:
        """Update scoring weights configuration."""
        # Deactivate current config
        await db.execute(
            update(WeightConfig)
            .where(WeightConfig.is_active == True)
            .values(is_active=False)
        )
        
        # Create new active config
        new_weights = WeightConfig(
            impact_weight=weight_data.get('impact_weight', 0.4),
            urgency_weight=weight_data.get('urgency_weight', 0.35),
            effort_weight=weight_data.get('effort_weight', 0.25),
            strategic_weight=weight_data.get('strategic_weight', 0.15),
            trend_weight=weight_data.get('trend_weight', 0.1),
            updated_by=updated_by,
            is_active=True
        )
        
        db.add(new_weights)
        await db.commit()
        await db.refresh(new_weights)
        return new_weights
    
    async def get_weight_history(self, db: AsyncSession) -> List[WeightConfig]:
        """Get historical weight configurations."""
        query = select(WeightConfig).order_by(WeightConfig.updated_at.desc())
        result = await db.execute(query)
        return result.scalars().all()