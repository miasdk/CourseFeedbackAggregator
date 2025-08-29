#!/usr/bin/env python
"""
Test Canvas API Connection and Data Access
"""

import json
import sys
from services.canvas_client import CanvasClient
from pprint import pprint

def test_canvas_connection():
    """Test Canvas API connection with the new token"""
    print("=" * 60)
    print("TESTING CANVAS API CONNECTION")
    print("=" * 60)
    
    try:
        # Initialize Canvas client
        client = CanvasClient()
        print("✅ Canvas client initialized\n")
        
        # Test connection
        print("Testing connection...")
        connection_result = client.test_connection()
        
        if connection_result["connected"]:
            print("✅ Successfully connected to Canvas!\n")
            print("User Information:")
            print(f"  Name: {connection_result['user']['name']}")
            print(f"  ID: {connection_result['user']['id']}")
            print(f"  Email: {connection_result['user'].get('email', 'N/A')}")
            print(f"\nPermissions:")
            print(f"  Accessible Courses: {connection_result['permissions']['courses_accessible']}")
            print(f"  Can Read Courses: {connection_result['permissions']['can_read_courses']}")
        else:
            print(f"❌ Connection failed: {connection_result.get('error')}")
            return False
        
        print("\n" + "=" * 60)
        print("FETCHING COURSE DATA")
        print("=" * 60)
        
        # Get courses
        courses = client.get_courses()
        print(f"\n📚 Found {len(courses)} accessible courses\n")
        
        if courses:
            # Show first 5 courses
            print("Sample Courses:")
            for i, course in enumerate(courses[:5], 1):
                print(f"\n{i}. {course['name']}")
                print(f"   Code: {course['course_code']}")
                print(f"   Term: {course['term']}")
                print(f"   Students: {course['enrollment_count']}")
                print(f"   Canvas ID: {course['canvas_id']}")
            
            # Get details for the first course
            if courses:
                first_course = courses[0]
                print("\n" + "=" * 60)
                print(f"DETAILED VIEW: {first_course['name']}")
                print("=" * 60)
                
                details = client.get_course_details(first_course['canvas_id'])
                if details:
                    print("\nCourse Details:")
                    print(f"  Teachers: {', '.join([t['name'] for t in details.get('teachers', [])])}")
                    print(f"  Start Date: {details.get('start_at', 'N/A')}")
                    print(f"  End Date: {details.get('end_at', 'N/A')}")
                    
                    # Check for feedback
                    print("\n📝 Checking for course feedback...")
                    feedback = client.get_course_feedback(first_course['canvas_id'])
                    print(f"  Found {len(feedback)} feedback items")
                    
                    if feedback:
                        print("\n  Sample Feedback:")
                        for fb in feedback[:3]:
                            print(f"    - Source: {fb['source']}")
                            if fb['source'] == 'discussion':
                                print(f"      Topic: {fb.get('discussion_topic', 'N/A')}")
                            elif fb['source'] == 'quiz':
                                print(f"      Title: {fb.get('title', 'N/A')}")
            
            # Save sample data for analysis
            print("\n" + "=" * 60)
            print("SAVING SAMPLE DATA")
            print("=" * 60)
            
            sample_data = {
                "connection": connection_result,
                "total_courses": len(courses),
                "sample_courses": courses[:10],
                "first_course_details": details if courses else None
            }
            
            with open("canvas_sample_data.json", "w") as f:
                json.dump(sample_data, f, indent=2, default=str)
            
            print("✅ Sample data saved to canvas_sample_data.json")
            
            return True
        else:
            print("⚠️ No courses found. This might be a permissions issue.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_canvas_connection()
    sys.exit(0 if success else 1)