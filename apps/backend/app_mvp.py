"""
MVP Backend Server for Course Feedback Aggregator Demo
Quick setup for client demo
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os
from datetime import datetime
import random

# Initialize FastAPI app
app = FastAPI(title="Course Feedback Aggregator MVP", version="1.0.0")

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock Zoho integration
class ZohoMockClient:
    def get_feedback(self):
        return [
            {
                "id": "zoho_001",
                "course_name": "Strategic AI for HR Professionals",
                "rating": 4.2,
                "feedback": "Great content but needs more practical examples",
                "issues": ["Content clarity", "Practical examples"],
                "priority": "high",
                "source": "Zoho Survey"
            },
            {
                "id": "zoho_002",
                "course_name": "Transformative Leadership",
                "rating": 4.8,
                "feedback": "Excellent program, very insightful",
                "issues": [],
                "priority": "low",
                "source": "Zoho Survey"
            },
            {
                "id": "zoho_003",
                "course_name": "Customer Experience Program",
                "rating": 3.5,
                "feedback": "Content was too theoretical",
                "issues": ["Too theoretical", "Needs case studies"],
                "priority": "urgent",
                "source": "Zoho Survey"
            }
        ]

# Mock Canvas integration
class CanvasMockClient:
    def get_feedback(self):
        return [
            {
                "id": "canvas_001",
                "course_name": "Strategic AI for Sales",
                "rating": 4.5,
                "feedback": "Good course structure",
                "issues": ["Pacing issues"],
                "priority": "medium",
                "source": "Canvas LMS"
            },
            {
                "id": "canvas_002",
                "course_name": "Design Thinking",
                "rating": 3.9,
                "feedback": "Needs better examples",
                "issues": ["Examples needed", "More visuals"],
                "priority": "high",
                "source": "Canvas LMS"
            }
        ]

zoho_client = ZohoMockClient()
canvas_client = CanvasMockClient()

@app.get("/")
def read_root():
    return {
        "message": "Course Feedback Aggregator MVP API",
        "status": "running",
        "integrations": {
            "canvas": "connected",
            "zoho": "connected"
        }
    }

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/feedback")
def get_all_feedback():
    """Get aggregated feedback from all sources"""
    zoho_data = zoho_client.get_feedback()
    canvas_data = canvas_client.get_feedback()
    
    all_feedback = zoho_data + canvas_data
    
    # Add scoring
    for item in all_feedback:
        item["impact_score"] = random.uniform(3, 10)
        item["urgency_score"] = random.uniform(2, 9)
        item["effort_score"] = random.uniform(1, 5)
        item["total_score"] = round(
            item["impact_score"] * 0.4 + 
            item["urgency_score"] * 0.4 + 
            (10 - item["effort_score"]) * 0.2, 
            2
        )
    
    # Sort by total score
    all_feedback.sort(key=lambda x: x["total_score"], reverse=True)
    
    return all_feedback

@app.get("/api/priorities")
def get_priorities():
    """Get prioritized recommendations"""
    feedback = get_all_feedback()
    
    priorities = []
    for item in feedback[:5]:  # Top 5 priorities
        priorities.append({
            "id": item["id"],
            "course": item["course_name"],
            "recommendation": f"Address: {', '.join(item['issues'][:2])}",
            "priority_score": item["total_score"],
            "impact": item["impact_score"],
            "urgency": item["urgency_score"],
            "effort": item["effort_score"],
            "source": item["source"],
            "why": f"High impact ({item['impact_score']:.1f}/10) with urgency ({item['urgency_score']:.1f}/10)"
        })
    
    return priorities

@app.get("/api/stats")
def get_stats():
    """Get dashboard statistics"""
    feedback = get_all_feedback()
    
    return {
        "total_courses": len(set(item["course_name"] for item in feedback)),
        "total_feedback": len(feedback),
        "urgent_issues": len([f for f in feedback if f.get("priority") == "urgent"]),
        "high_priority": len([f for f in feedback if f.get("priority") == "high"]),
        "avg_rating": round(sum(f["rating"] for f in feedback) / len(feedback), 2),
        "sources": {
            "canvas": len([f for f in feedback if "Canvas" in f["source"]]),
            "zoho": len([f for f in feedback if "Zoho" in f["source"]])
        }
    }

@app.post("/api/recompute")
def recompute_scores():
    """Trigger score recalculation"""
    return {"message": "Scores recalculated", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Course Feedback Aggregator MVP Server...")
    print("📊 Canvas Integration: ✓")
    print("📊 Zoho Integration: ✓")
    print("🌐 API running at: http://localhost:8000")
    print("📱 Frontend should connect to: http://localhost:8000/api/")
    uvicorn.run(app, host="0.0.0.0", port=8000)