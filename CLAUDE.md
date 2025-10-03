# Course Feedback Aggregator - Complete Project Documentation

## Table of Contents

1. [Project Overview](#project-overview)
   - [Core Mission](#core-mission)
   - [Project Pivot Decision](#project-pivot-decision)
2. [Current Implementation Status](#current-implementation-status)
   - [Operational Components](#operational-components)
   - [Missing Components](#missing-components)
3. [Canvas Survey Data Architecture](#canvas-survey-data-architecture)
   - [Canvas API Endpoints](#canvas-api-endpoints)
   - [Survey Detection Logic](#survey-detection-logic)
   - [Student Feedback Data Structures](#student-feedback-data-structures)
   - [Key Integration Insights](#key-integration-insights)
4. [System Architecture](#system-architecture)
   - [Database Schema](#database-schema)
   - [Data Flow Architecture](#data-flow-architecture)
   - [System Architecture Diagrams](#system-architecture-diagrams)
5. [Priority Scoring Engine (MVP)](#priority-scoring-engine-mvp)
   - [Core Algorithm](#core-algorithm)
   - [Explainable Recommendations](#explainable-recommendations)
6. [Implementation Roadmap](#implementation-roadmap)
   - [Phase 1: Canvas Survey Discovery](#phase-1-canvas-survey-discovery)
   - [Phase 2: Student Response Extraction](#phase-2-student-response-extraction)
   - [Phase 3: Priority Scoring Engine](#phase-3-priority-scoring-engine)
   - [Phase 4: Dashboard Integration](#phase-4-dashboard-integration)
7. [Updated Frontend Architecture](#updated-frontend-architecture)
   - [Component Structure](#component-structure)
   - [API Integration Updates](#api-integration-updates)
8. [Repository Structure](#repository-structure)
9. [Phase 1: Canvas Integration - Actionable Next Steps](#phase-1-canvas-integration---actionable-next-steps)
   - [Immediate Tasks](#immediate-tasks-week-1)
   - [Week 1 Deliverables](#week-1-deliverables)
   - [Canvas API Testing](#canvas-api-testing)
10. [Development Commands](#development-commands)
   - [Backend](#backend)
   - [Frontend](#frontend)
   - [Canvas Integration Testing](#canvas-integration-testing)
11. [Technology Stack](#technology-stack)
12. [Success Metrics](#success-metrics)

## Project Overview

**Course Feedback Aggregation & Priority Intelligence System** - A Canvas-native platform that aggregates student feedback from Canvas course surveys/quizzes into a unified analytics system with intelligent prioritization scoring and explainable recommendations for course improvements.

### Core Mission
Build an explainable prioritization system that extracts student feedback from Canvas course surveys, scores what to "fix" first, and shows the "why" behind each recommendation in a live dashboard with tunable weights.

### Project Pivot Decision
Based on stakeholder meeting (Sep 25, 2024), the project has pivoted to **Canvas-only integration**:
- **Eliminated**: Zoho surveys (contained outdated advisor feedback)
- **Focus**: Canvas surveys provide actual student insights - the valuable data source
- **Technical Discovery**: Course surveys appear as quizzes within Canvas courses
- **Key Advantage**: No manual webhook configuration - scalable API-based solution

## Current Implementation Status

**Last Updated**: October 3, 2025
**Implementation Phase**: Phase 2 Complete (Student Response Extraction) - BLOCKED on Canvas API Issue
**Overall Progress**: ~65% Backend Complete, Frontend Mock Only

### Completed Components

#### 1. Database Layer (Neon PostgreSQL)
- **Status**: COMPLETE - Fully implemented and migrated
- **Schema**: All tables created (courses, canvas_surveys, student_feedback, feedback_responses, course_priorities)
- **Migrations**: Alembic configured with 2 migrations applied
- **Connection**: Async SQLAlchemy 2.0 with asyncpg driver
- **Location**: `apps/backend/app/models/`

#### 2. Canvas API Integration
- **Status**: COMPLETE - Modular client architecture
- **Configuration**: See `.env.example` for required credentials
- **Clients Implemented**:
  - `CanvasBaseClient` - Shared auth, pagination, HTTP logic
  - `CanvasCoursesClient` - Course discovery and metadata
  - `CanvasQuizzesClient` - Quiz/survey discovery and questions
  - `CanvasSubmissionsClient` - Quiz submission extraction (limited for surveys)
  - `CanvasQuizReportsClient` - **NEW**: CSV report generation for complete survey responses
- **Location**: `apps/backend/app/services/canvas/`

#### 3. Survey Discovery System
- **Status**: OPERATIONAL
- **Features**:
  - Detects feedback surveys via title patterns and quiz settings
  - Confidence scoring (0.0-1.0) for survey identification
  - Stores surveys with metadata in database
- **Endpoints**:
  - `GET /quizzes/sync-surveys` - Discover and store surveys
  - `GET /quizzes/surveys` - List identified surveys
- **Location**: `apps/backend/app/api/quizzes.py`

#### 4. Student Response Extraction Pipeline
- **Status**: IMPLEMENTED but BLOCKED (see Critical Issues)
- **Architecture**: Quiz Reports CSV workflow
  1. Generate student_analysis report via Canvas API
  2. Poll for CSV file completion
  3. Download and parse CSV with pandas
  4. Extract individual student responses with essay text
  5. Categorize and store in database
- **Response Processor**:
  - `parse_csv_student_response()` - Handles CSV data structure
  - Text analysis for improvement suggestions
  - Critical issue detection
  - Question categorization (content, instructor, technical, overall)
- **Location**:
  - `apps/backend/app/services/canvas/reports.py`
  - `apps/backend/app/services/response_processor.py`
  - `apps/backend/app/api/feedback.py`

#### 5. Frontend Dashboard (Mock Data)
- **Status**: MOCK DATA ONLY - Not connected to backend
- **React 18 + TypeScript** with Tailwind CSS + shadcn/ui
- **Components**: PriorityRecommendations, CoursesList, DashboardOverview, ScoringControls
- **Mock API integration** with tunable weight sliders

### Missing/Incomplete Components

#### 1. Priority Scoring Engine
- **Status**: NOT IMPLEMENTED
- **Impact**: HIGH - Core business logic missing
- **Dependencies**: Requires working student response extraction
- **Spec Available**: Yes (see Priority Scoring Engine section)
- **Estimated Effort**: 1-2 weeks

#### 2. Feedback Aggregation Service
- **Status**: NOT IMPLEMENTED
- **Impact**: HIGH - Required for priority scoring
- **Features Needed**:
  - Course-level metrics calculation
  - Theme-based categorization
  - Sentiment analysis
- **Estimated Effort**: 1 week

#### 3. Frontend-Backend Integration
- **Status**: NOT STARTED
- **Impact**: MEDIUM - Frontend currently uses mock data
- **Requirements**: Update API client, connect components
- **Estimated Effort**: 3-5 days

### Critical Issues Blocking Progress

#### Issue #1: Canvas Quiz Reports API Returns 500 Error (BLOCKER)

**Problem**: Canvas instance returns `500 Internal Server Error` when attempting to generate Quiz Reports for survey-type quizzes.

**Technical Details**:
```bash
POST https://executiveeducation.instructure.com/api/v1/courses/42/quizzes/481/reports
Response: 500 Internal Server Error
```

**Root Cause**: Survey-type quizzes (`quiz_type: "survey"`, `assignment_id: NULL`) in Canvas LMS have restricted API access to protect student anonymity:

| API Method | Graded Quiz | Survey Quiz | Essay Text Available? |
|------------|-------------|-------------|----------------------|
| Quiz Submissions API | Works - Returns `submission_data` | FAILS - Returns `submission_data: null` | NO |
| Quiz Statistics API | Works - Returns essay text | PARTIAL - Returns user IDs only, NO text | NO |
| **Quiz Reports CSV API** | Works - Full data | **Should work but 500 error** | **BLOCKED** |

**Impact**:
- **CRITICAL** - Without essay text, priority scoring engine cannot function
- Cannot detect improvement suggestions from student feedback
- Cannot identify critical issues or sentiment
- 85 student submissions found but 0 responses extracted

**Evidence**:
```
Test Sync Result:
- Survey: b60da567-3b38-4ae3-8b45-82fc4b28363b (Course Feedback - Quiz 481)
- Status: "error"
- Submissions Found: 0 (due to API failure)
- Responses Parsed: 0
- Error: "Error fetching quiz reports: Server error '500 Internal Server Error'"
```

**Implementation Completed**:
- DONE: Full Quiz Reports CSV workflow implemented
- DONE: CSV parsing with pandas
- DONE: Database schema updated for CSV data structure
- DONE: Response processor handles CSV format
- **BLOCKED waiting for Canvas API fix**

**Next Steps**:
1. **Contact Canvas Administrator** to investigate 500 error
   - Possible causes: Report generation disabled, quota limits, permissions
   - May need Canvas instance configuration changes
2. **Alternative**: Check if pre-generated reports exist
   - Can manually download CSV from Canvas UI
   - Bypass API and import directly (one-time workaround)
3. **Fallback Option**: Use Quiz Statistics API (partial data)
   - Gets multiple choice responses but NO essay text
   - 60% solution - better than nothing but loses critical data

**Code Ready**: Once Canvas API issue is resolved, sync endpoint should work immediately. No additional development needed.

**Developer Handoff Notes**:
- Implementation follows Canvas API documentation exactly
- Error is Canvas instance-specific, not code issue
- See `apps/backend/app/services/canvas/reports.py` for implementation
- Test endpoint: `POST /feedback/sync/{survey_id}`

## Canvas Survey Data Architecture

Canvas course surveys are implemented as quizzes within Canvas courses. Our system identifies and extracts student feedback from these quiz submissions using the Canvas API.

### Canvas API Endpoints

#### Course & Quiz Discovery
```http
GET /api/v1/courses
GET /api/v1/courses/{course_id}/quizzes
GET /api/v1/courses/{course_id}/quizzes/{quiz_id}
GET /api/v1/courses/{course_id}/quizzes/{quiz_id}/questions
```

#### Student Response Extraction
```http
GET /api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions
GET /api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{id}?include[]=submission_history
GET /api/v1/quiz_submissions/{quiz_submission_id}/questions
```

**Note:** Student answers are retrieved via `submission_data` property when using `include[]=submission_history` parameter (recommended) or via the Quiz Submission Questions API endpoint.

### Survey Detection Logic

Identifying which Canvas quizzes are actually course feedback surveys:

```python
def identify_feedback_surveys(quizzes: List[Dict]) -> List[Dict]:
    """
    Identify Canvas quizzes that are actually course feedback surveys
    Based on title patterns, question types, and quiz settings
    """
    feedback_patterns = [
        'course evaluation', 'course feedback', 'course review',
        'satisfaction survey', 'course rating', 'end of course',
        'student feedback', 'course survey', 'evaluation'
    ]

    feedback_surveys = []
    for quiz in quizzes:
        title_lower = quiz.get('title', '').lower()

        # Check title patterns
        if any(pattern in title_lower for pattern in feedback_patterns):
            # Additional validation checks
            if is_likely_feedback_survey(quiz):
                feedback_surveys.append({
                    **quiz,
                    'identified_as': 'feedback_survey',
                    'confidence': calculate_survey_confidence(quiz)
                })

    return feedback_surveys

def is_likely_feedback_survey(quiz: Dict) -> bool:
    """Additional validation for survey identification"""
    # Check if quiz is ungraded (typical for feedback surveys)
    if quiz.get('points_possible') == 0:
        return True

    # Check quiz type
    if quiz.get('quiz_type') in ['survey', 'graded_survey']:
        return True

    # Check if it's anonymous (common for feedback)
    if quiz.get('anonymous_submissions', False):
        return True

    return False
```

### Student Feedback Data Structures

**Canvas Quiz/Survey Structure**:
```json
{
  "id": 12345,
  "title": "End of Course Evaluation - Spring 2024",
  "quiz_type": "survey",
  "points_possible": 0,
  "anonymous_submissions": true,
  "question_count": 15,
  "published": true,
  "assignment_id": 67890,
  "course_id": 1234
}
```

**Student Feedback Response Structure**:
```json
{
  "submission_id": 987654,
  "quiz_id": 12345,
  "user_id": null,  // Anonymous submission
  "submitted_at": "2024-03-15T14:30:00Z",
  "attempt": 1,
  "workflow_state": "complete",
  "score": null,  // Ungraded survey
  "quiz_submission_questions": [
    {
      "id": 1,
      "question_text": "How would you rate the overall course content?",
      "question_type": "multiple_choice_question",
      "answer": "4",
      "answer_text": "Very Good"
    },
    {
      "id": 2,
      "question_text": "What aspects of the course were most valuable?",
      "question_type": "essay_question",
      "answer": "The practical case studies and group discussions were extremely helpful. The instructor's real-world examples made complex concepts easier to understand."
    },
    {
      "id": 3,
      "question_text": "What improvements would you suggest?",
      "question_type": "essay_question",
      "answer": "The pace was too fast in Module 3. More time for hands-on exercises would be beneficial. Also, the video quality in some lectures was poor."
    },
    {
      "id": 4,
      "question_text": "Rate the instructor's effectiveness",
      "question_type": "numerical_question",
      "answer": "4.5"
    }
  ]
}

**Processed Feedback Structure**:
```python
@dataclass
class CanvasStudentFeedback:
    submission_id: int
    course_id: int
    course_name: str
    quiz_id: int
    survey_title: str
    student_id: Optional[int]  # May be anonymous
    submitted_at: datetime
    response_data: Dict[str, Any]  # Raw Canvas response

    # Processed feedback sections
    ratings: Dict[str, int]  # Question ID -> rating score
    text_responses: Dict[str, str]  # Question ID -> text response
    multiple_choice: Dict[str, str]  # Question ID -> selected choice

    # Categorized feedback
    course_content_rating: Optional[int]
    instructor_rating: Optional[int]
    technical_issues: List[str]
    improvement_suggestions: List[str]
    critical_issues: List[str]  # Flagged as urgent
```

### Key Integration Insights

1. **Survey Identification**: Canvas quizzes used for feedback typically have `quiz_type: 'survey'`, zero points, and titles containing "evaluation", "feedback", or "survey"

2. **Anonymous Responses**: Most course feedback surveys have `anonymous_submissions: true`, resulting in `user_id: null` in submissions

3. **Question Categorization**: Feedback questions can be automatically categorized based on keywords:
   - **Course Content**: "content", "materials", "curriculum", "topics"
   - **Instructor**: "instructor", "teaching", "presentation", "facilitator"
   - **Technical**: "platform", "video", "audio", "technical", "access"
   - **Overall**: "overall", "general", "course rating"

4. **Critical Issue Detection**: Text responses containing keywords like "broken", "cannot access", "crashes", "urgent" should be flagged as critical

5. **Response Volume Metrics**: Canvas API provides total enrollment counts, enabling calculation of response rates for priority weighting

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

-- Canvas surveys/quizzes that contain feedback
CREATE TABLE canvas_surveys (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id INTEGER REFERENCES courses(id),
    canvas_quiz_id INTEGER NOT NULL,
    survey_title VARCHAR(255) NOT NULL,
    quiz_type VARCHAR(50), -- 'survey', 'graded_survey', 'practice_quiz'
    is_anonymous BOOLEAN DEFAULT FALSE,
    points_possible INTEGER DEFAULT 0,
    question_count INTEGER,
    response_count INTEGER DEFAULT 0,
    identification_confidence DECIMAL(3,2), -- How confident we are this is feedback
    created_at TIMESTAMP DEFAULT NOW(),
    last_synced TIMESTAMP,
    UNIQUE(course_id, canvas_quiz_id)
);

-- Student feedback responses from Canvas
CREATE TABLE student_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    canvas_survey_id UUID REFERENCES canvas_surveys(id),
    course_id INTEGER REFERENCES courses(id),
    canvas_submission_id INTEGER NOT NULL,
    student_canvas_id INTEGER, -- May be NULL for anonymous
    submitted_at TIMESTAMP,
    attempt_number INTEGER DEFAULT 1,
    workflow_state VARCHAR(50), -- 'complete', 'pending_review', etc.
    raw_response_data JSONB NOT NULL, -- Full Canvas submission data
    processed_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(canvas_survey_id, canvas_submission_id)
);

-- Individual question responses from student feedback
CREATE TABLE feedback_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_feedback_id UUID REFERENCES student_feedback(id) ON DELETE CASCADE,
    canvas_question_id INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50), -- 'multiple_choice_question', 'essay_question', 'numerical_question'
    response_text TEXT, -- For essay/text responses
    response_numeric DECIMAL(10,2), -- For numerical responses (ratings)
    selected_answer_text VARCHAR(500), -- For multiple choice
    question_category VARCHAR(100), -- Auto-categorized: 'course_content', 'instructor', 'technical', etc.
    sentiment_score DECIMAL(3,2), -- Future: AI sentiment analysis
    contains_improvement_suggestion BOOLEAN DEFAULT FALSE,
    is_critical_issue BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Course priority scores (enhanced for Canvas data)
CREATE TABLE course_priorities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    course_id INTEGER REFERENCES courses(id) UNIQUE,
    priority_score DECIMAL(5,4), -- 0.0000 to 1.0000
    impact_score DECIMAL(5,4),
    urgency_score DECIMAL(5,4),
    effort_score DECIMAL(5,4),
    recency_score DECIMAL(5,4),

    -- Canvas-specific metrics
    total_student_responses INTEGER DEFAULT 0,
    student_response_rate DECIMAL(3,2), -- Responses / total students
    average_course_rating DECIMAL(3,2), -- Average across rating questions
    critical_issues_count INTEGER DEFAULT 0,
    improvement_suggestions_count INTEGER DEFAULT 0,

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

-- Indexes for performance
CREATE INDEX idx_canvas_surveys_course_id ON canvas_surveys(course_id);
CREATE INDEX idx_student_feedback_survey_id ON student_feedback(canvas_survey_id);
CREATE INDEX idx_feedback_responses_student_feedback_id ON feedback_responses(student_feedback_id);
CREATE INDEX idx_course_priorities_score ON course_priorities(priority_score DESC);
CREATE INDEX idx_feedback_responses_category ON feedback_responses(question_category);
CREATE INDEX idx_canvas_surveys_quiz_id ON canvas_surveys(canvas_quiz_id);
CREATE INDEX idx_student_feedback_course_id ON student_feedback(course_id);
```

### Data Flow Architecture

#### Primary Data Pipeline
```mermaid
graph LR
    A[Canvas Courses API] --> B[Course Discovery]
    B --> C[Survey Detection]
    C --> D[Student Response Extraction]
    D --> E[Response Processing & Categorization]
    E --> F[Priority Scoring Engine]
    F --> G[Dashboard Analytics]

    H[Canvas Quiz API] --> C
    I[Canvas Submissions API] --> D
```

#### Detailed Processing Flow
1. **Course & Survey Discovery**
   - Canvas courses retrieved via API (`/api/v1/courses`)
   - Quiz discovery and survey identification within courses
   - Survey metadata stored with confidence scores

2. **Student Response Extraction**
   - Quiz submissions retrieved (`/api/v1/courses/{id}/quizzes/{id}/submissions`)
   - Anonymous and identified student responses processed
   - Raw Canvas data stored for audit trail

3. **Response Processing & Categorization**
   - Individual questions and answers extracted and categorized
   - Text analysis for improvement suggestions and critical issues
   - Question types classified (content, instructor, technical, overall)

4. **Intelligence Layer**
   - Priority score calculation optimized for student feedback metrics
   - Theme-based improvement categorization and effort estimation
   - Real-time score updates when new student responses arrive

5. **User Interface**
   - Canvas-native dashboard with student feedback insights
   - Response rate and participation metrics
   - Drill-down to individual student responses and themes

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

    CANVAS_SURVEYS {
        uuid id PK
        int course_id FK
        int canvas_quiz_id
        string survey_title
        string quiz_type
        boolean is_anonymous
        int points_possible
        decimal identification_confidence
    }

    STUDENT_FEEDBACK {
        uuid id PK
        uuid canvas_survey_id FK
        int course_id FK
        int canvas_submission_id
        int student_canvas_id
        timestamp submitted_at
        jsonb raw_response_data
    }

    FEEDBACK_RESPONSES {
        uuid id PK
        uuid student_feedback_id FK
        int canvas_question_id
        string question_text
        string question_type
        text response_text
        decimal response_numeric
        string question_category
        boolean is_critical_issue
    }

    COURSE_PRIORITIES {
        uuid id PK
        int course_id FK
        decimal priority_score
        decimal impact_score
        decimal urgency_score
        decimal effort_score
        decimal recency_score
        int total_student_responses
        decimal student_response_rate
        int critical_issues_count
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

    COURSES ||--o{ CANVAS_SURVEYS : "contains surveys"
    COURSES ||--o{ COURSE_PRIORITIES : "has priority"
    COURSES ||--o{ STUDENT_FEEDBACK : "receives feedback"
    CANVAS_SURVEYS ||--o{ STUDENT_FEEDBACK : "generates responses"
    STUDENT_FEEDBACK ||--o{ FEEDBACK_RESPONSES : "contains answers"
```

#### Component Architecture
```mermaid
graph TB
    subgraph "External Systems"
        CL[Canvas LMS]
    end

    subgraph "Canvas Integration"
        CA[Canvas API Client]
        SD[Survey Discovery]
        RE[Response Extraction]
    end

    subgraph "FastAPI Backend"
        API[API Router]
        CS[Canvas Service]
        SS[Survey Service]
        FS[Feedback Service]
        PS[Priority Service]
        TS[Theme Service]
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
        TC[Theme Categorizer]
        WM[Weight Manager]
    end

    CL --> CA
    CA --> SD
    CA --> RE
    SD --> SS
    RE --> FS

    SS --> API
    FS --> API
    CS --> API
    PS --> API
    TS --> API

    SS --> DB
    FS --> DB
    PS --> DB

    FS --> TC
    PS --> PE
    PE --> EG
    TC --> PE
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
            WK[Canvas Sync Workers]
        end

        subgraph "Neon"
            DB[(PostgreSQL Database)]
            BR[Database Branches]
        end

        subgraph "External APIs"
            CA[Canvas API]
        end
    end

    subgraph "Development"
        DEV[Local Development]
        TEST[Canvas API Testing]
    end

    FE <--> BE
    BE <--> DB
    BE --> CA
    DEV --> TEST
    TEST --> CA
```

## Algorithmic Approach & Evolution Strategy

### Key Principle: Iterative Refinement
All algorithms in this system are **reference implementations** designed to evolve. We expect significant refinement based on:

1. **Data-Driven Calibration**: Real Canvas API responses will reveal actual data patterns
2. **Stakeholder Feedback**: Priority accuracy will be validated by course administrators
3. **Pattern Recognition**: Machine learning enhancements in future phases
4. **Performance Metrics**: Algorithm effectiveness measured against improvement outcomes

### Algorithm Evolution Pipeline
```
Initial Implementation (Week 1-2)
  ↓ Canvas Data Collection
  ↓ Pattern Analysis
  ↓ Algorithm Refinement
  ↓ Stakeholder Validation
  ↓ Production Deployment
  ↓ Continuous Improvement
```

## Priority Scoring Engine (Reference Implementation)

**Note**: These algorithms are starting points that will be refined through real-world usage.

### Core Algorithm (Subject to Evolution)

```python
def calculate_canvas_priority_score(course_id: int, weights: Dict = None) -> Dict:
    """
    REFERENCE IMPLEMENTATION - Will be tuned with real data
    Enhanced priority scoring for Canvas student feedback
    Emphasizes direct student insights over proxy metrics
    """
    if weights is None:
        weights = get_active_weights()

    course_data = get_canvas_feedback_summary(course_id)

    # 1. IMPACT: Student participation and feedback volume
    response_rate = course_data.student_responses / max(course_data.total_students, 1)
    participation_impact = min(response_rate * 2, 1.0)  # Higher weight for participation

    # Feedback density (responses with actionable content)
    feedback_density = course_data.responses_with_suggestions / max(course_data.student_responses, 1)
    impact_score = min(participation_impact + (feedback_density * 0.3), 1.0)

    # 2. URGENCY: Poor ratings and critical issues from students
    rating_urgency = 0.0
    if course_data.average_course_rating:
        rating_urgency = max(0, (3.0 - course_data.average_course_rating) / 2.0)

    # Critical issues reported by students
    critical_issues_ratio = course_data.critical_issues / max(course_data.student_responses, 1)
    urgency_score = min(rating_urgency + (critical_issues_ratio * 0.6), 1.0)

    # 3. EFFORT: Categorized by student feedback themes
    effort_analysis = categorize_canvas_improvement_themes(course_id)
    effort_score = 1.0 - calculate_implementation_effort(effort_analysis)

    # 4. RECENCY: Recent course runs and feedback
    days_since_feedback = (datetime.now() - course_data.last_feedback_date).days
    recency_score = max(0, 1.0 - (days_since_feedback / 90))  # 90-day decay

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

        # Canvas-specific metrics
        "student_response_rate": response_rate,
        "total_student_responses": course_data.student_responses,
        "average_course_rating": course_data.average_course_rating,
        "critical_issues_count": course_data.critical_issues,

        "explanation": generate_canvas_explanation(
            course_data, impact_score, urgency_score, effort_score, recency_score
        ),
        "top_improvement_themes": get_top_improvement_themes(course_id),
        "student_sentiment_summary": calculate_sentiment_summary(course_id)
    }

def categorize_canvas_improvement_themes(course_id: int) -> Dict:
    """
    Categorize student feedback themes for effort estimation
    Based on actual student feedback patterns from Canvas
    """
    feedback_responses = get_course_feedback_responses(course_id)

    themes = {
        "content_updates": 0,      # Outdated materials, missing content
        "instructional_clarity": 0, # Confusing explanations, pace issues
        "technical_platform": 0,   # Canvas issues, video problems, access
        "assessment_design": 0,     # Assignment clarity, grading rubrics
        "interaction_engagement": 0, # Discussion, peer interaction, activities
        "structural_redesign": 0    # Fundamental course restructuring needs
    }

    # Analyze student responses for themes
    for response in feedback_responses:
        text = response.response_text.lower() if response.response_text else ""

        if any(word in text for word in ["outdated", "old", "current", "update", "recent"]):
            themes["content_updates"] += 1
        elif any(word in text for word in ["confusing", "unclear", "fast", "slow", "pace"]):
            themes["instructional_clarity"] += 1
        elif any(word in text for word in ["canvas", "video", "audio", "technical", "broken", "access"]):
            themes["technical_platform"] += 1
        elif any(word in text for word in ["assignment", "rubric", "grading", "criteria", "unclear"]):
            themes["assessment_design"] += 1
        elif any(word in text for word in ["discussion", "interaction", "engage", "boring", "active"]):
            themes["interaction_engagement"] += 1
        elif any(word in text for word in ["redesign", "restructure", "completely", "overhaul", "redo"]):
            themes["structural_redesign"] += 1

    return themes

def calculate_implementation_effort(themes: Dict) -> float:
    """
    Estimate implementation effort based on student feedback themes
    Returns 0.0 (easy) to 1.0 (very difficult)
    """
    effort_weights = {
        "content_updates": 0.2,        # Relatively easy content fixes
        "instructional_clarity": 0.3,   # Moderate - requires instructional design
        "assessment_design": 0.4,       # Moderate-high - rubric and assignment redesign
        "interaction_engagement": 0.5,  # High - requires activity redesign
        "technical_platform": 0.6,     # High - requires IT support
        "structural_redesign": 0.9      # Very high - complete course overhaul
    }

    total_issues = sum(themes.values())
    if total_issues == 0:
        return 0.1  # Minimal effort if no specific themes identified

    weighted_effort = sum(count * effort_weights[theme] for theme, count in themes.items())
    return min(weighted_effort / total_issues, 1.0)
```

### Explainable Recommendations

```python
def generate_canvas_explanation(course_data, impact, urgency, effort, recency) -> str:
    """Generate human-readable explanation for Canvas student feedback priority score"""
    explanations = []

    # Student participation impact
    if impact > 0.7:
        response_rate = course_data.student_responses / max(course_data.total_students, 1)
        explanations.append(f"High student engagement: {response_rate:.1%} response rate with actionable feedback")

    # Urgency from student concerns
    if urgency > 0.6:
        if course_data.critical_issues > 0:
            explanations.append(f"Critical student issues: {course_data.critical_issues} urgent problems reported")
        if course_data.average_course_rating < 3.0:
            explanations.append(f"Poor student satisfaction: {course_data.average_course_rating:.1f}/5 average rating")

    # Implementation effort
    if effort > 0.7:
        explanations.append("Quick wins: Student suggestions focus on easily addressable improvements")
    elif effort < 0.3:
        explanations.append("Complex improvements: Student feedback indicates major structural changes needed")

    # Recent student feedback
    if recency > 0.8:
        explanations.append("Current concerns: Recent student feedback shows ongoing course issues")

    # Student sentiment summary
    if hasattr(course_data, 'sentiment_breakdown'):
        positive_ratio = course_data.sentiment_breakdown.get('positive', 0) / max(course_data.student_responses, 1)
        if positive_ratio < 0.4:
            explanations.append(f"Negative sentiment: Only {positive_ratio:.1%} of student feedback is positive")

    return "; ".join(explanations) if explanations else "Standard priority based on student feedback patterns"
```

## Implementation Roadmap

### Phase 1: Canvas Survey Discovery (Week 1)
**Goal**: Build Canvas course and survey detection system

**Tasks**:
- [ ] Implement Canvas API client with proper authentication
- [ ] Build course discovery and metadata extraction
- [ ] Create survey identification algorithm (quiz title patterns, settings)
- [ ] Implement survey confidence scoring
- [ ] Build database models for Canvas surveys and courses

**Deliverables**:
- Working Canvas API client with full authentication
- Survey discovery endpoint that identifies feedback surveys
- Database persistence for discovered courses and surveys
- Basic admin interface showing discovered surveys

**Acceptance Criteria**:
- Canvas API client successfully authenticates and retrieves course data
- Survey discovery identifies 80%+ of actual feedback surveys in test courses
- Database stores discovered courses and surveys with proper relationships
- Admin interface shows discovered surveys with confidence scores

### Phase 2: Student Response Extraction (Week 2)
**Goal**: Extract and process student feedback from Canvas quizzes

**Tasks**:
- [ ] Build Canvas quiz submission extraction
- [ ] Implement response parsing and categorization
- [ ] Create student feedback processing pipeline
- [ ] Build question categorization system (content, instructor, technical)
- [ ] Implement basic text analysis for improvement suggestions

**Deliverables**:
- Student response extraction from Canvas quiz submissions
- Structured feedback storage with categorization
- Response processing pipeline with error handling
- Data validation and deduplication system

**Acceptance Criteria**:
- Student response extraction works for all identified feedback surveys
- Response processing categorizes questions and answers correctly
- Text analysis identifies improvement themes in student feedback
- Database stores structured student feedback with proper categorization

### Phase 3: Priority Scoring Engine (Week 3)
**Goal**: Implement Canvas-optimized priority scoring

**Tasks**:
- [ ] Build priority calculation engine for Canvas data
- [ ] Implement theme-based effort estimation
- [ ] Create explanation generation system
- [ ] Build priority score caching and updates
- [ ] Add weight configuration management

**Deliverables**:
- Priority scores for all courses with student feedback
- Explainable recommendations with theme analysis
- Tunable weight system with real-time recalculation
- Priority score explanations and improvement themes

**Acceptance Criteria**:
- Priority scores calculated for all courses with student feedback
- Explanations clearly show why courses are prioritized based on student input
- Weight adjustments update priorities in real-time
- Theme analysis provides actionable improvement categories

### Phase 4: Dashboard Integration (Week 4)
**Goal**: Connect frontend to Canvas data pipeline

**Tasks**:
- [ ] Update frontend components for Canvas data structure
- [ ] Build course feedback detail views
- [ ] Implement priority explanation displays
- [ ] Add student response rate and participation metrics
- [ ] Create Canvas sync status and health monitoring

**Deliverables**:
- Dashboard displaying real Canvas course feedback
- Priority recommendations with student-focused explanations
- Course-level feedback analysis with theme breakdown
- Admin interface for Canvas sync management

**Acceptance Criteria**:
- Dashboard displays real Canvas student feedback data
- Users can drill down from priority scores to specific student responses
- Canvas sync status shows health and last update information
- System scales to handle multiple courses with hundreds of student responses

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
│   │   │   │   ├── canvas.py        # Canvas sync endpoints
│   │   │   │   └── surveys.py       # Survey discovery and validation
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
│   │   │   │   ├── canvas/          # Canvas API integration (separated by resource)
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── base.py      # Shared auth, pagination, HTTP logic
│   │   │   │   │   ├── courses.py   # Courses API methods
│   │   │   │   │   ├── quizzes.py   # Quizzes API methods
│   │   │   │   │   └── submissions.py # Submissions API methods
│   │   │   │   ├── survey_service.py      # Survey detection logic
│   │   │   │   ├── feedback_service.py    # Feedback processing
│   │   │   │   ├── priority_service.py    # Priority calculation
│   │   │   │   └── attribution_service.py # Course attribution
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

## Phase 1: Canvas Integration Foundation - Actionable Next Steps

### Immediate Tasks (Week 1)

#### 1. Canvas API Client Setup
```bash
# Test Canvas API connectivity
cd apps/backend
python -c "import httpx; r = httpx.get('https://your-canvas-instance.instructure.com/api/v1/courses',
  headers={'Authorization': 'Bearer YOUR_CANVAS_API_TOKEN'});
  print(f'Connected: {r.status_code == 200}')"
```

#### 2. Database & Backend Structure Setup
```bash
cd apps/backend

# Create new directory structure
mkdir -p app/{models,schemas,services,api,core,utils,canvas}
touch app/{models,schemas,services,api,core,utils,canvas}/__init__.py

# Initialize Alembic for migrations
pip install alembic sqlalchemy asyncpg httpx
alembic init alembic
```

#### 3. Canvas Integration Models
Create the following files in order:

**Priority 1: Canvas Models**
- `app/models/course.py` - Canvas course data
- `app/models/canvas_survey.py` - Canvas quiz/survey model
- `app/models/student_feedback.py` - Student response model
- `app/models/feedback_response.py` - Individual question responses
- `app/models/priority.py` - Priority scores

**Priority 2: Canvas Service Layer**
- `app/canvas/client.py` - Canvas API client wrapper
- `app/services/canvas_service.py` - Canvas data synchronization
- `app/services/survey_service.py` - Survey detection logic
- `app/services/response_service.py` - Response extraction

#### 4. First Migration & Canvas Sync
```bash
# Generate initial migration
alembic revision --autogenerate -m "Canvas integration schema"

# Apply migration
alembic upgrade head

# Test Canvas course discovery
python -m app.canvas.client --discover-courses
```

#### 5. Survey Detection Implementation
Create survey detection service:
- `app/services/survey_detector.py` - Implement reference algorithm
- `app/api/canvas.py` - Canvas sync endpoints
- `app/schemas/canvas.py` - Pydantic models for Canvas data

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

**New Directories to Create:**
1. `app/canvas/` - Canvas-specific integration code
2. `app/models/` - SQLAlchemy ORM models
3. `app/schemas/` - Pydantic validation schemas
4. `app/services/` - Business logic services
5. `app/core/` - Core configuration and database setup

**Files to Remove/Archive:**
1. Remove `app/api/zoho/` directory (no longer needed)
2. Archive webhook endpoints (may repurpose for Canvas webhooks later)

**Environment Variables to Add:**
```env
# Add to apps/backend/.env
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/coursefeedback
CANVAS_API_TOKEN=your_canvas_api_token_here
CANVAS_BASE_URL=https://your-canvas-instance.instructure.com
CANVAS_SYNC_INTERVAL_HOURS=24  # How often to sync Canvas data
SURVEY_CONFIDENCE_THRESHOLD=0.7  # Minimum confidence for survey identification

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