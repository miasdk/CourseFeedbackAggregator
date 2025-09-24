# Course Feedback Aggregator - Complete Project Documentation

## Table of Contents

1. [Project Overview](#project-overview)
   - [Core Mission](#core-mission)
2. [Current Implementation Status](#current-implementation-status)
   - [Operational Components](#operational-components)
   - [Missing Components](#missing-components)
3. [Zoho Survey Data Structures](#zoho-survey-data-structures)
   - [1. Chief Advisor Course Review Worksheet](#1-chief-advisor-course-review-worksheet)
   - [2. Course Review Worksheet](#2-course-review-worksheet)
   - [3. EE Instructor Course Reviewer Worksheet](#3-ee-instructor-course-reviewer-worksheet)
   - [Survey Type Detection Logic](#survey-type-detection-logic)
   - [Key Data Insights for Database Design](#key-data-insights-for-database-design)
4. [System Architecture](#system-architecture)
   - [Database Schema](#database-schema)
   - [Data Flow Architecture](#data-flow-architecture)
   - [System Architecture Diagrams](#system-architecture-diagrams)
5. [Priority Scoring Engine (MVP)](#priority-scoring-engine-mvp)
   - [Core Algorithm](#core-algorithm)
   - [Explainable Recommendations](#explainable-recommendations)
6. [Implementation Roadmap](#implementation-roadmap)
   - [Phase 1: Database Foundation](#phase-1-database-foundation)
   - [Phase 2: Canvas Integration](#phase-2-canvas-integration)
   - [Phase 3: Data Processing](#phase-3-data-processing)
   - [Phase 4: Priority Scoring Engine](#phase-4-priority-scoring-engine)
   - [Phase 5: Frontend Integration](#phase-5-frontend-integration)
   - [Phase 6: Production Deployment](#phase-6-production-deployment)
7. [Updated Frontend Architecture](#updated-frontend-architecture)
   - [Component Structure](#component-structure)
   - [API Integration Updates](#api-integration-updates)
8. [Proposed Repository Structure](#proposed-repository-structure)
9. [Phase 1: Database Foundation - Actionable Next Steps](#phase-1-database-foundation---actionable-next-steps)
   - [Immediate Tasks](#immediate-tasks-this-week)
   - [Week 1 Deliverables](#week-1-deliverables)
   - [Repository Structure Changes Needed](#repository-structure-changes-needed)
10. [Development Commands](#development-commands)
   - [Backend](#backend)
   - [Frontend](#frontend)
   - [Database Operations](#database-operations)
11. [Technology Stack](#technology-stack)
12. [Success Metrics](#success-metrics)

## Project Overview

**Course Feedback Aggregation & Priority Intelligence System** - A platform that unifies course feedback from Canvas LMS and Zoho Surveys into a single database with intelligent prioritization scoring and explainable recommendations for course improvements.

### Core Mission
Build an explainable prioritization system that pulls course feedback from Canvas and Zoho into one database, scores what to "fix" first, and shows the "why" behind each recommendation in a live dashboard with tunable weights.

## Current Implementation Status

### Operational Components

#### 1. Zoho Survey Webhook Integration
- **Real-time webhook endpoint**: `/webhooks/zoho-survey`
- **Three survey types configured**:
  - Chief Advisor - Course Review Worksheet (98 responses)
  - Course Review Worksheet (31 responses)
  - EE Instructor - Course Reviewer Worksheet (87 responses)
- **Automatic survey type detection** based on payload structure
- **Structured data extraction** from course feedback

#### 2. Canvas API Foundation
- **API Token**: `15908~n7rLxPkkfXxZVkaLZ2CBNL9QzXCew8cCQmxaK4arEMtYWwJAUfaW3JQmn3Le2QuY`
- **Base URL**: `https://executiveeducation.instructure.com`
- **Testing infrastructure** functional
- **Course data structure** documented

#### 3. Frontend Dashboard (Mock Data)
- **React 18 + TypeScript** with Tailwind CSS + shadcn/ui
- **Working components**: PriorityRecommendations, CoursesList, DashboardOverview, ScoringControls
- **Mock API integration** with tunable weight sliders

### Missing Components
- Database layer (no persistence)
- Canvas integration (no data fetching)
- Priority scoring engine (no business logic)
- Course attribution system

## Zoho Survey Data Structures

The webhook endpoint successfully receives and processes three distinct survey types. Each has unique field structures and data patterns that inform our database schema and mapping logic.

### 1. Chief Advisor Course Review Worksheet

**Response Volume**: 98 responses
**Key Characteristics**: Module-based feedback (1-4), company/title info, testimonial data
**Reviewer Role**: `chief_advisor`

**Sample Payload Structure**:
```json
{
  "response_id": "12345678901234567890",
  "survey_id": "987654321",
  "collector_id": "456789123",
  "collector_name": "Chief Advisor - Course Review Worksheet",
  "response_start_time": "2024-01-15T10:30:00Z",

  // Course identification
  "course_name": "Advanced Leadership Strategy",

  // Reviewer information (unique to Chief Advisor)
  "reviewer_first_name": "Sarah",
  "reviewer_last_name": "Johnson",
  "reviewer_title": "VP of Operations",
  "reviewer_company": "TechCorp Industries",
  "reviewer_email": "sarah.johnson@techcorp.com",

  // Course Overview feedback
  "course_overview_rating": 4,
  "course_overview_positive": "Excellent strategic frameworks and real-world applications",
  "course_overview_improvements": "Could use more industry-specific case studies",

  // Module-based feedback (1-4)
  "module_1_rating": 4,
  "module_1_positive": "Strong foundational concepts",
  "module_1_improvements": "More interactive exercises needed",

  "module_2_rating": 5,
  "module_2_positive": "Outstanding facilitator engagement",
  "module_2_improvements": "",

  "module_3_rating": 3,
  "module_3_positive": "Good content coverage",
  "module_3_improvements": "Pacing was too fast, need more time for discussion",

  "module_4_rating": 4,
  "module_4_positive": "Practical tools and templates",
  "module_4_improvements": "Templates could be more customizable",

  // Program Wrap-Up
  "program_wrapup_rating": 4,
  "program_wrapup_positive": "Good synthesis and action planning",
  "program_wrapup_improvements": "Follow-up resources would be valuable",

  // Marketing/Testimonial (unique to Chief Advisor)
  "testimonial_text": "This program transformed how our leadership team approaches strategic planning. Highly recommended.",
  "allow_testimonial_use": "Yes",
  "wants_video_testimonial": "No"
}
```

**Processed Data Structure**:
```json
{
  "response_id": "12345678901234567890",
  "survey_type": "chief_advisor_course_review",
  "course_name": "Advanced Leadership Strategy",

  "reviewer": {
    "first_name": "Sarah",
    "last_name": "Johnson",
    "title": "VP of Operations",
    "company": "TechCorp Industries",
    "email": "sarah.johnson@techcorp.com",
    "full_name": "Sarah Johnson",
    "role": "chief_advisor"
  },

  "course_overview": {
    "rating": 4,
    "positive_comments": "Excellent strategic frameworks...",
    "improvement_suggestions": "Could use more industry-specific...",
    "has_improvements": true
  },

  "modules": {
    "module_1": {"rating": 4, "positive_comments": "...", "improvement_suggestions": "...", "has_improvements": true},
    "module_2": {"rating": 5, "positive_comments": "...", "improvement_suggestions": "", "has_improvements": false},
    "module_3": {"rating": 3, "positive_comments": "...", "improvement_suggestions": "...", "has_improvements": true},
    "module_4": {"rating": 4, "positive_comments": "...", "improvement_suggestions": "...", "has_improvements": true}
  },

  "program_wrapup": {
    "rating": 4,
    "positive_comments": "Good synthesis and action planning",
    "improvement_suggestions": "Follow-up resources would be valuable",
    "has_improvements": true
  },

  "marketing": {
    "testimonial_text": "This program transformed how...",
    "allow_testimonial_use": true,
    "wants_video_testimonial": false
  },

  "analysis": {
    "total_sections_with_improvements": 4,
    "has_marketing_value": true,
    "reviewer_seniority": "chief_advisor"
  }
}
```

### 2. Course Review Worksheet

**Response Volume**: 31 responses
**Key Characteristics**: Two-section structure, showstopper flags, document attachments
**Reviewer Role**: `general_reviewer`

**Sample Payload Structure**:
```json
{
  "response_id": "23456789012345678901",
  "survey_id": "876543210",
  "collector_id": "345678912",
  "collector_name": "Course Review Worksheet",
  "response_start_time": "2024-01-20T14:15:00Z",

  // Course identification
  "course_name": "Digital Marketing Fundamentals",

  // Reviewer information (basic)
  "reviewer_first_name": "Michael",
  "reviewer_last_name": "Chen",
  "reviewer_email": "michael.chen@company.com",

  // Section 1 feedback
  "section_1_area": "Content Structure & Flow",
  "section_1_overall_rating": 3,
  "section_1_positive": "Well-organized modules with clear learning objectives",
  "section_1_improvements": "Module 2 needs better transition between topics. Some concepts introduced too quickly.",
  "section_1_showstopper": "No",
  "section_1_showstopper_details": "",
  "section_1_documents": "",

  // Section 2 feedback
  "section_2_area": "Technical Implementation",
  "section_2_overall_rating": 2,
  "section_2_positive": "Good use of real-world examples",
  "section_2_improvements": "Video quality is poor in Module 3. Audio cuts out frequently. Platform keeps crashing during exercises.",
  "section_2_showstopper": "Yes - it needs to be fixed ASAP!",
  "section_2_showstopper_details": "Platform crashes prevent students from completing assignments. This blocks course progression.",
  "section_2_documents": "error_screenshots.pdf"
}
```

**Processed Data Structure**:
```json
{
  "response_id": "23456789012345678901",
  "survey_type": "course_review_worksheet",
  "course_name": "Digital Marketing Fundamentals",
  "reviewer_email": "michael.chen@company.com",
  "reviewer_name": "Michael Chen",
  "reviewer_role": "general_reviewer",

  "section_1": {
    "area": "Content Structure & Flow",
    "overall_rating": 3,
    "positive_comments": "Well-organized modules with clear learning objectives",
    "improvement_suggestions": "Module 2 needs better transition between topics...",
    "is_showstopper": false,
    "showstopper_details": null,
    "documents": null
  },

  "section_2": {
    "area": "Technical Implementation",
    "overall_rating": 2,
    "positive_comments": "Good use of real-world examples",
    "improvement_suggestions": "Video quality is poor in Module 3...",
    "is_showstopper": true,
    "showstopper_details": "Platform crashes prevent students from completing assignments...",
    "documents": "error_screenshots.pdf"
  },

  "metadata": {
    "survey_source": "zoho_course_review_worksheet",
    "submitted_at": "2024-01-20T14:15:00Z",
    "processing_timestamp": "2024-01-20T14:15:23.456Z",
    "collector_name": "Course Review Worksheet"
  }
}
```

### 3. EE Instructor Course Reviewer Worksheet

**Response Volume**: 87 responses
**Key Characteristics**: Same two-section structure as Course Review, but from instructor perspective
**Reviewer Role**: `ee_instructor`

**Sample Payload Structure**:
```json
{
  "response_id": "34567890123456789012",
  "survey_id": "765432109",
  "collector_id": "234567891",
  "collector_name": "EE Instructor - Course Reviewer Worksheet",
  "response_start_time": "2024-01-18T09:45:00Z",

  // Course identification
  "course_name": "Executive Finance for Non-Financial Managers",

  // Reviewer information (instructor)
  "reviewer_first_name": "Dr. Jennifer",
  "reviewer_last_name": "Rodriguez",
  "reviewer_email": "j.rodriguez@university.edu",

  // Section 1 feedback (instructor perspective)
  "section_1_area": "Curriculum Design & Learning Outcomes",
  "section_1_overall_rating": 4,
  "section_1_positive": "Clear learning objectives aligned with executive needs. Good balance of theory and practical application.",
  "section_1_improvements": "Case studies should include more recent examples. Module 4 learning outcomes too broad.",
  "section_1_showstopper": "No",
  "section_1_showstopper_details": "",
  "section_1_documents": "",

  // Section 2 feedback (instructor perspective)
  "section_2_area": "Instructional Materials & Resources",
  "section_2_overall_rating": 5,
  "section_2_positive": "Excellent instructor guides and supplementary materials. Video content is professional quality.",
  "section_2_improvements": "Would benefit from additional assessment rubrics for group projects.",
  "section_2_showstopper": "No",
  "section_2_showstopper_details": "",
  "section_2_documents": "suggested_rubrics.docx"
}
```

**Processed Data Structure**:
```json
{
  "response_id": "34567890123456789012",
  "survey_type": "ee_instructor_course_review",
  "course_name": "Executive Finance for Non-Financial Managers",
  "reviewer_email": "j.rodriguez@university.edu",
  "reviewer_name": "Dr. Jennifer Rodriguez",
  "reviewer_role": "ee_instructor",

  "section_1": {
    "area": "Curriculum Design & Learning Outcomes",
    "overall_rating": 4,
    "positive_comments": "Clear learning objectives aligned with executive needs...",
    "improvement_suggestions": "Case studies should include more recent examples...",
    "is_showstopper": false,
    "showstopper_details": null,
    "documents": null
  },

  "section_2": {
    "area": "Instructional Materials & Resources",
    "overall_rating": 5,
    "positive_comments": "Excellent instructor guides and supplementary materials...",
    "improvement_suggestions": "Would benefit from additional assessment rubrics...",
    "is_showstopper": false,
    "showstopper_details": null,
    "documents": "suggested_rubrics.docx"
  },

  "metadata": {
    "survey_source": "zoho_ee_instructor_course_review",
    "submitted_at": "2024-01-18T09:45:00Z",
    "processing_timestamp": "2024-01-18T09:45:31.789Z",
    "collector_name": "EE Instructor - Course Reviewer Worksheet"
  }
}
```

### Survey Type Detection Logic

The webhook automatically detects survey types based on payload fields:

```python
def detect_survey_type(payload: Dict[str, Any]) -> str:
    # Chief Advisor: Has module ratings and company info
    if any(key in payload for key in [
        "course_overview_rating", "module_1_rating", "module_2_rating",
        "reviewer_title", "reviewer_company"
    ]):
        return "chief_advisor_course_review"

    # EE Instructor vs Course Review: Both have section structure
    elif payload.get("collector_name") and "ee instructor" in payload.get("collector_name", "").lower():
        return "ee_instructor_course_review"

    # Course Review Worksheet: Has section areas and showstopper flags
    elif any(key in payload for key in [
        "section_1_area", "section_2_area", "section_1_showstopper", "section_2_showstopper"
    ]):
        return "course_review_worksheet"

    else:
        return "unknown_survey_type"
```

### Key Data Insights for Database Design

1. **Course Attribution Challenge**: Course names vary between surveys ("Advanced Leadership Strategy" vs "Adv Leadership" vs "Leadership Strategy - Advanced")

2. **Reviewer Hierarchy**: Chief Advisors > EE Instructors > General Reviewers (for priority weighting)

3. **Showstopper Criticality**: Technical issues flagged as showstoppers should trigger immediate priority scoring

4. **Content vs Technical Feedback**: Different improvement categories require different effort estimation (content changes vs platform fixes)

5. **Marketing Value**: Chief Advisor testimonials provide additional business value beyond course improvement

## System Architecture

### Database Schema

```sql
-- Canvas course master data
CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    canvas_id INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    course_code VARCHAR(100),
    workflow_state VARCHAR(50),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    total_students INTEGER,
    enrollment_term_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Survey feedback responses
CREATE TABLE survey_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_type VARCHAR(50) NOT NULL, -- 'chief_advisor', 'course_review', 'ee_instructor'
    source_response_id VARCHAR(100) UNIQUE,
    course_id INTEGER REFERENCES courses(id),
    course_name_raw VARCHAR(255) NOT NULL, -- Original survey course name
    reviewer_email VARCHAR(255),
    reviewer_name VARCHAR(255),
    reviewer_role VARCHAR(100), -- 'chief_advisor', 'ee_instructor', 'general'
    reviewer_title VARCHAR(255),
    reviewer_company VARCHAR(255),
    raw_payload JSONB NOT NULL,
    processed_at TIMESTAMP DEFAULT NOW(),
    attributed_at TIMESTAMP,
    attribution_confidence DECIMAL(3,2), -- 0.0 to 1.0
    attribution_method VARCHAR(100) -- 'exact_match', 'fuzzy_match', 'manual'
);

-- Structured feedback sections extracted from responses
CREATE TABLE feedback_sections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_response_id UUID REFERENCES survey_responses(id) ON DELETE CASCADE,
    section_type VARCHAR(100) NOT NULL, -- 'course_overview', 'module_1', 'section_1', etc.
    section_name VARCHAR(255), -- 'Module 1', 'Course Overview', etc.
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    positive_feedback TEXT,
    improvement_suggestions TEXT,
    is_showstopper BOOLEAN DEFAULT FALSE,
    showstopper_details TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Course priority scores (cached calculations)
CREATE TABLE course_priorities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id INTEGER REFERENCES courses(id) UNIQUE,
    priority_score DECIMAL(5,4), -- 0.0000 to 1.0000
    impact_score DECIMAL(5,4),
    urgency_score DECIMAL(5,4),
    effort_score DECIMAL(5,4),
    recency_score DECIMAL(5,4),
    total_responses INTEGER DEFAULT 0,
    responses_with_improvements INTEGER DEFAULT 0,
    showstopper_count INTEGER DEFAULT 0,
    average_rating DECIMAL(3,2),
    last_feedback_date TIMESTAMP,
    calculated_at TIMESTAMP DEFAULT NOW(),
    weights_used JSONB -- Store weights used for calculation
);

-- Weight configurations (tunable via UI)
CREATE TABLE scoring_weights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    impact_weight DECIMAL(3,2) DEFAULT 0.40,
    urgency_weight DECIMAL(3,2) DEFAULT 0.35,
    effort_weight DECIMAL(3,2) DEFAULT 0.15,
    recency_weight DECIMAL(3,2) DEFAULT 0.10,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT weights_sum_check CHECK (
        impact_weight + urgency_weight + effort_weight + recency_weight = 1.00
    )
);

-- Course mapping for ambiguous survey course names
CREATE TABLE course_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    survey_course_name VARCHAR(255) NOT NULL,
    canvas_course_id INTEGER REFERENCES courses(id),
    confidence_score DECIMAL(3,2),
    mapping_method VARCHAR(100),
    verified_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(survey_course_name, canvas_course_id)
);

-- Indexes for performance
CREATE INDEX idx_survey_responses_course_id ON survey_responses(course_id);
CREATE INDEX idx_feedback_sections_response_id ON feedback_sections(survey_response_id);
CREATE INDEX idx_course_priorities_score ON course_priorities(priority_score DESC);
CREATE INDEX idx_survey_responses_source_type ON survey_responses(source_type);
```

### Data Flow Architecture

#### Primary Data Pipeline
```mermaid
graph LR
    A[Zoho Survey Response] --> B[Webhook Endpoint]
    B --> C[FastAPI Parser]
    C --> D[Neon PostgreSQL]
    D --> E[Priority Engine]
    E --> F[React Dashboard]

    G[Canvas LMS] --> H[API Client]
    H --> D

    F --> I[Weight Adjustments]
    I --> E
```

#### Detailed Processing Flow
1. **Data Ingestion**
   - Zoho Survey responses arrive via webhook (`/webhooks/zoho-survey`)
   - Canvas course data pulled via API client
   - Raw payloads stored with metadata

2. **Data Processing**
   - Course attribution (fuzzy matching survey names to Canvas courses)
   - Feedback section extraction (ratings, comments, show-stoppers)
   - Data validation and cleaning

3. **Intelligence Layer**
   - Priority score calculation (Impact × Urgency × Effort × Recency)
   - Explanation generation for each recommendation
   - Tunable weight system for score adjustment

4. **User Interface**
   - Real-time dashboard updates
   - Drill-down feedback views
   - Manual course mapping for edge cases

### System Architecture Diagrams

#### Database Entity Relationships
```mermaid
erDiagram
    COURSES {
        int id PK
        int canvas_id UK
        string name
        string course_code
        string workflow_state
        timestamp start_date
        timestamp end_date
        int total_students
    }

    SURVEY_RESPONSES {
        uuid id PK
        string source_type
        string source_response_id UK
        int course_id FK
        string course_name_raw
        string reviewer_email
        jsonb raw_payload
        timestamp processed_at
    }

    FEEDBACK_SECTIONS {
        uuid id PK
        uuid survey_response_id FK
        string section_type
        string section_name
        int rating
        text positive_feedback
        text improvement_suggestions
        boolean is_showstopper
    }

    COURSE_PRIORITIES {
        uuid id PK
        int course_id FK
        decimal priority_score
        decimal impact_score
        decimal urgency_score
        decimal effort_score
        decimal recency_score
        int total_responses
        int showstopper_count
    }

    SCORING_WEIGHTS {
        uuid id PK
        string name
        decimal impact_weight
        decimal urgency_weight
        decimal effort_weight
        decimal recency_weight
        boolean is_active
    }

    COURSE_MAPPINGS {
        uuid id PK
        string survey_course_name
        int canvas_course_id FK
        decimal confidence_score
        string mapping_method
    }

    COURSES ||--o{ SURVEY_RESPONSES : "has responses"
    COURSES ||--o{ COURSE_PRIORITIES : "has priority"
    COURSES ||--o{ COURSE_MAPPINGS : "maps to"
    SURVEY_RESPONSES ||--o{ FEEDBACK_SECTIONS : "contains sections"
```

#### Component Architecture
```mermaid
graph TB
    subgraph "External Systems"
        ZS[Zoho Surveys]
        CL[Canvas LMS]
    end

    subgraph "Data Ingestion"
        WH[Webhook Handler]
        CA[Canvas API Client]
    end

    subgraph "FastAPI Backend"
        API[API Router]
        WS[Webhook Service]
        CS[Canvas Service]
        AS[Attribution Service]
        PS[Priority Service]
        FS[Feedback Service]
    end

    subgraph "Database Layer"
        DB[(Neon PostgreSQL)]
        MIG[Alembic Migrations]
    end

    subgraph "Frontend Dashboard"
        RC[React Components]
        STS[State Management]
        ACL[API Client]
    end

    subgraph "Intelligence Engine"
        PE[Priority Engine]
        EG[Explanation Generator]
        WM[Weight Manager]
    end

    ZS --> WH
    CL --> CA
    WH --> WS
    CA --> CS

    WS --> API
    CS --> API
    API --> AS
    API --> PS
    API --> FS

    AS --> DB
    PS --> DB
    FS --> DB

    PS --> PE
    PE --> EG
    WM --> PE

    ACL --> API
    RC --> ACL
    STS --> RC
```

#### Deployment Architecture
```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Vercel"
            FE[React Frontend]
        end

        subgraph "Railway/Render"
            BE[FastAPI Backend]
            WK[Worker Processes]
        end

        subgraph "Neon"
            DB[(PostgreSQL Database)]
            BR[Database Branches]
        end

        subgraph "External APIs"
            ZA[Zoho API]
            CA[Canvas API]
        end
    end

    subgraph "Development"
        DEV[Local Development]
        NG[ngrok Tunnel]
    end

    FE <--> BE
    BE <--> DB
    BE --> ZA
    BE --> CA

    DEV --> NG
    NG --> ZA
```

## Priority Scoring Engine (MVP)

### Core Algorithm

```python
def calculate_priority_score(course_id: int, weights: dict = None) -> dict:
    """
    Calculate priority score based on feedback data
    Returns: Complete scoring breakdown with explanations
    """
    if weights is None:
        weights = get_active_weights()

    # Gather data
    course_data = get_course_feedback_summary(course_id)

    # 1. IMPACT: Affected student volume
    impact_score = min(
        course_data.responses_with_improvements / max(course_data.total_responses, 1),
        1.0
    )

    # 2. URGENCY: Critical issues + poor ratings
    showstopper_penalty = min(course_data.showstopper_count * 0.3, 1.0)
    rating_penalty = max(0, (3.0 - course_data.average_rating) / 2.0)  # Below 3/5 is urgent
    urgency_score = min(showstopper_penalty + rating_penalty, 1.0)

    # 3. EFFORT: Estimated implementation difficulty (inverse score)
    effort_categories = categorize_improvement_types(course_id)
    effort_score = 1.0 - calculate_effort_estimate(effort_categories)

    # 4. RECENCY: Recent feedback matters more
    days_since_last = (datetime.now() - course_data.last_feedback_date).days
    recency_score = max(0, 1.0 - (days_since_last / 30))  # 30-day decay

    # Calculate weighted final score
    priority_score = (
        impact_score * weights["impact"] +
        urgency_score * weights["urgency"] +
        effort_score * weights["effort"] +
        recency_score * weights["recency"]
    )

    return {
        "priority_score": round(priority_score, 4),
        "impact_score": round(impact_score, 4),
        "urgency_score": round(urgency_score, 4),
        "effort_score": round(effort_score, 4),
        "recency_score": round(recency_score, 4),
        "weights_used": weights,
        "explanation": generate_explanation(course_data, impact_score, urgency_score, effort_score, recency_score),
        "recommendations": generate_recommendations(course_data)
    }

def categorize_improvement_types(course_id: int) -> dict:
    """Simple keyword-based categorization for effort estimation"""
    improvements = get_improvement_suggestions(course_id)

    categories = {"content": 0, "technical": 0, "design": 0, "major": 0}

    for improvement in improvements:
        text = improvement.lower()
        if any(word in text for word in ["video", "system", "broken", "technical"]):
            categories["technical"] += 1
        elif any(word in text for word in ["redesign", "restructure", "overhaul"]):
            categories["major"] += 1
        elif any(word in text for word in ["layout", "interface", "navigation"]):
            categories["design"] += 1
        else:
            categories["content"] += 1

    return categories

def calculate_effort_estimate(categories: dict) -> float:
    """Return effort score (0.0 = easy, 1.0 = very difficult)"""
    weights = {"content": 0.1, "design": 0.3, "technical": 0.6, "major": 0.9}
    total_issues = sum(categories.values())

    if total_issues == 0:
        return 0.1  # Minimal effort if no specific improvements

    weighted_effort = sum(count * weights[category] for category, count in categories.items())
    return min(weighted_effort / total_issues, 1.0)
```

### Explainable Recommendations

```python
def generate_explanation(course_data, impact, urgency, effort, recency) -> str:
    """Generate human-readable explanation for priority score"""
    explanations = []

    if impact > 0.7:
        explanations.append(f"High impact: {course_data.responses_with_improvements}/{course_data.total_responses} responses suggest improvements")

    if urgency > 0.6:
        if course_data.showstopper_count > 0:
            explanations.append(f"Critical issues: {course_data.showstopper_count} show-stopper problems identified")
        if course_data.average_rating < 3.0:
            explanations.append(f"Poor satisfaction: Average rating {course_data.average_rating}/5")

    if effort > 0.7:
        explanations.append("Quick wins: Most suggested improvements appear to be low-effort content changes")

    if recency > 0.8:
        explanations.append("Active feedback: Recent responses indicate ongoing student concerns")

    return "; ".join(explanations) if explanations else "Standard priority based on feedback patterns"
```

## Implementation Roadmap

### Phase 1: Database Foundation 
**Goal**: Establish data persistence

**Tasks**:
- [ ] Set up Neon PostgreSQL database
- [ ] Implement SQLAlchemy models matching schema above
- [ ] Create Alembic migration system
- [ ] Update webhook endpoint to persist data
- [ ] Test end-to-end data flow: webhook → database

**Acceptance Criteria**:
- All webhook data persisted in database
- Survey responses queryable by course
- Database migrations working

### Phase 2: Canvas Integration 
**Goal**: Course master data and attribution

**Tasks**:
- [ ] Implement Canvas API client
- [ ] Create `/api/canvas/sync-courses` endpoint
- [ ] Build fuzzy matching for course names
- [ ] Implement course attribution logic
- [ ] Add manual mapping interface for edge cases

**Acceptance Criteria**:
- Canvas courses imported and kept in sync
- 80%+ of survey responses automatically attributed to courses
- Manual mapping queue functional for ambiguous cases

### Phase 3: Data Processing (Week 3)
**Goal**: Structure feedback for analysis

**Tasks**:
- [ ] Build feedback section extraction service
- [ ] Implement data validation and cleaning
- [ ] Create aggregation queries for course summaries
- [ ] Add basic metrics endpoints (response counts, averages)

**Acceptance Criteria**:
- Structured feedback sections extracted from all response types
- Course feedback summaries available via API
- Data quality validation in place

### Phase 4: Priority Scoring Engine 
**Goal**: MVP prioritization system

**Tasks**:
- [ ] Implement priority calculation algorithm
- [ ] Create scoring weights management
- [ ] Build explanation generation
- [ ] Add batch recalculation endpoints
- [ ] Implement tunable weight system

**Acceptance Criteria**:
- Priority scores calculated for all courses with feedback
- Weights adjustable via API
- Explanations generated for each priority score
- Scores recalculated when new feedback arrives

### Phase 5: Frontend Integration 
**Goal**: Connect real backend to dashboard

**Tasks**:
- [ ] Replace mock API calls with real endpoints
- [ ] Implement weight slider functionality
- [ ] Add course feedback detail views
- [ ] Create priority explanation panels
- [ ] Add manual course mapping interface

**Acceptance Criteria**:
- Dashboard displays real course data
- Weight adjustments update priorities in real-time
- Users can drill down into specific feedback
- Manual mapping interface functional

### Phase 6: Production Deployment (Week 6)
**Goal**: Live system

**Tasks**:
- [ ] Deploy backend to Railway/Render
- [ ] Configure production Neon PostgreSQL
- [ ] Deploy frontend to Vercel
- [ ] Update Zoho webhooks to production URLs
- [ ] Set up monitoring and alerts

**Acceptance Criteria**:
- System operational in production
- Webhooks flowing to production database
- Dashboard accessible with real data

## Updated Frontend Architecture

### Component Structure
```
apps/frontend/src/
├── components/
│   ├── ui/                          # shadcn/ui primitives
│   ├── courses/
│   │   ├── CoursesList.tsx          # Updated: real API calls
│   │   ├── CourseCard.tsx           # New: individual course display
│   │   └── CourseFeedbackDetail.tsx # New: detailed feedback view
│   ├── priorities/
│   │   ├── PriorityRecommendations.tsx  # Updated: real priority data
│   │   ├── RecommendationCard.tsx       # Updated: show explanations
│   │   └── PriorityExplanation.tsx      # New: why this priority
│   ├── scoring/
│   │   ├── ScoringControls.tsx          # Updated: API weight updates
│   │   ├── WeightSlider.tsx             # Updated: real-time updates
│   │   └── ScoreBreakdown.tsx           # New: show score components
│   ├── feedback/
│   │   ├── FeedbackSummary.tsx          # New: aggregated feedback
│   │   ├── ShowstopperAlerts.tsx        # New: critical issues
│   │   └── SentimentIndicator.tsx       # Future: AI sentiment
│   └── admin/
│       ├── CourseMappingQueue.tsx       # New: manual attribution
│       └── WebhookStatus.tsx            # New: system health
├── services/
│   ├── api.ts                           # Updated: real backend calls
│   ├── courses.ts                       # New: course management
│   ├── priorities.ts                    # New: priority operations
│   └── weights.ts                       # New: weight management
└── types/
    ├── Course.ts                        # Canvas + survey course types
    ├── SurveyResponse.ts                # Zoho webhook types
    ├── Priority.ts                      # Priority scoring types
    └── Feedback.ts                      # Feedback section types
```

### API Integration Updates

```typescript
// services/api.ts - Updated with real endpoints
export class ApiClient {
  private baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  async getCourses(): Promise<Course[]> {
    return this.get('/api/courses');
  }

  async getCoursePriorities(): Promise<CoursePriority[]> {
    return this.get('/api/priorities');
  }

  async updateWeights(weights: ScoringWeights): Promise<void> {
    return this.post('/api/weights', weights);
  }

  async getCourseFeedback(courseId: number): Promise<CourseFeedback> {
    return this.get(`/api/courses/${courseId}/feedback`);
  }

  async manuallyMapCourse(surveyCourseName: string, canvasId: number): Promise<void> {
    return this.post('/api/course-mappings', { surveyCourseName, canvasId });
  }
}
```

## Proposed Repository Structure

```
CourseFeedbackAggregator/
├── apps/
│   ├── backend/                     # FastAPI Backend
│   │   ├── app/
│   │   │   ├── api/                 # API endpoints
│   │   │   │   ├── __init__.py
│   │   │   │   ├── courses.py       # Course management endpoints
│   │   │   │   ├── priorities.py    # Priority scoring endpoints
│   │   │   │   ├── weights.py       # Weight configuration endpoints
│   │   │   │   ├── feedback.py      # Feedback retrieval endpoints
│   │   │   │   ├── webhooks.py      # Zoho webhook handlers
│   │   │   │   ├── canvas.py        # Canvas sync endpoints
│   │   │   │   └── mappings.py      # Course mapping endpoints
│   │   │   ├── core/                # Core business logic
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py      # Database configuration
│   │   │   │   ├── dependencies.py  # FastAPI dependencies
│   │   │   │   └── config.py        # Settings and configuration
│   │   │   ├── models/              # SQLAlchemy models
│   │   │   │   ├── __init__.py
│   │   │   │   ├── course.py        # Course model
│   │   │   │   ├── survey.py        # Survey response model
│   │   │   │   ├── feedback.py      # Feedback section model
│   │   │   │   ├── priority.py      # Priority scoring model
│   │   │   │   └── mapping.py       # Course mapping model
│   │   │   ├── services/            # Business logic services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── canvas_service.py      # Canvas API integration
│   │   │   │   ├── priority_service.py    # Priority calculation
│   │   │   │   ├── attribution_service.py # Course attribution
│   │   │   │   ├── feedback_service.py    # Feedback processing
│   │   │   │   └── webhook_service.py     # Webhook processing
│   │   │   ├── schemas/             # Pydantic schemas
│   │   │   │   ├── __init__.py
│   │   │   │   ├── course.py        # Course schemas
│   │   │   │   ├── survey.py        # Survey schemas
│   │   │   │   ├── feedback.py      # Feedback schemas
│   │   │   │   ├── priority.py      # Priority schemas
│   │   │   │   └── webhook.py       # Webhook schemas
│   │   │   └── utils/               # Utility functions
│   │   │       ├── __init__.py
│   │   │       ├── fuzzy_match.py   # Course name matching
│   │   │       ├── text_analysis.py # Text processing
│   │   │       └── zoho_auth.py     # Token management
│   │   ├── alembic/                 # Database migrations
│   │   │   ├── versions/
│   │   │   ├── env.py
│   │   │   └── script.py.mako
│   │   ├── tests/                   # Backend tests
│   │   │   ├── __init__.py
│   │   │   ├── test_api/
│   │   │   ├── test_services/
│   │   │   └── test_models/
│   │   ├── requirements.txt
│   │   ├── alembic.ini
│   │   └── main.py                  # FastAPI app entry
│   │
│   └── frontend/                    # React Frontend
│       ├── src/
│       │   ├── components/
│       │   │   ├── ui/              # shadcn/ui primitives
│       │   │   ├── courses/         # Course-related components
│       │   │   │   ├── CoursesList.tsx
│       │   │   │   ├── CourseCard.tsx
│       │   │   │   └── CourseFeedbackDetail.tsx
│       │   │   ├── priorities/      # Priority-related components
│       │   │   │   ├── PriorityRecommendations.tsx
│       │   │   │   ├── RecommendationCard.tsx
│       │   │   │   └── PriorityExplanation.tsx
│       │   │   ├── scoring/         # Scoring controls
│       │   │   │   ├── ScoringControls.tsx
│       │   │   │   ├── WeightSlider.tsx
│       │   │   │   └── ScoreBreakdown.tsx
│       │   │   ├── feedback/        # Feedback display
│       │   │   │   ├── FeedbackSummary.tsx
│       │   │   │   └── ShowstopperAlerts.tsx
│       │   │   ├── admin/           # Admin interfaces
│       │   │   │   ├── CourseMappingQueue.tsx
│       │   │   │   └── WebhookStatus.tsx
│       │   │   └── layout/          # Layout components
│       │   │       ├── ApplicationLayout.tsx
│       │   │       ├── Navbar.tsx
│       │   │       └── HeaderNav.tsx
│       │   ├── services/            # API integration
│       │   │   ├── api.ts           # Main API client
│       │   │   ├── courses.ts       # Course operations
│       │   │   ├── priorities.ts    # Priority operations
│       │   │   ├── weights.ts       # Weight management
│       │   │   └── feedback.ts      # Feedback operations
│       │   ├── types/               # TypeScript types
│       │   │   ├── Course.ts
│       │   │   ├── SurveyResponse.ts
│       │   │   ├── Priority.ts
│       │   │   └── Feedback.ts
│       │   ├── hooks/               # Custom React hooks
│       │   │   ├── useCourses.ts
│       │   │   ├── usePriorities.ts
│       │   │   └── useWeights.ts
│       │   ├── stores/              # State management
│       │   │   ├── courseStore.ts
│       │   │   ├── priorityStore.ts
│       │   │   └── weightStore.ts
│       │   └── lib/                 # Utilities
│       │       ├── utils.ts
│       │       └── constants.ts
│       ├── public/
│       ├── package.json
│       └── vite.config.ts
│
├── database/                        # Database setup and migrations
│   ├── init.sql                     # Initial schema
│   ├── seed_data.sql               # Sample data for testing
│   └── docker-compose.yml          # Local PostgreSQL setup
│
├── scripts/                         # Development scripts
│   ├── setup_dev.sh                # Development environment setup
│   ├── deploy.sh                   # Deployment script
│   └── test_webhook.py             # Webhook testing utility
│
├── docs/                           # Project documentation
│   ├── api.md                      # API documentation
│   ├── database.md                 # Database schema docs
│   └── deployment.md               # Deployment guide
│
├── .env.example                    # Environment template
├── .gitignore
├── README.md
└── CLAUDE.md                       # This file
```

## Phase 1: Database Foundation - Actionable Next Steps

### Immediate Tasks (This Week)

#### 1. Database Setup
```bash
# Create Neon PostgreSQL database
# URL: https://console.neon.tech/
# Database name: coursefeedback
# Get connection string for .env
```

#### 2. Backend Structure Setup
```bash
cd apps/backend

# Create new directory structure
mkdir -p app/{models,schemas,services,api,core,utils}
mkdir -p app/{models,schemas,services,api,core,utils}/__init__.py

# Initialize Alembic for migrations
pip install alembic
alembic init alembic
```

#### 3. SQLAlchemy Models Implementation
Create the following files in order:

**Priority 1: Core Models**
- `app/models/course.py` - Canvas course data
- `app/models/survey.py` - Survey response model
- `app/models/feedback.py` - Feedback sections
- `app/models/priority.py` - Priority scores
- `app/models/mapping.py` - Course mappings

**Priority 2: Database Configuration**
- `app/core/database.py` - Database connection and session management
- `app/core/config.py` - Environment variables and settings
- `alembic/env.py` - Configure Alembic with SQLAlchemy models

#### 4. First Migration
```bash
# Generate initial migration
alembic revision --autogenerate -m "Initial database schema"

# Apply migration
alembic upgrade head
```

#### 5. Update Webhook Endpoint
Modify existing webhook to persist data:
- `app/api/webhooks.py` - Update to save to database
- `app/services/webhook_service.py` - Create service for webhook processing

### Week 1 Deliverables

**✅ Success Criteria:**
- [ ] Neon PostgreSQL database created and accessible
- [ ] SQLAlchemy models implemented for all core tables
- [ ] Database migrations working (alembic upgrade/downgrade)
- [ ] Webhook endpoint saving survey responses to database
- [ ] Basic API endpoints for retrieving stored data

**🔧 Commands to Run:**
```bash
# Backend setup
cd apps/backend
pip install sqlalchemy asyncpg alembic pydantic-settings
alembic init alembic

# Test database connection
python -c "from app.core.database import engine; print('Database connected!')"

# Apply migrations
alembic upgrade head

# Test webhook persistence
curl -X POST http://localhost:8000/webhooks/zoho-survey \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'

# Verify data in database
psql $DATABASE_URL -c "SELECT COUNT(*) FROM survey_responses;"
```

### Repository Structure Changes Needed

**Move/Rename:**
1. `app/services/zoho_auth.py` → `app/utils/zoho_auth.py` (token utility)
2. Create `app/core/database.py` (new)
3. Create `app/models/` directory (new)
4. Create `app/schemas/` directory (new)
5. Restructure `app/api/` with specific endpoint files

**Environment Variables to Add:**
```env
# Add to apps/backend/.env
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/coursefeedback
CANVAS_API_TOKEN=15908~n7rLxPkkfXxZVkaLZ2CBNL9QzXCew8cCQmxaK4arEMtYWwJAUfaW3JQmn3Le2QuY
CANVAS_BASE_URL=https://executiveeducation.instructure.com
ZOHO_CLIENT_ID=1000.LFJC5W9CC2VV5A0VBHZBI8HFY0OWYH
ZOHO_CLIENT_SECRET=your_secret_here
ZOHO_REFRESH_TOKEN=to_be_obtained

# Add to apps/frontend/.env
VITE_API_URL=http://localhost:8000
```

## Development Commands

### Backend
```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head  # Apply database migrations
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd apps/frontend
npm install
npm run dev          # Start Vite development server (port 5173)
npm run start        # Alternative start command (same as dev)
npm run build        # Build for production using Vite
npm run preview      # Preview production build locally
```

### Database Operations
```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Reset to specific revision
alembic downgrade <revision_id>
```

## Technology Stack

### Backend
- **FastAPI** (Python 3.11+) - Modern async API framework
- **SQLAlchemy 2.0** - ORM with async support and modern syntax
- **Alembic** - Database schema migrations and versioning
- **Neon PostgreSQL** - Serverless PostgreSQL with branching (simplifies database setup)
- **Pydantic v2** - Data validation and serialization
- **httpx** - Async HTTP client for Canvas API integration
- **asyncpg** - Fast async PostgreSQL adapter
- **python-dotenv** - Environment variable management

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** + **shadcn/ui** components
- **TanStack Query** - API state management
- **Recharts** - Data visualization
- **Vite** - Build tool and dev server
- **Zustand** - Lightweight state management

### Infrastructure
- **Backend**: Railway/Render (containerized deployment)
- **Frontend**: Vercel (optimized React deployment)
- **Database**: Neon PostgreSQL (serverless with automatic scaling)
- **Webhooks**: ngrok (development) → production URLs
- **Monitoring**: Built-in logging with optional external monitoring

## Success Metrics

### Phase 1 Success Criteria
- [ ] All survey webhook data persisting to database
- [ ] Database queries working for survey responses
- [ ] Course data structure ready for Canvas integration
- [ ] Migration system functional for schema changes

### Next Phase Preview (Phase 2)
- Canvas API integration
- Course attribution system
- Fuzzy matching for course names
- Manual mapping interface for edge cases

---

**Current Status**: 25% Complete (Webhook infrastructure operational)
**Next Milestone**: Database persistence with structured data (Phase 1)
**Immediate Focus**: SQLAlchemy models and database migrations
**Timeline**: Phase 1 completion target - 1 week