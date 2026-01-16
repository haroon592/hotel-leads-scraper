# Hotel Leads Scraper - GitHub Actions + n8n

Automated hotel leads scraper that runs on GitHub Actions and integrates with n8n.

## 🚀 Setup Instructions

### 1. Create GitHub Repository

1. Create a new **private** repository on GitHub (e.g., `hotel-leads-scraper`)
2. Push this code to the repository:

```bash
cd /home/centrox/Development/selenium
git init
git add .
git commit -m "Initial commit: Hotel leads scraper"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/hotel-leads-scraper.git
git push -u origin main
```

### 2. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

- **LOGIN_EMAIL**: `stevekuzara@gmail.com`
- **LOGIN_PASSWORD**: `1Thotel47`
- **N8N_WEBHOOK_URL**: (Get this from n8n - see below)

### 3. Set up n8n Workflow

Create this workflow in n8n:

#### **Node 1: Schedule Trigger**
- Trigger: Every Monday at 9:00 AM
- Or use Cron: `0 9 * * 1`

#### **Node 2: HTTP Request - Trigger GitHub Action**
- Method: POST
- URL: `https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/actions/workflows/scraper.yml/dispatches`
- Authentication: Header Auth
  - Name: `Authorization`
  - Value: `Bearer YOUR_GITHUB_TOKEN`
- Headers:
  - `Accept`: `application/vnd.github.v3+json`
  - `Content-Type`: `application/json`
- Body (JSON):
```json
{
  "ref": "main",
  "inputs": {
    "webhook_url": "{{$node.Webhook.json.webhookUrl}}"
  }
}
```

#### **Node 3: Webhook (to receive results)**
- Method: POST
- Path: `/hotel-leads-results`
- Copy the webhook URL and add it to GitHub Secrets as `N8N_WEBHOOK_URL`

#### **Node 4: Process Results**
- Add your logic to handle the downloaded leads
- Available data:
  - `status`: success/error
  - `timestamp`: when it ran
  - `stats.total_downloaded`: number of leads
  - `links.artifacts`: URL to download CSV files

### 4. Create GitHub Personal Access Token

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with these scopes:
   - `repo` (full control)
   - `workflow` (update workflows)
3. Copy the token and use it in n8n HTTP Request node

## 📊 How It Works

1. **n8n Schedule Trigger** fires weekly
2. **n8n** calls GitHub API to start the workflow
3. **GitHub Actions** runs the scraper:
   - Logs in to hotelprojectleads.com
   - Collects all lead links
   - Downloads CSV files (resumes from last run)
   - Stores progress in cache
4. **GitHub Actions** sends results to n8n webhook
5. **n8n** processes the results and downloads artifacts if needed

## 🔄 Manual Trigger

You can also trigger manually:
- In GitHub: Actions tab → Select workflow → Run workflow
- In n8n: Test the workflow

## 📦 Downloading CSV Files

CSV files are stored as GitHub Artifacts for 30 days:
1. Go to Actions → Select the run
2. Scroll to Artifacts section
3. Download the `leads-XXX.zip` file

Or use n8n to download automatically using the artifact URL.

## ⚙️ Configuration

Edit `.github/workflows/scraper.yml`:

- **Schedule**: Change `cron: '0 9 * * 1'` for different timing
- **Timeout**: Change `timeout-minutes: 360` (default 6 hours)
- **Retention**: Change `retention-days: 30` for artifacts

## 🐛 Troubleshooting

- Check GitHub Actions logs for errors
- Verify secrets are set correctly
- Ensure n8n webhook is accessible from internet
- Check if GitHub API token has correct permissions

## 💰 Free Tier Limits

- **GitHub Actions**: 2,000 minutes/month (private repo), unlimited (public repo)
- **Artifacts Storage**: 500 MB (private), 2 GB (public)
- Each run takes ~30-60 minutes depending on leads count
