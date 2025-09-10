import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, JSON, ForeignKey, text, select
from datetime import datetime
from typing import Optional, List
from .config import settings

class Base(DeclarativeBase):
    pass

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(50), index=True, nullable=False)  # "canvas_847" or "zoho_ai_program"
    course_name = Column(String(255), nullable=False)
    student_email = Column(String(255))
    student_name = Column(String(255))
    feedback_text = Column(Text)
    rating = Column(Float)  # 1-5 scale normalized
    severity = Column(String(20))  # critical/high/medium/low
    source = Column(String(10), nullable=False, index=True)  # "canvas" or "zoho"
    source_id = Column(String(100))  # Original ID for provenance
    created_at = Column(DateTime, default=datetime.utcnow)
    last_modified = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Feedback(course_id='{self.course_id}', source='{self.source}', rating={self.rating})>"

class Priority(Base):
    __tablename__ = "priorities"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(50), nullable=False, index=True)
    issue_summary = Column(Text, nullable=False)
    priority_score = Column(Integer, nullable=False)  # 1-5 scale
    impact_score = Column(Float, nullable=False)  # 1-5
    urgency_score = Column(Float, nullable=False)  # 1-5
    effort_score = Column(Float, nullable=False)  # 1-5
    strategic_score = Column(Float, default=3.0)  # 1-5
    trend_score = Column(Float, default=3.0)  # 1-5
    students_affected = Column(Integer, default=0)
    feedback_ids = Column(JSON)  # Array of contributing feedback IDs
    evidence = Column(JSON)  # Student quotes and source links
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to reviews
    reviews = relationship("Review", back_populates="priority", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Priority(course_id='{self.course_id}', score={self.priority_score}, students={self.students_affected})>"

class WeightConfig(Base):
    __tablename__ = "weight_configs"
    
    id = Column(Integer, primary_key=True)
    impact_weight = Column(Float, default=0.40, nullable=False)  # Student impact focus
    urgency_weight = Column(Float, default=0.35, nullable=False)  # Time-sensitive issues
    effort_weight = Column(Float, default=0.25, nullable=False)  # Quick wins preference
    strategic_weight = Column(Float, default=0.15, nullable=False)  # Course goal alignment
    trend_weight = Column(Float, default=0.10, nullable=False)  # Issue trajectory
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(255))  # Admin who changed weights
    is_active = Column(Boolean, default=True)  # Only one active config at a time

    def __repr__(self):
        return f"<WeightConfig(impact={self.impact_weight}, urgency={self.urgency_weight}, effort={self.effort_weight})>"

class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True)
    priority_id = Column(Integer, ForeignKey('priorities.id'), nullable=False)
    reviewer_name = Column(String(255), nullable=False)
    validated = Column(Boolean, default=False)
    action_taken = Column(String(50))  # "implemented", "rejected", "deferred"
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship back to priority
    priority = relationship("Priority", back_populates="reviews")

    def __repr__(self):
        return f"<Review(priority_id={self.priority_id}, validated={self.validated}, action='{self.action_taken}')>"

class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    canvas_id = Column(String(50), nullable=False, unique=True, index=True)
    zoho_id = Column(String(100), index=True)
    name = Column(String(255), nullable=False)
    course_code = Column(String(50))
    account_id = Column(Integer)
    workflow_state = Column(String(20))  # active, completed, archived
    created_at = Column(DateTime, default=datetime.utcnow)
    start_at = Column(DateTime)
    end_at = Column(DateTime)
    enrollment_term_id = Column(Integer)
    total_students = Column(Integer)
    is_active = Column(Boolean, default=True)
    last_synced = Column(DateTime)
    canvas_uuid = Column(String(100))
    default_view = Column(String(50))
    time_zone = Column(String(50))

    def __repr__(self):
        return f"<Course(canvas_id='{self.canvas_id}', name='{self.name}', state='{self.workflow_state}')>"

# Convert postgresql:// to postgresql+asyncpg:// for async support
if settings.database_url:
    if settings.database_url.startswith("postgresql://"):
        # Parse the URL and rebuild without sslmode parameters
        from urllib.parse import urlparse, parse_qs, urlunparse
        parsed = urlparse(settings.database_url)
        
        # Build asyncpg compatible URL
        database_url = f"postgresql+asyncpg://{parsed.netloc}{parsed.path}"
        
        # Add non-SSL query parameters if any (asyncpg handles SSL differently)
        if parsed.query:
            # Filter out SSL parameters that asyncpg doesn't support as query parameters
            excluded_params = {'sslmode', 'channel_binding', 'sslrootcert', 'sslcert', 'sslkey'}
            query_params = parse_qs(parsed.query)
            filtered_params = {k: v for k, v in query_params.items() if k not in excluded_params}
            
            if filtered_params:
                import urllib.parse
                query_string = urllib.parse.urlencode(filtered_params, doseq=True)
                database_url += f"?{query_string}"
    else:
        database_url = settings.database_url
else:
    database_url = "sqlite+aiosqlite:///./feedback.db"  # Fallback to SQLite

# Async database engine and session  
engine = create_async_engine(
    database_url,
    echo=settings.debug,
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300     # Recycle connections every 5 minutes
)

async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def create_tables():
    """Create all database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        
    # Create default weight configuration if none exists
    async with async_session() as session:
        # Check if we have any weight configs
        result = await session.execute(
            text("SELECT COUNT(*) FROM weight_configs WHERE is_active = true")
        )
        count = result.scalar()
        
        if count == 0:
            # Create default weight configuration
            default_weights = WeightConfig(
                impact_weight=0.40,
                urgency_weight=0.35, 
                effort_weight=0.25,
                strategic_weight=0.15,
                trend_weight=0.10,
                updated_by="system",
                is_active=True
            )
            session.add(default_weights)
            await session.commit()

async def get_db():
    """Dependency for getting database session"""
    async with async_session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def get_active_weights() -> WeightConfig:
    """Get the currently active weight configuration"""
    async with async_session() as session:
        query = select(WeightConfig).where(WeightConfig.is_active == True).order_by(WeightConfig.updated_at.desc()).limit(1)
        result = await session.execute(query)
        weights = result.scalar_one_or_none()
        if weights:
            return weights
        else:
            # Return default weights if none found
            return WeightConfig()