#!/usr/bin/env python3
"""
Quick Canvas Test - Sample a few courses to understand data structure
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import re

load_dotenv()

def api_request(endpoint: str, params=None):
    """Quick API request"""
    access_token = os.getenv('CANVAS_ACCESS_TOKEN')
    api_url = os.getenv('CANVAS_API_URL', 'https://executiveeducation.instructure.com')
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    
    url = f"{api_url}/api/v1/{endpoint}"
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code}: {endpoint}")
            return None
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def quick_course_sample():
    """Sample a few courses to understand data structures"""
    print("🔍 QUICK CANVAS DATA SAMPLE")
    print("="*50)
    
    # Get first few courses from account 1
    courses = api_request('accounts/1/courses', {'per_page': 5})
    if not courses:
        print("No courses found")
        return
    
    print(f"Found {len(courses)} sample courses:")
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'courses': []
    }
    
    for course in courses:
        course_id = course.get('id')
        course_name = course.get('name', 'Unnamed')
        
        print(f"\n📚 {course_name} (ID: {course_id})")
        print(f"   State: {course.get('workflow_state')}")
        
        course_data = {
            'id': course_id,
            'name': course_name,
            'state': course.get('workflow_state'),
            'discussions': [],
            'assignments': [],
            'sample_content': {}
        }
        
        # Get discussions
        discussions = api_request(f'courses/{course_id}/discussion_topics')
        if discussions:
            print(f"   📝 {len(discussions)} discussions")
            course_data['discussions'] = discussions[:2]  # Sample first 2
            
            # Get entries from first discussion
            if discussions:
                first_disc = discussions[0]
                entries = api_request(f'courses/{course_id}/discussion_topics/{first_disc["id"]}/entries')
                if entries:
                    print(f"      • First discussion has {len(entries)} entries")
                    # Sample first entry
                    if entries:
                        first_entry = entries[0]
                        message = first_entry.get('message', '')
                        clean_message = re.sub(r'<[^>]+>', '', message)
                        course_data['sample_content']['discussion_entry'] = {
                            'raw_message': message[:200],
                            'clean_message': clean_message[:200],
                            'created_at': first_entry.get('created_at'),
                            'user_id': first_entry.get('user_id')
                        }
        
        # Get assignments
        assignments = api_request(f'courses/{course_id}/assignments')
        if assignments:
            print(f"   📚 {len(assignments)} assignments")
            course_data['assignments'] = assignments[:2]  # Sample first 2
            
            # Try to get submissions from first assignment
            if assignments:
                first_assign = assignments[0]
                submissions = api_request(
                    f'courses/{course_id}/assignments/{first_assign["id"]}/submissions',
                    {'include[]': 'submission_comments'}
                )
                if submissions:
                    print(f"      • First assignment has {len(submissions)} submissions")
                    # Look for comments
                    comments_found = 0
                    for sub in submissions:
                        comments = sub.get('submission_comments', [])
                        if comments:
                            comments_found += len(comments)
                            # Sample first comment
                            if 'assignment_comment' not in course_data['sample_content']:
                                course_data['sample_content']['assignment_comment'] = {
                                    'comment': comments[0].get('comment', '')[:200],
                                    'created_at': comments[0].get('created_at'),
                                    'author_id': comments[0].get('author_id')
                                }
                    
                    if comments_found > 0:
                        print(f"      • Found {comments_found} total comments")
        
        results['courses'].append(course_data)
    
    # Save results
    with open('quick_canvas_sample.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Sample data saved to: quick_canvas_sample.json")
    
    # Print summary
    total_discussions = sum(len(c.get('discussions', [])) for c in results['courses'])
    total_assignments = sum(len(c.get('assignments', [])) for c in results['courses'])
    
    print(f"\n📊 SAMPLE SUMMARY:")
    print(f"   • {len(results['courses'])} courses sampled")
    print(f"   • {total_discussions} discussions found")
    print(f"   • {total_assignments} assignments found")
    
    # Show sample content types
    content_types = []
    for course in results['courses']:
        for content_type in course.get('sample_content', {}).keys():
            if content_type not in content_types:
                content_types.append(content_type)
    
    if content_types:
        print(f"   • Content types available: {', '.join(content_types)}")
    
    return results

if __name__ == "__main__":
    quick_course_sample()