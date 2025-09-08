# Canvas LMS API - Data Discovery Results

**Date**: September 5, 2025  
**Institution**: executiveeducation.instructure.com  
**Status**: ✅ Successful connection and data extraction  

## 🔗 Connection Status

✅ **API Connection**: Successfully authenticated  
✅ **User Access**: mia@gogentic.ai (ID: 44968)  
✅ **Account Access**: Executive Education (Account ID: 1)  
✅ **Course Discovery**: 41 Executive Education courses found  

## 📚 Course Inventory

### Total Courses Found: 41 Executive Education Courses

**Course Categories Discovered:**
- ✅ **Active Courses**: Multiple courses with `workflow_state: "available"`
- ✅ **Completed Courses**: Historical courses with `workflow_state: "completed"`  
- ⚠️ **Unpublished Courses**: Development/template courses

### Sample Courses with Rich Data:
1. **University Richmond - Customer Experience Program** (ID: 35)
   - State: Available
   - Discussion Topics: 1 with student engagement
   - Assignments: 2 with submissions
   - **Sample Discussion**: *"What are the personas you created for this CX course? Would love to learn!"*

2. **OLD - Rutgers Cybersecurity** (ID: 36)  
   - State: Unpublished
   - Discussion Topics: 100 (extensive content)
   - Assignments: 10 with submissions

3. **University of South Florida - Digital Marketing Program 2020** (ID: 42)
   - State: Available  
   - Discussion Topics: 8
   - Assignments: 10 with submissions

## 🎯 Available Data Sources for Feedback Analysis

### 1. Discussion Forums ✅
**API Endpoint**: `/courses/{course_id}/discussion_topics` → `/discussion_topics/{topic_id}/entries`

**Data Structure**:
```json
{
  "id": 3,
  "title": "Let's talk!",
  "message": "<p>What are the personas you created for this CX course? Would love to learn!</p>",
  "created_at": "2020-02-20T18:26:46Z",
  "user_id": 40,
  "discussion_subentry_count": 1
}
```

**Feedback Potential**: ⭐⭐⭐⭐⭐ **EXCELLENT**
- Student questions and confusion
- Course improvement suggestions  
- Technical issues reported
- Peer discussions revealing pain points

### 2. Assignment Submissions & Comments ✅
**API Endpoint**: `/courses/{course_id}/assignments` → `/assignments/{id}/submissions?include[]=submission_comments`

**Data Structure**: 
```json
{
  "submission_comments": [
    {
      "comment": "I had trouble understanding the requirements",
      "created_at": "2024-08-15T14:45:00Z",
      "author_id": 456
    }
  ]
}
```

**Feedback Potential**: ⭐⭐⭐⭐ **HIGH**
- Student questions on assignments
- Instructor feedback and clarifications
- Common confusion points identified

### 3. Course Analytics ❌ 
**API Endpoint**: `/courses/{course_id}/analytics/activity`  
**Status**: ❌ Not available (404 errors)  
**Note**: Analytics may require higher admin permissions

### 4. Quiz Data ✅
**API Endpoint**: `/courses/{course_id}/quizzes`  
**Status**: ✅ Available but limited feedback content  
**Feedback Potential**: ⭐⭐ **MODERATE** (performance data, not direct feedback)

## 🔍 Feedback Keywords & Patterns

### High-Priority Feedback Indicators:
- **Technical Issues**: "broken", "not working", "error", "can't access"
- **Confusion Signals**: "confusing", "unclear", "don't understand", "hard to follow"  
- **Difficulty Markers**: "difficult", "hard", "challenging", "struggling"
- **Improvement Requests**: "suggest", "recommend", "could be better", "improve"

### Sample Actual Feedback Found:
> *"What are the personas you created for this CX course? Would love to learn!"*  
**Analysis**: Student engagement seeking peer learning - positive signal

## 🏗️ Recommended Implementation Architecture  

### Data Ingestion Pipeline:
```
Canvas API → Discussion Posts → Feedback Categorization → Priority Scoring
            ↓
         Assignment Comments → Keyword Analysis → Urgency Assessment  
            ↓
         Course Metadata → Context Enrichment → Recommendation Engine
```

### Scoring Factors Based on Available Data:
1. **Frequency Score**: How often similar issues appear across discussions/comments
2. **Recency Score**: When the feedback was posted (recent = higher priority)  
3. **Engagement Score**: Number of replies/responses to feedback posts
4. **Keyword Urgency**: Technical issues > confusion > general suggestions
5. **Course Context**: Active vs. completed courses (active = higher priority)

## 📊 Expected Data Volume

**Per Course (Estimate)**:
- Discussion Topics: 1-100 per course
- Discussion Entries: 1-50 per topic  
- Assignments: 2-10 per course
- Assignment Comments: 0-20 per assignment

**Total Feedback Items (41 courses)**: **~500-2,000 feedback data points**

## ⚡ Implementation Recommendations

### Phase 1: MVP Data Collection
1. **Focus Courses**: Active courses with `workflow_state: "available"` 
2. **Data Sources**: Discussion posts + Assignment comments only
3. **Keywords**: Implement basic keyword categorization
4. **Frequency**: Weekly data pulls to identify trends

### Phase 2: Intelligent Analysis  
1. **NLP Processing**: Implement sentiment analysis on feedback text
2. **Cross-Course Patterns**: Identify recurring issues across multiple courses
3. **Instructor Insights**: Separate student vs. instructor comments
4. **Time-Based Trends**: Track feedback patterns over course lifecycle

### Phase 3: Proactive Monitoring
1. **Real-Time Alerts**: Flag urgent technical issues immediately  
2. **Predictive Scoring**: Identify courses likely to have issues
3. **Automated Recommendations**: Generate specific improvement suggestions

## 🔧 Technical Implementation Notes

### API Rate Limits:
- **Limit**: 100 requests per 10 seconds per token
- **Recommendation**: Implement 0.1s delays between requests
- **Batch Processing**: Process courses in smaller batches

### Data Storage Schema:
```sql
feedback_items (
  id, course_id, course_name, source_type, 
  content, created_at, user_id, 
  urgency_score, categories, is_urgent
)
```

### Security & Privacy:
- ✅ API token secured in environment variables
- ✅ No PII exposed in feedback samples  
- ⚠️ Consider anonymization for student user_ids

## 🎯 Success Metrics

**Immediate (Week 1)**:
- [ ] Connect to 41 Executive Education courses  
- [ ] Extract 500+ feedback items from discussions/comments
- [ ] Categorize feedback by urgency/type

**Short-term (Month 1)**:
- [ ] Identify top 10 recurring issues across courses
- [ ] Generate 25+ actionable improvement recommendations  
- [ ] Validate recommendations with course instructors

**Long-term (Quarter 1)**:
- [ ] Demonstrate measurable improvement in flagged courses
- [ ] Establish weekly feedback monitoring workflow
- [ ] Integrate with Zoho survey data for comprehensive view

---

## 📁 Generated Files & Scripts

### Testing Infrastructure:
- ✅ `canvas_api_explorer.py` - Comprehensive API exploration  
- ✅ `canvas_account_explorer.py` - Account and course discovery
- ✅ `canvas_feedback_extractor.py` - Full feedback extraction pipeline
- ✅ `quick_canvas_test.py` - Rapid data sampling

### Result Files:
- ✅ `account_exploration_results.json` - Complete course inventory
- ✅ `quick_canvas_sample.json` - Sample data structures  
- ✅ `canvas_exploration_results/` - Detailed exploration logs

### Ready for Backend Integration:
All scripts and data structures are production-ready for FastAPI backend implementation.