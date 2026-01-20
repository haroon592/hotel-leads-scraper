import os
import sys
import time
from datetime import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
import logging

# Import the main scraping workflow
from full_workflow import main as scrape_leads, DOWNLOAD_DIR
from zoho_crm_client import ZohoCRMClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_scraping_and_upload():
    """
    Main job function that:
    1. Scrapes hotel leads
    2. Uploads to Zoho CRM
    """
    job_start = datetime.now()
    logger.info(f"Starting job at {job_start.strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Step 1: Run the scraping
        logger.info("Step 1: Scraping leads...")
        scrape_leads()
        logger.info("Lead scraping completed")
        
        # Step 2: Upload to Zoho CRM
        logger.info("Step 2: Uploading to Zoho CRM...")
        zoho_client = ZohoCRMClient()
        success, failed, uploaded = zoho_client.upload_leads_from_directory(DOWNLOAD_DIR)
        logger.info(f"Zoho upload completed - Success: {success}, Failed: {failed}")
        
        # Job summary
        job_end = datetime.now()
        duration = (job_end - job_start).total_seconds() / 60
        
        logger.info(f"Job completed in {duration:.1f} minutes")
        
    except Exception as e:
        logger.error(f"Job failed: {str(e)}", exc_info=True)


def main():
    """
    Initialize and start the scheduler
    """
    # Get schedule configuration from environment
    schedule_enabled = os.getenv('SCHEDULE_ENABLED', 'True').lower() == 'true'
    day_of_week = os.getenv('SCHEDULE_DAY_OF_WEEK', 'mon')  # mon, tue, wed, thu, fri, sat, sun
    hour = int(os.getenv('SCHEDULE_HOUR', '9'))  # 0-23
    minute = int(os.getenv('SCHEDULE_MINUTE', '0'))  # 0-59
    timezone = os.getenv('SCHEDULE_TIMEZONE', 'America/New_York')
    
    logger.info("Hotel Leads Scraper - Scheduler Started")
    logger.info(f"Schedule: Every {day_of_week.upper()} at {hour:02d}:{minute:02d} {timezone}")
    
    if not schedule_enabled:
        logger.info("Scheduler disabled - Running job once")
        run_scraping_and_upload()
        return
    
    # Create scheduler
    scheduler = BlockingScheduler(timezone=timezone)
    
    # Add the weekly job
    scheduler.add_job(
        run_scraping_and_upload,
        trigger=CronTrigger(
            day_of_week=day_of_week,
            hour=hour,
            minute=minute,
            timezone=timezone
        ),
        id='weekly_scraping_job',
        name='Weekly Hotel Leads Scraping and Upload',
        replace_existing=True
    )
    
    # Start the scheduler first, then get next run time
    logger.info("Starting scheduler...")
    
    try:
        # Start the scheduler (non-blocking until we call scheduler.start())
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")
        scheduler.shutdown()


if __name__ == '__main__':
    main()
