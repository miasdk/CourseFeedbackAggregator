import requests
import json
from datetime import datetime

# Your ngrok URL
WEBHOOK_URL = "https://unilluminant-marion-severally.ngrok-free.dev/api/webhooks/zoho-survey"

# Test payload matching your Zoho form structure
test_payload = {
    # Core identification fields
    "course_name": "Introduction to Data Science",
    "reviewer_first_name": "John",
    "reviewer_last_name": "Doe",
    "reviewer_email": "john.doe@example.com",

    # Section 1 - First feedback area
    "section_1_area": "Course Content",
    "section_1_overall_rating": "4",
    "section_1_positive": "Great examples and clear explanations throughout the course",
    "section_1_improvements": "Would benefit from more hands-on exercises and practice problems",
    "section_1_showstopper": "No",
    "section_1_showstopper_details": "",

    # Section 2 - Second feedback area
    "section_2_area": "Instructor Performance",
    "section_2_overall_rating": "5",
    "section_2_positive": "Very engaging and knowledgeable instructor",
    "section_2_improvements": "Could provide more office hours for Q&A",
    "section_2_showstopper": "No",
    "section_2_showstopper_details": "",

    # Metadata fields
    "response_id": "TEST_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
    "response_start_time": datetime.utcnow().isoformat(),
    "response_end_time": datetime.utcnow().isoformat(),
    "survey_id": "SURVEY_COURSE_REVIEW_001"
}

print("=" * 50)
print("Testing Webhook Endpoint")
print("=" * 50)
print(f"URL: {WEBHOOK_URL}")
print(f"Payload: {json.dumps(test_payload, indent=2)[:200]}...")  # Show first 200 chars

try:
    # Send POST request
    response = requests.post(
        WEBHOOK_URL,
        json=test_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )

    print(f"\n✅ Status Code: {response.status_code}")

    if response.status_code == 200:
        print(f"✅ Response: {json.dumps(response.json(), indent=2)}")
        print("\n🎉 SUCCESS! Your webhook is working correctly!")
    else:
        print(f"❌ Error Response: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"❌ Connection Error: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check if FastAPI server is running (port 8000)")
    print("2. Check if ngrok is running")
    print("3. Verify the ngrok URL is correct")