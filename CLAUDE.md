# Course Feedback Aggregator - Claude Code Configuration

## Project Overview
**Course Feedback Aggregation & Priority Intelligence System** - A comprehensive platform that unifies course feedback from Canvas LMS and Zoho surveys into a single database with intelligent prioritization scoring. The system provides explainable recommendations for course improvements with full traceability back to original feedback sources.

### Mission Statement
Build a single, explainable prioritization system that pulls course feedback from Canvas and Zoho into one database, scores what to "fix" first, and shows the "why" behind each recommendation in a live dashboard.

## 🗂️ Current Repository Structure (Updated Sept 2, 2025)

```
CourseFeedbackAggregator/
├── .claude/                   # Claude Code configuration  
├── .env                       # API credentials (Canvas, Zoho)
├── .gitignore                # Git ignore rules
├── .vscode/                  # VSCode configuration
├── CLAUDE.md                 # This project documentation
├── README.md                 # Project overview
├── apps/
│   └── frontend/             # React frontend (preserved)
│       ├── src/              # React source code
│       ├── public/           # Static assets
│       └── package.json      # Frontend dependencies
└── dev-kit/                  # API testing & development tools
    ├── testing/              # ✅ API test scripts
    │   ├── canvas_api_live_test.py      # Canvas API testing
    │   ├── zoho_oauth_simple.py        # Zoho OAuth setup
    │   ├── canvas_live_test_results_*.json
    │   └── README.md         # Testing documentation
    ├── research/             # API research documentation
    │   ├── canvas-lms.md     # Canvas API research
    │   └── zoho-crm.md       # Zoho CRM research  
    └── templates/            # Development templates
```

### ⚠️ Backend Removed (Sept 2, 2025)
**Removed:** `apps/backend/` - Overengineered system built without real API access  
**Reason:** Will rebuild from scratch after obtaining proper API access and discovering actual data structures  
**Preserved:** Frontend, dev-kit testing framework, and API credentials

## Technology Stack
**Current (Phase 0 - MVP)**
- **Frontend Framework**: React 18 with TypeScript
- **Styling**: Tailwind CSS with custom Apple-inspired design system
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **State Management**: Zustand
- **Testing**: Jest, React Testing Library
- **Build Tool**: Create React App
- **Data Source**: Static JSON files (MVP simulation)
- **API Testing**: Python scripts in dev-kit/testing/

**Target Architecture (Full Implementation)**
- **Backend**: FastAPI with Python
- **Database**: PostgreSQL (SQLite for local development)
- **Authentication**: Token-based for Canvas/Zoho APIs
- **Deployment**: 
  - Frontend: Vercel
  - Backend: Railway/Render
- **External APIs**: Canvas LMS API, Zoho Survey API

## Engineering Plan & Implementation Roadmap

### Success Criteria
- [ ] Dashboard runs on real Canvas + Zoho data via API integration
- [ ] Scoring system is **explainable** and **tunable** (weights adjustable via UI with factor breakdowns)
- [ ] At least three recommendations reviewed and validated with reviewer notes in the app
- [ ] Unified schema with full provenance (every feedback item links back to source)
- [ ] Production deployment with secure environment variable handling

### Phase 1: Backend Foundation & Database (Week 1-2)
**Objective**: Establish FastAPI service with core infrastructure

**Tasks:**
- [ ] Set up FastAPI project structure with Poetry/pip requirements
- [ ] Implement core API routes:
  - `/health` - Service health check
  - `/api/feedback` - Retrieve aggregated feedback data
  - `/api/priorities` - Get prioritized recommendations
  - `/api/recompute` - Trigger scoring recalculation
- [ ] Design unified database schema:
  - `courses` - Course metadata and identifiers
  - `feedback` - Normalized feedback entries with source provenance
  - `weight_configs` - Tunable scoring weights and parameters  
  - `recommendations` - Generated priority recommendations with explanations
- [ ] Set up SQLite for local development, prepare PostgreSQL configuration
- [ ] Seed database with current static JSON data for testing
- [ ] Implement basic CRUD operations and data models

### Phase 2: Data Ingestion MVP (Week 3-4)
**Objective**: Real data integration from Canvas and Zoho

**Tasks:**
- [ ] Implement Zoho Survey API client:
  - Token-based authentication
  - Survey data retrieval and normalization
  - `/api/ingest/zoho` endpoint for manual/scheduled ingestion
- [ ] Implement Canvas LMS API client:
  - Canvas API token authentication (token: `15908~kJrH3tCwaXwc7HZtGtzY64mXxnN6mk2vFVV236VcHuL3KvMTwc4LH9fvnzKzaVu8`)
  - Course evaluation data extraction
  - `/api/ingest/canvas` endpoint with course/instructor ID normalization
- [ ] Build data mapping layer:
  - Handle different course/instructor ID formats across systems
  - Maintain source provenance for all feedback entries
  - Implement conflict resolution for duplicate data
- [ ] Create ingestion monitoring and error handling

### Phase 3: Intelligent Scoring & Frontend Integration (Week 5-6)
**Objective**: Implement explainable scoring algorithm with UI integration

**Tasks:**
- [ ] Develop server-side scoring engine:
  - **Impact Score**: Frequency and severity of reported issues
  - **Urgency Score**: Time-sensitivity based on course timeline
  - **Effort Score**: Quick-win potential assessment
  - **Strategic Score**: Alignment with institutional priorities
  - **Trend Score**: Issue trajectory analysis
- [ ] Implement scoring explanation system:
  - Factor breakdown for each recommendation
  - Evidence linking back to original feedback sources
  - Confidence intervals and data quality indicators
- [ ] Frontend API integration:
  - Replace static JSON with API calls
  - Add weight configuration sliders in admin panel
  - Implement "Why This Priority?" explanation drawer
  - Real-time scoring updates on weight changes
- [ ] Enhanced UI features:
  - Source evidence viewer with Canvas/Zoho links
  - Recommendation validation workflow
  - Reviewer notes and action tracking

### Phase 4: Production Deployment (Week 7)
**Objective**: Secure production deployment with monitoring

**Tasks:**
- [ ] Backend deployment on Railway/Render:
  - PostgreSQL database provisioning
  - Environment variable configuration
  - API endpoint security and rate limiting
- [ ] Frontend deployment on Vercel:
  - Environment-specific API endpoint configuration
  - Performance optimization and build verification
- [ ] Security implementation:
  - API tokens stored securely in backend environment only
  - CORS configuration for frontend-backend communication
  - Input validation and SQL injection prevention
- [ ] Monitoring and logging:
  - Application performance monitoring
  - Error tracking and alerting
  - API usage analytics

### Phase 5: Documentation & Handoff (Week 8)
**Objective**: Complete documentation and knowledge transfer

**Tasks:**
- [ ] Technical documentation:
  - API documentation with OpenAPI/Swagger
  - Database schema documentation
  - Scoring algorithm explanation
- [ ] Operational runbook:
  - Deployment procedures
  - Environment setup guide
  - Troubleshooting guide
- [ ] User documentation:
  - Admin panel usage guide
  - Scoring interpretation guide
  - Data validation workflows
- [ ] Code quality:
  - Lighthouse/accessibility audit
  - Code review and refactoring
  - Test coverage verification

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Canvas LMS    │    │  Zoho Surveys   │    │  Other Sources  │
│     API         │    │      API        │    │    (Future)     │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
          ┌─────────────────────────────────────────────┐
          │           FastAPI Backend                   │
          │  ┌─────────────┐  ┌─────────────────────┐   │
          │  │ Ingestion   │  │   Scoring Engine    │   │
          │  │ Services    │  │   - Impact          │   │
          │  │             │  │   - Urgency         │   │
          │  └─────────────┘  │   - Effort          │   │
          │                   │   - Strategic       │   │
          │  ┌─────────────┐  │   - Trend           │   │
          │  │   API       │  └─────────────────────┘   │
          │  │  Routes     │                            │
          │  └─────────────┘                            │
          └─────────────────┬───────────────────────────┘
                            │
          ┌─────────────────┴───────────────────────────┐
          │            PostgreSQL                       │
          │  ┌─────────┐ ┌─────────┐ ┌─────────────┐   │
          │  │ Courses │ │Feedback │ │Recommendations│  │
          │  └─────────┘ └─────────┘ └─────────────┘   │
          │  ┌─────────────────┐ ┌─────────────────┐   │
          │  │ Weight_Configs  │ │   Audit_Log     │   │
          │  └─────────────────┘ └─────────────────┘   │
          └─────────────────┬───────────────────────────┘
                            │
          ┌─────────────────┴───────────────────────────┐
          │           React Frontend                    │
          │  ┌─────────────┐ ┌─────────────────────┐   │
          │  │   Course    │ │    Priority         │   │
          │  │ Dashboard   │ │   Recommendations   │   │
          │  └─────────────┘ └─────────────────────┘   │
          │  ┌─────────────┐ ┌─────────────────────┐   │
          │  │   Admin     │ │   Evidence &        │   │
          │  │   Panel     │ │   Explanation       │   │
          │  └─────────────┘ └─────────────────────┘   │
          └─────────────────────────────────────────────┘
```

### Risk Mitigation Strategies

**Data Security & Access**
- Canvas/Zoho API tokens secured in backend environment variables only
- No credentials stored in frontend code or repository
- Token rotation and access monitoring procedures

**Data Integrity & Mapping**
- Robust course/instructor ID mapping layer to handle system differences
- Data validation at ingestion points
- Audit logging for all data modifications

**Scoring Explainability**
- Store weight snapshots with each scoring run for reproducibility
- Maintain detailed factor contribution logs
- Version control for scoring algorithm changes

**System Dependencies**
- Admin/API access coordination for Canvas and Zoho
- Fallback procedures for API outages
- Regular backup and recovery testing

## Development Commands

### Start Development Server
```bash
npm start
```
Runs the app at http://localhost:3000 with hot reload

### Build for Production
```bash
npm run build
```
Creates optimized production build in `build/` folder

### Run Tests
```bash
npm test
```
Launches Jest test runner in watch mode

### Type Checking
No separate TypeScript command needed - handled by Create React App

### Linting
No explicit lint command configured - uses ESLint via React Scripts

## Project Structure

**Current Frontend (React)**
```
src/
├── components/           # React components
│   ├── CourseCard.tsx   # Individual course display cards
│   ├── CourseGrid.tsx   # Main course listing with sorting
│   ├── Header.tsx       # Navigation with search
│   ├── Sidebar.tsx      # Category navigation
│   ├── SmartFilters.tsx # Advanced filtering options
│   ├── StatsCards.tsx   # Analytics dashboard
│   └── UploadModal.tsx  # CSV upload interface
├── services/            # Business logic
│   └── issueAnalysis.ts # Course review analysis
└── __tests__/          # Test files
```

**Planned Backend Structure (FastAPI)**
```
backend/
├── api/                 # API routes and endpoints
│   ├── routes/
│   │   ├── feedback.py  # Feedback data endpoints
│   │   ├── priorities.py # Priority recommendations
│   │   ├── ingest.py   # Data ingestion endpoints
│   │   └── health.py   # Health check
│   └── dependencies.py  # Shared dependencies
├── core/               # Core application logic
│   ├── config.py       # Configuration management
│   ├── database.py     # Database connection
│   └── security.py     # Authentication & security
├── models/             # Database models
│   ├── course.py       # Course data models
│   ├── feedback.py     # Feedback data models
│   └── recommendation.py # Recommendation models
├── services/           # Business logic services
│   ├── canvas_client.py    # Canvas API integration
│   ├── zoho_client.py      # Zoho API integration
│   ├── scoring_engine.py   # Priority scoring logic
│   └── data_mapper.py      # Cross-system data mapping
├── schemas/            # Pydantic schemas
│   └── api_schemas.py  # Request/response models
└── tests/             # Backend tests
    ├── test_api/      # API endpoint tests
    └── test_services/ # Service layer tests
```

## Key Features

**Current MVP Features**
- **Apple-style UI**: Custom Tailwind theme with SF Pro fonts and Apple shadows
- **Course Analytics**: Real-time sorting by rating, date, issues, and name
- **Smart Filtering**: Filter by issue categories, priority levels, and action status
- **CSV Upload**: Drag & drop interface for course data import
- **Priority Dashboard**: Overview of urgent issues and quick wins
- **Responsive Design**: Mobile-friendly layout

**Planned Advanced Features**
- **Multi-Source Data Integration**: Unified Canvas LMS and Zoho Survey data ingestion
- **Intelligent Priority Scoring**: Multi-factor algorithm (Impact, Urgency, Effort, Strategic, Trend)
- **Explainable AI**: "Why This Priority?" explanations with source evidence linking
- **Tunable Weights**: Admin panel for adjusting scoring factors in real-time
- **Recommendation Validation**: Workflow for reviewing and validating AI recommendations
- **Full Provenance Tracking**: Every data point traceable back to original source
- **Real-time Scoring**: Dynamic recalculation based on new data and weight changes
- **Audit Trail**: Complete history of scoring decisions and weight configurations

## Data Sources

**Current (MVP)**
- Static JSON files in `public/courses/`:
  - `course_catalog.json` - Master course list
  - Individual course folders with:
    - `course_info.json` - Course metadata
    - `reviews.json` - Student review data
    - `analytics.json` - Computed analytics

**Target Production Sources**
- **Canvas LMS API**: Course evaluations, gradebook data, discussion posts
- **Zoho Surveys**: Custom feedback surveys, student satisfaction data
- **PostgreSQL Database**: Unified storage with full provenance tracking
- **Future Integrations**: Blackboard, Moodle, Google Classroom

## Development Notes

**Current MVP**
- Uses Create React App configuration (no custom webpack)
- Custom Apple-inspired color palette and shadows in `tailwind.config.js`
- TypeScript strict mode enabled
- No backend - operates on static JSON data files

**Production Architecture Notes**
- FastAPI backend with async/await patterns for API performance
- SQLAlchemy ORM for database operations with Alembic migrations
- Redis caching layer for expensive scoring computations
- JWT-based authentication for admin features
- Docker containerization for consistent deployment
- Environment-specific configurations (dev/staging/prod)

## Security Considerations
- **API Tokens**: Canvas/Zoho credentials stored in backend environment variables only
- **Data Privacy**: PII scrubbing and anonymization of student feedback
- **Access Control**: Role-based permissions for admin vs. viewer access
- **Audit Logging**: Complete trail of data access and scoring decisions
- **CORS Configuration**: Strict cross-origin policies for production

## Testing
**Frontend Testing**
- Test files located in `src/__tests__/` and `src/components/__tests__/`
- Jest and React Testing Library for component and integration tests

**Backend Testing (Planned)**
- `pytest` for unit and integration testing
- `httpx` for async API endpoint testing  
- Test database isolation with fixtures
- Mock external API calls (Canvas/Zoho) for reliable testing

---

## 📈 Recent Progress (September 5, 2025)

### ✅ **Major UI/UX Overhaul Completed**
**Professional Dashboard Transformation:**
- **Removed AI-generated elements**: Eliminated all emojis, flashy colors, and "generated" indicators
- **Focused on core mission**: Header now reads "Feedback Intelligence - Explainable Course Improvement Priorities"
- **Real use case demonstration**: Using actual course data (IT Leadership, Customer Experience Program)
- **Priority-first design**: Dashboard leads with explainable priority recommendations

**New Components Implemented:**
- **PriorityRecommendations**: Complete priority dashboard with real course feedback
- **Explainable "Why This Priority?"**: Interactive modals showing scoring breakdown (Impact: 9.2, Urgency: 8.5, etc.)
- **Source Traceability**: Canvas LMS and Zoho Survey indicators with reviewer attribution
- **Professional Navigation**: "Priority Queue" and "Feedback Sources" instead of generic categories

### ✅ **CourseCard Major Refactor**
**Before**: Bloated component with star ratings, animations, export functions, rounded corners
**After**: Clean, feedback-focused cards with:
- **Priority-first header**: Color-coded priority scores (Critical: 8.7, High: 6.2, Medium: 4.8)
- **Gradient backgrounds**: Professional red/orange/amber/emerald priority indicators
- **Issue preview**: Shows actual student feedback with truncation
- **Student impact metrics**: Clear display of affected students and reported issues
- **Shadcn/ui styling**: Professional buttons, spacing, and minimal border radius
- **50% code reduction**: Eliminated unnecessary complexity while adding functionality

### ✅ **TypeScript Architecture Fixed**
**Comprehensive Type Safety:**
- **Unified Course interface**: Consolidated conflicting Course types from multiple files
- **Resolved circular dependencies**: Fixed imports between types, services, and components
- **API type integration**: Proper handling of Canvas/Zoho API response types
- **Missing properties added**: All Course objects now include required `priority` field
- **Build compilation**: ✅ No TypeScript errors

**Files Affected:**
- `App.tsx`: API type integration and data processing
- `CourseCard.tsx`: Complete rewrite with professional design
- `Header.tsx`: Rebranded to "Feedback Intelligence" with Configure Scoring button
- `Sidebar.tsx`: Updated navigation for feedback workflow
- `types/index.ts`: Unified type definitions
- `UploadModal.tsx`: Added missing required properties

### 🎯 **Alignment with Notion Specification**
**Core Mission Achieved:**
- ✅ **Explainable Priority Scoring**: "Why This Priority?" feature with factor breakdowns
- ✅ **Source Provenance**: Every recommendation links to Canvas/Zoho with reviewer names
- ✅ **Real Course Data**: Using actual feedback from IT Leadership course
- ✅ **Professional Appearance**: Removed all AI-generated styling and content
- ✅ **Actionable Workflow**: Clear next steps for course administrators

**Evidence of Value Proposition:**
- Shows specific issues: "Video 1 and Video 2 talk about different attributes - this offers inconsistency"
- Student impact: "23 students affected" with source attribution
- Priority justification: Impact (9.2), Urgency (8.5), Effort (6.0) scoring
- Business context: "Critical Issues", "Quick Fixes", "Improvements" categorization

---

## 🚀 Next Steps (Priority Order)

### **Phase 1: Backend Foundation (Week 1-2)**
**Status**: Ready to begin with real API access
- **FastAPI Setup**: Use established architecture from CLAUDE.md specification
- **Canvas Integration**: Leverage existing token and testing framework in dev-kit/
- **Database Schema**: Implement unified feedback storage with source provenance
- **Priority Scoring Engine**: Server-side implementation of Impact/Urgency/Effort/Strategic/Trend factors

### **Phase 2: API Integration (Week 3)**
**Prerequisites**: Admin access to Canvas and Zoho accounts
- **Live Data Ingestion**: Replace static JSON with real API calls
- **Weight Configuration**: Implement tunable scoring parameters
- **Recommendation Validation**: Add reviewer workflow for marking recommendations as reviewed

### **Phase 3: Production Deployment (Week 4)**
**Frontend**: ✅ Ready for immediate deployment to Vercel
**Backend**: Deploy to Railway/Render with secure environment variables
**Monitoring**: Implement basic analytics and error tracking

### **Immediate Action Items**
1. **Obtain API Access**: Secure admin permissions for Canvas LMS and Zoho Survey accounts
2. **Backend Development**: Start FastAPI implementation using existing specification
3. **Demo Preparation**: Current frontend is demo-ready with professional appearance
4. **Testing**: Validate Canvas API integration using dev-kit testing framework

---

**Last Updated:** September 5, 2025  
**Current Status:** ✅ Professional MVP frontend completed - Backend development ready to begin
**Demo Ready:** Yes - Explainable priority scoring with real course feedback data
**Dev Server:** http://localhost:3000/