#!/bin/bash

# Hotel Leads Scraper - Quick Setup Script

echo "🚀 Setting up Hotel Leads Scraper for GitHub Actions + n8n"
echo "============================================================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing git repository..."
    git init
    git branch -M main
else
    echo "✓ Git repository already initialized"
fi

# Check if remote is set
if ! git remote | grep -q origin; then
    echo ""
    echo "❓ Enter your GitHub repository URL:"
    echo "   (e.g., https://github.com/username/hotel-leads-scraper.git)"
    read -p "Repository URL: " repo_url
    
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo "✓ Remote 'origin' added"
    else
        echo "⚠️  Skipping remote setup (you can add it later)"
    fi
else
    echo "✓ Git remote already configured"
fi

# Add and commit files
echo ""
echo "📝 Adding files to git..."
git add .
git status

echo ""
read -p "Do you want to commit and push? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git commit -m "Initial commit: Hotel leads scraper with GitHub Actions"
    
    echo ""
    echo "🚀 Pushing to GitHub..."
    git push -u origin main
    
    echo ""
    echo "✅ Code pushed successfully!"
else
    echo "⚠️  Skipping commit and push"
fi

echo ""
echo "============================================================"
echo "📋 NEXT STEPS:"
echo "============================================================"
echo ""
echo "1️⃣  Configure GitHub Secrets (in your repo → Settings → Secrets):"
echo "   - LOGIN_EMAIL: stevekuzara@gmail.com"
echo "   - LOGIN_PASSWORD: 1Thotel47"
echo "   - N8N_WEBHOOK_URL: (get from n8n - see step 3)"
echo ""
echo "2️⃣  Create GitHub Personal Access Token:"
echo "   - Go to: https://github.com/settings/tokens"
echo "   - Generate token with 'repo' and 'workflow' scopes"
echo "   - Save it for n8n configuration"
echo ""
echo "3️⃣  Set up n8n workflow:"
echo "   - Import n8n-workflow.json into your n8n instance"
echo "   - Update GitHub username/repo in 'Trigger GitHub Action' node"
echo "   - Copy webhook URL from 'Webhook - Receive Results' node"
echo "   - Add webhook URL to GitHub Secrets as N8N_WEBHOOK_URL"
echo ""
echo "4️⃣  Test the workflow:"
echo "   - In GitHub: Actions tab → Hotel Leads Scraper → Run workflow"
echo "   - Or wait for scheduled trigger (Monday 9 AM)"
echo ""
echo "📖 For detailed instructions, see README.md"
echo "============================================================"
