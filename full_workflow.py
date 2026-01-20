from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json
import subprocess
from threading import Thread, Lock
from collections import deque
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

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

HPL_USERNAME = os.getenv('HPL_USERNAME', 'stevekuzara@gmail.com')
HPL_PASSWORD = os.getenv('HPL_PASSWORD', '1Thotel47')

NUM_BROWSERS = int(os.getenv('NUM_BROWSERS', '5'))  # Parallel browsers for downloading
HEADLESS = os.getenv('HEADLESS', 'True').lower() == 'true'

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

def kill_chrome_processes():
    """Kill any existing Chrome/ChromeDriver processes to avoid conflicts"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe'], 
                         stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], 
                         stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        else:  # Linux/Mac
            subprocess.run(['pkill', '-9', 'chrome'], 
                         stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
            subprocess.run(['pkill', '-9', 'chromedriver'], 
                         stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        time.sleep(1)  # Wait for processes to terminate
    except Exception as e:
        pass  # Ignore errors if no processes found

def create_driver(headless=True):
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-software-rasterizer")
    
    # Use unique user data directory to avoid conflicts
    import tempfile
    import uuid
    user_data_dir = tempfile.mkdtemp(prefix=f"chrome_{uuid.uuid4().hex[:8]}_")
    options.add_argument(f"--user-data-dir={user_data_dir}")
    
    # Disable shared memory to avoid conflicts
    options.add_argument("--disable-dev-shm-usage")
    
    prefs = {
        "download.default_directory": DOWNLOAD_DIR,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Local Chrome
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(180)  # Increased from 90 to 180 seconds for slow internet
    driver.set_script_timeout(180)     # Increased from 90 to 180 seconds for slow internet
    return driver

def wait_for_download_complete(download_dir, timeout=30):
    """
    Wait for any download to complete in the download directory.
    Returns True if a file was downloaded, False otherwise.
    """
    start_time = time.time()
    initial_files = set(os.listdir(download_dir))
    
    while time.time() - start_time < timeout:
        current_files = set(os.listdir(download_dir))
        new_files = current_files - initial_files
        
        # Check if there are any .crdownload or .tmp files (download in progress)
        in_progress = any(f.endswith(('.crdownload', '.tmp')) for f in current_files)
        
        if new_files and not in_progress:
            # A new file appeared and no downloads in progress
            return True
        
        time.sleep(0.5)
    
    return False

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
        print(f"Found {len(existing)} existing links.")
        use = input("Use existing link file? (y/n) ").strip().lower()
        if use == 'y':
            return existing

    driver = create_driver(headless=False)
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://hotelprojectleads.com/login")
        wait.until(EC.presence_of_element_located((By.ID, 'user_login')))
        driver.find_element(By.ID, 'user_login').send_keys(HPL_USERNAME)
        driver.find_element(By.ID, 'user_pass').send_keys(HPL_PASSWORD)
        driver.find_element(By.ID, 'wp-submit').click()
        time.sleep(4)

        cookies = driver.get_cookies()
        save_json(COOKIES_FILE, cookies)

        driver.get(RESULTS_URL)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
        time.sleep(3)

        all_links = []
        page = 1
        while True:
            print(f"Collecting page {page}...")
            
            # Wait for page to fully load - wait for table rows to be present
            try:
                WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.TAG_NAME, 'tr'))
                )
                time.sleep(3)  # Extra wait for dynamic content
            except:
                print(f"Warning: Page {page} took too long to load, retrying...")
                time.sleep(5)
                driver.refresh()
                time.sleep(5)
                
            rows = driver.find_elements(By.TAG_NAME, 'tr')
            found = 0
            for row in rows:
                for a in row.find_elements(By.TAG_NAME, 'a'):
                    href = a.get_attribute('href')
                    if href and 'lead-detail' in href and href not in all_links:
                        all_links.append(href)
                        found += 1
                            
            print(f"Page {page}: Found {found} leads (Total: {len(all_links)})")
            
            # Save progress after each page
            save_json(LINKS_FILE, all_links)

            try:
                # Wait a bit before looking for next button
                time.sleep(2)
                
                # Scroll to bottom to ensure pagination loads
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                next_button = None
                
                # Try multiple methods to find next button
                # Method 1: Look for anchor tags with "next" text
                anchors = driver.find_elements(By.TAG_NAME, 'a')
                for a in anchors:
                    try:
                        t = a.text.strip().lower()
                        if t in ['next', '>', 'next page', '»', '›']:
                            next_button = a
                            break
                    except:
                        continue
                
                # Method 2: Try CSS selectors
                if not next_button:
                    selectors = ["a.next", "a[rel='next']", ".pagination a.next", "a[aria-label='Next']"]
                    for sel in selectors:
                        try:
                            next_button = driver.find_element(By.CSS_SELECTOR, sel)
                            if next_button:
                                break
                        except:
                            continue
                
                # Method 3: Check if next button is disabled (last page indicator)
                if next_button:
                    try:
                        classes = next_button.get_attribute('class') or ''
                        if 'disabled' in classes.lower():
                            print("Next button is disabled. Last page reached.")
                            break
                    except:
                        pass
                
                if not next_button:
                    # No next button found - could be last page or page didn't load
                    if found == 0:
                        # No leads on this page either, likely an error
                        print("No leads found and no next button. Checking if page loaded correctly...")
                        time.sleep(5)
                        
                        # Retry once
                        driver.refresh()
                        time.sleep(5)
                        
                        # Check again
                        anchors = driver.find_elements(By.TAG_NAME, 'a')
                        for a in anchors:
                            try:
                                t = a.text.strip().lower()
                                if t in ['next', '>', 'next page', '»', '›']:
                                    next_button = a
                                    break
                            except:
                                continue
                        
                        if not next_button:
                            print("Still no next button after retry. Last page reached.")
                            break
                    else:
                        print("Last page reached.")
                        break
                
                # Click next button
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                
                # Try clicking with JavaScript if normal click fails
                try:
                    next_button.click()
                except:
                    driver.execute_script("arguments[0].click();", next_button)
                
                page += 1
                time.sleep(3)  # Wait longer between pages for slow internet
                
            except Exception as e:
                print(f"Pagination ended: {e}")
                break

        print(f"Collection complete: {len(all_links)} total links")
        return all_links
    except Exception as e:
        print(f"Error collecting links: {e}")
        # Save whatever we collected before the error
        if 'all_links' in locals() and all_links:
            save_json(LINKS_FILE, all_links)
        return all_links if 'all_links' in locals() else []
    finally:
        try:
            driver.quit()
        except:
            pass


def worker_browser(worker_id, links_deque, cookies):
    driver = None
    while True:
        try:
            with links_lock:
                if not links_deque:
                    break
                href = links_deque.popleft()
            
            lead_id = extract_lead_id(href)
            
            try:
                if driver is None:
                    driver = create_driver(headless=HEADLESS)
                    driver.get('https://hotelprojectleads.com/')
                    time.sleep(0.5)
                    for c in cookies:
                        try:
                            driver.add_cookie(c)
                        except:
                            pass
                    time.sleep(0.2)
                
                csv_url = f"https://hotelprojectleads.com/members/lead/csv?id={lead_id}"
                driver.get(csv_url)
                
                download_success = wait_for_download_complete(DOWNLOAD_DIR, timeout=60)
                
                if not download_success:
                    time.sleep(5)
                    download_success = wait_for_download_complete(DOWNLOAD_DIR, timeout=30)
                
                rfp_path = os.path.join(DOWNLOAD_DIR, "rfp.csv")
                if os.path.exists(rfp_path):
                    new_path = os.path.join(DOWNLOAD_DIR, f"{lead_id}.csv")
                    try:
                        if os.path.exists(new_path):
                            os.remove(new_path)
                        os.rename(rfp_path, new_path)
                        download_success = True
                    except Exception as e:
                        with print_lock:
                            print(f"[Browser-{worker_id}] Error renaming file: {e}")
                
                with stats_lock:
                    stats["downloaded"] += 1
                    current = stats["downloaded"]
                    total = stats["total"]
                
                if download_success:
                    print(f"[Browser-{worker_id}] ✓ {lead_id} ({current}/{total})")
                
                save_progress(lead_id, 'success')
                
            except Exception as e:
                with stats_lock:
                    stats["failed"] += 1
                print(f"[Browser-{worker_id}] ✗ {lead_id}")
                save_progress(lead_id, 'failed')
                
                try:
                    if driver:
                        driver.quit()
                        driver = None
                except:
                    pass
                
                time.sleep(2)
                
        except Exception as e:
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
    print("Cleaning up any existing Chrome processes...")
    kill_chrome_processes()
    
    all_links = collect_all_links()

    progress = load_progress()
    to_download = [l for l in all_links if extract_lead_id(l) not in progress['downloaded']]

    print(f"Total: {len(all_links)} | Downloaded: {len(progress['downloaded'])} | Remaining: {len(to_download)}")

    if not to_download:
        print("Nothing to download.")
        return

    cookies = load_json(COOKIES_FILE)
    if not cookies:
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

    print(f"Download complete: {stats['downloaded']} success, {stats['failed']} failed")

if __name__ == '__main__':
    main() 