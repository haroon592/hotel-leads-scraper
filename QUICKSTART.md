# 🚀 Quick Start: Deploy in 10 Minutes

## What You'll Get
- ✅ Free automated scraping every week (GitHub Actions)
- ✅ n8n integration for workflow automation
- ✅ No server costs
- ✅ Automatic resume from failures
- ✅ Secure credential storage

---

## 📝 Pre-requisites

Before starting, make sure you have:
- [ ] GitHub account (free)
- [ ] n8n instance (cloud or self-hosted)
- [ ] Website credentials: `stevekuzara@gmail.com` / `1Thotel47`

---

## ⚡ Quick Setup (10 Minutes)

### 1️⃣ Create GitHub Repository (2 min)

```bash
# In your terminal
cd /home/centrox/Development/selenium

# Initialize git
git init
git branch -M main

# Create a NEW EMPTY repository on GitHub:
# Go to: https://github.com/new
# Name: hotel-leads-scraper
# Private: YES
# Initialize with README: NO

# Add remote (replace with YOUR username)
git remote add origin https://github.com/YOUR_USERNAME/hotel-leads-scraper.git

# Push code
git add .
git commit -m "Initial commit"
git push -u origin main
```

✅ **Done!** Your code is now on GitHub.

---

### 2️⃣ Create GitHub Token for n8n (2 min)

1. Go to: https://github.com/settings/tokens
2. Click: **Generate new token (classic)**
3. Settings:
   - Note: `n8n-automation`
   - Expiration: `No expiration`
   - Scopes: ✅ `repo` + ✅ `workflow`
4. Click: **Generate token**
5. **COPY AND SAVE** the token: `ghp_xxxxxxxxxxxx`

✅ **Done!** Token created.

---

### 3️⃣ Set up n8n Webhook (2 min)

1. Open **n8n**
2. Create **New Workflow**
3. Add **Webhook** node:
   - HTTP Method: `POST`
   - Path: `hotel-leads-results`
4. **Copy the webhook URL**
   - Example: `https://your-n8n.app/webhook/hotel-leads-results`
5. **SAVE THIS URL** - you need it next!

✅ **Done!** Webhook ready.

---

### 4️⃣ Configure GitHub Secrets (2 min)

Go to: `https://github.com/YOUR_USERNAME/hotel-leads-scraper/settings/secrets/actions`

Click **"New repository secret"** three times:

| Name | Value |
|------|-------|
| `LOGIN_EMAIL` | `stevekuzara@gmail.com` |
| `LOGIN_PASSWORD` | `1Thotel47` |
| `N8N_WEBHOOK_URL` | `https://your-n8n.app/webhook/hotel-leads-results` |

✅ **Done!** Secrets configured.

---

### 5️⃣ Complete n8n Workflow (2 min)

In n8n:

1. **Import workflow**:
   - Click: **Options** → **Import from File**
   - Select: `n8n-workflow.json` from your project
   - Click: **Import**

2. **Update "Trigger GitHub Action" node**:
   - Click the node
   - Change URL to:
     ```
     https://api.github.com/repos/YOUR_USERNAME/hotel-leads-scraper/actions/workflows/scraper.yml/dispatches
     ```
   - Set **Authentication**:
     - Type: **Header Auth**
     - Name: `Authorization`
     - Value: `Bearer ghp_your_token_from_step_2`

3. **Activate** the workflow (toggle in top-right)

✅ **Done!** n8n ready to trigger.

---

### 6️⃣ Test Everything (2 min)

#### Option A: Test from GitHub

1. Go to: `https://github.com/YOUR_USERNAME/hotel-leads-scraper/actions`
2. Click: **Hotel Leads Scraper**
3. Click: **Run workflow**
4. Select branch: `main`
5. Click: **Run workflow**

#### Option B: Test from n8n

1. In n8n workflow, click: **Test workflow**
2. Wait for GitHub Action to trigger
3. Check GitHub Actions tab for progress

**Expected Result:**
- ✅ GitHub Action starts running
- ✅ Takes 30-60 minutes to complete
- ✅ n8n webhook receives results
- ✅ You can download CSV files from Artifacts

✅ **Done!** Everything works!

---

## 📅 Schedule Configuration

Your scraper is now set to run **every Monday at 9:00 AM UTC**.

### Change Schedule:

Edit `.github/workflows/scraper.yml`:

```yaml
schedule:
  - cron: '0 9 * * 1'  # Current: Monday 9 AM
```

**Common schedules:**
```yaml
- cron: '0 6 * * *'     # Every day at 6 AM
- cron: '0 9 * * 1,4'   # Monday and Thursday at 9 AM
- cron: '0 */12 * * *'  # Every 12 hours
- cron: '0 0 1 * *'     # First day of each month
```

After changing, commit and push:
```bash
git add .github/workflows/scraper.yml
git commit -m "Update schedule"
git push
```

---

## 📥 Downloading Results

### Method 1: From GitHub (Manual)

1. Go to: Actions → Select run
2. Scroll to **Artifacts**
3. Click: **leads-XXX** to download ZIP
4. Extract ZIP to get CSV files

### Method 2: From n8n (Automated)

Add HTTP Request node after success in n8n:
- Method: `GET`
- URL: `{{ $json.links.artifacts }}`
- Authentication: Bearer token (same as before)

This downloads files automatically to n8n!

---

## 🎯 What Happens Each Run?

```
Monday 9:00 AM UTC
├─ n8n triggers GitHub Action
├─ GitHub Action starts
│  ├─ Install Chrome
│  ├─ Install Python + Selenium
│  ├─ Restore previous progress (resumes from last time)
│  ├─ Login to website
│  ├─ Collect lead links (if needed)
│  ├─ Download CSV files (skips already downloaded)
│  ├─ Save progress
│  └─ Upload files to Artifacts
├─ Send results to n8n webhook
└─ n8n processes results
   └─ You get notification!
```

**Time:** ~30-60 minutes per run  
**Cost:** $0 (free!)  
**Reliability:** High (auto-retry on failures)

---

## 💡 Pro Tips

### 1. Monitor Progress

Check logs in real-time:
- Go to: `https://github.com/YOUR_USERNAME/hotel-leads-scraper/actions`
- Click on running workflow
- Click: **scrape** job
- Watch live logs!

### 2. Resume from Failures

If the script fails or times out:
- ✅ It automatically saves progress
- ✅ Next run will skip already downloaded leads
- ✅ Just run it again - it continues where it left off

### 3. Manual Trigger Anytime

Don't wait for schedule:
- Go to Actions → Run workflow
- Or test from n8n anytime

### 4. Keep Artifacts Longer

Edit `.github/workflows/scraper.yml`:
```yaml
retention-days: 30  # Change to 90 (max)
```

### 5. Notifications

Add to your n8n workflow:
- Email node
- Telegram node
- Slack node
- Discord webhook
- etc.

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| **Action doesn't start** | Check GitHub token permissions (`repo` + `workflow`) |
| **Login fails** | Verify `LOGIN_EMAIL` and `LOGIN_PASSWORD` in GitHub secrets |
| **n8n doesn't receive data** | Check `N8N_WEBHOOK_URL` is correct and webhook is active |
| **"No permission" error** | Regenerate GitHub token with correct scopes |
| **Timeout after 6 hours** | Increase `timeout-minutes` in workflow file |
| **Out of GitHub minutes** | Check usage at Settings → Billing (2000 free/month) |

### Still stuck?

1. Check GitHub Actions logs (most detailed error messages)
2. Check n8n execution logs
3. Verify all 3 secrets are set correctly
4. Try manual test first before schedule
5. Read `COMPLETE_SETUP_GUIDE.md` for details

---

## 📊 Cost Breakdown

| Service | Free Tier | Usage | Cost |
|---------|-----------|-------|------|
| **GitHub Actions** | 2,000 min/month | ~60 min/run × 4 runs/month = 240 min | **$0** ✅ |
| **GitHub Storage** | 500 MB | ~50 MB per run × 4 = 200 MB | **$0** ✅ |
| **n8n Cloud** | 5,000 executions | ~2 per run × 4 = 8 | **$0** ✅ |

**Total monthly cost: $0** 🎉

---

## ✅ Success Checklist

- [ ] GitHub repository created and code pushed
- [ ] GitHub Personal Access Token created with `repo` + `workflow` scopes
- [ ] n8n webhook created and URL copied
- [ ] 3 GitHub Secrets set: `LOGIN_EMAIL`, `LOGIN_PASSWORD`, `N8N_WEBHOOK_URL`
- [ ] n8n workflow imported and configured
- [ ] GitHub Actions URL updated in n8n node
- [ ] Workflow tested manually
- [ ] Can see logs in GitHub Actions
- [ ] n8n receives webhook data
- [ ] Can download artifacts from GitHub
- [ ] Schedule is set correctly

---

## 🎓 What You've Built

You now have a **production-ready, automated lead scraper** that:

1. ✅ Runs automatically every week (or any schedule you want)
2. ✅ Costs $0 to operate
3. ✅ Integrates seamlessly with n8n
4. ✅ Stores credentials securely
5. ✅ Resumes from failures automatically
6. ✅ Provides detailed logs
7. ✅ Downloads files to GitHub Artifacts
8. ✅ Sends results to n8n for processing
9. ✅ Can be monitored and controlled remotely
10. ✅ Scales to handle thousands of leads

**Congratulations! 🎉**

---

## 📚 Additional Resources

- **Complete Guide**: `COMPLETE_SETUP_GUIDE.md` (detailed explanations)
- **README**: `README.md` (quick reference)
- **Test Setup**: Run `python test_setup.py` to verify installation
- **Workflow File**: `.github/workflows/scraper.yml` (GitHub Actions config)
- **n8n Workflow**: `n8n-workflow.json` (import into n8n)

---

## 🚀 Next Steps

1. **Run your first scrape** (manual test)
2. **Wait for scheduled run** (Monday 9 AM)
3. **Add notifications** (Telegram/Slack/Email)
4. **Automate artifact downloads** (in n8n)
5. **Process CSV data** (database, spreadsheet, etc.)
6. **Customize schedule** (daily, weekly, monthly)

**You're all set!** Your automated scraper is ready to run. 🎊

---

Need help? Check `COMPLETE_SETUP_GUIDE.md` for detailed troubleshooting!
