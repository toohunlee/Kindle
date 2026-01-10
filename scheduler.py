#!/usr/bin/env python3
"""
Scheduler for Kindle News Delivery
Runs the news delivery at specified time every day
"""

import schedule
import time
import logging
from datetime import datetime
import sys

from main import main as run_delivery, load_config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def job():
    """Job to run daily"""
    logger.info("Starting scheduled news delivery...")
    try:
        run_delivery()
    except Exception as e:
        logger.error(f"Error in scheduled job: {e}", exc_info=True)


def main():
    """Main scheduler function"""
    logger.info("="*80)
    logger.info("Kindle News Delivery Scheduler - Starting")
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)

    # Load config to get delivery time
    config = load_config()
    delivery_time = config.get('news', {}).get('delivery_time', '06:00')

    logger.info(f"Scheduled to run daily at {delivery_time}")

    # Schedule the job
    schedule.every().day.at(delivery_time).do(job)

    # Optional: run immediately on start
    run_now = input(f"Run delivery now? (y/n, default=n): ").strip().lower()
    if run_now == 'y':
        logger.info("Running delivery immediately...")
        job()

    logger.info("Scheduler is now running. Press Ctrl+C to stop.")

    # Keep running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("\nScheduler stopped by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
