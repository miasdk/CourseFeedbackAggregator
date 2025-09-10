# Course Feedback Aggregator - System Architecture

## Overall System Architecture

```mermaid
graph TB
    %% External Data Sources
    subgraph "External APIs"
        A1[Canvas LMS API<br/>executiveeducation.instructure.com]
        A2[Zoho CRM API<br/>www.zohoapis.com]
    end
    
    %% Frontend Layer
    subgraph "Frontend - Vercel"
        B1[React TypeScript App]
        B2[Priority Dashboard]
        B3[Admin Panel]
        B4[Weight Configuration]
    end
    
    %% Backend Layer - Railway
    subgraph "Backend API - Railway"
        subgraph "FastAPI MVC Architecture"
            C1[Controllers Layer<br/>API Endpoints]
            C2[Services Layer<br/>Business Logic]
            C3[Models Layer<br/>Database Models]
            C4[Views Layer<br/>Response Serializers]
        end
        
        C5[Canvas API Client]
        C6[Zoho API Client]
        C7[Priority Scoring Engine]
        C8[Data Ingestion Service]
    end
    
    %% Database Layer
    subgraph "Database - Neon PostgreSQL"
        D1[(Feedback Table)]
        D2[(Priorities Table)]
        D3[(Weight Configs Table)]
        D4[(Reviews Table)]
        D5[(Courses Table)]
    end
    
    %% Data Flow
    A1 --> C5
    A2 --> C6
    
    C5 --> C8
    C6 --> C8
    C8 --> D1
    C8 --> D5
    
    D1 --> C7
    D3 --> C7
    D5 --> C7
    C7 --> D2
    
    C1 --> C2
    C2 --> C3
    C3 --> D1
    C3 --> D2
    C3 --> D3
    C3 --> D4
    C3 --> D5
    
    C2 --> C4
    C4 --> B1
    
    B1 --> C1
    B2 --> C1
    B3 --> C1
    B4 --> C1
    
    D2 --> D4
```

## MVC Backend Architecture Detail

```mermaid
graph TB
    %% API Layer (Controllers)
    subgraph "Controllers Layer"
        CA[Feedback Controller<br/>/api/v1/feedback]
        CB[Priority Controller<br/>/api/v1/priorities]
        CC[Weight Controller<br/>/api/v1/weights]
        CD[Ingestion Controller<br/>/api/v1/ingest]
        CE[Review Controller<br/>/api/v1/reviews]
    end
    
    %% Business Logic (Services)
    subgraph "Services Layer"
        SA[FeedbackService<br/>CRUD Operations]
        SB[PriorityService<br/>Scoring Algorithm]
        SC[IngestionService<br/>Data Processing]
        SD[CanvasAPIService<br/>External API Client]
        SE[ZohoAPIService<br/>External API Client]
        SF[ScoringService<br/>Priority Calculation]
    end
    
    %% Data Access (Models)
    subgraph "Models Layer"
        MA[Feedback Model]
        MB[Priority Model]
        MC[WeightConfig Model]
        MD[Review Model]
        ME[Course Model]
    end
    
    %% Response Formatting (Views)
    subgraph "Views Layer"
        VA[FeedbackResponse Schema]
        VB[PriorityResponse Schema]
        VC[WeightConfigResponse Schema]
        VD[IngestionResponse Schema]
        VE[ReviewResponse Schema]
    end
    
    %% Relationships
    CA --> SA
    CB --> SB
    CC --> SA
    CD --> SC
    CE --> SA
    
    SA --> MA
    SB --> MB
    SB --> MC
    SC --> SD
    SC --> SE
    SF --> MA
    SF --> MB
    SF --> MC
    
    SA --> VA
    SB --> VB
    SA --> VC
    SC --> VD
    SA --> VE
```

## Data Ingestion Flow

```mermaid
sequenceDiagram
    participant Admin
    participant API as FastAPI Backend
    participant Canvas as Canvas LMS
    participant Zoho as Zoho CRM  
    participant DB as Neon PostgreSQL
    participant Scoring as Priority Engine
    
    %% Canvas Ingestion
    Admin->>+API: POST /api/v1/ingest/canvas
    API->>+Canvas: GET /courses/{id}/discussion_topics
    Canvas-->>-API: Discussion data
    API->>+Canvas: GET /courses/{id}/assignments
    Canvas-->>-API: Assignment comments
    
    API->>+DB: INSERT INTO feedback (source='canvas')
    API->>+DB: INSERT INTO courses
    DB-->>-API: Success
    
    %% Zoho Ingestion  
    API->>+Zoho: GET /crm/v2/Deals
    Zoho-->>-API: Deal/Program data
    API->>+Zoho: GET /survey/v1/responses
    Zoho-->>-API: Survey responses
    
    API->>+DB: INSERT INTO feedback (source='zoho')
    DB-->>-API: Success
    
    %% Priority Calculation
    API->>+Scoring: Calculate priorities
    Scoring->>+DB: SELECT FROM feedback WHERE course_id
    DB-->>-Scoring: Feedback data
    Scoring->>+DB: SELECT FROM weight_configs WHERE is_active
    DB-->>-Scoring: Weight configuration
    
    Scoring-->>API: Priority recommendations
    API->>+DB: INSERT INTO priorities
    DB-->>-API: Success
    
    API-->>-Admin: Ingestion complete
```

## Deployment Architecture

### Frontend Deployment (Vercel)
```yaml
Platform: Vercel
Framework: React 18 + TypeScript + Vite
Domain: coursefeedback-app.vercel.app
Environment Variables:
  - VITE_API_BASE_URL=https://coursefeedback-api.railway.app
Build Command: npm run build
Output Directory: dist
```

### Backend Deployment (Railway)
```yaml
Platform: Railway
Framework: FastAPI + Python 3.11
Domain: coursefeedback-api.railway.app
Environment Variables:
  - DATABASE_URL=postgresql://neondb_owner:***@ep-misty-pond-adzovwj0-pooler...
  - CANVAS_ACCESS_TOKEN=15908~***
  - ZOHO_CLIENT_ID=1000.***
  - ZOHO_ACCESS_TOKEN=1000.***
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Database (Neon PostgreSQL)
```yaml
Platform: Neon
Engine: PostgreSQL 15
Connection: Pooled connection with SSL
Region: US East 1 (AWS)
Scaling: Autoscaling enabled
Backup: Automated daily backups
```

## API Endpoint Structure

### Core API Endpoints
```
GET    /api/v1/health                    # Health check
GET    /api/v1/feedback                  # List all feedback
POST   /api/v1/feedback                  # Create feedback entry
GET    /api/v1/feedback/{id}             # Get specific feedback

GET    /api/v1/priorities                # List priority recommendations
POST   /api/v1/priorities/recompute      # Trigger priority recalculation
GET    /api/v1/priorities/{id}           # Get specific priority
POST   /api/v1/priorities/{id}/review    # Submit priority review

GET    /api/v1/weights                   # Get active weight configuration
PUT    /api/v1/weights                   # Update weight configuration
GET    /api/v1/weights/history           # Weight change history

POST   /api/v1/ingest/canvas             # Trigger Canvas data ingestion
POST   /api/v1/ingest/zoho               # Trigger Zoho data ingestion
GET    /api/v1/ingest/status             # Get ingestion status

GET    /api/v1/courses                   # List courses
GET    /api/v1/courses/{id}/analytics    # Course analytics
```

### API Response Format
```json
{
  "success": true,
  "data": {
    "id": 123,
    "course_id": "canvas_847", 
    "issue_summary": "Video quality issues affecting student comprehension",
    "priority_score": 8,
    "scoring_breakdown": {
      "impact_score": 9.2,
      "urgency_score": 8.5,
      "effort_score": 6.0,
      "strategic_score": 7.0,
      "trend_score": 8.0
    },
    "evidence": {
      "student_quotes": [...],
      "source_links": [...],
      "affected_students": 23
    }
  },
  "metadata": {
    "timestamp": "2025-09-10T12:00:00Z",
    "version": "1.0.0"
  }
}
```

## Security Architecture

### Authentication & Authorization
```mermaid
graph LR
    A[Frontend Request] --> B[API Gateway]
    B --> C{API Key Valid?}
    C -->|Yes| D[Route to Controller]
    C -->|No| E[Return 401]
    
    D --> F{Admin Endpoint?}
    F -->|Yes| G{Admin Token?}
    F -->|No| H[Process Request]
    G -->|Yes| H
    G -->|No| I[Return 403]
```

### Data Protection
- **API Keys**: Canvas/Zoho tokens stored as Railway environment variables
- **Database**: SSL-required connections to Neon PostgreSQL
- **Student Data**: Email/name fields support anonymization
- **CORS**: Restricted to frontend domain only

## Performance & Scaling

### Database Optimization
- **Connection Pooling**: AsyncPG with 20 max connections
- **Indexes**: Strategic indexes on frequently queried columns
- **Query Optimization**: Async/await patterns for all database operations

### API Performance
- **Rate Limiting**: 100 requests/10 seconds per IP
- **Caching**: Redis caching for expensive scoring calculations (future)
- **Async Processing**: Background jobs for data ingestion

### Monitoring
- **Health Checks**: `/health` endpoint for Railway monitoring
- **Error Tracking**: Structured logging for debugging
- **Analytics**: API usage metrics and response times

## Environment Configuration

### Development
```bash
DATABASE_URL=postgresql://localhost:5432/coursefeedback_dev
CANVAS_ACCESS_TOKEN=dev_token
ENVIRONMENT=development
DEBUG=True
```

### Production
```bash
DATABASE_URL=postgresql://neondb_owner:***@ep-misty-pond-adzovwj0-pooler...
CANVAS_ACCESS_TOKEN=15908~***
ENVIRONMENT=production  
DEBUG=False
```

## Migration & Deployment Pipeline

### Development Workflow
1. **Local Development**: SQLite for rapid iteration
2. **Feature Branch**: Deploy to Railway preview environment
3. **Testing**: Automated API tests against preview database
4. **Production**: Merge to main triggers production deployment

### Database Migrations
```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Add new column"
```

This architecture ensures scalability, maintainability, and clear separation of concerns while providing full traceability from external APIs to frontend recommendations.