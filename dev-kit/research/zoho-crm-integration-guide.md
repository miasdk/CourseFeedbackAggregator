# Zoho CRM API Connection Tutorial

## Quick Start Guide

### What You Need
- Zoho CRM account (admin@zschool.com)
- 5 minutes to set up authentication
- Python environment (optional for testing)

### Goal
Connect to Zoho CRM API and extract course feedback data for your aggregation system.

---

## Step 1: Get API Credentials

### Access Zoho Developer Console
1. **Visit:** https://api-console.zoho.com/
2. **Login with:** admin@zschool.com
3. **Click:** "Add Client" → "Self Client"

### Create API Application
```
Client Name: Course Feedback Aggregator
Homepage URL: http://localhost:8000
Authorized Redirect URI: http://localhost:8000/callback
Scopes: ZohoCRM.modules.ALL, ZohoCRM.settings.READ
```

**Save these credentials:**
- Client ID: `[COPY FROM CONSOLE]`
- Client Secret: `[COPY FROM CONSOLE]`

---

## Step 2: Generate Access Token

### Method A: Browser Flow (Recommended)

1. **Create Authorization URL:**
```
https://accounts.zoho.com/oauth/v2/auth?scope=ZohoCRM.modules.ALL,ZohoCRM.settings.READ&client_id=YOUR_CLIENT_ID&response_type=code&access_type=offline&redirect_uri=http://localhost:8000/callback
```

2. **Visit URL in browser** → Grant permissions → Get authorization code from redirect
3. **Exchange code for token:**

```bash
curl -X POST https://accounts.zoho.com/oauth/v2/token \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=http://localhost:8000/callback" \
  -d "code=AUTHORIZATION_CODE"
```

**Save the response:**
- Access Token: `[FOR API CALLS]`
- Refresh Token: `[FOR TOKEN RENEWAL]`

---

## Step 3: Test Connection

### Basic API Test
```bash
curl "https://www.zohoapis.com/crm/v8/org" \
  -H "Authorization: Zoho-oauthtoken YOUR_ACCESS_TOKEN"
```

**Expected Response:**
```json
{
  "org": [{
    "company_name": "Your Organization",
    "id": "123456789"
  }]
}
```

### Python Test (Optional)
```python
import requests

headers = {"Authorization": "Zoho-oauthtoken YOUR_ACCESS_TOKEN"}
response = requests.get("https://www.zohoapis.com/crm/v8/org", headers=headers)

if response.status_code == 200:
    print("✅ Connected to Zoho CRM!")
    print(response.json())
else:
    print(f"❌ Connection failed: {response.status_code}")
```

---

## Step 4: Discover Your Data

### List Available Modules
```bash
curl "https://www.zohoapis.com/crm/v8/settings/modules" \
  -H "Authorization: Zoho-oauthtoken YOUR_ACCESS_TOKEN"
```

**Look for modules containing:**
- Course feedback
- Survey responses  
- Student evaluations
- Custom modules

### Get Sample Records
```bash
curl "https://www.zohoapis.com/crm/v8/MODULE_NAME?per_page=5" \
  -H "Authorization: Zoho-oauthtoken YOUR_ACCESS_TOKEN"
```

Replace `MODULE_NAME` with modules like:
- `Leads` (student leads)
- `Contacts` (student contacts)
- `Custom` (custom feedback module)

---

## Step 5: Extract Course Feedback

### Get Records with Specific Fields
```bash
curl "https://www.zohoapis.com/crm/v8/Custom?fields=Course_Name,Rating,Comments,Student_ID&per_page=50" \
  -H "Authorization: Zoho-oauthtoken YOUR_ACCESS_TOKEN"
```

### Filter by Date Range
```bash
curl "https://www.zohoapis.com/crm/v8/Custom/search?criteria=(Modified_Time:greater_equal:2024-01-01T00:00:00Z)" \
  -H "Authorization: Zoho-oauthtoken YOUR_ACCESS_TOKEN"
```

### Search by Course Name
```bash
curl "https://www.zohoapis.com/crm/v8/Custom/search?criteria=Course_Name:equals:Strategic%20AI" \
  -H "Authorization: Zoho-oauthtoken YOUR_ACCESS_TOKEN"
```

---

## Essential Documentation Links

### Authentication & Setup
- **OAuth Setup Guide:** https://www.zoho.com/crm/developer/docs/api/v8/oauth-overview.html
- **API Console:** https://api-console.zoho.com/
- **Self Client Setup:** https://www.zoho.com/crm/developer/docs/api/v8/self-client.html

### Core API References  
- **Main API Docs:** https://www.zoho.com/crm/developer/docs/api/v8/
- **Get Records API:** https://www.zoho.com/crm/developer/docs/api/v8/get-records.html
- **Search Records API:** https://www.zoho.com/crm/developer/docs/api/v8/search-records.html
- **Module Metadata:** https://www.zoho.com/crm/developer/docs/api/v8/module-meta.html

### Survey Integration
- **Zoho Survey + CRM:** https://www.zoho.com/survey/crm-integration.html
- **Custom Fields Guide:** https://www.zoho.com/crm/help/customization/custom-fields.html
- **Data Model Visualization:** https://www.zoho.com/crm/developer/docs/data-model/

---

## Common Issues & Solutions

### Issue: 401 Unauthorized
**Solution:** Token expired - use refresh token:
```bash
curl -X POST https://accounts.zoho.com/oauth/v2/token \
  -d "refresh_token=YOUR_REFRESH_TOKEN" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "grant_type=refresh_token"
```

### Issue: 429 Rate Limited  
**Solution:** Wait 60 seconds, implement delays between calls
- **Limit:** 100 calls per minute
- **Recommendation:** 1 call per second maximum

### Issue: Module Not Found
**Solution:** Check module names:
```bash
curl "https://www.zohoapis.com/crm/v8/settings/modules" \
  -H "Authorization: Zoho-oauthtoken YOUR_ACCESS_TOKEN" \
  | grep "api_name"
```

### Issue: No Data Found
**Solution:** Check if custom modules exist or data is in standard modules like Leads/Contacts

---

## Next Steps

1. **Set up credentials** using Step 1-2
2. **Test connection** using Step 3
3. **Discover your data structure** using Step 4
4. **Extract feedback data** using Step 5
5. **Combine with Canvas data** for your course aggregator

### For Your Course Aggregator Project
Once connected, you'll extract data like:
```json
{
  "Course_Name": "Strategic AI for HR",
  "Student_Email": "student@company.com", 
  "Rating": 4,
  "Comments": "Great content, needs more examples",
  "Show_Stopper": false,
  "Modified_Time": "2024-08-15T14:30:00Z"
}
```

This data will combine with your Canvas LMS data to power the "what to fix first" prioritization system.