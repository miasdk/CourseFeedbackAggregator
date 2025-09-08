# Course Feedback Aggregator - Setup & Architecture Documentation

## System Architecture Overview

Based on Canvas API exploration (41 Executive Education courses discovered), our system processes real feedback data from discussion forums and assignment comments to generate explainable priority recommendations.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Data Sources"
        Canvas[Canvas LMS API<br/>41 Executive Education Courses]
        Zoho[Zoho Survey API<br/>Future Integration]
    end
    
    subgraph "Data Ingestion Layer"
        CI[Canvas Ingestion Service<br/>Rate Limit: 100 req/10s]
        ZI[Zoho Ingestion Service<br/>OAuth 2.0]
        DM[Data Mapper<br/>Course ID Normalization]
    end
    
    subgraph "Processing Engine"
        NLP[NLP Processing<br/>Keyword Categorization]
        SE[Scoring Engine<br/>5 Factor Algorithm]
        RE[Recommendation Engine<br/>Explainable AI]
    end
    
    subgraph "Data Storage"
        PG[(PostgreSQL<br/>Production)]
        SQ[(SQLite<br/>Development)]
        RD[(Redis Cache<br/>Scoring Results)]
    end
    
    subgraph "API Layer"
        FA[FastAPI Backend<br/>Python 3.11+]
        AUTH[JWT Authentication<br/>Admin Features]
    end
    
    subgraph "Frontend"
        REACT[React 18 + TypeScript<br/>Dashboard UI]
        WC[Weight Configuration<br/>Admin Panel]
        EX[Explanation Interface<br/>Why This Priority?]
    end
    
    Canvas --> CI
    Zoho --> ZI
    CI --> DM
    ZI --> DM
    DM --> NLP
    NLP --> SE
    SE --> RE
    RE --> PG
    SE --> RD
    PG --> FA
    RD --> FA
    FA --> REACT
    REACT --> WC
    REACT --> EX
    
    style Canvas fill:#e1f5fe
    style SE fill:#f3e5f5
    style REACT fill:#e8f5e8
```

### Canvas API Data Flow

```mermaid
sequenceDiagram
    participant FE as Frontend Dashboard
    participant API as FastAPI Backend
    participant CE as Canvas Extractor
    participant CA as Canvas API
    participant DB as PostgreSQL
    participant SC as Scoring Engine

    FE->>API: GET /api/priorities
    API->>DB: Query recommendations
    
    Note over API: Background Ingestion Process
    API->>CE: Trigger data ingestion
    CE->>CA: GET /courses (41 courses)
    CE->>CA: GET /discussion_topics
    CE->>CA: GET /assignments + comments
    
    CA-->>CE: Raw discussion data
    CA-->>CE: Assignment feedback
    
    CE->>CE: Categorize feedback<br/>(confusion, technical, suggestions)
    CE->>CE: Calculate urgency score<br/>(technical=5, confusion=3, etc)
    CE->>DB: Store normalized feedback
    
    DB->>SC: Trigger scoring calculation
    SC->>SC: Apply 5-factor algorithm<br/>(Impact, Urgency, Effort, Strategic, Trend)
    SC->>DB: Store recommendations + explanations
    
    DB-->>API: Return prioritized recommendations
    API-->>FE: JSON response with explanations
```

## Database Schema (ERD)

```mermaid
erDiagram
    COURSES {
        int id PK
        varchar canvas_id UK
        varchar name
        varchar workflow_state "available|completed|unpublished"
        timestamp start_at
        timestamp end_at
        varchar account_id
        varchar course_code
        timestamp created_at
        timestamp updated_at
        int active_students
    }
    
    FEEDBACK_ITEMS {
        int id PK
        int course_id FK
        varchar source_type "discussion|assignment|survey"
        varchar canvas_source_id UK
        text content
        int user_id
        timestamp created_at
        int urgency_score "0-10"
        json categories "confusion|technical|suggestions"
        boolean is_urgent
        varchar reviewer_id
        text reviewer_notes
        timestamp processed_at
    }
    
    PRIORITY_RECOMMENDATIONS {
        int id PK
        int course_id FK
        varchar title
        text description
        float priority_score "0.0-10.0"
        varchar priority_level "critical|high|medium|low"
        json scoring_breakdown
        text explanation
        int affected_students
        boolean is_reviewed
        varchar reviewed_by
        timestamp reviewed_at
        timestamp created_at
        timestamp updated_at
    }
    
    SCORING_WEIGHTS {
        int id PK
        varchar factor_name "impact|urgency|effort|strategic|trend"
        float weight "0.0-1.0"
        varchar description
        boolean is_active
        varchar updated_by
        timestamp updated_at
    }
    
    FEEDBACK_SOURCES {
        int id PK
        int feedback_item_id FK
        varchar source_system "canvas|zoho"
        varchar source_url
        varchar source_reference
        json metadata
        timestamp last_synced
    }
    
    COURSES ||--o{ FEEDBACK_ITEMS : "generates"
    COURSES ||--o{ PRIORITY_RECOMMENDATIONS : "has"
    FEEDBACK_ITEMS ||--|| FEEDBACK_SOURCES : "traces_to"
    FEEDBACK_ITEMS }|--|| PRIORITY_RECOMMENDATIONS : "supports"
    SCORING_WEIGHTS }|--|| PRIORITY_RECOMMENDATIONS : "weights"
```

## Canvas Integration Architecture

### Data Ingestion Strategy

**Available Data Sources (Verified):**
- ✅ **Discussion Topics**: `/courses/{id}/discussion_topics` → `/discussion_topics/{id}/entries`
- ✅ **Assignment Comments**: `/courses/{id}/assignments` → `/assignments/{id}/submissions?include[]=submission_comments`
- ✅ **Course Metadata**: Workflow states, enrollment periods, account information
- ❌ **Course Analytics**: Not available (404) - requires higher admin permissions

**Rate Limiting & Performance:**
```python
# Canvas API Limits: 100 requests per 10 seconds
RATE_LIMIT_DELAY = 0.1  # seconds between requests
BATCH_SIZE = 10         # courses processed in parallel
RETRY_ATTEMPTS = 3      # failed request retries
```

### Feedback Categorization System

```mermaid
flowchart TD
    FB[Raw Feedback Text] --> KW[Keyword Detection]
    
    KW --> TECH[Technical Issues<br/>Score: +5]
    KW --> URG[Urgent Keywords<br/>Score: +10] 
    KW --> CONF[Confusion Signals<br/>Score: +3]
    KW --> DIFF[Difficulty Markers<br/>Score: +2]
    KW --> SUGG[Suggestions<br/>Score: +1]
    KW --> POS[Positive Feedback<br/>Score: +0]
    
    TECH --> CALC[Calculate Total<br/>Urgency Score]
    URG --> CALC
    CONF --> CALC
    DIFF --> CALC
    SUGG --> CALC
    POS --> CALC
    
    CALC --> CLASS{Score >= 5?}
    CLASS -->|Yes| URGENT[Mark as Urgent<br/>High Priority]
    CLASS -->|No| NORMAL[Standard Priority<br/>Queue for Analysis]
    
    URGENT --> DB[(Database Storage)]
    NORMAL --> DB
```

**Keyword Categories:**
```python
feedback_keywords = {
    'technical_issues': ['broken', 'not working', 'error', 'crash', 'can\'t access'],
    'urgent': ['urgent', 'critical', 'immediately', 'asap', 'emergency'],
    'confusion': ['confusing', 'confused', 'unclear', 'don\'t understand'],
    'difficulty': ['difficult', 'hard', 'challenging', 'struggling'],
    'suggestions': ['suggest', 'recommend', 'should', 'could be better'],
    'positive': ['great', 'excellent', 'helpful', 'clear', 'good']
}
```

## Five-Factor Scoring Algorithm

```mermaid
graph LR
    subgraph "Input Data"
        F1[Feedback Frequency<br/>Cross-Course Patterns]
        F2[Issue Recency<br/>Timeline Analysis]
        F3[Student Engagement<br/>Reply Counts]
        F4[Keyword Urgency<br/>Weighted Categories]
        F5[Course Context<br/>Active vs Completed]
    end
    
    subgraph "Scoring Factors"
        IF[Impact Factor<br/>Weight: 0.25<br/>How many affected?]
        UF[Urgency Factor<br/>Weight: 0.25<br/>How time-sensitive?]
        EF[Effort Factor<br/>Weight: 0.20<br/>Quick win potential?]
        SF[Strategic Factor<br/>Weight: 0.20<br/>Institutional alignment?]
        TF[Trend Factor<br/>Weight: 0.10<br/>Issue trajectory?]
    end
    
    subgraph "Output"
        PS[Priority Score<br/>0.0 - 10.0]
        EX[Explanation Text<br/>Factor Breakdown]
        REC[Recommendations<br/>Actionable Items]
    end
    
    F1 --> IF
    F2 --> UF
    F3 --> EF
    F4 --> SF
    F5 --> TF
    
    IF --> PS
    UF --> PS
    EF --> PS
    SF --> PS
    TF --> PS
    
    PS --> EX
    PS --> REC
```

## Expected Data Volume

**Per Course Analysis (41 Executive Education Courses):**
- Discussion Topics: 1-100 per course
- Discussion Entries: 1-50 per topic
- Assignments: 2-10 per course
- Assignment Comments: 0-20 per assignment

**Total Projected Data:**
- **Feedback Items**: 500-2,000 data points
- **Processing Time**: 15-30 minutes full ingestion
- **Storage Requirements**: ~50MB initial data
- **API Requests**: ~1,500-3,000 requests per full sync

## Deployment Architecture

### Development Environment
```bash
# Backend (FastAPI)
cd backend/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Frontend (React)
cd apps/frontend/
npm install
npm start  # http://localhost:3000

# Database
docker run --name postgres-dev -e POSTGRES_PASSWORD=dev -p 5432:5432 -d postgres:15
```

### Production Deployment
```yaml
# Docker Compose Production Setup
services:
  backend:
    build: ./backend
    environment:
      - CANVAS_ACCESS_TOKEN=${CANVAS_ACCESS_TOKEN}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on: [postgres, redis]
  
  frontend:
    build: ./apps/frontend
    environment:
      - REACT_APP_API_URL=${API_URL}
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=feedback_aggregator
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
```

## Security Implementation

### API Token Management
```python
# Canvas API Integration
headers = {
    'Authorization': f'Bearer {os.getenv("CANVAS_ACCESS_TOKEN")}',
    'Accept': 'application/json'
}

# Secure environment variables (backend only)
CANVAS_ACCESS_TOKEN=15908~kJrH3tCwaXwc7HZtGtzY64mXxnN6mk2vFVV236VcHuL3KvMTwc4LH9fvnzKzaVu8
DATABASE_URL=postgresql://user:pass@localhost/feedback_db
REDIS_URL=redis://localhost:6379
JWT_SECRET_KEY=your-256-bit-secret
```

### Data Privacy & Anonymization
- Student user_ids anonymized in storage
- PII scrubbed from feedback text
- Canvas URLs stored for traceability (admin only)
- Audit logging for all data access

## Success Metrics & Monitoring

### Phase 1 Metrics (Week 1)
- [ ] 41 Executive Education courses connected
- [ ] 500+ feedback items extracted and categorized
- [ ] 25+ priority recommendations generated
- [ ] 95% API request success rate

### Phase 2 Metrics (Month 1)
- [ ] Top 10 recurring issues identified across courses
- [ ] 3+ recommendations validated by instructors
- [ ] <2 second dashboard response time
- [ ] Weekly automated data ingestion

### Phase 3 Metrics (Quarter 1)
- [ ] Measurable improvement in flagged courses
- [ ] Integration with Zoho survey data
- [ ] Real-time alert system for urgent issues
- [ ] 90%+ recommendation accuracy rate

---

**Last Updated:** September 5, 2025  
**Canvas Integration Status:** ✅ API Tested & Verified  
**Data Sources Confirmed:** Discussion Forums, Assignment Comments, Course Metadata  
**Expected Launch:** 2-3 weeks for MVP with real Canvas data