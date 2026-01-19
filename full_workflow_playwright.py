from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
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

# Browserless.io configuration
BROWSERLESS_API_KEY = "2Tosq0CEfUH1tWa9ba858b6cb12463f9d5943054dfda50606"
USE_BROWSERLESS = True
BROWSERLESS_URL = f"wss://chrome.browserless.io?token={BROWSERLESS_API_KEY}"

NUM_BROWSERS = 5

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

def collect_all_links():
    existing = load_json(LINKS_FILE)
    if existing:
        with print_lock:
            print(f"Found existing links file with {len(existing)} links.")
        use = input("Use existing link file? (y/n) ").strip().lower()
        if use == 'y':
            return existing

    with sync_playwright() as p:
        if USE_BROWSERLESS:
            browser = p.chromium.connect_over_cdp(BROWSERLESS_URL)
        else:
            browser = p.chromium.launch(headless=False)
        
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.set_default_timeout(90000)

        try:
            # Login
            page.goto("https://hotelprojectleads.com/login")
            page.fill('#user_login', 'stevekuzara@gmail.com')
            page.fill('#user_pass', '1Thotel47')
            page.click('#wp-submit')
            time.sleep(4)

            # Save cookies
            cookies = context.cookies()
            save_json(COOKIES_FILE, cookies)
            with print_lock:
                print(f"Saved {len(cookies)} cookies to {COOKIES_FILE}")

            # Go to results page
            page.goto(RESULTS_URL)
            time.sleep(3)

            all_links = []
            page_num = 1
            
            while True:
                with print_lock:
                    print(f"Collecting page {page_num}...")
                time.sleep(2)
                
                # Find all lead links
                rows = page.locator('tr').all()
                found = 0
                for row in rows:
                    links = row.locator('a').all()
                    for link in links:
                        try:
                            href = link.get_attribute('href')
                            if href and 'lead-detail' in href and href not in all_links:
                                all_links.append(href)
                                found += 1
                        except:
                            pass
                
                with print_lock:
                    print(f"  Found {found} new leads. Total: {len(all_links)}")
                
                # Save progress after each page
                save_json(LINKS_FILE, all_links)
                with print_lock:
                    print(f"  ✓ Saved progress to {LINKS_FILE}")

                # TEMPORARY: Stop after collecting 5 leads for testing
                if len(all_links) >= 5:
                    with print_lock:
                        print(f"  🧪 TEST MODE: Stopping at 5 leads")
                    break

                # Try to find next button
                try:
                    next_button = None
                    anchors = page.locator('a').all()
                    for a in anchors:
                        try:
                            text = a.text_content().strip().lower()
                            if text in ['next', '>', 'next page', '»', '›']:
                                next_button = a
                                break
                        except:
                            pass
                    
                    if not next_button:
                        selectors = ["a.next", "a[rel='next']", ".pagination a.next"]
                        for sel in selectors:
                            try:
                                next_button = page.locator(sel).first
                                if next_button.is_visible():
                                    break
                            except:
                                pass
                    
                    if not next_button:
                        with print_lock:
                            print("No next button found. Last page reached.")
                        break
                    
                    next_button.scroll_into_view_if_needed()
                    time.sleep(0.5)
                    next_button.click()
                    page_num += 1
                    time.sleep(2)
                except Exception as e:
                    with print_lock:
                        print(f"Pagination ended: {e}")
                    break

            with print_lock:
                print(f"Final save: {len(all_links)} links to {LINKS_FILE}")
            return all_links
            
        except Exception as e:
            with print_lock:
                print(f"Error collecting links: {e}")
            # Save whatever we collected before the error
            if 'all_links' in locals() and all_links:
                save_json(LINKS_FILE, all_links)
                with print_lock:
                    print(f"Saved {len(all_links)} links before error")
            return all_links if 'all_links' in locals() else []
        finally:
            context.close()
            browser.close()


def worker_browser(worker_id, links_deque, cookies):
    playwright = sync_playwright().start()
    browser = None
    context = None
    
    try:
        if USE_BROWSERLESS:
            browser = playwright.chromium.connect_over_cdp(BROWSERLESS_URL)
        else:
            browser = playwright.chromium.launch(headless=True)
        
        context = browser.new_context(accept_downloads=True)
        
        # Add cookies
        context.add_cookies(cookies)
        
        page = context.new_page()
        page.set_default_timeout(90000)
        
        while True:
            try:
                with links_lock:
                    if not links_deque:
                        break
                    href = links_deque.popleft()
                
                lead_id = extract_lead_id(href)
                
                try:
                    csv_url = f"https://hotelprojectleads.com/members/lead/csv?id={lead_id}"
                    page.goto(csv_url)
                    time.sleep(2)
                    
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
                    time.sleep(2)
                    
            except Exception as e:
                with print_lock:
                    print(f"[Browser-{worker_id}] Error: {e}")
                time.sleep(2)
    
    finally:
        try:
            if context:
                context.close()
            if browser:
                browser.close()
            playwright.stop()
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

    # TEMPORARY: Limit to first 5 leads for testing
    if len(links_deque) > 5:
        with print_lock:
            print(f"🧪 TEST MODE: Limiting to first 5 leads (out of {len(links_deque)})")
        links_deque = deque(list(links_deque)[:5])
        stats["total"] = 5

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
    main()
