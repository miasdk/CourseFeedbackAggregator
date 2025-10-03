# Canvas Feedback Aggregator - Backend API

A FastAPI-based backend for aggregating and analyzing student feedback from Canvas LMS course surveys. Features modular Canvas API integration, async database operations, and intelligent survey detection.

## Tech Stack

- **Python 3.13** - Modern async/await patterns with type hints
- **FastAPI** - High-performance async web framework
- **SQLAlchemy 2.0** - Async ORM with PostgreSQL
- **Neon PostgreSQL** - Serverless database with branching
- **Alembic** - Database migrations
- **httpx** - Async HTTP client for Canvas API
- **Pandas** - CSV data processing
- **Pydantic v2** - Request/response validation

## Project Structure

```
app/
├── api/                    # FastAPI route handlers
│   ├── courses.py         # Course management endpoints
│   ├── feedback.py        # Student feedback sync and retrieval
│   ├── quizzes.py         # Survey discovery and management
│   └── ...
├── core/                   # Core configuration
│   ├── config.py          # Settings management
│   └── database.py        # Database connection
├── models/                 # SQLAlchemy ORM models
│   ├── course.py          # Course model
│   ├── canvas_survey.py   # Survey/quiz model
│   ├── student_feedback.py # Student submission model
│   └── feedback_response.py # Individual answer model
├── schemas/                # Pydantic validation schemas
│   ├── course.py
│   ├── feedback.py
│   └── quiz.py
├── services/               # Business logic layer
│   ├── canvas/            # Canvas API clients
│   │   ├── base.py        # Shared auth/pagination
│   │   ├── courses.py     # Course API client
│   │   ├── quizzes.py     # Quiz API client
│   │   ├── submissions.py # Submission API client
│   │   └── reports.py     # Quiz Reports CSV client
│   ├── survey_detector.py # Survey identification logic
│   ├── response_processor.py # Response parsing & categorization
│   └── feedback_aggregation.py # Metrics calculation
└── main.py                 # Application entry point

alembic/
└── versions/               # Database migrations
    ├── initial_schema.py
    └── update_unique_constraint.py
```

## Key Features

### 1. Modular Canvas API Integration

**Architecture**: 5 specialized API clients sharing common base functionality:

```python
# Base client handles auth, pagination, retries
class CanvasBaseClient:
    - Bearer token authentication
    - Automatic pagination (Link header parsing)
    - Exponential backoff retry logic
    - Async HTTP with httpx

# Specialized clients for each Canvas API resource
CanvasCoursesClient      # Course discovery
CanvasQuizzesClient      # Quiz/survey detection
CanvasSubmissionsClient  # Submission extraction
CanvasQuizReportsClient  # CSV report generation
```

**Location**: `app/services/canvas/`

### 2. Quiz Reports CSV Pipeline

**Challenge**: Canvas survey responses only accessible via CSV export with async polling.

**Implementation**:
```python
async def get_all_student_responses(course_id, quiz_id):
    # 1. Generate report
    report = await generate_report(course_id, quiz_id)

    # 2. Poll for completion (2s intervals, 5min timeout)
    csv_url = await poll_report_completion(report['id'])

    # 3. Download CSV
    df = await download_csv(csv_url)

    # 4. Parse with pandas and structure data
    return structure_responses(df)
```

**Location**: `app/services/canvas/reports.py`

### 3. Intelligent Survey Detection

Automatically identifies which Canvas quizzes are course feedback surveys:

```python
def identify_feedback_surveys(quizzes):
    # Title patterns
    patterns = ['evaluation', 'feedback', 'survey', 'satisfaction']

    # Quiz settings
    - anonymous_submissions == True
    - quiz_type == 'survey'
    - points_possible == 0

    # Confidence scoring (0.0-1.0)
    confidence = calculate_survey_confidence(quiz)

    return surveys_with_confidence_scores
```

**Location**: `app/services/survey_detector.py`

### 4. Response Text Analysis

Categorizes and flags student responses:

```python
# Auto-categorization
categories = ['course_content', 'instructor', 'technical', 'assessment']

# Text analysis
- Improvement suggestion detection
- Critical issue flagging ("broken", "urgent")
- Keyword-based classification

# Database storage with categories
feedback_responses.question_category = 'instructor'
feedback_responses.is_critical_issue = True
```

**Location**: `app/services/response_processor.py`

### 5. Advanced Database Schema

**Relationships**:
```
courses (1) -> canvas_surveys (many)
canvas_surveys (1) -> student_feedback (many)
student_feedback (1) -> feedback_responses (many)
courses (1) -> course_priorities (1)
```

**Advanced Features**:
- Composite unique constraints
- JSONB for raw data storage
- Async operations with SQLAlchemy 2.0
- Alembic migrations for schema evolution

**Models**: `app/models/`

## API Endpoints

### Course Management
```http
GET  /courses                    # List Canvas courses
GET  /courses/{id}               # Get course details
POST /courses/sync               # Sync courses from Canvas
```

### Survey Discovery
```http
POST /quizzes/sync-surveys       # Discover and identify surveys
GET  /quizzes/surveys            # List identified surveys (paginated)
GET  /quizzes/surveys/{id}       # Get survey details
```

### Student Feedback
```http
POST /feedback/sync/{survey_id}  # Extract student responses
GET  /feedback/surveys/{id}      # Get survey submissions
GET  /feedback/courses/{id}/summary    # Aggregated metrics
GET  /feedback/courses/{id}/categories # Category breakdowns
```

## Setup & Installation

### Prerequisites
- Python 3.13+
- PostgreSQL (or Neon account)
- Canvas LMS API token

### Installation

1. **Clone repository**
```bash
git clone <repo-url>
cd apps/backend
```

2. **Create virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

Required environment variables:
```env
# Database
DATABASE_URL=postgresql://user:pass@host/db

# Canvas API
CANVAS_API_TOKEN=your_token_here
CANVAS_BASE_URL=https://your-instance.instructure.com
CANVAS_ACCOUNT_ID=1

# Application
ENVIRONMENT=development
DEBUG=True
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start development server**
```bash
uvicorn app.main:app --reload --port 8000
```

API will be available at `http://localhost:8000`
Interactive docs at `http://localhost:8000/docs`

## Development Workflow

### Running the Server
```bash
# Development with auto-reload
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing Canvas Integration
```bash
# Test course discovery
curl http://localhost:8000/courses

# Test survey sync
curl -X POST http://localhost:8000/quizzes/sync-surveys

# Test feedback extraction
curl -X POST http://localhost:8000/feedback/sync/{survey_id}
```

## Architecture Decisions

### Why Async Throughout?
- Canvas API calls are I/O-bound
- Database operations benefit from async
- FastAPI supports async natively
- Better concurrency for multiple API calls

### Why Modular Canvas Clients?
- Separation of concerns (each API resource = one client)
- Shared base functionality (auth, pagination, retries)
- Easier testing and maintenance
- Clear dependency boundaries

### Why Quiz Reports CSV?
- **Only way** to get complete survey responses from Canvas
- Statistics API: No essay text for surveys
- Submissions API: Returns NULL for survey responses
- CSV export: Full data including essay responses

### Why Two Unique Constraints?
- Original: `(survey_id, submission_id)` for Submissions API
- Updated: `(survey_id, student_id)` for CSV data
- Migration preserves data integrity during transition

## Known Issues & Limitations

### Canvas API 500 Error (BLOCKER)

**Issue**: Quiz Reports API returns 500 error when generating reports.

**Impact**: Cannot extract student essay responses (critical for analysis).

**Workaround Options**:
1. Contact Canvas administrator
2. Use pre-generated CSV files
3. Fallback to Statistics API (partial data, no essays)

**Code Status**: Implementation complete, waiting for Canvas API fix.

**Details**: See CLAUDE.md "Critical Issues" section.

### Missing Components
- Priority scoring engine (business logic not implemented)
- Feedback aggregation service (partial implementation)
- Unit tests
- Integration tests
- API documentation customization

## Code Quality

**Strengths**:
- Type hints throughout
- Comprehensive docstrings
- Modular architecture
- Error handling and logging
- Migration version control

**Areas for Improvement**:
- Test coverage (0%)
- API documentation
- Monitoring/observability
- Caching layer
- Rate limiting

## Performance Considerations

**Database**:
- Indexes on foreign keys
- Indexes on frequently queried fields (timestamp, status)
- JSONB for flexible querying

**API Calls**:
- Async HTTP for concurrency
- Pagination handling for large datasets
- Retry logic with exponential backoff

**Future Optimizations**:
- Redis caching for Canvas API responses
- Background tasks for long-running syncs
- Batch processing for multiple surveys

## Contributing

This is a portfolio/contract project. For production use:

1. Add comprehensive test suite
2. Implement remaining features (priority scoring, aggregation)
3. Add monitoring and alerting
4. Set up CI/CD pipeline
5. Add API documentation
6. Implement rate limiting

## License

Contract work - All rights reserved

## Contact

For questions about this codebase, see PORTFOLIO.md for technical overview and architecture decisions.
