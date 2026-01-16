#!/usr/bin/env python3
"""
Sends scraper results to n8n webhook
"""
import json
import sys
import os
import requests
from datetime import datetime

def main():
    if len(sys.argv) < 2:
        print("Usage: send_results.py <webhook_url>")
        sys.exit(1)
    
    webhook_url = sys.argv[1]
    
    # Load progress data
    progress_data = {}
    if os.path.exists('download_progress.json'):
        with open('download_progress.json', 'r') as f:
            progress_data = json.load(f)
    
    # Count downloaded files
    downloaded_count = 0
    if os.path.exists('lead_downloads'):
        downloaded_count = len([f for f in os.listdir('lead_downloads') if f.endswith('.csv')])
    
    # Prepare payload for n8n
    payload = {
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "run_id": os.environ.get('GITHUB_RUN_ID', 'unknown'),
        "run_number": os.environ.get('GITHUB_RUN_NUMBER', 'unknown'),
        "stats": {
            "total_downloaded": len(progress_data.get('downloaded', [])),
            "total_failed": len(progress_data.get('failed', [])),
            "files_in_folder": downloaded_count
        },
        "links": {
            "workflow_run": f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}",
            "artifacts": f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}#artifacts"
        }
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        response.raise_for_status()
        print(f"✓ Successfully sent results to n8n: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"✗ Failed to send results to n8n: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
