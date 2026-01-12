#!/usr/bin/env python3
"""
Kindle News Delivery - Main Script
Orchestrates the scraping, formatting, and delivery of news to Kindle
"""

import yaml
import logging
import sys
from datetime import datetime
import os

from scrapers import NYTScraperSelenium
from scrapers.nyt_scraper_api import NYTScraperAPI
from formatters import EpubFormatter
from utils import KindleSender

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('kindle_news.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_file='config.yaml'):
    """Load configuration from YAML file"""
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        logger.info(f"Configuration loaded from {config_file}")
        return config
    except FileNotFoundError:
        logger.error(f"Configuration file {config_file} not found")
        logger.error("Please create config.yaml from config.example.yaml")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)


def scrape_news(config):
    """Scrape news from NYT"""
    max_articles = config.get('news', {}).get('max_articles', 10)

    nyt_articles = []

    # Try API-based scraping first (more reliable)
    api_key = config.get('nyt', {}).get('api_key')
    if api_key:
        try:
            logger.info("Starting NYT Business scraping with API...")
            nyt_scraper = NYTScraperAPI(api_key)
            nyt_articles = nyt_scraper.scrape(max_articles=max_articles)
            logger.info(f"Successfully scraped {len(nyt_articles)} NYT articles via API")
            return nyt_articles
        except Exception as e:
            logger.error(f"Error scraping NYT via API: {e}")
            logger.info("Falling back to Selenium scraping...")

    # Fallback to Selenium if API fails or not configured
    if not nyt_articles:
        try:
            logger.info("Starting NYT Business scraping with Selenium...")
            nyt_scraper = NYTScraperSelenium(
                config['nyt']['email'],
                config['nyt']['password'],
                headless=True
            )
            nyt_articles = nyt_scraper.scrape(max_articles=max_articles)
            logger.info(f"Successfully scraped {len(nyt_articles)} NYT articles via Selenium")
        except Exception as e:
            logger.error(f"Error scraping NYT with Selenium: {e}")

    return nyt_articles


def format_news(nyt_articles):
    """Format articles for Kindle"""
    try:
        logger.info("Formatting articles for Kindle as EPUB...")
        formatter = EpubFormatter()
        epub_file = formatter.format_for_kindle(nyt_articles)
        logger.info("Formatting complete")
        return epub_file
    except Exception as e:
        logger.error(f"Error formatting articles: {e}")
        return None


def send_to_kindle(config, epub_file):
    """Send formatted content to Kindle"""
    try:
        logger.info("Sending to Kindle...")

        sender = KindleSender(
            config['email']['smtp_server'],
            config['email']['smtp_port'],
            config['email']['sender_email'],
            config['email']['sender_password']
        )

        today = datetime.now().strftime('%m-%d-%y')
        subject = today

        success = sender.send_to_kindle(
            config['kindle']['email'],
            epub_file,
            subject=subject
        )

        if success:
            logger.info("Successfully sent to Kindle!")
            return True
        else:
            logger.error("Failed to send to Kindle")
            return False

    except Exception as e:
        logger.error(f"Error sending to Kindle: {e}")
        return False


def save_backup(epub_file):
    """EPUB file is already saved, just return the path"""
    if epub_file and os.path.exists(epub_file):
        logger.info(f"Backup saved to {epub_file}")
        return epub_file
    else:
        logger.error("EPUB file not found for backup")
        return None


def main():
    """Main execution function"""
    logger.info("="*80)
    logger.info("Kindle News Delivery - Starting")
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*80)

    # Load configuration
    config = load_config()

    # Scrape news
    nyt_articles = scrape_news(config)

    if not nyt_articles:
        logger.error("No articles were scraped. Exiting.")
        sys.exit(1)

    logger.info(f"Total articles scraped: {len(nyt_articles)} NYT")

    # Format articles as EPUB
    epub_file = format_news(nyt_articles)

    if not epub_file:
        logger.error("Failed to format articles. Exiting.")
        sys.exit(1)

    # Save backup (already saved by formatter)
    backup_file = save_backup(epub_file)

    # Send to Kindle
    success = send_to_kindle(config, epub_file)

    logger.info("="*80)
    if success:
        logger.info("Kindle News Delivery - Completed Successfully")
        if backup_file:
            logger.info(f"Backup saved to: {backup_file}")
    else:
        logger.error("Kindle News Delivery - Failed")
        if backup_file:
            logger.info(f"Content saved to: {backup_file}")
    logger.info("="*80)

    return 0 if success else 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\nProcess interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)
