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
    course_id = Column(String(50), ForeignKey('courses.course_id'), index=True, nullable=False)
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
    
    # Relationship back to course
    course = relationship("Course", back_populates="feedback")

    def __repr__(self):
        return f"<Feedback(course_id='{self.course_id}', source='{self.source}', rating={self.rating})>"

class Priority(Base):
    __tablename__ = "priorities"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(50), ForeignKey('courses.course_id'), nullable=False, index=True)
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
    
    # Relationships
    course = relationship("Course", back_populates="priorities")
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
    
    course_id = Column(String(50), primary_key=True, index=True)  # "canvas_847", "zoho_ai_program"
    course_name = Column(String(255), nullable=False)
    instructor_name = Column(String(255))
    canvas_id = Column(String(100), unique=True, index=True)
    zoho_program_id = Column(String(100), unique=True, index=True)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String(20), default='active')  # active/completed/archived
    course_metadata = Column(JSON)  # Additional course info
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    feedback = relationship("Feedback", back_populates="course")
    priorities = relationship("Priority", back_populates="course")

    def __repr__(self):
        return f"<Course(course_id='{self.course_id}', name='{self.course_name}', status='{self.status}')>"

# Convert postgresql:// to postgresql+asyncpg:// for async support
if settings.database_url:
    if settings.database_url.startswith("postgresql://"):
        # Parse the URL and rebuild for asyncpg compatibility
        from urllib.parse import urlparse, parse_qs, urlunparse
        parsed = urlparse(settings.database_url)
        
        # Build asyncpg compatible URL without SSL query parameters
        database_url = f"postgresql+asyncpg://{parsed.netloc}{parsed.path}"
        
        # For asyncpg, SSL is handled automatically for Neon and other cloud providers
        # We don't need to pass sslmode parameters in the URL
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

async def seed_initial_data():
    """Seed database with initial courses, sample feedback, and real API data"""
    from datetime import datetime, timedelta
    from ..controllers.ingest_controller import IngestController
    from ..controllers.priority_controller import PriorityController
    from sqlalchemy import func
    
    async with async_session() as session:
        # Check if data already exists
        course_count = await session.scalar(select(func.count()).select_from(Course))
        if course_count > 0:
            print("Database already seeded, skipping...")
            return
        
        print("🚀 Seeding database with initial data...")
        
        # 1. Create default weight configuration
        print("⚖️ Creating weight configuration...")
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
        
        # 2. Create sample courses
        print("📚 Creating sample courses...")
        canvas_courses = [
            {
                "course_id": "canvas_847",
                "course_name": "IT Leadership Development Program",
                "instructor_name": "Dr. Sarah Johnson",
                "canvas_id": "847",
                "status": "active",
                "start_date": datetime.now() - timedelta(days=30),
                "end_date": datetime.now() + timedelta(days=60)
            },
            {
                "course_id": "canvas_892", 
                "course_name": "Customer Experience Excellence",
                "instructor_name": "Prof. Michael Chen",
                "canvas_id": "892",
                "status": "active",
                "start_date": datetime.now() - timedelta(days=15),
                "end_date": datetime.now() + timedelta(days=75)
            }
        ]
        
        zoho_programs = [
            {
                "course_id": "zoho_ai_fundamentals",
                "course_name": "AI Fundamentals for Business Leaders", 
                "instructor_name": "Dr. Alex Kumar",
                "zoho_program_id": "ai_fundamentals",
                "status": "active",
                "start_date": datetime.now() - timedelta(days=20),
                "end_date": datetime.now() + timedelta(days=70)
            }
        ]
        
        # Add courses to database
        for course_data in canvas_courses + zoho_programs:
            course = Course(**course_data)
            session.add(course)
        await session.commit()
        
        # 3. Try real API ingestion
        controller = IngestController()
        
        # Try Canvas API (this will now update existing courses)
        if settings.canvas_access_token:
            print("🎓 Attempting Canvas API ingestion...")
            try:
                result = await controller.ingest_canvas_feedback(session, "847")
                if result.get('success'):
                    print(f"✅ Canvas: {result.get('feedback_count', 0)} feedback items")
                else:
                    print(f"⚠️ Canvas API failed: {result.get('error')}")
            except Exception as e:
                print(f"❌ Canvas error: {str(e)}")
                # Rollback any failed transaction
                await session.rollback()
        
        # Try Zoho API (this will now update existing courses)  
        if settings.zoho_access_token:
            print("📊 Attempting Zoho API ingestion...")
            try:
                result = await controller.ingest_zoho_feedback(session, "ai_fundamentals")
                if result.get('success'):
                    print(f"✅ Zoho: {result.get('feedback_count', 0)} feedback items")
                else:
                    print(f"⚠️ Zoho API failed: {result.get('error')}")
            except Exception as e:
                print(f"❌ Zoho error: {str(e)}")
                # Rollback any failed transaction
                await session.rollback()
        
        # 4. Add sample feedback if APIs didn't provide enough data
        feedback_count = await session.scalar(select(func.count()).select_from(Feedback))
        if feedback_count < 3:
            print("💬 Adding sample feedback...")
            sample_feedback = [
                {
                    "course_id": "canvas_847",
                    "course_name": "IT Leadership Development Program",
                    "feedback_text": "The video content in module 3 is confusing and doesn't match the written materials.",
                    "rating": 2.5,
                    "severity": "high",
                    "student_email": "john.doe@example.com",
                    "student_name": "John Doe",
                    "source": "canvas",
                    "source_id": "sample_1"
                },
                {
                    "course_id": "canvas_892",
                    "course_name": "Customer Experience Excellence", 
                    "feedback_text": "Technical issues with the platform made it difficult to submit assignments on time.",
                    "rating": 2.0,
                    "severity": "critical",
                    "student_email": "bob.wilson@example.com",
                    "student_name": "Bob Wilson",
                    "source": "canvas",
                    "source_id": "sample_2"
                }
            ]
            
            for feedback_data in sample_feedback:
                feedback = Feedback(**feedback_data)
                session.add(feedback)
            await session.commit()
        
        # 5. Calculate initial priorities
        print("🎯 Calculating priorities...")
        priority_controller = PriorityController()
        for course_data in canvas_courses + zoho_programs:
            await priority_controller.recalculate_priorities(session, course_data["course_id"])
        
        print("✅ Database seeding complete!")

async def init_database(seed_data=True):
    """Initialize database with optional seeding"""
    print("🔧 Initializing database...")
    await create_tables()
    
    if seed_data:
        await seed_initial_data()
    else:
        # Still create default weight config even without seeding
        async with async_session() as session:
            result = await session.execute(
                text("SELECT COUNT(*) FROM weight_configs WHERE is_active = true")
            )
            count = result.scalar()
            
            if count == 0:
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