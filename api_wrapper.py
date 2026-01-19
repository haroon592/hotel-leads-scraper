from flask import Flask, jsonify, send_file, request
import os
import json
import zipfile
from datetime import datetime
import threading
import time
from full_workflow import main as run_scraper, load_progress, stats

app = Flask(__name__)

# Track job status
job_status = {
    "running": False,
    "last_run": None,
    "last_result": None,
    "error": None
}

def run_scraper_background():
    """Run scraper in background thread"""
    global job_status
    try:
        job_status["running"] = True
        job_status["error"] = None
        
        # Debug: Print environment variables
        import os
        print(f"DEBUG: USE_BROWSERLESS = {os.getenv('USE_BROWSERLESS')}")
        api_key = os.getenv('BROWSERLESS_API_KEY', 'NOT_SET')
        key_preview = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else api_key
        print(f"DEBUG: BROWSERLESS_API_KEY = {key_preview} (length: {len(api_key)})")
        
        # Run the scraper
        run_scraper()
        
        # Get results
        progress = load_progress()
        result = {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "total_leads": stats["total"],
            "downloaded": stats["downloaded"],
            "failed": stats["failed"],
            "all_time_downloaded": len(progress["downloaded"]),
            "all_time_failed": len(progress["failed"])
        }
        
        job_status["last_result"] = result
        job_status["last_run"] = datetime.now().isoformat()
        
    except Exception as e:
        job_status["error"] = str(e)
        job_status["last_result"] = {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
    finally:
        job_status["running"] = False

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/status', methods=['GET'])
def status():
    """Get current job status"""
    return jsonify(job_status)

@app.route('/scrape', methods=['POST'])
def scrape():
    """Start scraping job"""
    if job_status["running"]:
        return jsonify({
            "status": "error",
            "message": "Scraper is already running"
        }), 409
    
    # Start scraper in background thread
    thread = threading.Thread(target=run_scraper_background, daemon=True)
    thread.start()
    
    return jsonify({
        "status": "started",
        "message": "Scraping job started",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/scrape/sync', methods=['POST'])
def scrape_sync():
    """Run scraper synchronously (blocks until complete)"""
    if job_status["running"]:
        return jsonify({
            "status": "error",
            "message": "Scraper is already running"
        }), 409
    
    try:
        run_scraper_background()
        return jsonify(job_status["last_result"])
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/results', methods=['GET'])
def get_results():
    """Get last scraping results"""
    if not job_status["last_result"]:
        return jsonify({
            "status": "error",
            "message": "No results available yet"
        }), 404
    
    return jsonify(job_status["last_result"])

@app.route('/download/csv', methods=['GET'])
def download_csv():
    """Download all CSV files as a zip"""
    download_dir = os.path.join(os.getcwd(), "lead_downloads")
    
    if not os.path.exists(download_dir):
        return jsonify({"error": "No downloads available"}), 404
    
    # Create zip file
    zip_path = "leads_export.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for root, dirs, files in os.walk(download_dir):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, arcname=file)
    
    return send_file(zip_path, as_attachment=True, download_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")

@app.route('/download/json', methods=['GET'])
def download_json():
    """Get all lead data as JSON"""
    download_dir = os.path.join(os.getcwd(), "lead_downloads")
    
    if not os.path.exists(download_dir):
        return jsonify({"error": "No downloads available"}), 404
    
    all_data = []
    for file in os.listdir(download_dir):
        if file.endswith('.csv'):
            file_path = os.path.join(download_dir, file)
            # Read CSV and convert to dict (you may need to parse CSV properly)
            with open(file_path, 'r') as f:
                all_data.append({
                    "filename": file,
                    "content": f.read()
                })
    
    return jsonify({
        "total_files": len(all_data),
        "files": all_data,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/progress', methods=['GET'])
def get_progress():
    """Get download progress"""
    progress = load_progress()
    return jsonify({
        "downloaded": len(progress["downloaded"]),
        "failed": len(progress["failed"]),
        "downloaded_ids": progress["downloaded"],
        "failed_ids": progress["failed"]
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)
