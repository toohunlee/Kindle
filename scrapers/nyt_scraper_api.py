"""
New York Times API Scraper
Uses official NYT API to fetch articles - more reliable than web scraping
"""

import requests
from datetime import datetime
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NYTScraperAPI:
    def __init__(self, api_key):
        """
        Initialize NYT API Scraper

        Args:
            api_key: NYT API key
        """
        self.api_key = api_key
        self.base_url = "https://api.nytimes.com/svc"

    def get_top_stories(self, section='business', max_articles=10):
        """
        Fetch top stories from NYT Top Stories API

        Args:
            section: Section name (business, technology, science, etc.)
            max_articles: Maximum number of articles to return

        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"Fetching top {max_articles} articles from NYT {section} section via API...")

            # Top Stories API endpoint
            url = f"{self.base_url}/topstories/v2/{section}.json"

            params = {
                'api-key': self.api_key
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'OK':
                logger.error(f"API returned non-OK status: {data.get('status')}")
                return []

            results = data.get('results', [])
            articles = []

            for item in results[:max_articles]:
                # Extract article information
                article = {
                    'headline': item.get('title', 'No title'),
                    'author': item.get('byline', '').replace('By ', ''),
                    'date': item.get('published_date', ''),
                    'abstract': item.get('abstract', ''),
                    'url': item.get('url', ''),
                    'content': self._format_article_content(item)
                }

                articles.append(article)
                logger.info(f"Found article: {article['headline']}")

            logger.info(f"Successfully fetched {len(articles)} articles from NYT API")
            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from NYT API: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []

    def get_most_popular(self, period=1, max_articles=10):
        """
        Fetch most popular articles from NYT Most Popular API

        Args:
            period: Time period in days (1, 7, or 30)
            max_articles: Maximum number of articles to return

        Returns:
            List of article dictionaries
        """
        try:
            logger.info(f"Fetching most popular articles from past {period} day(s) via API...")

            # Most Popular API endpoint - most viewed
            url = f"{self.base_url}/mostpopular/v2/viewed/{period}.json"

            params = {
                'api-key': self.api_key
            }

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            if data.get('status') != 'OK':
                logger.error(f"API returned non-OK status: {data.get('status')}")
                return []

            results = data.get('results', [])
            articles = []

            for item in results[:max_articles]:
                # Extract article information
                article = {
                    'headline': item.get('title', 'No title'),
                    'author': item.get('byline', '').replace('By ', ''),
                    'date': item.get('published_date', ''),
                    'abstract': item.get('abstract', ''),
                    'url': item.get('url', ''),
                    'content': self._format_article_content(item)
                }

                articles.append(article)
                logger.info(f"Found article: {article['headline']}")

            logger.info(f"Successfully fetched {len(articles)} popular articles from NYT API")
            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from NYT API: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []

    def _format_article_content(self, item):
        """
        Format article content from API response

        The API doesn't provide full article text, only abstract.
        We'll format available information nicely.
        """
        parts = []

        # Add abstract/summary
        abstract = item.get('abstract', '')
        if abstract:
            parts.append(abstract)

        # Add additional context if available
        lead_paragraph = item.get('lead_paragraph', '')
        if lead_paragraph and lead_paragraph != abstract:
            parts.append(lead_paragraph)

        # If we have multimedia, mention it
        multimedia = item.get('multimedia', [])
        if multimedia:
            parts.append(f"\n[This article includes {len(multimedia)} image(s)]")

        # Add a note about full article
        url = item.get('url', '')
        if url:
            parts.append(f"\n\nRead the full article at: {url}")

        return '\n\n'.join(parts) if parts else 'Content not available via API.'

    def scrape(self, max_articles=10, use_popular=False):
        """
        Main scraping function - compatible with existing code interface

        Args:
            max_articles: Maximum number of articles to fetch
            use_popular: If True, use Most Popular API instead of Top Stories

        Returns:
            List of article dictionaries
        """
        if use_popular:
            return self.get_most_popular(period=1, max_articles=max_articles)
        else:
            return self.get_top_stories(section='business', max_articles=max_articles)


if __name__ == "__main__":
    # Test the API scraper
    import yaml
    import os

    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        api_key = config.get('nyt', {}).get('api_key')
        if not api_key:
            print("Please add 'api_key' to the 'nyt' section in config.yaml")
            exit(1)

        scraper = NYTScraperAPI(api_key)

        print("\n=== Testing Top Stories API ===")
        articles = scraper.get_top_stories(section='business', max_articles=3)

        print(f"\nFetched {len(articles)} articles:")
        for i, article in enumerate(articles, 1):
            print(f"\n{i}. {article['headline']}")
            print(f"   Author: {article['author']}")
            print(f"   Date: {article['date']}")
            print(f"   Abstract: {article['abstract'][:100]}...")

        print("\n\n=== Testing Most Popular API ===")
        popular = scraper.get_most_popular(period=1, max_articles=3)

        print(f"\nFetched {len(popular)} popular articles:")
        for i, article in enumerate(popular, 1):
            print(f"\n{i}. {article['headline']}")
            print(f"   Author: {article['author']}")
            print(f"   Date: {article['date']}")

    except FileNotFoundError:
        print("Please create config.yaml from config.example.yaml")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
