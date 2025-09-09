# Course Feedback Aggregator

**Intelligent Course Improvement Prioritization System**

A comprehensive platform that unifies course feedback from Canvas LMS and Zoho surveys into a single database with intelligent 5-point prioritization scoring. The system provides explainable recommendations for course improvements with full traceability back to original feedback sources.

## 🎯 Mission Statement

Build a single, explainable prioritization system that pulls course feedback from Canvas and Zoho into one database, scores what to "fix" first using a 5-point scale, and shows the "why" behind each recommendation in a live dashboard.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Canvas LMS    │    │  Zoho CRM       │    │   Frontend      │
│     API         │    │   Survey API    │    │   React App     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
          ┌─────────────────────────────────────────────┐
          │           FastAPI Backend                   │
          │  ┌─────────────┐  ┌─────────────────────┐   │
          │  │ Ingestion   │  │   5-Point Scoring   │   │
          │  │ Services    │  │   Engine            │   │
          │  │             │  │   - Impact (40%)    │   │
          │  └─────────────┘  │   - Urgency (35%)   │   │
          │                   │   - Effort (25%)    │   │
          │  ┌─────────────┐  └─────────────────────┘   │
          │  │   API       │                            │
          │  │  Routes     │                            │
          │  └─────────────┘                            │
          └─────────────────┬───────────────────────────┘
                            │
          ┌─────────────────┴───────────────────────────┐
          │        Neon PostgreSQL Database             │
          │  ┌─────────┐ ┌─────────┐ ┌─────────────┐   │
          │  │feedback │ │priorities│ │weight_configs│  │
          │  └─────────┘ └─────────┘ └─────────────┘   │
          │  ┌─────────────────┐                       │
          │  │    reviews      │                       │
          │  └─────────────────┘                       │
          └─────────────────────────────────────────────┘
```

## 🎛️ Priority Tuning System

### **Dynamic Weight Configuration**
The system allows administrators to tune priority calculations in real-time based on their current context and institutional needs.

#### **Scoring Categories Explained**

**1. Impact (Student Effect)**
- **What it measures**: How many students are affected and severity of impact
- **High Impact (5)**: "23 students can't complete Module 3 assignment"
- **Medium Impact (3)**: "8 students confused about video content"
- **Low Impact (1)**: "2 students want optional reading materials"

**2. Urgency (Time Sensitivity)**
- **What it measures**: Time sensitivity and course flow disruption
- **High Urgency (5)**: "Assignment due tomorrow but instructions are broken"
- **Medium Urgency (3)**: "Video content needs updating before next semester"
- **Low Urgency (1)**: "Course description could be more engaging"

**3. Effort (Fix Complexity - Inverted)**
- **What it measures**: How easy/hard it is to fix (quick wins score higher)
- **Low Effort/High Score (5)**: "Fix typo in assignment instructions" (2 minutes)
- **Medium Effort (3)**: "Update video with current software version" (2 hours)
- **High Effort/Low Score (1)**: "Redesign entire module structure" (2 weeks)

**4. Strategic (Course Alignment)**
- **What it measures**: Alignment with course goals and institutional priorities
- **High Strategic (5)**: "Core learning objective isn't being met"
- **Medium Strategic (3)**: "Assessment doesn't align with course goals"
- **Low Strategic (1)**: "Nice-to-have feature request"

**5. Trend (Issue Trajectory)**
- **What it measures**: Whether the issue is getting worse or better over time
- **High Trend (5)**: "Complaints increasing each week"
- **Medium Trend (3)**: "Consistent feedback over time"
- **Low Trend (1)**: "Only reported once recently"

#### **Use Case Scenarios**

**Crisis Mode (Semester Starting Soon)**
```
Urgency: 5/5    Impact: 4/5    Effort: 2/5    Strategic: 1/5    Trend: 1/5
Result: Critical technical issues prioritized regardless of fix complexity
```

**Strategic Planning (Between Semesters)**
```
Strategic: 5/5    Trend: 4/5    Impact: 3/5    Effort: 4/5    Urgency: 1/5
Result: Long-term improvements with good ROI rise to top
```

**Quick Wins for Morale**
```
Effort: 5/5    Impact: 4/5    Urgency: 2/5    Strategic: 2/5    Trend: 1/5
Result: Simple fixes that make students happy get prioritized
```

#### **Real-time Tuning Workflow**
1. **View Current Priorities**: See recommendations with default weights
2. **Adjust Sliders**: Drag weight sliders based on current needs
3. **Instant Preview**: Watch priority scores update in real-time
4. **Recompute Scores**: Save new weights and apply to all recommendations
5. **Review Changes**: See how the priority list reordered

## 📊 Database Schema & ERD

### Core Tables

#### 1. `feedback` - Unified Feedback Storage
```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    course_id VARCHAR(50) NOT NULL,           -- "canvas_847" or "zoho_ai_program"
    course_name VARCHAR(255) NOT NULL,
    student_email VARCHAR(255),
    student_name VARCHAR(255),
    feedback_text TEXT,
    rating REAL CHECK (rating >= 1 AND rating <= 5),  -- 1-5 normalized scale
    severity VARCHAR(20),                      -- critical/high/medium/low
    source VARCHAR(10) NOT NULL,              -- "canvas" or "zoho"
    source_id VARCHAR(100),                   -- Original ID for provenance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- Indexes for performance
CREATE INDEX idx_feedback_course_id ON feedback(course_id);
CREATE INDEX idx_feedback_source ON feedback(source);
CREATE INDEX idx_feedback_severity ON feedback(severity);
```

#### 2. `priorities` - Computed Priority Recommendations
```sql
CREATE TABLE priorities (
    id SERIAL PRIMARY KEY,
    course_id VARCHAR(50) NOT NULL,
    issue_summary TEXT NOT NULL,
    priority_score INTEGER CHECK (priority_score >= 1 AND priority_score <= 5),  -- 5-point scale
    impact_score REAL CHECK (impact_score >= 1 AND impact_score <= 5),
    urgency_score REAL CHECK (urgency_score >= 1 AND urgency_score <= 5),
    effort_score REAL CHECK (effort_score >= 1 AND effort_score <= 5),
    students_affected INTEGER DEFAULT 0,
    feedback_ids JSON,                        -- Array of contributing feedback IDs
    evidence JSON,                            -- Student quotes and source links
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for priority querying
CREATE INDEX idx_priorities_score ON priorities(priority_score DESC);
CREATE INDEX idx_priorities_course ON priorities(course_id);
```

#### 3. `weight_configs` - Tunable Scoring Parameters
```sql
CREATE TABLE weight_configs (
    id SERIAL PRIMARY KEY,
    impact_weight REAL DEFAULT 0.40,         -- Student impact focus
    urgency_weight REAL DEFAULT 0.35,        -- Time-sensitive issues
    effort_weight REAL DEFAULT 0.25,         -- Quick wins preference
    strategic_weight REAL DEFAULT 0.15,      -- Course goal alignment
    trend_weight REAL DEFAULT 0.10,          -- Issue trajectory
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255)                  -- Admin who changed weights
);
```

#### 4. `reviews` - Validation & Action Tracking
```sql
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    priority_id INTEGER REFERENCES priorities(id),
    reviewer_name VARCHAR(255) NOT NULL,
    validated BOOLEAN DEFAULT false,
    action_taken VARCHAR(50),                -- "implemented", "rejected", "deferred"
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Entity Relationship Diagram

```
┌─────────────┐    1:N    ┌─────────────┐    1:N    ┌─────────────┐
│  feedback   │ ◄───────► │ priorities  │ ◄───────► │   reviews   │
│             │           │             │           │             │
│ • course_id │           │ • issue_sum │           │ • validated │
│ • rating    │           │ • score(1-5)│           │ • notes     │
│ • severity  │           │ • evidence  │           │ • action    │
│ • source    │           │             │           │             │
└─────────────┘           └─────────────┘           └─────────────┘
                                 │
                                 │ uses
                                 ▼
                          ┌─────────────┐
                          │weight_config│
                          │             │
                          │ • impact:40%│
                          │ • urgency:35│
                          │ • effort:25%│
                          │ • strategic │
                          │ • trend     │
                          └─────────────┘
```

## 🔄 Data Flow Process

### 1. **Data Ingestion**
```python
# Canvas LMS → Unified Format
canvas_feedback = {
    "course_id": "canvas_847",
    "feedback_text": "Video content is inconsistent",
    "rating": 3.2,  # Normalized to 1-5
    "severity": "high",
    "source": "canvas",
    "source_id": "assignment_123"
}

# Zoho CRM → Unified Format  
zoho_feedback = {
    "course_id": "zoho_ai_program", 
    "feedback_text": "Need more practical examples",
    "rating": 4.1,
    "severity": "medium",
    "source": "zoho",
    "source_id": "contact_456"
}
```

### 2. **Priority Scoring (5-Point Scale)**
```python
def calculate_priority_score(feedback_group, weights):
    # Aggregate feedback for similar issues
    impact = calculate_impact(students_affected, avg_severity)      # 1-5
    urgency = calculate_urgency(show_stoppers, course_timeline)     # 1-5
    effort = calculate_effort(issue_complexity, fix_difficulty)     # 1-5
    strategic = calculate_strategic(course_goals, institutional)    # 1-5
    trend = calculate_trend(historical_frequency)                   # 1-5
    
    # Weighted calculation using admin-tuned weights
    weighted_score = (
        impact * weights.impact_weight +      # Default: 40%
        urgency * weights.urgency_weight +    # Default: 35%
        (6 - effort) * weights.effort_weight + # Default: 25% (inverted)
        strategic * weights.strategic_weight + # Default: 15%
        trend * weights.trend_weight          # Default: 10%
    )
    
    return round(weighted_score)  # Returns 1-5
```

### 3. **Priority Levels**
```python
PRIORITY_LEVELS = {
    5: {"label": "CRITICAL", "action": "Fix immediately", "color": "red"},
    4: {"label": "HIGH",     "action": "Fix this week",  "color": "orange"}, 
    3: {"label": "MEDIUM",   "action": "Fix this month", "color": "yellow"},
    2: {"label": "LOW",      "action": "Consider fixing", "color": "blue"},
    1: {"label": "MINIMAL",  "action": "Monitor only",   "color": "gray"}
}
```

## 🚀 Technology Stack

### Backend (FastAPI)
- **Framework**: FastAPI 0.104.1
- **Database**: Neon PostgreSQL (serverless)
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: API token-based
- **Deployment**: Railway

### Frontend (React)
- **Framework**: React 18 + TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: Zustand
- **Deployment**: Vercel

### External APIs
- **Canvas LMS API**: Course evaluations, discussions, assignments
- **Zoho CRM API**: Survey responses, course ratings

## 📁 Project Structure

```
CourseFeedbackAggregator/
├── apps/
│   ├── frontend/                 # React dashboard
│   │   ├── src/
│   │   │   ├── components/       # UI components
│   │   │   ├── services/        # API clients
│   │   │   └── types/           # TypeScript definitions
│   │   └── package.json
│   └── backend/                  # FastAPI service
│       ├── .env                  # API credentials
│       ├── requirements.txt      # Python dependencies
│       └── app/
│           ├── main.py          # FastAPI app
│           ├── config.py        # Settings
│           ├── database.py      # Models & DB
│           ├── api/             # Route handlers
│           ├── clients/         # Canvas/Zoho APIs
│           └── scoring/         # Priority engine
├── dev-kit/
│   ├── testing/                  # API discovery scripts
│   │   ├── canvas/              # Canvas API tests
│   │   └── zoho/                # Zoho API tests
│   └── research/                # Integration guides
├── CLAUDE.md                     # Development documentation
└── README.md                     # This file
```

## 🔧 Development Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Neon PostgreSQL account

### Backend Setup
```bash
cd apps/backend
pip install -r requirements.txt

# Environment variables in .env file:
DATABASE_URL=postgresql://neondb_owner:...@neon.tech/neondb
CANVAS_ACCESS_TOKEN=your_canvas_token
ZOHO_ACCESS_TOKEN=your_zoho_token

# Run development server
python -m app.main
```

### Frontend Setup
```bash
cd apps/frontend
npm install
npm start
```

## 📈 API Endpoints

### Core Endpoints
- `GET /health` - System health check
- `GET /api/feedback` - Retrieve aggregated feedback
- `GET /api/priorities` - Get prioritized recommendations
- `POST /api/ingest/canvas` - Trigger Canvas data sync
- `POST /api/ingest/zoho` - Trigger Zoho data sync

### Admin Endpoints
- `GET /admin/weights` - Get current scoring weights
- `PUT /admin/weights` - Update scoring weights
- `GET /admin/debug/{priority_id}` - Debug priority calculation

## 🎯 Success Metrics

- [ ] Dashboard runs on real Canvas + Zoho data
- [ ] 5-point scoring system with tunable weights via UI
- [ ] Explainable "Why?" panels showing factor breakdown
- [ ] At least 3 recommendations validated by admin
- [ ] Complete source provenance (every item traceable)
- [ ] Real-time weight adjustment with instant priority reordering
- [ ] Production deployment with monitoring

## 🔐 Security & Privacy

- API tokens stored securely in backend environment only
- Student PII handling with anonymization options
- Role-based access control for admin features
- Complete audit trail of scoring decisions and weight changes
- CORS configuration for production domains

---

**Last Updated**: September 9, 2025  
**Status**: Core backend foundation with priority tuning system ready for development  
**Next Phase**: Implement scoring engine and API endpoints