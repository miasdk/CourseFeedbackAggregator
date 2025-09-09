#!/usr/bin/env python3
"""
Insert realistic mock course feedback data for demo purposes
Demonstrates how the aggregation system works with real-world feedback
"""

import asyncio
import httpx
from datetime import datetime, timedelta
import random

# Mock feedback data that demonstrates the system's capabilities
MOCK_CANVAS_FEEDBACK = [
    # IT Leadership Course - Critical Issues
    {
        "course_name": "IT Leadership Fundamentals",
        "course_id": "canvas_847",
        "student_name": "Sarah Johnson",
        "student_email": "sarah.j@company.com",
        "feedback_text": "The video quality in Module 3 is extremely poor - completely pixelated and audio cuts out. This makes it impossible to follow along with the technical demonstrations. Several students have complained about this.",
        "rating": 2.0,
        "severity": "critical",
        "source": "canvas",
        "source_id": "discussion_post_3847"
    },
    {
        "course_name": "IT Leadership Fundamentals", 
        "course_id": "canvas_847",
        "student_name": "Mike Chen",
        "student_email": "m.chen@company.com",
        "feedback_text": "Assignment 2 requirements are confusing and contradictory. The rubric says one thing but the instructions say another. I've spent hours trying to figure out what's actually expected.",
        "rating": 2.5,
        "severity": "high",
        "source": "canvas",
        "source_id": "assignment_feedback_291"
    },
    {
        "course_name": "IT Leadership Fundamentals",
        "course_id": "canvas_847", 
        "student_name": "Jennifer Rodriguez",
        "student_email": "j.rodriguez@company.com",
        "feedback_text": "Great course overall, but the final project timeline is unrealistic. Two weeks is not enough for the scope of work required, especially with our regular job responsibilities.",
        "rating": 3.5,
        "severity": "medium",
        "source": "canvas",
        "source_id": "course_evaluation_84"
    },
    {
        "course_name": "IT Leadership Fundamentals",
        "course_id": "canvas_847",
        "student_name": "David Park",
        "student_email": "d.park@company.com", 
        "feedback_text": "The instructor is excellent and very knowledgeable. However, the course platform keeps logging me out every 10 minutes which is extremely disruptive during video lectures.",
        "rating": 3.0,
        "severity": "high",
        "source": "canvas",
        "source_id": "discussion_post_3901"
    },
    
    # Customer Experience Program - Medium Priority Issues  
    {
        "course_name": "Customer Experience Excellence",
        "course_id": "canvas_652",
        "student_name": "Lisa Thompson",
        "student_email": "l.thompson@company.com",
        "feedback_text": "Module 4 case studies are outdated - they reference companies and technologies from 2018. Would be much more relevant with current examples.",
        "rating": 3.5,
        "severity": "medium", 
        "source": "canvas",
        "source_id": "feedback_form_156"
    },
    {
        "course_name": "Customer Experience Excellence",
        "course_id": "canvas_652",
        "student_name": "Robert Kim",
        "student_email": "r.kim@company.com",
        "feedback_text": "Love the interactive elements and group discussions. The peer feedback system works really well. Only suggestion is to add more practical exercises.",
        "rating": 4.5,
        "severity": "low",
        "source": "canvas", 
        "source_id": "course_survey_89"
    }
]

MOCK_ZOHO_FEEDBACK = [
    # IT Leadership Course Feedback from CRM
    {
        "course_name": "IT Leadership Fundamentals",
        "course_id": "zoho_it_leadership", 
        "student_name": "Amanda Foster",
        "student_email": "a.foster@company.com",
        "feedback_text": "Technical issues with course access - login problems persist for over a week. IT support hasn't resolved this yet. Missing critical learning time.",
        "rating": 1.5,
        "severity": "critical",
        "source": "zoho",
        "source_id": "crm_case_78234"
    },
    {
        "course_name": "IT Leadership Fundamentals", 
        "course_id": "zoho_it_leadership",
        "student_name": "Carlos Martinez", 
        "student_email": "c.martinez@company.com",
        "feedback_text": "Course content is excellent and directly applicable to my role. The leadership frameworks are exactly what I needed. Instructor responds quickly to questions.",
        "rating": 4.8,
        "severity": "low",
        "source": "zoho",
        "source_id": "survey_response_445"
    },
    {
        "course_name": "IT Leadership Fundamentals",
        "course_id": "zoho_it_leadership",
        "student_name": "Emily Watson", 
        "student_email": "e.watson@company.com",
        "feedback_text": "Video lectures are great but downloadable resources are missing or broken links. Can't access the leadership assessment tools mentioned in Week 3.",
        "rating": 3.0,
        "severity": "medium",
        "source": "zoho", 
        "source_id": "crm_feedback_992"
    },
    
    # Customer Experience Program from Zoho Surveys
    {
        "course_name": "Customer Experience Excellence",
        "course_id": "zoho_cx_program",
        "student_name": "Thomas Anderson",
        "student_email": "t.anderson@company.com", 
        "feedback_text": "Fantastic course with real-world applications. The customer journey mapping exercise was particularly valuable. Would recommend to all customer-facing teams.",
        "rating": 4.7,
        "severity": "low",
        "source": "zoho",
        "source_id": "survey_cx_678"
    },
    {
        "course_name": "Customer Experience Excellence", 
        "course_id": "zoho_cx_program",
        "student_name": "Rachel Green",
        "student_email": "r.green@company.com",
        "feedback_text": "Course is too basic for experienced professionals. Need advanced track with more sophisticated CX strategies and metrics. Current level is introductory at best.",
        "rating": 2.8,
        "severity": "medium",
        "source": "zoho",
        "source_id": "feedback_form_334"
    }
]

async def insert_mock_feedback():
    """Insert mock feedback data via the backend API"""
    print("🚀 Inserting realistic mock course feedback data for demo...")
    
    # Combine all feedback
    all_feedback = MOCK_CANVAS_FEEDBACK + MOCK_ZOHO_FEEDBACK
    
    async with httpx.AsyncClient() as client:
        inserted_count = 0
        
        for feedback in all_feedback:
            # Add timestamps and active status
            feedback_data = {
                **feedback,
                "created_at": (datetime.now() - timedelta(days=random.randint(1, 30))).isoformat(),
                "last_modified": datetime.now().isoformat(),
                "is_active": True
            }
            
            try:
                # Insert directly into database via a mock endpoint (we'll create this)
                response = await client.post(
                    "http://127.0.0.1:8001/api/mock/insert_feedback",
                    json=feedback_data
                )
                
                if response.status_code == 200:
                    inserted_count += 1
                    print(f"✅ Inserted: {feedback['course_name']} - {feedback['student_name']}")
                else:
                    print(f"❌ Failed to insert feedback: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error inserting feedback: {e}")
        
        print(f"\n🎯 Successfully inserted {inserted_count}/{len(all_feedback)} feedback items")
        
        # Check final status
        try:
            status_response = await client.get("http://127.0.0.1:8001/api/ingest/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"📊 Database now contains:")
                print(f"   Total feedback: {status_data['data_summary']['total_feedback']}")
                print(f"   Canvas: {status_data['data_summary']['by_source']['canvas']}")
                print(f"   Zoho: {status_data['data_summary']['by_source']['zoho']}")
                print(f"   Unique courses: {status_data['data_summary']['unique_courses']}")
        except Exception as e:
            print(f"❌ Error checking status: {e}")

if __name__ == "__main__":
    asyncio.run(insert_mock_feedback())