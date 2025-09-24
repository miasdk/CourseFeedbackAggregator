# Webhook Edge Cases & Failure Scenarios

## Survey Schema Evolution

### Field Name Changes
**Problem:** Zoho updates survey question text, breaking field mappings
```json
// Current mapping
"section_1_positive": "Your positive comments for (1): We want to be sure to keep this!"

// After Zoho update
"section_1_positive": "Your positive feedback for Section 1: Keep this content!"
```

**Impact:** Webhook receives null values, data processing fails
**Mitigation:** 
- Version field mappings with timestamps
- Fallback field name patterns
- Alert system for sudden null increases

### Survey Structure Changes
**Problem:** Survey owner adds/removes questions without updating webhook
```json
// Original: 2 sections
{
  "section_1_area": "Module 1",
  "section_2_area": "Module 2"
}

// Updated: 3 sections added
{
  "section_1_area": "Module 1", 
  "section_2_area": "Module 2",
  "section_3_area": "Module 3"  // New - not mapped in webhook
}
```

**Impact:** Data loss, incomplete processing
**Mitigation:** 
- Monitor for unmapped fields in payloads
- Dynamic field discovery alerts
- Survey change notification system

## Course Name Ambiguity

### Duplicate Course Names
**Problem:** Multiple courses with similar names
```json
{
  "course_name": "Leadership" // Which one?
}
```
**Examples:**
- "Leadership" vs "Leadership Excellence" vs "Executive Leadership"
- "Women in Leadership" vs "WIL" vs "Women Leadership"
- "Module 1" without course context

**Impact:** Wrong course attribution, data contamination
**Mitigation:**
- Require course codes in survey setup
- Fuzzy matching with confidence scores
- Manual review queue for ambiguous matches

### Course Name Evolution
**Problem:** Course names change over time
```json
// Term 1
"course_name": "Women in Leadership - Personal Assessment"

// Term 2  
"course_name": "WIL Personal Development Assessment"
```

**Impact:** Same course appears as two different courses
**Mitigation:**
- Course alias mapping table
- Historical name tracking
- Cross-reference with Canvas course IDs

## Webhook Reliability Issues

### Network Failures
**Problem:** Webhook delivery failures during high traffic
```python
# Zoho webhook timeout scenarios:
- Network latency > 30 seconds
- Server downtime during peak hours
- ngrok tunnel disconnections
- Rate limiting from hosting provider
```

**Impact:** Lost survey responses, data gaps
**Mitigation:**
- Implement webhook retry logic (exponential backoff)
- Queue system for failed deliveries
- Health check endpoints
- Multiple webhook URLs (primary/backup)

### Malformed Payloads
**Problem:** Zoho sends invalid JSON or unexpected data types
```json
// Expected
{
  "response_id": "wIf1OL8s",
  "course_name": "Leadership"
}

// Actual malformed payload
{
  "response_id": null,
  "course_name": ["Leadership", "Module 1"], // Array instead of string
  "invalid_field": "<script>alert('xss')</script>"
}
```

**Impact:** JSON parsing errors, application crashes
**Mitigation:**
- Strict input validation
- Data type checking before processing
- Sanitize all string inputs
- Fallback to raw payload storage

### Duplicate Webhook Calls
**Problem:** Zoho fires multiple webhooks for same response
```json
// Same response_id received multiple times
{
  "response_id": "wIf1OL8s", 
  "timestamp_1": "2025-09-24T10:00:00Z",
  "timestamp_2": "2025-09-24T10:00:05Z"  // 5 seconds later
}
```

**Impact:** Duplicate data processing, skewed analytics
**Mitigation:**
- Idempotent webhook processing
- Response ID deduplication
- Processing timestamps tracking
- Database unique constraints

## Survey Detection Logic Issues

### Collector Name Inconsistencies
**Problem:** Detection relies on exact collector name matches
```python
# Expected
"collector_name": "EE Instructor - Course Reviewer Worksheet"

# Actual variations
"EE Instructor Course Review"           # Missing dashes
"EE-Instructor-Course-Review"           # Different format  
"EE INSTRUCTOR COURSE REVIEWER"         # All caps
"ee instructor course reviewer"         # All lowercase
```

**Impact:** Wrong survey type detection, incorrect processing
**Mitigation:**
- Normalize collector names (lowercase, remove special chars)
- Multiple detection criteria (not just collector name)
- Confidence scoring for survey type detection
- Manual review queue for unmatched surveys

### Field Overlap Between Survey Types
**Problem:** Different surveys share common field names
```json
// Both surveys have similar fields but different meanings
// Chief Advisor Survey
{
  "course_overview_rating": "5",  // 5-point scale
  "module_1_rating": "Excellent"
}

// Course Review Worksheet  
{
  "section_1_overall_rating": "5",      // Same scale, different context
  "section_1_showstopper": "Excellent"  // Wrong field type
}
```

**Impact:** Misclassification, wrong processing logic applied
**Mitigation:**
- Use unique field combinations for detection
- Survey ID-based routing instead of field detection
- Validation rules per survey type
- Processing confidence indicators

## High Volume Scenarios

### Batch Survey Submissions
**Problem:** 100+ responses submitted simultaneously
```python
# Webhook flood scenario
- 150 webhook calls in 30 seconds
- Server overwhelmed, timeouts occur
- Some responses processed, others lost
- No way to identify which ones failed
```

**Impact:** Partial data loss, inconsistent state
**Mitigation:**
- Rate limiting on webhook endpoint
- Queue-based processing (Redis/RabbitMQ)
- Batch processing capabilities
- Response tracking and retry logic

### Survey Response Spikes
**Problem:** Unexpected high-volume periods
```python
# Examples:
- End of semester survey push (500+ responses/hour)
- Marketing campaign drives survey completions
- Automated survey distribution from Canvas LMS
```

**Impact:** System overload, processing delays
**Mitigation:**
- Auto-scaling infrastructure
- Processing queue monitoring
- Alert thresholds for unusual volumes
- Graceful degradation strategies

## Data Quality Issues

### Incomplete Responses
**Problem:** Required fields missing due to survey logic
```json
{
  "response_id": "abc123",
  "course_name": "",           // Empty required field
  "section_1_area": null,      // Null value
  "section_1_improvements": "  " // Whitespace only
}
```

**Impact:** Processing failures, incomplete data analysis
**Mitigation:**
- Field validation with specific error messages
- Graceful handling of empty/null values
- Data completeness scoring
- Follow-up data collection strategies

### Encoding Issues
**Problem:** Special characters in survey responses
```json
{
  "section_1_improvements": "The café's Wi-Fi is causing issues with thé video playback — students can't access course materials properly."
}
```

**Impact:** Character encoding errors, data corruption
**Mitigation:**
- UTF-8 encoding enforcement
- Character sanitization
- Special character handling
- Input length limits

## Security & Privacy Concerns

### Data Exposure
**Problem:** Webhook URLs accessible without authentication
```python
# Anyone can POST to webhook endpoint
POST /webhooks/zoho-survey
{
  "fake_data": "malicious_payload"
}
```

**Impact:** Data injection, system abuse
**Mitigation:**
- Webhook signature verification
- IP address whitelisting (Zoho servers only)
- Rate limiting per IP
- Input validation and sanitization

### PII Handling
**Problem:** Personal information in survey responses
```json
{
  "reviewer_email": "john.doe@company.com",
  "section_1_improvements": "John Smith in accounting told me the system crashes when he enters his SSN 123-45-6789"
}
```

**Impact:** Privacy violations, compliance issues
**Mitigation:**
- PII detection and redaction
- Data retention policies
- Encryption at rest and in transit
- Access controls and audit logs