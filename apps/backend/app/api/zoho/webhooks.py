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
    Unified webhook endpoint for all Zoho Survey webhook payloads
    Automatically detects survey type and processes accordingly
    """
    
    try:
        #1. Get the JSON payload from Zoho
        payload = await request.json()
        
        #2. Detect survey type based on payload structure
        survey_type = detect_survey_type(payload)
        
        #3. Log the incoming payload (for debugging)
        print("\n" + "="*60)
        print(f"WEBHOOK RECEIVED - {survey_type.upper().replace('_', ' ')}")
        print("="*60)
        print(f"Course: {payload.get('course_name', 'Unknown')}")
        print(f"Reviewer: {payload.get('reviewer_first_name', 'Unknown')}")
        print(f"Response ID: {payload.get('response_id', 'Unknown')}")
        print(f"Survey Type: {survey_type}")
        print(f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("\nFull Payload:")
        print(json.dumps(payload, indent=2))
        print("="*60 + "\n")

        #4. Validate required fields exist
        required_fields = ["response_id", "course_name"]
        missing_fields = [field for field in required_fields if not payload.get(field)]

        if missing_fields:
            logger.warning(f"Missing required fields: {missing_fields}")
            raise HTTPException(status_code=400, detail=f"Missing fields: {missing_fields}")

        #5. Process based on survey type
        if survey_type == "chief_advisor_course_review":
            processed_feedback = process_chief_advisor_feedback(payload)
        elif survey_type == "course_review_worksheet" or survey_type == "ee_instructor_course_review":
            # Both use the same two-section structure - your existing function handles both
            processed_feedback = process_course_feedback(payload)
        else:
            processed_feedback = process_unknown_survey(payload)

        #6. Store in database (To be implemented)
        # await store_feedback_data(processed_feedback)

        #7. Return success response quickly
        return {
            "status": "received", 
            "response_id": payload.get("response_id"),
            "survey_type": survey_type
        }

    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook payload")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


def detect_survey_type(payload: Dict[str, Any]) -> str:
    """
    Detect which survey type based on unique fields in the payload
    """
    # Chief Advisor Course Review has module ratings and company info
    if any(key in payload for key in [
        "course_overview_rating", 
        "module_1_rating", 
        "module_2_rating",
        "reviewer_title",
        "reviewer_company"
    ]):
        return "chief_advisor_course_review"
    
    # EE Instructor vs regular Course Review - both have same structure
    # Distinguish by collector name if available
    elif payload.get("collector_name") and "ee instructor" in payload.get("collector_name", "").lower():
        return "ee_instructor_course_review"
    
    # Original Course Review Worksheet and EE Instructor both have section areas
    elif any(key in payload for key in [
        "section_1_area",
        "section_2_area", 
        "section_1_showstopper",
        "section_2_showstopper"
    ]):
        return "course_review_worksheet"
    
    # Default fallback
    else:
        return "unknown_survey_type"


# Keep your existing process_course_feedback function unchanged
def process_course_feedback(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process Course Review Worksheet AND EE Instructor feedback - same structure"""
    
    # Determine reviewer role based on detection
    survey_type = detect_survey_type(payload)
    reviewer_role = "ee_instructor" if survey_type == "ee_instructor_course_review" else "general_reviewer"
    
    return {
        # Core identification
        "response_id": payload.get("response_id"),
        "survey_type": survey_type,
        "course_name": payload.get("course_name"),
        "reviewer_email": payload.get("reviewer_email"),
        "reviewer_name": f"{payload.get('reviewer_first_name', '')} {payload.get('reviewer_last_name', '')}".strip(),
        "reviewer_role": reviewer_role,
        
        # Section 1 feedback
        "section_1": {
            "area": payload.get("section_1_area"),
            "overall_rating": payload.get("section_1_overall_rating"),
            "positive_comments": payload.get("section_1_positive"),
            "improvement_suggestions": payload.get("section_1_improvements"),
            "is_showstopper": payload.get("section_1_showstopper", "").lower() in ["yes", "yes - it needs to be fixed asap!"],
            "showstopper_details": payload.get("section_1_showstopper_details"),
            "documents": payload.get("section_1_documents")
        },
        
        # Section 2 feedback
        "section_2": {
            "area": payload.get("section_2_area"),
            "overall_rating": payload.get("section_2_overall_rating"),
            "positive_comments": payload.get("section_2_positive"),
            "improvement_suggestions": payload.get("section_2_improvements"),
            "is_showstopper": payload.get("section_2_showstopper", "").lower() in ["yes", "yes - it needs to be fixed asap!"],
            "showstopper_details": payload.get("section_2_showstopper_details"),
            "documents": payload.get("section_2_documents")
        },
        
        # Metadata
        "metadata": {
            "survey_source": f"zoho_{survey_type}",
            "submitted_at": payload.get("response_start_time"),
            "processing_timestamp": datetime.utcnow().isoformat(),
            "collector_name": payload.get("collector_name"),
            "collector_id": payload.get("collector_id"),
            "survey_id": payload.get("survey_id")
        }
    }


def process_chief_advisor_feedback(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Process Chief Advisor Course Review Worksheet feedback"""
    return {
        # Core identification
        "response_id": payload.get("response_id"),
        "survey_type": "chief_advisor_course_review",
        "course_name": payload.get("course_name"),
        
        # Reviewer information
        "reviewer": {
            "first_name": payload.get("reviewer_first_name"),
            "last_name": payload.get("reviewer_last_name"),
            "title": payload.get("reviewer_title"),
            "company": payload.get("reviewer_company"),
            "email": payload.get("reviewer_email"),
            "full_name": f"{payload.get('reviewer_first_name', '')} {payload.get('reviewer_last_name', '')}".strip(),
            "role": "chief_advisor"
        },
        
        # Course Overview feedback
        "course_overview": {
            "rating": payload.get("course_overview_rating"),
            "positive_comments": payload.get("course_overview_positive"),
            "improvement_suggestions": payload.get("course_overview_improvements"),
            "has_improvements": bool(payload.get("course_overview_improvements", "").strip())
        },
        
        # Module feedback (1-4)
        "modules": {
            "module_1": {
                "rating": payload.get("module_1_rating"),
                "positive_comments": payload.get("module_1_positive"),
                "improvement_suggestions": payload.get("module_1_improvements"),
                "has_improvements": bool(payload.get("module_1_improvements", "").strip())
            },
            "module_2": {
                "rating": payload.get("module_2_rating"),
                "positive_comments": payload.get("module_2_positive"),
                "improvement_suggestions": payload.get("module_2_improvements"),
                "has_improvements": bool(payload.get("module_2_improvements", "").strip())
            },
            "module_3": {
                "rating": payload.get("module_3_rating"),
                "positive_comments": payload.get("module_3_positive"),
                "improvement_suggestions": payload.get("module_3_improvements"),
                "has_improvements": bool(payload.get("module_3_improvements", "").strip())
            },
            "module_4": {
                "rating": payload.get("module_4_rating"),
                "positive_comments": payload.get("module_4_positive"),
                "improvement_suggestions": payload.get("module_4_improvements"),
                "has_improvements": bool(payload.get("module_4_improvements", "").strip())
            }
        },
        
        # Program Wrap-Up feedback
        "program_wrapup": {
            "rating": payload.get("program_wrapup_rating"),
            "positive_comments": payload.get("program_wrapup_positive"),
            "improvement_suggestions": payload.get("program_wrapup_improvements"),
            "has_improvements": bool(payload.get("program_wrapup_improvements", "").strip())
        },
        
        # Marketing/Testimonial data
        "marketing": {
            "testimonial_text": payload.get("testimonial_text"),
            "allow_testimonial_use": payload.get("allow_testimonial_use", "").lower() == "yes",
            "wants_video_testimonial": payload.get("wants_video_testimonial", "").lower() == "yes"
        },
        
        # Metadata
        "metadata": {
            "survey_source": "zoho_chief_advisor_course_review",
            "submitted_at": payload.get("response_start_time"),
            "processing_timestamp": datetime.utcnow().isoformat(),
            "collector_name": payload.get("collector_name"),
            "collector_id": payload.get("collector_id"),
            "survey_id": payload.get("survey_id")
        },
        
        # Analysis flags for prioritization
        "analysis": {
            "total_sections_with_improvements": sum([
                bool(payload.get("course_overview_improvements", "").strip()),
                bool(payload.get("module_1_improvements", "").strip()),
                bool(payload.get("module_2_improvements", "").strip()),
                bool(payload.get("module_3_improvements", "").strip()),
                bool(payload.get("module_4_improvements", "").strip()),
                bool(payload.get("program_wrapup_improvements", "").strip())
            ]),
            "has_marketing_value": bool(payload.get("testimonial_text", "").strip()),
            "reviewer_seniority": "chief_advisor"
        }
    }


def process_unknown_survey(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Fallback processor for unrecognized survey types"""
    return {
        "response_id": payload.get("response_id"),
        "survey_type": "unknown",
        "course_name": payload.get("course_name"),
        "reviewer_name": f"{payload.get('reviewer_first_name', '')} {payload.get('reviewer_last_name', '')}".strip(),
        "raw_payload": payload,
        "metadata": {
            "survey_source": "zoho_unknown_survey",
            "submitted_at": payload.get("response_start_time"),
            "processing_timestamp": datetime.utcnow().isoformat(),
            "collector_name": payload.get("collector_name"),
            "needs_manual_review": True
        }
    }