# Hotel Leads Scraper - Deployment Guide

## Architecture

```
n8n (Scheduler) → HTTP Request → Your API Service → Selenium Scraper → Return Results → n8n → Zoho CRM
```

## Deployment Options

### Option 1: Fly.io (FREE - Recommended)

**Pros:**
- Free tier: 3 shared VMs
- Persistent storage included
- Auto-sleep when idle (perfect for weekly runs)
- Easy deployment

**Steps:**

1. Install Fly CLI:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Login and create app:
```bash
fly auth login
fly launch --no-deploy
```

3. Set secrets:
```bash
fly secrets set LOGIN_EMAIL="your-email@example.com"
fly secrets set LOGIN_PASSWORD="your-password"
```

4. Deploy:
```bash
fly deploy
```

5. Your API will be at: `https://hotel-leads-scraper.fly.dev`

---

### Option 2: Render (FREE)

**Pros:**
- 750 free hours/month
- Easy GitHub integration
- Auto-deploy on push

**Steps:**

1. Push code to GitHub

2. Go to [render.com](https://render.com) → New Web Service

3. Connect your GitHub repo

4. Render will auto-detect `render.yaml`

5. Add environment variables:
   - `LOGIN_EMAIL`
   - `LOGIN_PASSWORD`

6. Deploy!

---

### Option 3: Railway ($5/month)

**Pros:**
- Always-on (no cold starts)
- $5 credit free, then $5/month
- Very reliable

**Steps:**

1. Go to [railway.app](https://railway.app)

2. New Project → Deploy from GitHub

3. Add environment variables

4. Deploy

---

## API Endpoints

### 1. Start Scraping (Async)
```
POST /scrape
```
Returns immediately, scraper runs in background.

### 2. Start Scraping (Sync)
```
POST /scrape/sync
```
Waits for completion (may timeout on n8n, use async instead).

### 3. Check Status
```
GET /status
```
Returns current job status.

### 4. Get Results
```
GET /results
```
Returns last scraping results as JSON.

### 5. Download CSV Files
```
GET /download/csv
```
Downloads all CSV files as a zip.

### 6. Get Progress
```
GET /progress
```
Returns download progress.

---

## n8n Workflow Setup

### Step 1: Schedule Trigger
- Node: **Schedule Trigger**
- Cron: `0 0 * * 0` (Every Sunday at midnight)

### Step 2: Start Scraping
- Node: **HTTP Request**
- Method: `POST`
- URL: `https://your-service.fly.dev/scrape`
- Wait: 5 seconds

### Step 3: Poll for Completion
- Node: **HTTP Request** (in a loop)
- Method: `GET`
- URL: `https://your-service.fly.dev/status`
- Check if `running: false`
- Use **Wait** node between polls (30 seconds)

### Step 4: Get Results
- Node: **HTTP Request**
- Method: `GET`
- URL: `https://your-service.fly.dev/results`

### Step 5: Download CSV Files
- Node: **HTTP Request**
- Method: `GET`
- URL: `https://your-service.fly.dev/download/csv`
- Response Format: Binary

### Step 6: Extract and Process CSVs
- Node: **Extract from File** (unzip)
- Node: **Spreadsheet File** (read CSV)

### Step 7: Upload to Zoho CRM
- Node: **Zoho CRM**
- Operation: Create/Update records
- Map CSV fields to CRM fields

---

## Alternative: Simpler n8n Workflow

If you want to avoid polling, use webhooks:

### Modified API (add to api_wrapper.py):

```python
@app.route('/scrape/webhook', methods=['POST'])
def scrape_webhook():
    """Start scraping and call webhook when done"""
    webhook_url = request.json.get('webhook_url')
    
    def run_and_notify():
        run_scraper_background()
        # Call webhook when done
        import requests
        requests.post(webhook_url, json=job_status["last_result"])
    
    thread = threading.Thread(target=run_and_notify, daemon=True)
    thread.start()
    
    return jsonify({"status": "started"})
```

### n8n Workflow:
1. **Schedule Trigger**
2. **Webhook** (wait for response)
3. **HTTP Request** → POST to `/scrape/webhook` with webhook URL
4. When scraping completes, webhook receives results
5. **Zoho CRM** node uploads data

---

## Cost Comparison

| Platform | Cost | Best For |
|----------|------|----------|
| Fly.io | FREE | Weekly/monthly runs |
| Render | FREE | Weekly/monthly runs |
| Railway | $5/month | Always-on, high reliability |
| DigitalOcean | $5/month | More control |
| AWS Lambda | ~$0.50/month | Very infrequent runs |

**Recommendation:** Start with **Fly.io** (free). If you need better reliability, upgrade to Railway ($5/month).

---

## Testing Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variables:
```bash
export LOGIN_EMAIL="your-email"
export LOGIN_PASSWORD="your-password"
```

3. Run API:
```bash
python api_wrapper.py
```

4. Test endpoints:
```bash
# Health check
curl http://localhost:8080/health

# Start scraping
curl -X POST http://localhost:8080/scrape

# Check status
curl http://localhost:8080/status

# Get results
curl http://localhost:8080/results
```

---

## Security Notes

1. **Never commit credentials** - Use environment variables
2. **Use HTTPS** - All platforms provide free SSL
3. **Add authentication** - Consider adding API key to endpoints
4. **Rate limiting** - Add rate limiting to prevent abuse

---

## Troubleshooting

### Issue: Selenium fails in Docker
- Solution: Use `firefox-esr` (included in Dockerfile)

### Issue: Memory errors
- Solution: Increase VM memory or reduce `NUM_BROWSERS`

### Issue: Timeout on n8n
- Solution: Use async endpoint + polling instead of sync

### Issue: Cold starts (Render/Fly.io)
- Solution: First request may take 30s to wake up, subsequent requests are fast

---

## Next Steps

1. Deploy to Fly.io or Render
2. Test API endpoints
3. Set up n8n workflow
4. Configure Zoho CRM integration
5. Test end-to-end
6. Set up monitoring/alerts
