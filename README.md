# Hotel Leads Scraper API

Automated Selenium scraper for Hotel Project Leads, deployed as a REST API for n8n integration.

## 🚀 Quick Start

### 1. Deploy to Fly.io (FREE)

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login
fly auth login

# Deploy
fly launch --no-deploy
fly secrets set LOGIN_EMAIL="your-email@example.com"
fly secrets set LOGIN_PASSWORD="your-password"
fly deploy
```

**Read the complete guide:** [FLYIO_DEPLOYMENT_STEP_BY_STEP.md](FLYIO_DEPLOYMENT_STEP_BY_STEP.md)

### 2. Test Your API

```bash
chmod +x test_api.sh
./test_api.sh your-app-name
```

### 3. Use in n8n

Add HTTP Request nodes pointing to your Fly.io URL:
- `POST /scrape` - Start scraping
- `GET /status` - Check progress
- `GET /results` - Get results
- `GET /download/csv` - Download CSV files

## 📚 Documentation

- **[FLYIO_DEPLOYMENT_STEP_BY_STEP.md](FLYIO_DEPLOYMENT_STEP_BY_STEP.md)** - Complete deployment guide for beginners
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Overview of all deployment options

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/status` | GET | Current job status |
| `/scrape` | POST | Start scraping (async) |
| `/scrape/sync` | POST | Start scraping (sync) |
| `/results` | GET | Last scraping results |
| `/download/csv` | GET | Download CSVs as zip |
| `/download/json` | GET | Get data as JSON |
| `/progress` | GET | Download progress |

## 🏗️ Architecture

```
n8n (Scheduler) 
    ↓
HTTP Request → Your Fly.io API
    ↓
Selenium Scraper (Firefox)
    ↓
Download CSV Files
    ↓
Return to n8n
    ↓
Upload to Zoho CRM
```

## 💰 Cost

**FREE** on Fly.io for weekly runs!

- 3 shared-cpu VMs
- 3GB storage
- 160GB bandwidth
- Auto-sleep when idle

## 🛠️ Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export LOGIN_EMAIL="your-email@example.com"
export LOGIN_PASSWORD="your-password"

# Run API
python api_wrapper.py

# Test locally
curl http://localhost:8080/health
```

## 📝 Files

- `full_workflow.py` - Original Selenium scraper
- `api_wrapper.py` - Flask API wrapper
- `Dockerfile` - Container configuration
- `fly.toml` - Fly.io configuration
- `requirements.txt` - Python dependencies
- `test_api.sh` - API testing script

## 🔒 Security

- Credentials stored as encrypted secrets on Fly.io
- Never commit `.env` or credentials to Git
- HTTPS enabled by default

## 🐛 Troubleshooting

### App not responding?
```bash
fly logs
```

### Need to restart?
```bash
fly apps restart
```

### Check status?
```bash
fly status
```

### SSH into container?
```bash
fly ssh console
```

## 📞 Support

- Fly.io Docs: https://fly.io/docs
- Fly.io Community: https://community.fly.io

## 📄 License

Private project for client use.
