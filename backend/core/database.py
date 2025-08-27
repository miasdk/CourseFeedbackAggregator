"""
Database connection and session management for Course Feedback Aggregator
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from models.database import Base
import os
from typing import Generator
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite:///./course_feedback.db"
)

# SQLite-specific configuration for development
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
            "timeout": 20
        },
        echo=False  # Set to True for SQL debugging
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()
        
else:
    # PostgreSQL configuration for production
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=False
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables in the database"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

def drop_tables():
    """Drop all tables (use with caution!)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("🗑️ All database tables dropped")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to drop tables: {e}")
        return False

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """
    Get database session with automatic cleanup
    Usage:
        with get_db_session() as db:
            # Your database operations
            pass
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()

def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI endpoints
    Usage in FastAPI:
        @app.get("/endpoint")
        def my_endpoint(db: Session = Depends(get_db)):
            # Your code here
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables and default data"""
    logger.info("🗄️ Initializing database...")
    
    # Create tables
    if not create_tables():
        return False
    
    # Check if we need to seed data
    with get_db_session() as db:
        from models.database import WeightConfig
        
        # Check if default weight config exists
        default_weights = db.query(WeightConfig).filter(
            WeightConfig.name == "default"
        ).first()
        
        if not default_weights:
            logger.info("📊 Seeding default weight configuration...")
            default_config = WeightConfig(
                name="default",
                description="Default scoring weights for priority calculation",
                impact_weight=0.35,
                urgency_weight=0.25,
                effort_weight=0.20,
                strategic_weight=0.15,
                trend_weight=0.05,
                is_active=True,
                created_by="system"
            )
            db.add(default_config)
            db.commit()
            logger.info("✅ Default configuration created")
    
    logger.info("🎉 Database initialization complete!")
    return True

def get_db_stats() -> dict:
    """Get database statistics and health info"""
    try:
        with get_db_session() as db:
            from models.database import Course, FeedbackItem, Recommendation, WeightConfig
            
            stats = {
                "tables": {
                    "courses": db.query(Course).count(),
                    "feedback_items": db.query(FeedbackItem).count(),
                    "recommendations": db.query(Recommendation).count(),
                    "weight_configs": db.query(WeightConfig).count()
                },
                "database_url": DATABASE_URL.split("://")[0] + "://***",  # Hide credentials
                "engine_info": {
                    "pool_size": getattr(engine.pool, 'size', 'N/A'),
                    "checked_out": getattr(engine.pool, 'checkedout', 'N/A'),
                    "overflow": getattr(engine.pool, 'overflow', 'N/A')
                }
            }
            return stats
    except Exception as e:
        return {"error": str(e)}

def reset_database():
    """Reset database - drop and recreate all tables"""
    logger.warning("⚠️ Resetting database - all data will be lost!")
    
    if drop_tables() and create_tables():
        return init_database()
    return False

# Health check function
def check_database_health() -> dict:
    """Check database connectivity and basic operations"""
    try:
        with get_db_session() as db:
            # Simple query to test connection
            result = db.execute("SELECT 1").fetchone()
            
            return {
                "healthy": True,
                "database_type": DATABASE_URL.split("://")[0],
                "test_query": "success" if result else "failed",
                "stats": get_db_stats()
            }
    except Exception as e:
        return {
            "healthy": False,
            "error": str(e),
            "database_type": DATABASE_URL.split("://")[0]
        }