# Canvas LMS API Connection Tutorial

## Quick Start Guide

### What You Have
- **Access Token:** `15908~DCn33yJkTvcwhKMBZRxwrZVUffFDvWVwW7uM7FKRJUVVhRLehvEJRvBBENcHED`
- **Institution:** executiveeducation.instructure.com
- **Admin Access:** mia@gogentic.ai (ID: 44968)

### Goal
Connect to Canvas LMS API and extract course feedback data (discussions, assignments, analytics) for your aggregation system.

---

## Step 1: Test Your Connection

### Basic Connection Test
```bash
curl "https://executiveeducation.instructure.com/api/v1/users/self" \
  -H "Authorization: Bearer 15908~DCn33yJkTvcwhKMBZRxwrZVUffFDvWVwW7uM7FKRJUVVhRLehvEJRvBBENcHED"
```

**Expected Response:**
```json
{
  "id": 44968,
  "name": "mia@gogentic.ai",
  "email": "mia@gogentic.ai",
  "login_id": "mia@gogentic.ai"
}
```

### Python Test (Optional)
```python
import requests

headers = {"Authorization": "Bearer 15908~DCn33yJkTvcwhKMBZRxwrZVUffFDvWVwW7uM7FKRJUVVhRLehvEJRvBBENcHED"}
response = requests.get("https://executiveeducation.instructure.com/api/v1/users/self", headers=headers)

if response.status_code == 200:
    print("✅ Connected to Canvas!")
    print(response.json())
else:
    print(f"❌ Connection failed: {response.status_code}")
```

---

## Step 2: Access Executive Education Courses

### Get All Accessible Courses
```bash
curl "https://executiveeducation.instructure.com/api/v1/courses?per_page=50&include[]=teachers&include[]=total_students&enrollment_state=active" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Troubleshoot Course Access
If you only see test courses, try these approaches:

**Check All Enrollment Types:**
```bash
curl "https://executiveeducation.instructure.com/api/v1/courses?enrollment_type[]=teacher&enrollment_type[]=ta&enrollment_type[]=student&enrollment_type[]=observer&per_page=100" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Check Account Context:**
```bash
curl "https://executiveeducation.instructure.com/api/v1/accounts" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Check by Account ID:**
```bash
curl "https://executiveeducation.instructure.com/api/v1/accounts/ACCOUNT_ID/courses" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Step 3: Extract Course Feedback Data

### 1. Discussion Posts (Primary Feedback Source)

**Get Discussion Topics:**
```bash
curl "https://executiveeducation.instructure.com/api/v1/courses/COURSE_ID/discussion_topics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get Discussion Entries (Student Posts):**
```bash
curl "https://executiveeducation.instructure.com/api/v1/courses/COURSE_ID/discussion_topics/TOPIC_ID/entries" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Assignment Submissions & Comments

**Get Assignments:**
```bash
curl "https://executiveeducation.instructure.com/api/v1/courses/COURSE_ID/assignments" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get Submission Comments:**
```bash
curl "https://executiveeducation.instructure.com/api/v1/courses/COURSE_ID/assignments/ASSIGNMENT_ID/submissions?include[]=submission_comments" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 3. Quiz Performance & Feedback

**Get Quizzes:**
```bash
curl "https://executiveeducation.instructure.com/api/v1/courses/COURSE_ID/quizzes" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get Quiz Statistics:**
```bash
curl "https://executiveeducation.instructure.com/api/v1/courses/COURSE_ID/quizzes/QUIZ_ID/statistics" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Course Analytics (Engagement Issues)

**Get Course Activity:**
```bash
curl "https://executiveeducation.instructure.com/api/v1/courses/COURSE_ID/analytics/activity" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Get Student Summaries:**
```bash
curl "https://executiveeducation.instructure.com/api/v1/courses/COURSE_ID/analytics/student_summaries" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Step 4: Find Feedback Keywords

### Search Discussion Posts for Issues
Look for posts containing feedback keywords:
- "confusing", "unclear", "difficult"
- "problem", "issue", "error"
- "suggest", "improve", "better"
- "broken", "not working", "can't access"

### Extract Show-Stopper Issues
High-priority keywords indicating urgent problems:
- "broken", "not working", "error", "crash"
- "cannot access", "can't load", "missing"
- "completely confused", "makes no sense"

---

## Essential Documentation Links

### Core API References
- **Canvas API Documentation:** https://canvas.instructure.com/doc/api/
- **Live API Explorer:** https://canvas.instructure.com/doc/api/live
- **Developer Guide:** https://canvas.instructure.com/doc/api/file.api_quickstart.html

### Course Content APIs
- **Courses API:** https://canvas.instructure.com/doc/api/courses.html
- **Assignments API:** https://canvas.instructure.com/doc/api/assignments.html
- **Discussions API:** https://canvas.instructure.com/doc/api/discussion_topics.html
- **Submissions API:** https://canvas.instructure.com/doc/api/submissions.html
- **Quizzes API:** https://canvas.instructure.com/doc/api/quizzes.html

### Analytics & Data
- **Analytics API:** https://canvas.instructure.com/doc/api/analytics.html
- **Users API:** https://canvas.instructure.com/doc/api/users.html
- **Modules API:** https://canvas.instructure.com/doc/api/modules.html

### Advanced Features
- **GraphQL API:** https://canvas.instructure.com/doc/api/file.graphql.html
- **Pagination Guide:** https://canvas.instructure.com/doc/api/file.pagination.html
- **Rate Limiting:** https://canvas.instructure.com/doc/api/file.throttling.html

---

## Rate Limits & Best Practices

### API Limits
- **Rate Limit:** 100 requests per 10 seconds per access token
- **Pagination:** Use `per_page=100` for efficient data retrieval
- **Headers:** Check `X-Rate-Limit-Remaining` in response headers

### Best Practices
```bash
# Add delay between requests
sleep 0.1

# Use pagination efficiently  
curl "URL?page=1&per_page=100"

# Include necessary data in one request
curl "URL?include[]=teachers&include[]=students&include[]=term"
```

---

## Common Issues & Solutions

### Issue: Only Seeing Test Courses
**Possible Causes:**
1. **Token scope limited** - Ask Matthew for broader permissions
2. **Not enrolled in Executive Education courses** - Request enrollment as instructor/admin
3. **Wrong account context** - Check account hierarchy

**Solution:** Contact Matthew with:
> "I can connect to Canvas but only see test courses. I need access to the 25 Executive Education courses mentioned in our project spec. Do I need different permissions or enrollment?"

### Issue: 401 Unauthorized
**Solutions:**
1. Check token format: `Bearer TOKEN` not `Bearer: TOKEN`
2. Verify token hasn't expired
3. Test with `/api/v1/users/self` endpoint first

### Issue: 403 Forbidden
**Solution:** Insufficient permissions - contact Canvas admin for course access

### Issue: Empty Discussion/Assignment Lists
**Cause:** Course may not have content yet or you lack permissions
**Solution:** Try with different courses or request content access

---

## Data Structure Examples

### Discussion Entry (Feedback Source)
```json
{
  "id": 123,
  "user_id": 456,
  "message": "The module 3 instructions are really confusing. Could we get clearer examples?",
  "created_at": "2024-08-15T10:30:00Z",
  "parent_id": null
}
```

### Assignment Submission Comment
```json
{
  "id": 789,
  "comment": "I had trouble understanding the requirements for this assignment",
  "created_at": "2024-08-15T14:45:00Z",
  "author_id": 456
}
```

### Course Analytics
```json
{
  "views": 150,
  "participations": 45,
  "date": "2024-08-15",
  "participation_rate": 0.30
}
```

---

## Next Steps for Your Project

1. **Resolve course access** - Contact Matthew about Executive Education course permissions
2. **Test data extraction** - Use the API calls above to get sample data
3. **Identify feedback patterns** - Look for discussion posts with feedback keywords
4. **Combine with Zoho data** - Merge Canvas discussions/comments with Zoho survey responses
5. **Build prioritization logic** - Score feedback by urgency, impact, and frequency

### Expected Canvas Feedback Data
Once you have proper course access, you'll extract:
- Student discussion posts about course issues
- Assignment submission comments with problems
- Quiz performance indicating content difficulty  
- Analytics showing engagement drop-offs
- Module-specific feedback and suggestions

This combines with Zoho CRM survey data to power your "what to fix first" course prioritization system.