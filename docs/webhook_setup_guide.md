# Webhook Setup & Testing Guide

## Prerequisites

### Required Tools
- **ngrok**: Public tunnel to local development server
- **FastAPI**: Backend server running locally
- **Postman/curl**: Testing webhook payloads (optional)
- **Zoho Survey Account**: Admin access to create webhooks

### Local Development Setup
```bash
# Install dependencies
pip install fastapi uvicorn python-multipart

# Clone your project
git clone <your-repo-url>
cd <project-directory>

# Install project dependencies
pip install -r requirements.txt
```

## Step 1: Start Local Backend Server

### Run FastAPI Development Server
```bash
# Navigate to project directory
cd /path/to/your/project

# Start the server
uvicorn main:app --reload --port 8000

# Verify server is running
curl http://localhost:8000/health
```

**Expected Output:**
```json
{"status": "healthy", "timestamp": "2025-09-24T10:00:00Z"}
```

### Verify Webhook Endpoint
```bash
# Test webhook endpoint exists
curl -X POST http://localhost:8000/webhooks/zoho-survey \
  -H "Content-Type: application/json" \
  -d '{"test": "payload"}'
```

**Expected Response:**
```json
{"status": "received", "response_id": null, "survey_type": "unknown_survey_type"}
```

## Step 2: Setup ngrok Tunnel

### Install ngrok
```bash
# macOS (using Homebrew)
brew install ngrok/ngrok/ngrok

# Windows (using Chocolatey)
choco install ngrok

# Linux (manual installation)
wget https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
unzip ngrok-stable-linux-amd64.zip
sudo mv ngrok /usr/local/bin
```

### Create ngrok Account & Setup Auth Token
1. Visit [ngrok.com](https://ngrok.com) and create account
2. Get your auth token from dashboard
3. Configure locally:
```bash
ngrok authtoken YOUR_AUTHTOKEN_HERE
```

### Start ngrok Tunnel
```bash
# Create tunnel to local server
ngrok http 8000

# Keep this terminal open - ngrok must run continuously
```

**Expected Output:**
```
ngrok by @inconshreveable

Session Status    online
Account           your-email@domain.com
Update            update available (version 3.x.x, Ctrl-C to stop)
Version           3.1.0
Region            United States (us)
Web Interface     http://127.0.0.1:4040
Forwarding        https://abc123.ngrok-free.app -> http://localhost:8000
```

### Important ngrok URLs
- **Public webhook URL**: `https://abc123.ngrok-free.app/webhooks/zoho-survey`
- **Web interface**: `http://127.0.0.1:4040` (to monitor requests)

## Step 3: Configure Zoho Survey Webhook

### Access Survey Webhook Settings
1. Log into Zoho Survey (zschool organization)
2. Navigate to your survey (e.g., "Chief Advisor - Course Review Worksheet")
3. Go to **Integrations > Webhook**
4. Click **"Create New Webhook"** or edit existing

### Webhook Configuration Form

**Name:** 
```
chief_advisor_course_review
```

**POST URL:**
```
https://your-ngrok-url.ngrok-free.app/webhooks/zoho-survey
```
*Replace `your-ngrok-url` with your actual ngrok subdomain*

**Request Body Format:** Select **JSON**

### JSON Request Body Configuration

**For Chief Advisor Survey:**
```json
{
  "reviewer_first_name": "First Name",
  "reviewer_last_name": "Last Name",
  "reviewer_title": "Title",
  "reviewer_company": "Company",
  "reviewer_email": "Email",
  "course_name": "Which course are you reviewing?",
  "course_overview_rating": "What is the overall rating for Course Overview?",
  "course_overview_positive": "Your positive comments for Course Overview: We want to be sure to keep this!",
  "course_overview_improvements": "Opportunities to improve (if any): Let's make this course better!",
  "module_1_rating": "What is the overall rating for Module 1?",
  "module_1_positive": "Your positive comments for Module 1: We want to be sure to keep this!",
  "module_1_improvements": "Opportunities to improve for Module 1 (if any): Let's make this course better!",
  "response_id": "Response ID",
  "response_start_time": "Response start time"
}
```

**For Course Review Worksheet:**
```json
{
  "reviewer_first_name": "First Name",
  "reviewer_last_name": "Last Name", 
  "reviewer_email": "Email",
  "course_name": "What course are you reviewing?",
  "section_1_area": "What part of the course are you reviewing for (1)?",
  "section_1_overall_rating": "What is the overall rating for (1)?",
  "section_1_positive": "Your positive comments for (1): We want to be sure to keep this!",
  "section_1_improvements": "Opportunities to improve for (1): Let's make this course better!",
  "section_1_showstopper": "Per opportunities to improve (1), is this a show stopper?",
  "response_id": "Response ID",
  "response_start_time": "Response start time"
}
```

### Save Webhook Configuration
1. Click **"Save"** or **"Create Webhook"**
2. Note the webhook status should show **"Active"**
3. Record the webhook ID for tracking

## Step 4: Test Webhook Integration

### Method 1: Submit Test Survey Response
1. Open survey in browser: `https://survey.zoho.com/zs/survey-preview/SURVEY_ID`
2. Fill out test response with dummy data:
   - Course: "Test Course 123"
   - Reviewer: "Test User"
   - Feedback: "This is a test response"
3. Submit survey
4. Monitor webhook reception

### Method 2: Monitor ngrok Web Interface
1. Open `http://127.0.0.1:4040` in browser
2. Watch for incoming POST requests to `/webhooks/zoho-survey`
3. Inspect request/response details
4. Verify JSON payload structure

### Method 3: Check Backend Logs
Monitor your FastAPI server terminal for webhook log output:
```
============================================================
WEBHOOK RECEIVED - CHIEF ADVISOR COURSE REVIEW
============================================================
Course: Test Course 123
Reviewer: Test
Response ID: wIf1OL8s
Survey Type: chief_advisor_course_review
Time: 2025-09-24 10:15:30 UTC

Full Payload:
{
  "reviewer_first_name": "Test",
  "course_name": "Test Course 123",
  "response_id": "wIf1OL8s"
  ...
}
============================================================
```

## Step 5: Troubleshooting Common Issues

### Webhook Not Receiving Data

**Check ngrok tunnel:**
```bash
curl -X GET https://your-ngrok-url.ngrok-free.app/health
```

**Verify endpoint path:**
- Webhook URL: `https://abc123.ngrok-free.app/webhooks/zoho-survey`
- NOT: `https://abc123.ngrok-free.app/webhook/zoho-survey` (missing 's')

**Check Zoho webhook status:**
1. Return to Zoho Survey webhook settings
2. Verify status shows "Active"
3. Check for error messages or failed delivery attempts

### JSON Parsing Errors

**Common causes:**
- Missing required fields in JSON configuration
- Incorrect field name mapping
- Special characters in survey questions

**Debug steps:**
1. Check raw payload in ngrok web interface
2. Validate JSON structure using online JSON validator
3. Compare actual field names with expected mappings

### Server Errors (500 responses)

**Check backend logs for Python stack traces:**
```bash
# Look for errors in your terminal running uvicorn
# Common issues:
# - Missing imports
# - Database connection errors
# - Invalid data type processing
```

**Test with minimal payload:**
```bash
curl -X POST https://your-ngrok-url.ngrok-free.app/webhooks/zoho-survey \
  -H "Content-Type: application/json" \
  -d '{
    "response_id": "test123",
    "course_name": "Test Course",
    "reviewer_first_name": "Test User"
  }'
```

### ngrok Session Expired

**Problem:** ngrok URL changes when restarted
**Solution:** 
1. Restart ngrok: `ngrok http 8000`
2. Get new URL from terminal output
3. Update Zoho webhook POST URL with new ngrok URL
4. Test again

### Webhook Timeouts

**Symptoms:** Zoho shows "delivery failed" or timeout errors
**Causes:** 
- Slow database operations in webhook handler
- Network connectivity issues
- Server overloaded

**Solutions:**
1. Optimize webhook processing speed (< 5 seconds)
2. Use async database operations
3. Return HTTP 200 immediately, process data asynchronously
4. Add request timeout monitoring

## Step 6: Production Deployment Considerations

### Replace ngrok with Production URL
Once testing is complete, replace ngrok URL with production server:
```bash
# Production webhook URL format
https://your-domain.com/webhooks/zoho-survey

# Update in Zoho Survey webhook settings
# Test with production environment
```

### Security Hardening
```python
# Add to production webhook handler
@router.post("/webhooks/zoho-survey")
async def receive_zoho_webhook(request: Request):
    # Verify webhook source
    client_ip = request.client.host
    if client_ip not in ALLOWED_ZOHO_IPS:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Rate limiting
    # Authentication headers
    # Input validation
```

### Monitoring & Alerting
- Set up uptime monitoring for webhook endpoint
- Configure alerts for webhook delivery failures
- Monitor response processing times
- Track webhook volume and patterns

## Testing Checklist

- [ ] Local FastAPI server running (port 8000)
- [ ] ngrok tunnel active and accessible
- [ ] Zoho webhook configured with correct ngrok URL
- [ ] JSON field mappings match survey questions exactly
- [ ] Test survey submission triggers webhook
- [ ] Backend logs show structured data processing
- [ ] Response processing completes without errors
- [ ] Survey type detection working correctly
- [ ] ngrok web interface shows successful POST requests
- [ ] All required fields present in webhook payload