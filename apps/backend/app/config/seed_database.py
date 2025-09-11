#!/usr/bin/env python3
"""
Database Seeding Script for Course Feedback Aggregator
Seeds the Neon PostgreSQL database with initial data and triggers real data ingestion
"""

import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import requests

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete, func

from app.config.database import Base, Course, Feedback, Priority, WeightConfig, Review
from app.config.config import settings
from app.controllers.ingest_controller import IngestController
from app.controllers.priority_controller import PriorityController


async def clear_database(session: AsyncSession):
    """Clear all existing data from the database."""
    print("🗑️  Clearing existing data...")
    
    # Delete in order to respect foreign key constraints
    await session.execute(delete(Review))
    await session.execute(delete(Priority))
    await session.execute(delete(Feedback))
    await session.execute(delete(Course))
    await session.execute(delete(WeightConfig))
    
    await session.commit()
    print("✅ Database cleared")


async def seed_weight_configs(session: AsyncSession):
    """Seed initial weight configurations."""
    print("⚖️  Seeding weight configurations...")
    
    # Default balanced weights
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
    print("✅ Weight configurations seeded")


async def seed_courses(session: AsyncSession):
    """Seed initial courses from Canvas and Zoho."""
    print("📚 Seeding courses...")
    
    # Canvas courses - using real course IDs from Executive Education
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
        },
        {
            "course_id": "canvas_915",
            "course_name": "Strategic Innovation Management",
            "instructor_name": "Dr. Emily Rodriguez",
            "canvas_id": "915",
            "status": "active",
            "start_date": datetime.now() - timedelta(days=45),
            "end_date": datetime.now() + timedelta(days=45)
        }
    ]
    
    # Zoho programs
    zoho_programs = [
        {
            "course_id": "zoho_ai_fundamentals",
            "course_name": "AI Fundamentals for Business Leaders",
            "instructor_name": "Dr. Alex Kumar",
            "zoho_program_id": "ai_fundamentals",
            "status": "active",
            "start_date": datetime.now() - timedelta(days=20),
            "end_date": datetime.now() + timedelta(days=70)
        },
        {
            "course_id": "zoho_digital_transformation",
            "course_name": "Digital Transformation Strategy",
            "instructor_name": "Prof. Lisa Wang",
            "zoho_program_id": "digital_transformation",
            "status": "active",
            "start_date": datetime.now() - timedelta(days=10),
            "end_date": datetime.now() + timedelta(days=80)
        }
    ]
    
    # Add all courses
    for course_data in canvas_courses + zoho_programs:
        course = Course(**course_data)
        session.add(course)
    
    await session.commit()
    print(f"✅ Seeded {len(canvas_courses)} Canvas courses and {len(zoho_programs)} Zoho programs")


async def ingest_real_canvas_data(session: AsyncSession):
    """Attempt to ingest real data from Canvas API."""
    print("🎓 Attempting Canvas API data ingestion...")
    
    controller = IngestController()
    
    # Try to ingest data for known course IDs
    canvas_course_ids = ["847", "892", "915", "1234", "5678"]  # Some may not exist
    
    success_count = 0
    for course_id in canvas_course_ids:
        try:
            print(f"  Fetching Canvas course {course_id}...")
            result = await controller.ingest_canvas_feedback(session, course_id)
            
            if result.get('success'):
                success_count += 1
                print(f"  ✅ Ingested {result.get('feedback_count', 0)} feedback items from course {course_id}")
            else:
                print(f"  ⚠️  Failed to ingest course {course_id}: {result.get('error')}")
        except Exception as e:
            print(f"  ❌ Error ingesting course {course_id}: {str(e)}")
    
    print(f"Canvas ingestion complete: {success_count}/{len(canvas_course_ids)} courses processed")


async def ingest_real_zoho_data(session: AsyncSession):
    """Attempt to ingest real data from Zoho CRM API."""
    print("📊 Attempting Zoho CRM API data ingestion...")
    
    controller = IngestController()
    
    # Try to ingest data for known program IDs
    zoho_program_ids = ["ai_fundamentals", "digital_transformation", "leadership_2024"]
    
    success_count = 0
    for program_id in zoho_program_ids:
        try:
            print(f"  Fetching Zoho program {program_id}...")
            result = await controller.ingest_zoho_feedback(session, program_id)
            
            if result.get('success'):
                success_count += 1
                source = result.get('source', 'unknown')
                print(f"  ✅ Ingested {result.get('feedback_count', 0)} feedback items from {program_id} (source: {source})")
            else:
                print(f"  ⚠️  Failed to ingest program {program_id}: {result.get('error')}")
        except Exception as e:
            print(f"  ❌ Error ingesting program {program_id}: {str(e)}")
    
    print(f"Zoho ingestion complete: {success_count}/{len(zoho_program_ids)} programs processed")


async def seed_sample_feedback(session: AsyncSession):
    """Seed sample feedback data for testing if API ingestion fails."""
    print("💬 Seeding sample feedback...")
    
    # Get all courses
    result = await session.execute(select(Course))
    courses = result.scalars().all()
    
    if not courses:
        print("  ⚠️  No courses found to seed feedback for")
        return
    
    sample_feedback_templates = [
        {
            "feedback_text": "The video content in module 3 is confusing and doesn't match the written materials.",
            "rating": 2.5,
            "severity": "high",
            "student_email": "john.doe@example.com",
            "student_name": "John Doe"
        },
        {
            "feedback_text": "Excellent course structure! The assignments really helped reinforce the concepts.",
            "rating": 4.8,
            "severity": "low",
            "student_email": "jane.smith@example.com",
            "student_name": "Jane Smith"
        },
        {
            "feedback_text": "Technical issues with the platform made it difficult to submit assignments on time.",
            "rating": 2.0,
            "severity": "critical",
            "student_email": "bob.wilson@example.com",
            "student_name": "Bob Wilson"
        },
        {
            "feedback_text": "The instructor's explanations are clear, but more practical examples would be helpful.",
            "rating": 3.5,
            "severity": "medium",
            "student_email": "alice.johnson@example.com",
            "student_name": "Alice Johnson"
        },
        {
            "feedback_text": "Course pace is too fast, struggling to keep up with the weekly modules.",
            "rating": 2.8,
            "severity": "high",
            "student_email": "charlie.brown@example.com",
            "student_name": "Charlie Brown"
        }
    ]
    
    feedback_count = 0
    for course in courses[:3]:  # Add feedback to first 3 courses
        for i, template in enumerate(sample_feedback_templates[:3]):  # 3 feedback per course
            feedback = Feedback(
                course_id=course.course_id,
                course_name=course.course_name,
                feedback_text=template["feedback_text"],
                rating=template["rating"],
                severity=template["severity"],
                student_email=template["student_email"],
                student_name=template["student_name"],
                source="canvas" if "canvas" in course.course_id else "zoho",
                source_id=f"sample_{course.course_id}_{i}",
                created_at=datetime.now() - timedelta(days=i*2),
                is_active=True
            )
            session.add(feedback)
            feedback_count += 1
    
    await session.commit()
    print(f"✅ Seeded {feedback_count} sample feedback items")


async def calculate_initial_priorities(session: AsyncSession):
    """Calculate priorities for all courses with feedback."""
    print("🎯 Calculating initial priorities...")
    
    controller = PriorityController()
    
    # Get all courses with feedback
    result = await session.execute(select(Course))
    courses = result.scalars().all()
    
    priority_count = 0
    for course in courses:
        # Check if course has feedback
        feedback_result = await session.execute(
            select(Feedback).where(Feedback.course_id == course.course_id)
        )
        if feedback_result.scalars().first():
            priorities = await controller.recalculate_priorities(session, course.course_id)
            priority_count += len(priorities)
            print(f"  ✅ Calculated {len(priorities)} priorities for {course.course_name}")
    
    print(f"✅ Total priorities calculated: {priority_count}")


async def display_summary(session: AsyncSession):
    """Display summary of seeded data."""
    print("\n📊 DATABASE SUMMARY")
    print("=" * 50)
    
    # Count records
    courses_count = await session.scalar(select(func.count()).select_from(Course))
    feedback_count = await session.scalar(select(func.count()).select_from(Feedback))
    priorities_count = await session.scalar(select(func.count()).select_from(Priority))
    weights_count = await session.scalar(select(func.count()).select_from(WeightConfig).where(WeightConfig.is_active == True))
    
    print(f"✅ Courses: {courses_count}")
    print(f"✅ Feedback Items: {feedback_count}")
    print(f"✅ Priorities: {priorities_count}")
    print(f"✅ Active Weight Configs: {weights_count}")
    
    # Show top priorities
    result = await session.execute(
        select(Priority)
        .order_by(Priority.priority_score.desc())
        .limit(3)
    )
    top_priorities = result.scalars().all()
    
    if top_priorities:
        print("\n🔥 TOP PRIORITIES:")
        for priority in top_priorities:
            print(f"  • Score {priority.priority_score}: {priority.issue_summary[:60]}...")
    
    print("\n✨ Database seeding complete!")


async def main():
    """Main seeding function."""
    print("🚀 Starting Database Seeding Process")
    print("=" * 50)
    
    db_info = settings.database_url[:50] + "..." if settings.database_url else "SQLite (local)"
    print(f"Database: {db_info}")
    print()
    
    # Create async engine
    if settings.database_url:
        # Use PostgreSQL
        if settings.database_url.startswith("postgresql://"):
            # Parse the URL and rebuild for asyncpg compatibility
            from urllib.parse import urlparse
            parsed = urlparse(settings.database_url)
            # Build asyncpg compatible URL without SSL query parameters
            db_url = f"postgresql+asyncpg://{parsed.netloc}{parsed.path}"
        else:
            db_url = settings.database_url
    else:
        # Fallback to SQLite
        db_url = "sqlite+aiosqlite:///./feedback.db"
    
    engine = create_async_engine(db_url, echo=False)
    
    # Create tables if they don't exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Ask user if they want to clear existing data
        response = input("Clear existing data? (y/N): ").lower()
        if response == 'y':
            await clear_database(session)
        
        # Seed data
        await seed_weight_configs(session)
        await seed_courses(session)
        
        # Try real API ingestion
        if settings.canvas_access_token:
            await ingest_real_canvas_data(session)
        else:
            print("⚠️  No Canvas API token found, skipping Canvas ingestion")
        
        if settings.zoho_access_token:
            await ingest_real_zoho_data(session)
        else:
            print("⚠️  No Zoho API token found, skipping Zoho ingestion")
        
        # Add sample feedback if needed
        feedback_count = await session.scalar(select(func.count()).select_from(Feedback))
        if feedback_count < 5:
            print("📝 Adding sample feedback since API ingestion returned limited data...")
            await seed_sample_feedback(session)
        
        # Calculate priorities
        await calculate_initial_priorities(session)
        
        # Display summary
        await display_summary(session)
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())