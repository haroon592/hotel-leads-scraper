# Deploy to Fly.io via Web Portal (Easiest Method!)

## Overview

You can deploy to Fly.io directly from GitHub using their web interface - **no CLI needed!** This is the easiest way for beginners.

---

## Step 1: Push Your Code to GitHub

First, we need to get your code on GitHub.

### Option A: If you already have Git installed

1. **Initialize Git in your project:**
```bash
cd /path/to/your/project
git init
```

2. **Add all files:**
```bash
git add .
```

3. **Commit:**
```bash
git commit -m "Initial commit - Hotel leads scraper"
```

4. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `hotel-leads-scraper`
   - Make it **Private** (to protect your code)
   - Don't initialize with README (we already have files)
   - Click "Create repository"

5. **Push to GitHub:**
```bash
git remote add origin https://github.com/YOUR-USERNAME/hotel-leads-scraper.git
git branch -M main
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username.

### Option B: Upload via GitHub Web Interface (Easier!)

1. **Go to GitHub:** https://github.com/new

2. **Create new repository:**
   - Name: `hotel-leads-scraper`
   - Privacy: **Private**
   - Click "Create repository"

3. **Upload files:**
   - Click "uploading an existing file"
   - Drag and drop ALL your project files:
     - `full_workflow.py`
     - `api_wrapper.py`
     - `Dockerfile`
     - `fly.toml`
     - `requirements.txt`
     - `.env.example` (NOT .env - never upload credentials!)
   - Click "Commit changes"

---

## Step 2: Sign Up for Fly.io

1. **Go to Fly.io:** https://fly.io/app/sign-up

2. **Sign up with GitHub:**
   - Click "Sign up with GitHub"
   - Authorize Fly.io to access your GitHub account
   - Complete your profile

3. **Add payment method:**
   - Go to https://fly.io/dashboard/personal/billing
   - Add a credit card (required for verification)
   - **Don't worry:** You won't be charged on the free tier!

---

## Step 3: Deploy from GitHub (Web Portal)

Now you're on the page you showed in the screenshot!

### Step 1: Choose "Launch from GitHub"

Click the **"Launch from GitHub"** tab (left side)

### Step 2: Connect GitHub Account

Click **"Sign in with GitHub"** button

This will:
- Connect your GitHub account to Fly.io
- Show all your repositories

### Step 3: Select Your Repository

1. You'll see a list of your GitHub repositories
2. Find and click **"hotel-leads-scraper"**
3. Click **"Launch"** or **"Deploy"**

### Step 4: Configure Your App

Fly.io will show a configuration screen:

#### App Name:
- Leave blank for auto-generated name, OR
- Enter: `hotel-leads-scraper`

#### Region:
- Select closest to you:
  - **US East:** `iad` (Virginia)
  - **US West:** `lax` (Los Angeles)
  - **Europe:** `ams` (Amsterdam)

#### Resources:
- **Memory:** 1024 MB (1GB) - default is fine
- **CPU:** Shared - default is fine

#### Environment Variables (IMPORTANT!):
Click **"Add environment variable"** and add:

1. **Variable 1:**
   - Name: `LOGIN_EMAIL`
   - Value: `stevekuzara@gmail.com`

2. **Variable 2:**
   - Name: `LOGIN_PASSWORD`
   - Value: `1Thotel47`

3. **Variable 3:**
   - Name: `PORT`
   - Value: `8080`

### Step 5: Deploy!

Click **"Deploy"** button at the bottom.

**What happens now:**
1. Fly.io reads your `Dockerfile`
2. Builds your app with Firefox and Python
3. Deploys it to their servers
4. Gives you a URL

**This takes 3-5 minutes.** You'll see a progress bar.

---

## Step 4: Get Your App URL

After deployment completes:

1. You'll see: **"Deployment successful!"** ✅

2. Your app URL will be shown:
   ```
   https://hotel-leads-scraper.fly.dev
   ```
   OR
   ```
   https://hotel-leads-scraper-abc123.fly.dev
   ```

3. **Copy this URL!** You'll need it for n8n.

---

## Step 5: Test Your API

Open a new terminal and test:

### Test 1: Health Check
```bash
curl https://your-app-name.fly.dev/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-19T12:34:56"
}
```

### Test 2: Status Check
```bash
curl https://your-app-name.fly.dev/status
```

**Expected response:**
```json
{
  "running": false,
  "last_run": null,
  "last_result": null,
  "error": null
}
```

✅ If you see these responses, your API is working!

---

## Step 6: View Your App in Dashboard

1. **Go to Fly.io Dashboard:** https://fly.io/dashboard

2. **Click on your app:** `hotel-leads-scraper`

3. **You'll see:**
   - **Overview:** App status, URL, region
   - **Metrics:** CPU, memory, bandwidth usage
   - **Logs:** Real-time logs (very useful for debugging!)
   - **Settings:** Environment variables, scaling options

---

## Managing Your App via Web Portal

### View Logs:
1. Go to your app in dashboard
2. Click **"Logs"** tab
3. See real-time logs

### Update Environment Variables:
1. Go to your app in dashboard
2. Click **"Settings"** or **"Secrets"**
3. Click **"Add secret"** or edit existing ones
4. App will automatically restart

### Restart Your App:
1. Go to your app in dashboard
2. Click **"Restart"** button
3. Wait 30 seconds

### Scale Your App:
1. Go to your app in dashboard
2. Click **"Scale"**
3. Adjust memory or CPU
4. Click **"Save"**

---

## Updating Your Code (Future Changes)

When you make changes to your code:

### Method 1: Via GitHub (Automatic)

1. **Edit your files locally**

2. **Push to GitHub:**
```bash
git add .
git commit -m "Updated scraper logic"
git push
```

3. **Fly.io auto-deploys!** (if you enabled auto-deploy)

### Method 2: Manual Redeploy

1. **Go to Fly.io dashboard**
2. **Click your app**
3. **Click "Deploy"** button
4. **Select "Redeploy from GitHub"**

---

## Troubleshooting via Web Portal

### Issue 1: App not responding

**Solution:**
1. Go to dashboard → Your app → Logs
2. Look for errors
3. Common issues:
   - Missing environment variables
   - Firefox not installed (check Dockerfile)
   - Port mismatch (should be 8080)

### Issue 2: "Application error"

**Solution:**
1. Check logs in dashboard
2. Look for Python errors
3. Make sure all files are uploaded to GitHub

### Issue 3: Can't access app URL

**Solution:**
1. App might be sleeping (free tier)
2. Make a request to wake it up:
```bash
curl https://your-app-name.fly.dev/health
```
3. Wait 30 seconds and try again

### Issue 4: Login fails in scraper

**Solution:**
1. Go to dashboard → Your app → Settings
2. Check environment variables:
   - `LOGIN_EMAIL` is correct
   - `LOGIN_PASSWORD` is correct
3. Update if needed
4. App will restart automatically

---

## Enable Auto-Deploy from GitHub

To automatically deploy when you push to GitHub:

1. **Go to your app in Fly.io dashboard**
2. **Click "Settings"**
3. **Find "GitHub Integration"**
4. **Enable "Auto-deploy"**
5. **Select branch:** `main`

Now every time you push to GitHub, Fly.io will automatically deploy!

---

## Comparison: Web Portal vs CLI

| Feature | Web Portal | CLI |
|---------|-----------|-----|
| **Ease of use** | ⭐⭐⭐⭐⭐ Very easy | ⭐⭐⭐ Moderate |
| **Setup time** | 5 minutes | 10 minutes |
| **GitHub required** | Yes | No |
| **View logs** | Click button | Run command |
| **Update env vars** | Click button | Run command |
| **Deploy** | Click button | Run command |
| **Best for** | Beginners | Developers |

**Recommendation:** Start with Web Portal! You can always install CLI later if needed.

---

## Your Deployment Checklist

- [ ] Code pushed to GitHub (private repo)
- [ ] Fly.io account created
- [ ] Payment method added (for verification)
- [ ] App deployed from GitHub
- [ ] Environment variables set (LOGIN_EMAIL, LOGIN_PASSWORD, PORT)
- [ ] App URL copied
- [ ] Health check tested
- [ ] Status endpoint tested
- [ ] Ready to connect to n8n!

---

## Next Steps

Now that your API is deployed, you can:

1. **Test it thoroughly** (run a scraping job)
2. **Set up n8n workflow** (call your API)
3. **Connect to Zoho CRM** (upload leads)
4. **Schedule weekly runs** (automate everything!)

---

## Cost Monitoring

To stay on free tier:

1. **Go to:** https://fly.io/dashboard/personal/billing
2. **Check "Usage" tab**
3. **Monitor:**
   - Compute time (should be ~10 min/week)
   - Bandwidth (should be ~100MB/week)
   - Storage (should be ~1GB)

**Your weekly scraper will easily stay FREE!**

---

## Getting Help

If you get stuck:

1. **Check logs in dashboard** (most issues show here)
2. **Fly.io docs:** https://fly.io/docs
3. **Fly.io community:** https://community.fly.io
4. **Ask me!** I'm here to help

---

## Summary

✅ **Web Portal Method is EASIER than CLI!**

You can:
- Deploy with a few clicks
- Manage everything in browser
- View logs visually
- Update settings easily
- No terminal commands needed!

**Your app will be live at:** `https://your-app-name.fly.dev`

Ready to connect to n8n and automate your lead scraping! 🚀
