from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import json
from threading import Thread, Lock
from collections import deque
from urllib.parse import urlparse, parse_qs

RESULTS_URL = (
    "https://hotelprojectleads.com/members/lead-search-results"
    "?region=na"
    "&types=255"
    "&stages=15"
    "&fromDate=2025-01-01"
    "&selectedLocals="
    "USAL,USAK,USAZ,USAR,USCA,USCO,USCT,USDE,USDC,USFL,USGA,USHI,"
    "USID,USIL,USIN,USIA,USKS,USKY,USLA,USME,USMD,USMA,USMI,USMN,"
    "USMS,USMO,USMT,USNE,USNV,USNH,USNJ,USNM,USNY,USNC,USND,USOH,"
    "USOK,USOR,USPA,USRI,USSC,USSD,USTN,USTX,USUT,USVT,USVA,USWA,"
    "USWV,USWI,USWY,CAAB,CABC,CAMB,CANB,CANL,CANT,CANS,CANU,CAON,"
    "CAPE,CAQC,CASK,CAYT,AI,AG,BS,BB,BZ,BM,VG,KY,CR,CU,DM,DO,SV,"
    "GL,GD,GP,GT,HT,HN,JM,MQ,MX,MS,AN,NI,PA,PR,BL,KN,LC,MF,PM,VC,"
    "TT,TC,VI"
    "&incExp=on"
)
DOWNLOAD_DIR = os.path.join(os.getcwd(), "lead_downloads")
LINKS_FILE = "all_lead_links.json"
PROGRESS_FILE = "download_progress.json"
COOKIES_FILE = "cookies.json"

NUM_BROWSERS = 5
HEADLESS = True

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

links_lock = Lock()
print_lock = Lock()
stats_lock = Lock()
stats = {"downloaded": 0, "failed": 0, "total": 0}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return json.load(f)

def create_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Use webdriver-manager to auto-install matching ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def load_progress():
    data = load_json(PROGRESS_FILE)
    if not data:
        return {"downloaded": [], "failed": []}
    return data

def save_progress(lead_id, status):
    try:
        p = load_progress()
        if status == 'success':
            if lead_id not in p['downloaded']:
                p['downloaded'].append(lead_id)
        else:
            if lead_id not in p['failed']:
                p['failed'].append(lead_id)
        save_json(PROGRESS_FILE, p)
    except Exception as e:
        with print_lock:
            print(f"Error saving progress: {e}")

def extract_lead_id(href):
    try:
        parsed = urlparse(href)
        q = parse_qs(parsed.query)
        if 'id' in q:
            return q['id'][0]
        return parsed.path.split('/')[-1]
    except:
        return href

def extract_lead_id(href):
    try:
        parsed = urlparse(href)
        q = parse_qs(parsed.query)
        if 'id' in q:
            return q['id'][0]
        return parsed.path.split('/')[-1]
    except:
        return href

def collect_all_links():
    existing = load_json(LINKS_FILE)
    if existing:
        with print_lock:
            print(f"Found existing links file with {len(existing)} links.")
        # Automatically use existing links in n8n mode (non-interactive)
        # To force re-collection, delete the all_lead_links.json file
        return existing

    driver = create_driver(headless=False)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://hotelprojectleads.com/login")
        wait.until(EC.presence_of_element_located((By.ID, 'user_login')))
        
        # Use environment variables for credentials (more secure)
        email = os.environ.get('LOGIN_EMAIL', 'stevekuzara@gmail.com')
        password = os.environ.get('LOGIN_PASSWORD', '1Thotel47')
        
        driver.find_element(By.ID, 'user_login').send_keys(email)
        driver.find_element(By.ID, 'user_pass').send_keys(password)
        driver.find_element(By.ID, 'wp-submit').click()
        time.sleep(4)

        cookies = driver.get_cookies()
        save_json(COOKIES_FILE, cookies)
        with print_lock:
            print(f"Saved {len(cookies)} cookies to {COOKIES_FILE}")

        driver.get(RESULTS_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(3)

        all_links = []
        page = 1
        while True:
            with print_lock:
                print(f"Collecting page {page}...")
            time.sleep(2)
            rows = driver.find_elements(By.TAG_NAME, 'tr')
            found = 0
            for row in rows:
                for a in row.find_elements(By.TAG_NAME, 'a'):
                    href = a.get_attribute('href')
                    if href and 'lead-detail' in href and href not in all_links:
                        all_links.append(href)
                        found += 1
            with print_lock:
                print(f"  Found {found} new leads. Total: {len(all_links)}")

            try:
                next_button = None
                anchors = driver.find_elements(By.TAG_NAME, 'a')
                for a in anchors:
                    t = a.text.strip().lower()
                    if t in ['next', '>', 'next page', '»', '›']:
                        next_button = a
                        break
                if not next_button:
                    selectors = ["a.next", "a[rel='next']", ".pagination a.next"]
                    for sel in selectors:
                        try:
                            next_button = driver.find_element(By.CSS_SELECTOR, sel)
                            break
                        except:
                            pass
                if not next_button:
                    with print_lock:
                        print("No next button found. Last page reached.")
                    break
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(0.5)
                next_button.click()
                page += 1
                time.sleep(2)
            except Exception as e:
                with print_lock:
                    print(f"Pagination ended: {e}")
                break

        save_json(LINKS_FILE, all_links)
        with print_lock:
            print(f"Saved {len(all_links)} links to {LINKS_FILE}")
        return all_links
    except Exception as e:
        with print_lock:
            print(f"Error collecting links: {e}")
        return []
    finally:
        try:
            driver.quit()
        except:
            pass


def worker_browser(worker_id, links_deque, cookies):
    driver = None
    downloads_since_restart = 0
    RESTART_EVERY = 100  # Restart browser every 100 downloads to prevent memory issues
    
    while True:
        try:
            with links_lock:
                if not links_deque:
                    break
                href = links_deque.popleft()
            
            lead_id = extract_lead_id(href)
            
            try:
                # Restart browser periodically to prevent memory leaks and connection issues
                if driver is None or downloads_since_restart >= RESTART_EVERY:
                    if driver is not None:
                        with print_lock:
                            print(f"[Browser-{worker_id}] 🔄 Restarting browser (processed {downloads_since_restart} leads)")
                        try:
                            driver.quit()
                        except:
                            pass
                        time.sleep(1)
                    
                    driver = create_driver(headless=HEADLESS)
                    driver.get('https://hotelprojectleads.com/')
                    time.sleep(0.5)
                    for c in cookies:
                        try:
                            driver.add_cookie(c)
                        except:
                            pass
                    time.sleep(0.2)
                    downloads_since_restart = 0
                
                csv_url = f"https://hotelprojectleads.com/members/lead/csv?id={lead_id}"
                driver.get(csv_url)
                time.sleep(2)
                downloads_since_restart += 1
                
                with stats_lock:
                    stats["downloaded"] += 1
                    current = stats["downloaded"]
                    total = stats["total"]
                
                with print_lock:
                    print(f"[Browser-{worker_id}] ✓ {lead_id} ({current}/{total})")
                
                save_progress(lead_id, 'success')
                
            except Exception as e:
                with stats_lock:
                    stats["failed"] += 1
                with print_lock:
                    print(f"[Browser-{worker_id}] ✗ {lead_id} - {str(e)[:50]}")
                save_progress(lead_id, 'failed')
                
                try:
                    if driver:
                        driver.quit()
                        driver = None
                except:
                    pass
                
                time.sleep(2)
                
        except Exception as e:
            with print_lock:
                print(f"[Browser-{worker_id}] Error: {e}")
            try:
                if driver:
                    driver.quit()
                    driver = None
            except:
                pass
            time.sleep(2)
    
    try:
        if driver:
            driver.quit()
    except:
        pass

def main():
    all_links = collect_all_links()

    progress = load_progress()
    to_download = [l for l in all_links if extract_lead_id(l) not in progress['downloaded']]

    with print_lock:
        print(f"\nTotal links: {len(all_links)}")
        print(f"Already downloaded: {len(progress['downloaded'])}")
        print(f"Remaining: {len(to_download)}")

    if not to_download:
        with print_lock:
            print("Nothing to download. Exiting.")
        return

    cookies = load_json(COOKIES_FILE)
    if not cookies:
        with print_lock:
            print("No cookies found. Please run collection first.")
        return

    links_deque = deque(to_download)
    stats["total"] = len(to_download)

    threads = []
    for i in range(NUM_BROWSERS):
        t = Thread(target=worker_browser, args=(i+1, links_deque, cookies), daemon=True)
        t.start()
        threads.append(t)
        time.sleep(0.5)

    for t in threads:
        t.join()

    with print_lock:
        print("\n" + "="*60)
        print("DOWNLOAD COMPLETE")
        print("="*60)
        print(f"Total: {stats['total']}")
        print(f"Downloaded: {stats['downloaded']}")
        print(f"Failed: {stats['failed']}")
        print("="*60)

if __name__ == '__main__':
    import sys
    
    # Output JSON summary for n8n to parse
    try:
        main()
        
        # Load final results
        progress = load_progress()
        summary = {
            "status": "success",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_leads": stats["total"],
            "downloaded": stats["downloaded"],
            "failed": stats["failed"],
            "all_time_downloaded": len(progress["downloaded"]),
            "all_time_failed": len(progress["failed"])
        }
        
        # Print JSON for n8n to capture
        print("\n" + "="*60)
        print("N8N_JSON_OUTPUT_START")
        print(json.dumps(summary, indent=2))
        print("N8N_JSON_OUTPUT_END")
        print("="*60)
        
        sys.exit(0)
        
    except Exception as e:
        error_summary = {
            "status": "error",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "error": str(e)
        }
        print("\n" + "="*60)
        print("N8N_JSON_OUTPUT_START")
        print(json.dumps(error_summary, indent=2))
        print("N8N_JSON_OUTPUT_END")
        print("="*60)
        sys.exit(1)
