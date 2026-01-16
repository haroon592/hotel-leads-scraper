# n8n Workflow Node Configuration

## Visual Workflow Structure

```
┌──────────────────┐
│ 1. Schedule      │
│    Trigger       │ ──┐
│                  │   │
│ ⏰ Every Monday  │   │
│    9:00 AM UTC   │   │
└──────────────────┘   │
                       │
                       ▼
┌──────────────────────────────────────┐
│ 3. HTTP Request                      │
│    Trigger GitHub Action             │
│                                      │
│ Method: POST                         │
│ URL: github.com/repos/{user}/{repo}/ │
│      actions/workflows/              │
│      scraper.yml/dispatches          │
│                                      │
│ Auth: Bearer {github_token}          │
│                                      │
│ Body: {                              │
│   "ref": "main",                     │
│   "inputs": {                        │
│     "webhook_url": "{{webhook}}"     │
│   }                                  │
│ }                                    │
└──────────────────────────────────────┘

         [GitHub Action Runs]
         (Takes 30-60 minutes)
                  │
                  │ Sends results
                  ▼
┌──────────────────────────────────────┐
│ 2. Webhook                           │
│    Receive Results                   │
│                                      │
│ Method: POST                         │
│ Path: /hotel-leads-results           │
│                                      │
│ Receives:                            │
│ {                                    │
│   "status": "success",               │
│   "timestamp": "...",                │
│   "run_id": "...",                   │
│   "stats": {                         │
│     "total_downloaded": 123,         │
│     "total_failed": 5,               │
│     "files_in_folder": 118           │
│   },                                 │
│   "links": {                         │
│     "workflow_run": "...",           │
│     "artifacts": "..."               │
│   }                                  │
│ }                                    │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│ 4. IF Node                           │
│    Check If Success                  │
│                                      │
│ Condition:                           │
│ {{ $json.status }} === "success"     │
└──────┬───────────────────────┬───────┘
       │                       │
       │ TRUE                  │ FALSE
       ▼                       ▼
┌──────────────┐      ┌─────────────────┐
│ 5. Format    │      │ 6. Format       │
│    Success   │      │    Error        │
│    Message   │      │    Message      │
│              │      │                 │
│ Shows:       │      │ Shows:          │
│ • Stats      │      │ • Error message │
│ • Links      │      │ • Logs link     │
│ • Download   │      │                 │
└──────┬───────┘      └────────┬────────┘
       │                       │
       │                       │
       └───────┬───────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ 7. Optional: Send Notification      │
│                                      │
│ Options:                             │
│ • Email                              │
│ • Telegram                           │
│ • Slack                              │
│ • Discord                            │
│ • SMS                                │
└──────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│ 8. Optional: Download Artifacts      │
│                                      │
│ HTTP Request:                        │
│ GET {{ $json.links.artifacts }}      │
│ Auth: Bearer {github_token}          │
│                                      │
│ Downloads all CSV files              │
└──────────────────────────────────────┘
```

---

## Detailed Node Configurations

### Node 1: Schedule Trigger

```json
{
  "name": "Schedule Trigger",
  "type": "n8n-nodes-base.scheduleTrigger",
  "parameters": {
    "rule": {
      "interval": [
        {
          "field": "weeks",
          "weeksInterval": 1,
          "triggerAtDay": 1,
          "triggerAtHour": 9,
          "triggerAtMinute": 0
        }
      ]
    }
  }
}
```

**What it does:**
- Triggers every Monday at 9:00 AM UTC
- Starts the entire workflow
- No input required

**Customization:**
```javascript
// Daily at 6 AM
"field": "days",
"daysInterval": 1,
"triggerAtHour": 6

// Every 12 hours
"field": "hours",
"hoursInterval": 12

// First day of month
"field": "months",
"monthsInterval": 1,
"triggerAtDay": 1
```

---

### Node 2: Webhook - Receive Results

```json
{
  "name": "Webhook - Receive Results",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "hotel-leads-results",
    "options": {
      "responseMode": "responseNode"
    }
  }
}
```

**What it does:**
- Listens for POST requests from GitHub Actions
- Receives JSON data with scraping results
- Must be in "production" mode (not test)

**Important:**
- Copy the **Production URL** (not Test URL)
- Format: `https://your-n8n.app/webhook/hotel-leads-results`
- Add this URL to GitHub Secrets as `N8N_WEBHOOK_URL`

**Data received:**
```json
{
  "status": "success" | "error",
  "timestamp": "2025-01-16T09:30:45",
  "run_id": "1234567890",
  "run_number": "42",
  "stats": {
    "total_downloaded": 150,
    "total_failed": 3,
    "files_in_folder": 147
  },
  "links": {
    "workflow_run": "https://github.com/...",
    "artifacts": "https://github.com/..."
  }
}
```

---

### Node 3: HTTP Request - Trigger GitHub Action

```json
{
  "name": "Trigger GitHub Action",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/actions/workflows/scraper.yml/dispatches",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "httpHeaderAuth",
    "sendHeaders": true,
    "headerParameters": {
      "parameters": [
        {
          "name": "Accept",
          "value": "application/vnd.github.v3+json"
        },
        {
          "name": "Authorization",
          "value": "Bearer YOUR_GITHUB_TOKEN"
        }
      ]
    },
    "sendBody": true,
    "contentType": "json",
    "body": {
      "ref": "main",
      "inputs": {
        "webhook_url": "={{ $node['Webhook - Receive Results'].json.webhookUrl }}"
      }
    }
  }
}
```

**What it does:**
- Calls GitHub API to start the workflow
- Passes webhook URL to GitHub Action
- Uses GitHub Personal Access Token for auth

**To configure:**

1. **Update URL:**
   - Replace `YOUR_USERNAME` with your GitHub username
   - Replace `YOUR_REPO` with your repository name

2. **Set Authentication:**
   - Type: Header Auth
   - Name: `Authorization`
   - Value: `Bearer ghp_xxxxxxxxxxxxx` (your GitHub token)

3. **Verify Headers:**
   - `Accept`: `application/vnd.github.v3+json`
   - `Content-Type`: `application/json`

**Body explanation:**
```json
{
  "ref": "main",           // Branch to run on
  "inputs": {
    "webhook_url": "..."   // Passes webhook URL to workflow
  }
}
```

---

### Node 4: IF - Check If Success

```json
{
  "name": "Check If Success",
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "string": [
        {
          "value1": "={{ $json.status }}",
          "operation": "equals",
          "value2": "success"
        }
      ]
    }
  }
}
```

**What it does:**
- Checks if `status` field equals "success"
- Routes to success path (TRUE) or error path (FALSE)

**Output:**
- **TRUE branch:** Success processing
- **FALSE branch:** Error handling

---

### Node 5: Format Success Message

```json
{
  "name": "Format Success Message",
  "type": "n8n-nodes-base.markdown",
  "parameters": {
    "content": "## 🎉 Scraping Successful!\n\n**Timestamp:** {{ $json.timestamp }}\n**Run ID:** {{ $json.run_id }}\n\n### Statistics\n- ✅ Total Downloaded: {{ $json.stats.total_downloaded }}\n- ❌ Failed: {{ $json.stats.total_failed }}\n- 📁 Files in Folder: {{ $json.stats.files_in_folder }}\n\n### Links\n- [View Run]({{ $json.links.workflow_run }})\n- [Download Files]({{ $json.links.artifacts }})"
  }
}
```

**What it does:**
- Formats success data into readable message
- Uses Markdown for nice formatting
- Displays statistics and download links

**Customization:**
Replace with:
- Set node (to structure data)
- Function node (to process data)
- Database node (to store results)
- Email node (to send notification)

---

### Node 6: Format Error Message

```json
{
  "name": "Format Error Message",
  "type": "n8n-nodes-base.markdown",
  "parameters": {
    "content": "## ⚠️ Scraping Failed\n\n**Timestamp:** {{ $json.timestamp }}\n**Run ID:** {{ $json.run_id }}\n\n### Error\n{{ $json.error || 'Unknown error' }}\n\n[View Logs]({{ $json.links.workflow_run }})"
  }
}
```

**What it does:**
- Formats error information
- Shows error message and log links
- Helps with debugging

---

### Node 7: Send Notification (Optional)

#### Option A: Telegram

```json
{
  "name": "Send Telegram",
  "type": "n8n-nodes-base.telegram",
  "parameters": {
    "operation": "sendMessage",
    "chatId": "YOUR_CHAT_ID",
    "text": "={{ $json.content }}",
    "additionalFields": {
      "parseMode": "Markdown"
    }
  }
}
```

#### Option B: Email

```json
{
  "name": "Send Email",
  "type": "n8n-nodes-base.emailSend",
  "parameters": {
    "fromEmail": "scraper@yourdomain.com",
    "toEmail": "you@email.com",
    "subject": "Hotel Leads Scraping Complete",
    "text": "={{ $json.content }}"
  }
}
```

#### Option C: Slack

```json
{
  "name": "Send Slack",
  "type": "n8n-nodes-base.slack",
  "parameters": {
    "operation": "post",
    "channel": "#scraper-alerts",
    "text": "={{ $json.content }}"
  }
}
```

---

### Node 8: Download Artifacts (Optional)

```json
{
  "name": "Download Artifacts",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "GET",
    "url": "={{ $json.links.artifacts }}",
    "authentication": "predefinedCredentialType",
    "nodeCredentialType": "httpHeaderAuth",
    "headerParameters": {
      "parameters": [
        {
          "name": "Authorization",
          "value": "Bearer YOUR_GITHUB_TOKEN"
        }
      ]
    },
    "options": {
      "response": {
        "responseFormat": "file"
      }
    }
  }
}
```

**What it does:**
- Downloads artifact ZIP file from GitHub
- Contains all CSV files
- Requires GitHub token authentication

**Next steps:**
- Extract ZIP
- Process CSV files
- Upload to storage
- Import to database

---

## Data Flow Diagram

```
USER TRIGGER (Manual/Schedule)
    │
    ▼
n8n: Schedule Trigger
    │
    ▼
n8n: HTTP Request → GitHub API
    │
    ▼
GitHub: Start workflow_dispatch
    │
    ▼
GitHub Actions: Run scraper.yml
    │
    ├─→ Install Chrome
    ├─→ Install Python
    ├─→ Restore cache (progress.json)
    ├─→ Run full_workflow.py
    │   ├─→ Login
    │   ├─→ Collect links
    │   ├─→ Download CSVs
    │   └─→ Save progress
    ├─→ Save cache
    ├─→ Upload artifacts (ZIP)
    └─→ Run send_results.py
        │
        ▼
n8n: Webhook receives data
    │
    ▼
n8n: IF node (check status)
    │
    ├─→ TRUE: Success message
    │   └─→ Send notification
    │       └─→ Download artifacts (optional)
    │
    └─→ FALSE: Error message
        └─→ Alert admin
```

---

## Testing the Workflow

### Test 1: Webhook Only

1. In n8n, open Webhook node
2. Copy **Test URL**
3. Open terminal:

```bash
curl -X POST https://your-n8n.app/webhook-test/hotel-leads-results \
  -H "Content-Type: application/json" \
  -d '{
    "status": "success",
    "timestamp": "2025-01-16T10:00:00",
    "run_id": "test123",
    "stats": {
      "total_downloaded": 100,
      "total_failed": 5,
      "files_in_folder": 95
    },
    "links": {
      "workflow_run": "https://github.com",
      "artifacts": "https://github.com"
    }
  }'
```

**Expected:** Webhook receives data, IF node processes it

---

### Test 2: GitHub Trigger Only

1. In n8n, disable Webhook node temporarily
2. Execute "Trigger GitHub Action" node
3. Check GitHub Actions tab for new run

**Expected:** GitHub Action starts running

---

### Test 3: Full Workflow

1. Enable all nodes
2. Click "Test Workflow" in n8n
3. Wait 30-60 minutes for GitHub Action
4. Check webhook receives results

**Expected:** Complete end-to-end flow works

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| **HTTP 401 Unauthorized** | Invalid GitHub token | Regenerate token with correct scopes |
| **HTTP 404 Not Found** | Wrong repo URL | Check username/repo name |
| **HTTP 422 Unprocessable** | Invalid input format | Check JSON body structure |
| **Webhook timeout** | Scraper takes too long | Normal - webhook triggers immediately, results come later |
| **No webhook call** | Webhook URL wrong in GitHub | Update `N8N_WEBHOOK_URL` secret |

---

## Advanced Customizations

### Add Conditional Logic

```javascript
// In IF node, add more conditions
{{ $json.stats.total_failed > 10 }}    // Alert if many failures
{{ $json.stats.files_in_folder < 50 }} // Alert if too few files
```

### Process CSV Data

Add Function node after download:

```javascript
// Parse CSV data
const csvData = $input.all();
const processed = csvData.map(row => ({
  hotel_name: row.name,
  location: row.address,
  contact: row.email
}));
return processed;
```

### Store in Database

Add Postgres/MySQL/MongoDB node:

```json
{
  "operation": "insert",
  "table": "hotel_leads",
  "columns": "hotel_name,location,contact",
  "values": "={{ $json.hotel_name }},={{ $json.location }},={{ $json.contact }}"
}
```

---

This workflow is fully customizable - adapt it to your needs! 🚀
