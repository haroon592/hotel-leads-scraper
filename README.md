# Hotel Leads Scraper

Automated scraper for hotelprojectleads.com that runs on GitHub Actions and integrates with n8n.

## What It Does

1. Logs into hotelprojectleads.com
2. Applies filters (region, types, stages, dates, locations)
3. Collects all lead URLs from search results
4. Downloads CSV files for each lead
5. Uploads CSVs to GitHub Artifacts
6. Sends results to n8n webhook

## GitHub Secrets Required

Set these in: `Settings → Secrets and variables → Actions`

- `LOGIN_EMAIL`: Your login email
- `LOGIN_PASSWORD`: Your password
- `N8N_WEBHOOK_URL`: Your n8n webhook URL

## Files

- `full_workflow.py` - Main scraper script
- `send_results.py` - Sends results to n8n
- `.github/workflows/scraper.yml` - GitHub Actions workflow
- `requirements.txt` - Python dependencies

## Run Manually

Go to: `Actions → Hotel Leads Scraper → Run workflow`

## Schedule

Default: Every Monday at 9:00 AM UTC

To change: Edit `.github/workflows/scraper.yml` - line with `cron: '0 9 * * 1'`
