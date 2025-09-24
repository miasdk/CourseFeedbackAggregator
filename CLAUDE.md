# Course Feedback Aggregator - Project Documentation

## Project Overview
**Course Feedback Aggregation & Priority Intelligence System** - A platform that unifies course feedback from Canvas LMS and Zoho Surveys into a single database with intelligent prioritization scoring and explainable recommendations.

### Core Mission
Build an explainable prioritization system that pulls course feedback from Canvas and Zoho into one database, scores what to "fix" first, and shows the "why" behind each recommendation in a live dashboard.

## Current Repository Structure

```
CourseFeedbackAggregator/
├── apps/
│   ├── frontend/                 # React 18 + TypeScript Dashboard
│   │   ├── src/
│   │   │   ├── components/       # UI Components
│   │   │   │   ├── ui/          # shadcn/ui components
│   │   │   │   ├── ApplicationLayout.tsx
│   │   │   │   ├── CoursesList.tsx
│   │   │   │   ├── DashboardOverview.tsx
│   │   │   │   ├── PriorityRecommendations.tsx
│   │   │   │   ├── RecommendationCard.tsx
│   │   │   │   └── ScoringControls.tsx
│   │   │   ├── services/        # API clients & utilities
│   │   │   ├── hooks/           # Custom React hooks
│   │   │   └── lib/             # Utilities & helpers
│   │   └── package.json
│   │
│   └── backend/                  # FastAPI Backend
│       ├── app/
│       │   ├── api/             # API endpoints
│       │   │   ├── courses.py
│       │   │   ├── feedback.py
│       │   │   ├── priorities.py
│       │   │   ├── ingest.py
│       │   │   ├── weights.py
│       │   │   └── mock.py
│       │   ├── services/        # Business logic (296 lines zoho_auth, 243 lines scoring)
│       │   │   ├── zoho_auth.py
│       │   │   ├── scoring_service.py
│       │   │   ├── priority_service.py
│       │   │   └── feedback_service.py
│       │   ├── clients/         # External API integrations (empty)
│       │   ├── config/          # Configuration (empty files)
│       │   ├── controllers/     # Controllers (empty)
│       │   ├── views/           # View layer (empty)
│       │   └── utils/           # Utilities (empty)
│       └── main.py              # FastAPI app entry (86 lines)
│
└── dev-kit/                     # Development & Testing Tools
    ├── testing/
    │   ├── canvas/              # Canvas LMS API testing
    │   └── zoho/                # Zoho OAuth & API testing
    └── research/                # API integration guides
```

## 🔄 Current Implementation Status

### Frontend (React Dashboard) - FUNCTIONAL
- **Status**: Working MVP with mock data
- **Components**:
  - PriorityRecommendations with explainable scoring
  - CoursesList with filtering and sorting
  - DashboardOverview with metrics
  - ScoringControls for weight adjustment
- **Data Source**: Currently using mock API endpoints
- **Deployment Ready**: Can deploy to Vercel immediately

### Backend (FastAPI) - WEBHOOK MVP OPERATIONAL
- **Status**: Webhook infrastructure functional, database layer pending
- **✅ Working Components**:
  - FastAPI application with CORS configured
  - **Zoho webhook endpoint** (`/api/webhooks/zoho-survey`) receiving real survey data
  - Service layer with scoring logic (243 lines)
  - Zoho OAuth token management (296 lines)
  - Priority calculation service (154 lines)
  - Mock API endpoints for frontend testing
  - **Real-time webhook payload logging and display**
- **🔄 Missing/Empty Components**:
  - Database models (no ORM implementation)
  - Database configuration (minimal placeholder implementation)
  - Controllers (0 lines in all controller files)
  - Views layer (0 lines)
  - Canvas client implementation
  - Persistent data storage (webhooks stored temporarily)

### API Integrations
- **Canvas LMS**: Testing scripts functional, production client not implemented
  - Token: `15908~n7rLxPkkfXxZVkaLZ2CBNL9QzXCew8cCQmxaK4arEMtYWwJAUfaW3JQmn3Le2QuY`
  - Base URL: `https://executiveeducation.instructure.com`
- **Zoho Surveys**: ✅ **Webhook implementation ACTIVE**
  - Client ID: `1000.LFJC5W9CC2VV5A0VBHZBI8HFY0OWYH`
  - **✅ Webhook URL**: `https://unilluminant-marion-severally.ngrok-free.dev/api/webhooks/zoho-survey`
  - **✅ Real survey data flowing**: Course feedback from "Women In Leadership" and other courses
  - **🎯 Focus**: Course feedback surveys only (instructor evals and program feedback excluded)

## Updated Engineering Plan

### Phase 1: Complete Backend Infrastructure (Priority 1)
**Goal**: Establish database and complete backend foundation

**Tasks**:
- [ ] Implement SQLAlchemy models for courses, feedback, recommendations
- [ ] Configure Neon PostgreSQL connection in config files
- [ ] Build database initialization and migration system
- [ ] Complete controller implementations
- [ ] Remove mock endpoints after real implementation

### Phase 2: Zoho Webhook Integration (Priority 2) - ✅ **MVP COMPLETE**
**Goal**: Capture survey feedback via webhooks

**Tasks**:
- [x] **Create webhook receiver endpoint** `/api/webhooks/zoho-survey` - OPERATIONAL
- [x] **Real-time payload processing** - receiving course feedback data
- [x] **Survey response parser** - extracting course names, ratings, feedback sections
- [ ] Implement webhook signature validation (security enhancement)
- [ ] Create attribution engine for course mapping (Canvas ID correlation)
- [ ] Handle historical data import from "Untried" section
- [ ] **Persistent data storage** (currently logging only)

**🎯 Current Webhook Data Structure**:
```json
{
  "course_name": "Women In Leadership",
  "reviewer_email": "enterprise.ecandassociates@gmail.com",
  "response_id": "CGC4SCMP",
  "section_1_area": "Module 1",
  "section_1_overall_rating": "4",
  "section_1_positive": "feedback text...",
  "section_1_improvements": "improvement suggestions...",
  "section_1_showstopper": "No - they can work around it, or NA.",
  "section_2_area": "Module 2",
  "section_2_overall_rating": "4",
  "section_2_positive": "feedback text...",
  "section_2_improvements": "improvement suggestions...",
  "section_2_showstopper": "No - they can work around it, or NA."
}
```

**📋 Unified Schema Strategy (Canvas ↔ Zoho Mapping)**:
```python
# Unified Feedback Record
{
    "id": "uuid",
    "source": "zoho_survey",  # or "canvas_discussion"
    "source_id": "response_id",  # Zoho: CGC4SCMP, Canvas: assignment_id
    "course_id": "canvas_course_id",  # Primary key from Canvas
    "course_name": "Women In Leadership",  # Normalized from both sources
    "reviewer_identifier": "email_hash",  # Privacy-safe reviewer ID
    "feedback_sections": [
        {
            "section_type": "module_1",
            "rating": 4,
            "positive_feedback": "text...",
            "improvement_areas": "text...",
            "is_showstopper": false,
            "showstopper_details": null
        }
    ],
    "metadata": {
        "submission_date": "2025-02-16T13:59:28",
        "processing_timestamp": "2025-09-23T19:50:08Z",
        "canvas_mapped": true,
        "confidence_score": 0.95
    }
}
```

**🎯 Course Feedback Survey Scope**:
- **Primary Focus**: Module-level course feedback for content improvement
- **Exclusions**: Instructor evaluations, program-wide feedback, technical support
- **Key Metrics**: Section ratings, improvement suggestions, show-stopper identification
- **Attribution**: Map Zoho course names to Canvas course IDs for unified reporting

### Phase 3: Canvas API Integration (Priority 3)
**Goal**: Pull course data and feedback from Canvas

**Tasks**:
- [ ] Implement Canvas client in `clients/canvas_client.py`
- [ ] Build course synchronization logic
- [ ] Extract feedback from discussions/assignments
- [ ] Create incremental sync mechanism

### Phase 4: Attribution & Scoring Engine (Priority 4)
**Goal**: Intelligent feedback processing and prioritization

**Tasks**:
- [ ] Build course identification from survey text
- [ ] Implement confidence scoring for attributions
- [ ] Complete multi-factor scoring system
- [ ] Create explainable recommendation generation

### Phase 5: Frontend-Backend Integration (Priority 5)
**Goal**: Connect real backend to React dashboard

**Tasks**:
- [ ] Replace mock API calls with real endpoints
- [ ] Implement real-time score updates
- [ ] Add authentication if needed
- [ ] Test end-to-end workflows

### Phase 6: Production Deployment (Priority 6)
**Goal**: Deploy complete system

**Tasks**:
- [ ] Deploy backend to Railway/Render
- [ ] Configure Neon PostgreSQL production
- [ ] Deploy frontend to Vercel
- [ ] Set up monitoring and logging
- [ ] Configure webhook URLs for production

## Technology Stack

### Frontend
- React 18 with TypeScript
- Tailwind CSS + shadcn/ui components
- React Query for API state management
- Recharts for data visualization
- Vite as build tool

### Backend
- FastAPI (Python 3.11+)
- SQLAlchemy for ORM (to be implemented)
- Neon PostgreSQL for database (to be configured)
- Pydantic for data validation
- httpx for external API calls

### Infrastructure
- Frontend: Vercel
- Backend: Railway/Render
- Database: Neon PostgreSQL
- Monitoring: TBD

## Development Commands

### Frontend
```bash
cd apps/frontend
npm install
npm run dev          # Start development server (port 5173)
npm run build        # Build for production
npm run preview      # Preview production build
```

### Backend
```bash
cd apps/backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003  # Start development server
```

## Environment Variables

### Backend (.env)
```env
# Database (TO BE CONFIGURED)
DATABASE_URL=postgresql://user:pass@host/dbname

# Canvas API
CANVAS_API_TOKEN=15908~n7rLxPkkfXxZVkaLZ2CBNL9QzXCew8cCQmxaK4arEMtYWwJAUfaW3JQmn3Le2QuY
CANVAS_BASE_URL=https://executiveeducation.instructure.com

# Zoho OAuth
ZOHO_CLIENT_ID=1000.LFJC5W9CC2VV5A0VBHZBI8HFY0OWYH
ZOHO_CLIENT_SECRET=your_secret_here
ZOHO_REFRESH_TOKEN=to_be_obtained
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8003
```

## 📊 Priority Scoring Algorithm

Current implementation in `scoring_service.py`:
- **Impact**: Student enrollment × feedback frequency
- **Urgency**: Severity keywords + timing factors
- **Effort**: Issue type classification
- **Strategic**: Alignment with institutional goals
- **Trend**: Pattern analysis over time

**Default Weights**:
- Impact: 0.4
- Urgency: 0.35
- Effort: 0.15
- Strategic: 0.1

## 🚀 Current Development Status

### ✅ **Webhook MVP Successfully Operational**
- **Real-time data ingestion**: Zoho survey responses flowing to FastAPI
- **Course feedback parsing**: Extracting ratings, feedback text, show-stopper flags
- **Development environment**: Local server + ngrok tunnel for Zoho connectivity
- **Data structure validation**: Confirmed course feedback schema compatibility

### **Current Development Setup**
```bash
# Backend Server
cd apps/backend
./venv/bin/python -m uvicorn app.main:app --reload --port 8000

# ngrok Tunnel (for Zoho webhooks)
ngrok http 8000
# URL: https://unilluminant-marion-severally.ngrok-free.dev/api/webhooks/zoho-survey

# Test Webhook
cd dev-kit/testing/zoho
python3 test_webhook_local.py
```

### **Live Data Flow Confirmed**
- **Survey**: "Women In Leadership" course feedback
- **Response ID**: CGC4SCMP
- **Data Quality**: Complete section ratings, detailed feedback text, show-stopper analysis
- **Webhook Reliability**: Successfully receiving and processing real survey submissions

## Known Issues & Next Steps

### Critical Issues
1. **🔄 Persistent Storage**: Webhook data logging only (no database persistence)
2. **No Database Models**: ORM models need implementation for unified schema
3. **Canvas Integration Missing**: Course ID mapping layer not implemented
4. **Controllers Empty**: Business logic needs to be moved to controllers

### Immediate Actions Required
1. Set up Neon PostgreSQL database
2. Implement SQLAlchemy models
3. Complete Canvas API client
4. Set up Zoho webhooks
5. Connect frontend to real backend

## Additional Documentation

### Zoho Survey Integration Strategy
Based on investigation, Zoho Survey API does not provide historical response retrieval. Recommended approach:
1. Use webhooks for new responses
2. Manual push from "Untried" section for historical data
3. Store raw webhook payloads for reprocessing
4. Implement idempotency checks

### Canvas Integration Notes
- Use official API documentation patterns
- Implement rate limiting (3000 requests/hour)
- Handle pagination for large datasets
- Cache frequently accessed data

##  Learning Resources

For detailed implementation guide, see:
- MVP Code-Along Guide (12-day structured learning plan)
- Canvas API Documentation: https://canvas.instructure.com/doc/api/
- Zoho Webhook Documentation: https://help.zoho.com/portal/en/kb/survey/hub/triggers/webhook/

---

**Last Updated**: September 22, 2025
**Current Focus**: Complete backend infrastructure and database implementation
**Demo Status**: Frontend functional with mock data
**Production Readiness**: ~40% complete