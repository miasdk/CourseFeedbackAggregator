from fastapi import APIRouter, Request, HTTPException
from typing import Dict, Any
import logging
import json
from datetime import datetime
from pathlib import Path 

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhooks/zoho-survey") 

async def receive_zoho_webhook(request: Request):
    """
    Receive and process Zoho Survey webhook payloads 
    """ 
    try: 
        #1. Get the JSON payload from Zoho
        payload = await request.json()
        
        #2. Log the incoming payload (for debugging)
        print("\n" + "="*60)
        print("WEBHOOK RECEIVED")
        print("="*60)
        print(f"Course: {payload.get('course_name', 'Unknown')}")
        print(f"Reviewer: {payload.get('reviewer_first_name', 'Unknown')}")
        print(f"Response ID: {payload.get('response_id', payload.get('responseId', 'Unknown'))}")
        print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("\n Full Payload:")
        print(json.dumps(payload, indent=2))
        print("="*60 + "\n")

        #3. Validate required fields exist 
        required_fields = ["response_id", "course_name"]
        missing_fields = [field for field in required_fields if not payload.get(field)]

        if missing_fields: 
            logger.warning(f"Missing required fields: {missing_fields}")
            raise HTTPException(status_code=400, detail=f"Missing fields: {missing_fields}")

        #4. Process course feedback data 
        processed_feedback = process_course_feedback(payload)

        #5. Store in database (To be implemented)

        #6. Return success response quickly 
        return {"status": "received", "response_id": payload.get("response_id")}

    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

def process_course_feedback(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        # Core identification
        "response_id": payload.get("response_id"),
        "course_name": payload.get("course_name"),
        "reviewer_email": payload.get("reviewer_email"),
        "reviewer_name": f"{payload.get('reviewer_first_name', '')} {payload.get('reviewer_last_name', '')}".strip(),
        
        # Section 1 feedback
        "section_1": {
            "area": payload.get("section_1_area"),
            "overall_rating": payload.get("section_1_overall_rating"),  # MISSING - ADD THIS
            "positive_comments": payload.get("section_1_positive"),
            "improvement_suggestions": payload.get("section_1_improvements"),
            "is_showstopper": payload.get("section_1_showstopper", "").lower() == "yes",
            "showstopper_details": payload.get("section_1_showstopper_details")
        },
        
        # Section 2 feedback
        "section_2": {
            "area": payload.get("section_2_area"),
            "overall_rating": payload.get("section_2_overall_rating"),  # MISSING - ADD THIS
            "positive_comments": payload.get("section_2_positive"),
            "improvement_suggestions": payload.get("section_2_improvements"),
            "is_showstopper": payload.get("section_2_showstopper", "").lower() == "yes",
            "showstopper_details": payload.get("section_2_showstopper_details")
        },
        
        # Metadata
        "survey_source": "zoho_course_review_worksheet",
        "submitted_at": payload.get("response_start_time"),
        "processing_timestamp": datetime.utcnow().isoformat()
    }



