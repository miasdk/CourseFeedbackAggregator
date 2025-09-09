#!/usr/bin/env python3
"""
Direct test of backend ingestion points to validate Canvas and Zoho clients
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# Add the backend app to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'apps/backend'))

# Set environment variables from the .env file
os.environ['CANVAS_ACCESS_TOKEN'] = '15908~n7rLxPkkfXxZVkaLZ2CBNL9QzXCew8cCQmxaK4arEMtYWwJAUfaW3JQmn3Le2QuY'
os.environ['CANVAS_API_URL'] = 'https://executiveeducation.instructure.com'
os.environ['ZOHO_ACCESS_TOKEN'] = '1000.9daae92c25e9badb9c336d4dc2f5b1cd.5b1830e9c265afdb55201aa719f7261f'
os.environ['ZOHO_CLIENT_ID'] = '1000.LFJC5W9CC2VV5A0VBHZBI8HFY0OWYH'
os.environ['ZOHO_CLIENT_SECRET'] = '7ecd8b1b8fc447be2edd83e137d2987e7824e3d682'

try:
    from apps.backend.app.clients.canvas_client import CanvasClient
    from apps.backend.app.clients.zoho_client import ZohoClient
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

async def test_canvas_ingestion():
    """Test Canvas client ingestion functionality"""
    print("🔍 TESTING CANVAS INGESTION CLIENT")
    print("="*50)
    
    try:
        canvas_client = CanvasClient()
        
        # Test basic API connectivity
        courses = await canvas_client.get_courses()
        print(f"✅ Canvas API connection successful")
        print(f"📚 Found {len(courses)} accessible courses")
        
        # Test feedback extraction from first course
        if courses:
            course = courses[0]
            course_id = str(course['id'])
            course_name = course.get('name', 'Unnamed')
            
            print(f"\n📖 Testing feedback extraction from: {course_name}")
            
            feedback_data = await canvas_client.extract_feedback_from_course(course_id)
            print(f"💬 Extracted {len(feedback_data)} feedback items")
            
            # Show sample feedback
            if feedback_data:
                sample = feedback_data[0]
                print(f"\n📋 SAMPLE FEEDBACK:")
                print(f"   Course: {sample['course_name']}")
                print(f"   Source: {sample['source']}")
                print(f"   Severity: {sample['severity']}")
                print(f"   Text: {sample['feedback_text'][:100]}...")
                if sample.get('rating'):
                    print(f"   Rating: {sample['rating']}/5.0")
        
        return {
            'success': True,
            'courses_found': len(courses),
            'feedback_extracted': len(feedback_data) if courses else 0
        }
        
    except Exception as e:
        print(f"❌ Canvas ingestion test failed: {str(e)}")
        return {'success': False, 'error': str(e)}

async def test_zoho_ingestion():
    """Test Zoho client ingestion functionality"""
    print("\n🔍 TESTING ZOHO INGESTION CLIENT")
    print("="*50)
    
    try:
        zoho_client = ZohoClient()
        
        # Test basic API connectivity by getting records from one module
        deals = await zoho_client.get_module_records('Deals', page=1, per_page=3)
        print(f"✅ Zoho API connection successful")
        print(f"📊 Found {len(deals)} deals to analyze")
        
        # Test feedback extraction from Deals module
        feedback_data = await zoho_client.extract_feedback_from_module('Deals')
        print(f"💬 Extracted {len(feedback_data)} feedback items from Deals")
        
        # Test feedback extraction from Contacts module  
        contacts_feedback = await zoho_client.extract_feedback_from_module('Contacts')
        print(f"💬 Extracted {len(contacts_feedback)} feedback items from Contacts")
        
        total_feedback = len(feedback_data) + len(contacts_feedback)
        
        # Show sample feedback
        if feedback_data:
            sample = feedback_data[0]
            print(f"\n📋 SAMPLE FEEDBACK:")
            print(f"   Course: {sample['course_name']}")
            print(f"   Source: {sample['source']}")
            print(f"   Module: {sample['context']['module']}")
            print(f"   Severity: {sample['severity']}")
            print(f"   Text: {sample['feedback_text'][:100]}...")
            if sample.get('rating'):
                print(f"   Rating: {sample['rating']}/5.0")
        
        return {
            'success': True,
            'deals_found': len(deals),
            'feedback_extracted': total_feedback
        }
        
    except Exception as e:
        print(f"❌ Zoho ingestion test failed: {str(e)}")
        return {'success': False, 'error': str(e)}

async def test_full_ingestion():
    """Test complete ingestion workflow"""
    print("\n🚀 TESTING COMPLETE INGESTION WORKFLOW")  
    print("="*60)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'canvas': {},
        'zoho': {},
        'total_feedback': 0,
        'ingestion_ready': False
    }
    
    # Test Canvas ingestion
    canvas_result = await test_canvas_ingestion()
    results['canvas'] = canvas_result
    
    # Test Zoho ingestion  
    zoho_result = await test_zoho_ingestion()
    results['zoho'] = zoho_result
    
    # Calculate totals
    if canvas_result['success'] and zoho_result['success']:
        canvas_feedback = canvas_result.get('feedback_extracted', 0)
        zoho_feedback = zoho_result.get('feedback_extracted', 0)
        results['total_feedback'] = canvas_feedback + zoho_feedback
        results['ingestion_ready'] = results['total_feedback'] > 0
        
        print(f"\n🎯 INGESTION SUMMARY:")
        print(f"   Canvas feedback: {canvas_feedback}")
        print(f"   Zoho feedback: {zoho_feedback}")
        print(f"   Total feedback: {results['total_feedback']}")
        print(f"   Ready for aggregation: {'✅ YES' if results['ingestion_ready'] else '❌ NO'}")
    
    # Save results
    with open('ingestion_test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: ingestion_test_results.json")
    
    if results['ingestion_ready']:
        print("\n✅ INGESTION POINTS VALIDATED: Backend clients are working correctly!")
        print("   • Canvas LMS client: Extracting feedback from courses")
        print("   • Zoho CRM client: Extracting feedback from deals/contacts") 
        print("   • Ready for course feedback aggregation")
    else:
        print("\n⚠️  ATTENTION NEEDED: Limited or no feedback data extracted")
        
    return results

async def main():
    """Run complete ingestion point validation"""
    print("🔧 BACKEND INGESTION POINTS VALIDATION")
    print("=" * 70)
    print(f"Timestamp: {datetime.now()}")
    print()
    
    try:
        results = await test_full_ingestion()
        return results['ingestion_ready']
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    asyncio.run(main())