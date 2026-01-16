# Complete Setup Guide: Hotel Leads Scraper with n8n + GitHub Actions

## 🏗️ Architecture Overview

```
┌─────────────┐
│   n8n       │
│  Schedule   │  Every Monday 9 AM
│  Trigger    │
└──────┬──────┘
       │
       │ HTTP POST
       ▼
┌─────────────────────────────────────┐
│   GitHub API                        │
│   Trigger workflow dispatch         │
│   POST /repos/{owner}/{repo}/       │
│        actions/workflows/           │
│        scraper.yml/dispatches       │
└──────┬──────────────────────────────┘
       │
       │ Starts
       ▼
┌─────────────────────────────────────┐
│   GitHub Actions Runner (Ubuntu)    │
│   ┌─────────────────────────────┐   │
│   │ 1. Install Chrome           │   │
│   │ 2. Install Python + Selenium│   │
│   │ 3. Restore cached data      │   │
│   │ 4. Run scraper script       │   │
│   │    - Login to website       │   │
│   │    - Collect lead links     │   │
│   │    - Download CSVs          │   │
│   │ 5. Save progress to cache   │   │
│   │ 6. Upload artifacts         │   │
│   └─────────────────────────────┘   │
└──────┬──────────────────────────────┘
       │
       │ POST results
       ▼
┌─────────────────────────────────────┐
│   n8n Webhook                       │
│   Receives JSON with:               │
│   - Status (success/error)          │
│   - Statistics (downloaded/failed)  │
│   - Links to artifacts              │
└──────┬──────────────────────────────┘
       │
       │ Process
       ▼
┌─────────────────────────────────────┐
│   Your n8n Workflow                 │
│   - Send notifications              │
│   - Download artifacts              │
│   - Store in database               │
│   - Whatever you need!              │
└─────────────────────────────────────┘
```

---

## 📋 Complete Step-by-Step Setup

### STEP 1: Create GitHub Repository

1. **Go to GitHub** and create a new repository:
   - Name: `hotel-leads-scraper` (or any name)
   - Visibility: **Private** (recommended for credentials)
   - ✅ Initialize with README: **No** (we already have files)

2. **Copy the repository URL**
   - Example: `https://github.com/yourusername/hotel-leads-scraper.git`

---

### STEP 2: Push Your Code to GitHub

Open terminal in your project directory and run:

```bash
cd /home/centrox/Development/selenium

# Run the setup script
./setup.sh
```

**OR manually:**

```bash
# Initialize git (if not already)
git init
git branch -M main

# Add remote
git remote add origin https://github.com/YOUR_USERNAME/hotel-leads-scraper.git

# Add files
git add .
git commit -m "Initial commit: Hotel leads scraper"

# Push to GitHub
git push -u origin main
```

---

### STEP 3: Create GitHub Personal Access Token (PAT)

This token allows n8n to trigger your GitHub Actions.

1. Go to **GitHub** → **Settings** → **Developer settings** → [**Personal access tokens**](https://github.com/settings/tokens) → **Tokens (classic)**

2. Click **"Generate new token (classic)"**

3. Configure the token:
   - **Note**: `n8n-trigger-token`
   - **Expiration**: 90 days (or no expiration)
   - **Select scopes**:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `workflow` (Update GitHub Action workflows)

4. Click **"Generate token"**

5. **COPY THE TOKEN** (you won't see it again!)
   - Example: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

---

### STEP 4: Set up n8n Webhook (First!)

**⚠️ Do this BEFORE setting GitHub secrets!**

1. **Open n8n** and create a new workflow

2. **Add a Webhook node**:
   - Click ➕ → Search "Webhook"
   - HTTP Method: `POST`
   - Path: `hotel-leads-results`
   - Click "Save"

3. **Copy the Webhook URL**:
   - Click on the Webhook node
   - Look for **"Test URL"** or **"Production URL"**
   - Example: `https://your-n8n.app/webhook/hotel-leads-results`
   - **COPY THIS URL** - you'll need it next!

---

### STEP 5: Configure GitHub Secrets

GitHub secrets store sensitive data securely.

1. Go to your **GitHub repository**

2. Navigate to: **Settings** → **Secrets and variables** → **Actions**

3. Click **"New repository secret"** for each:

   **Secret 1: LOGIN_EMAIL**
   - Name: `LOGIN_EMAIL`
   - Value: `stevekuzara@gmail.com`

   **Secret 2: LOGIN_PASSWORD**
   - Name: `LOGIN_PASSWORD`
   - Value: `1Thotel47`

   **Secret 3: N8N_WEBHOOK_URL**
   - Name: `N8N_WEBHOOK_URL`
   - Value: `https://your-n8n.app/webhook/hotel-leads-results` (from Step 4)

---

### STEP 6: Complete n8n Workflow Setup

#### **Import the workflow:**

1. In n8n, click **"Import from File"**
2. Select `n8n-workflow.json` from your project
3. Click "Import"

#### **Configure each node:**

---

**Node 1: Schedule Trigger**
- ✅ Already configured
- Runs every Monday at 9:00 AM UTC
- You can adjust: Settings → Interval → Custom cron

**Cron Examples:**
```
0 9 * * 1    # Every Monday at 9 AM
0 9 * * *    # Every day at 9 AM
0 */6 * * *  # Every 6 hours
```

---

**Node 2: Webhook - Receive Results**
- ✅ Already configured (you set this up in Step 4)
- Keep it as is
- Make sure it's **listening** (production mode)

---

**Node 3: Trigger GitHub Action**

This is the MOST IMPORTANT node to configure!

1. **Click on the node**

2. **Update the URL** with YOUR details:
   ```
   https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/actions/workflows/scraper.yml/dispatches
   ```
   Replace:
   - `YOUR_USERNAME` → your GitHub username
   - `YOUR_REPO` → your repository name (e.g., `hotel-leads-scraper`)

3. **Set up Authentication**:
   - Click "Credential for authentication"
   - Select "Create New"
   - Choose **"Header Auth"**
   - Name: `Authorization`
   - Value: `Bearer ghp_your_token_from_step_3`
   - Save credential

4. **Verify Headers** are set:
   - `Accept`: `application/vnd.github.v3+json`
   - `Content-Type`: `application/json`

5. **Verify Body**:
   ```json
   {
     "ref": "main",
     "inputs": {
       "webhook_url": "{{ $node['Webhook - Receive Results'].json.webhookUrl }}"
     }
   }
   ```

---

**Node 4: Check If Success**
- ✅ Already configured
- Splits flow based on success/failure

---

**Node 5 & 6: Format Messages**
- ✅ Already configured
- Creates readable summaries

---

**Node 7 & 8: Optional Notifications**
- These are disabled by default
- Enable if you want:
  - Telegram notifications
  - Slack messages
  - Email alerts
  - etc.

---

### STEP 7: Test the Setup

#### **Test 1: Manual GitHub Actions Trigger**

1. Go to your GitHub repository
2. Click **"Actions"** tab
3. Click **"Hotel Leads Scraper"** workflow
4. Click **"Run workflow"** button
5. Select branch: `main`
6. Click **"Run workflow"**

**Expected Result:**
- You'll see a new workflow run start
- It should complete in 30-60 minutes
- Check the logs for any errors

#### **Test 2: n8n Workflow Test**

1. In n8n, click **"Test Workflow"**
2. The Schedule Trigger will trigger manually
3. It should call GitHub API
4. Wait for GitHub Actions to finish
5. n8n webhook should receive results

**Expected Result:**
- GitHub Action starts
- After completion, webhook receives data
- You see success message in n8n

---

### STEP 8: Monitor & Download Results

#### **View Progress:**

1. **GitHub Actions Logs**:
   - Go to Actions tab → Select run
   - Click on "scrape" job
   - See live logs of the scraper

2. **Download CSV Files**:
   - After workflow completes
   - Scroll to "Artifacts" section
   - Download `leads-XXX.zip`
   - Extract to get all CSV files

#### **Automated Download (Optional)**:

Add this to your n8n workflow after the success node:

```
HTTP Request Node:
- Method: GET
- URL: {{ $json.links.artifacts }}
- Authentication: Bearer + GitHub Token
```

---

## 🎯 What Happens During a Run?

### Timeline:

```
00:00 - n8n Schedule Trigger fires
00:01 - GitHub Action starts
00:02 - Install Chrome & Python
00:03 - Restore cached data (cookies, progress)
00:05 - Login to website
00:10 - Collect all lead links (if not cached)
00:15 - Start downloading CSVs
30:00 - Still downloading (5 parallel browsers)
60:00 - Finish downloading
60:05 - Save progress to cache
60:10 - Upload artifacts to GitHub
60:15 - Send results to n8n webhook
60:16 - n8n processes results
60:17 - Done! ✅
```

---

## 💰 Cost Analysis

### GitHub Actions (Free Tier):

- **Private Repository**:
  - 2,000 minutes/month free
  - Each run ≈ 60 minutes
  - = ~33 runs/month = 8 runs/week ✅

- **Public Repository**:
  - Unlimited minutes! 🎉
  - But your code is public

### Storage:

- Cached data: ~1 MB (very small)
- Artifacts: ~10-50 MB per run (deleted after 30 days)
- Well within 500 MB limit ✅

### Recommendation:

✅ **Use Private Repo** for security
✅ You have plenty of free minutes for weekly runs

---

## 🔧 Customization Options

### Change Schedule:

Edit `.github/workflows/scraper.yml`:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Monday 9 AM
  # Change to:
  - cron: '0 6 * * *'  # Every day 6 AM
  - cron: '0 */12 * * *'  # Every 12 hours
```

### Change Timeout:

```yaml
jobs:
  scrape:
    timeout-minutes: 360  # 6 hours
    # Change to:
    timeout-minutes: 120  # 2 hours
```

### Change Browser Count:

Edit `full_workflow.py`:

```python
NUM_BROWSERS = 5  # Default
# Change to:
NUM_BROWSERS = 3  # Slower but more stable
NUM_BROWSERS = 10  # Faster but may cause issues
```

---

## 🐛 Troubleshooting

### Issue: GitHub Action fails immediately

**Check:**
- Are secrets set correctly?
- Is `LOGIN_EMAIL` and `LOGIN_PASSWORD` correct?
- Check Action logs for specific error

### Issue: n8n doesn't receive webhook

**Check:**
- Is webhook URL in GitHub secrets correct?
- Is webhook node in "production" mode in n8n?
- Is n8n accessible from internet? (not localhost)
- Check GitHub Action logs - did it try to send?

### Issue: Login fails

**Check:**
- Are credentials correct in GitHub secrets?
- Did website change login page structure?
- Check Action logs for screenshots (if you enable them)

### Issue: "No next button found"

**Reason:** Pagination structure changed or no more pages

**Fix:**
- Check if website layout changed
- Script will still download collected leads

### Issue: Downloads incomplete

**Reason:** Timeout or connection issues

**Fix:**
- Script automatically resumes from last run
- Just run it again - it will skip already downloaded leads

---

## 🔒 Security Best Practices

✅ **DO:**
- Use GitHub Secrets for credentials
- Use Private repository
- Rotate tokens regularly (every 90 days)
- Use environment variables in code

❌ **DON'T:**
- Hardcode credentials in code
- Commit `cookies.json` to git
- Share your GitHub token publicly
- Use personal access tokens with too many scopes

---

## 📊 Success Checklist

- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] GitHub Personal Access Token created
- [ ] GitHub Secrets configured (all 3)
- [ ] n8n workflow imported
- [ ] n8n webhook URL copied and added to GitHub
- [ ] GitHub Action URL updated in n8n
- [ ] Test run successful
- [ ] Can download artifacts
- [ ] Schedule is set correctly

---

## 🎓 Summary

You now have:

1. ✅ **Automated weekly scraping** (GitHub Actions)
2. ✅ **Free hosting** (no cost!)
3. ✅ **n8n integration** (webhook communication)
4. ✅ **Progress tracking** (resumes from last run)
5. ✅ **Secure credentials** (GitHub Secrets)
6. ✅ **Easy monitoring** (GitHub Actions logs)
7. ✅ **Automatic retries** (failed downloads tracked)

**Your scraper will now run every Monday automatically!** 🎉

---

## 📞 Need Help?

If you encounter issues:

1. Check GitHub Actions logs (most detailed)
2. Check n8n execution logs
3. Verify all secrets are set
4. Test manually first before relying on schedule
5. Check README.md for more details

Good luck! 🚀
