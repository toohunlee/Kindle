"""
New York Times Scraper with Selenium
More reliable scraper using Selenium WebDriver for authentication
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.webdriver_manager import WebDriverManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NYTScraperSelenium:
    def __init__(self, email, password, headless=True):
        self.email = email
        self.password = password
        self.headless = headless
        self.wm = WebDriverManager(headless=headless)
        self.driver = None

    def login(self):
        """Login to NYT with subscriber credentials using Selenium"""
        try:
            logger.info("Logging into NYT with Selenium...")
            self.driver = self.wm.create_driver()

            # Navigate to NYT login page
            login_url = "https://myaccount.nytimes.com/auth/login"
            self.driver.get(login_url)
            time.sleep(3)

            # Wait for and fill in email - try multiple strategies
            email_field = None
            try:
                # Try different selectors for email field
                email_selectors = [
                    (By.ID, "email"),
                    (By.NAME, "email"),
                    (By.CSS_SELECTOR, "input[type='email']"),
                    (By.XPATH, "//input[@type='email']"),
                    (By.XPATH, "//input[@name='email']")
                ]

                for by_type, selector in email_selectors:
                    try:
                        email_field = self.wm.wait_for_element(by_type, selector, timeout=5)
                        if email_field:
                            logger.info(f"Found email field with {by_type}: {selector}")
                            break
                    except:
                        continue

                if email_field:
                    email_field.clear()
                    email_field.send_keys(self.email)
                    logger.info("Entered email")
                else:
                    logger.error("Could not find email field")
                    self.wm.take_screenshot("nyt_no_email_field.png")
                    return False

            except Exception as e:
                logger.error(f"Error entering email: {e}")
                self.wm.take_screenshot("nyt_email_error.png")
                return False

            # Click continue/next button if exists
            try:
                continue_selectors = [
                    "//button[contains(text(), 'Continue')]",
                    "//button[contains(text(), 'continue')]",
                    "//button[@type='submit']"
                ]

                for selector in continue_selectors:
                    try:
                        continue_button = self.driver.find_element(By.XPATH, selector)
                        continue_button.click()
                        logger.info("Clicked Continue button")
                        time.sleep(3)
                        break
                    except:
                        continue
            except:
                pass  # Button might not exist, continue anyway

            # Wait for and fill in password - try multiple strategies
            password_field = None
            try:
                # Wait longer for page to load after Continue
                time.sleep(4)

                # Try different selectors for password field
                password_selectors = [
                    (By.ID, "password"),
                    (By.NAME, "password"),
                    (By.CSS_SELECTOR, "input[type='password']"),
                    (By.XPATH, "//input[@type='password']")
                ]

                for by_type, selector in password_selectors:
                    try:
                        password_field = self.wm.wait_for_element(by_type, selector, timeout=5)
                        if password_field:
                            logger.info(f"Found password field with {by_type}: {selector}")

                            # Wait for the field to be interactable
                            time.sleep(1)

                            # Check if element is displayed and enabled
                            if password_field.is_displayed() and password_field.is_enabled():
                                # Try to click first to focus
                                try:
                                    password_field.click()
                                    time.sleep(0.5)
                                except:
                                    pass

                                # Clear and send keys
                                try:
                                    password_field.clear()
                                except:
                                    pass  # Clear might fail, that's ok

                                password_field.send_keys(self.password)
                                logger.info("Entered password")
                                break
                            else:
                                logger.warning(f"Password field not ready: displayed={password_field.is_displayed()}, enabled={password_field.is_enabled()}")
                                password_field = None
                                continue
                    except Exception as e:
                        logger.warning(f"Failed with {by_type} {selector}: {e}")
                        continue

                if not password_field:
                    logger.error("Could not find valid password field")
                    # Take screenshot for debugging
                    self.wm.take_screenshot("nyt_no_password_field.png")
                    return False

            except Exception as e:
                logger.error(f"Error entering password: {e}")
                self.wm.take_screenshot("nyt_password_error.png")
                return False

            # Click submit/login button
            try:
                submit_selectors = [
                    "//button[@type='submit']",
                    "//button[contains(text(), 'Log in')]",
                    "//button[contains(text(), 'Login')]",
                ]

                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = self.wm.wait_for_clickable(By.XPATH, selector, timeout=5)
                        if submit_button:
                            break
                    except:
                        continue

                if submit_button:
                    submit_button.click()
                    logger.info("Clicked submit button")
                    time.sleep(5)  # Wait for login to complete
                else:
                    logger.error("Could not find submit button")
                    return False

            except Exception as e:
                logger.error(f"Error clicking submit: {e}")
                return False

            # Check if login was successful
            current_url = self.driver.current_url
            if "auth/login" not in current_url or "nytimes.com" in current_url:
                logger.info("Successfully logged into NYT")
                return True
            else:
                logger.error(f"Login may have failed. Current URL: {current_url}")
                # Take screenshot for debugging
                self.wm.take_screenshot("nyt_login_failed.png")
                return False

        except Exception as e:
            logger.error(f"Error during NYT login: {e}")
            return False

    def get_todays_articles(self, max_articles=10):
        """Fetch today's top articles from NYT Business section"""
        try:
            logger.info("Fetching today's NYT Business articles...")

            # Try Business section
            urls_to_try = [
                "https://www.nytimes.com/section/business",
                "https://www.nytimes.com/section/business/economy"
            ]

            articles = []

            for url in urls_to_try:
                if len(articles) >= max_articles:
                    break

                logger.info(f"Trying URL: {url}")
                self.driver.get(url)
                time.sleep(3)

                # Scroll to load more content
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                time.sleep(2)

                # Get page source and parse with BeautifulSoup
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')

                # Find article links - NYT uses various structures
                selectors = [
                    ('article', {}),
                    ('div', {'class': 'story-wrapper'}),
                    ('section', {'class': 'story-wrapper'}),
                ]

                article_elements = []
                for tag, attrs in selectors:
                    elements = soup.find_all(tag, attrs, limit=max_articles * 3)
                    article_elements.extend(elements)

                # Also try h2/h3 tags with links
                h_elements = soup.find_all(['h2', 'h3'], limit=max_articles * 3)
                article_elements.extend(h_elements)

                for element in article_elements:
                    if len(articles) >= max_articles:
                        break

                    # Extract article link
                    link = element.find('a')
                    if not link:
                        link = element.find_parent('a')

                    if link and link.get('href'):
                        article_url = link.get('href')

                        # Make absolute URL
                        if article_url.startswith('/'):
                            article_url = 'https://www.nytimes.com' + article_url

                        # Check if it's an article URL (contains year)
                        current_year = datetime.now().year
                        if f'/{current_year}/' not in article_url and f'/{current_year-1}/' not in article_url:
                            continue

                        # Get headline
                        headline = link.get_text(strip=True)
                        if not headline:
                            h_tag = element.find(['h1', 'h2', 'h3', 'h4'])
                            if h_tag:
                                headline = h_tag.get_text(strip=True)

                        if headline and article_url and article_url not in [a['url'] for a in articles]:
                            logger.info(f"Found article: {headline}")
                            articles.append({
                                'headline': headline,
                                'url': article_url
                            })

            logger.info(f"Found {len(articles)} articles")
            return articles

        except Exception as e:
            logger.error(f"Error fetching NYT articles: {e}")
            return []

    def get_article_content(self, url):
        """Fetch full article content"""
        try:
            logger.info(f"Fetching article content from {url}")

            self.driver.get(url)
            time.sleep(3)

            # Scroll to load full content
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')

            # Extract article metadata
            headline = soup.find('h1')
            headline_text = headline.get_text(strip=True) if headline else "No title"

            # Extract article body - try multiple selectors
            article_body = None
            body_selectors = [
                ('section', {'name': 'articleBody'}),
                ('article', {}),
                ('div', {'class': 'StoryBodyCompanionColumn'}),
                ('div', {'class': 'article-body'}),
            ]

            for tag, attrs in body_selectors:
                article_body = soup.find(tag, attrs)
                if article_body:
                    break

            paragraphs = []
            if article_body:
                # Get all paragraphs
                for p in article_body.find_all('p'):
                    text = p.get_text(strip=True)
                    # Filter out short paragraphs that might be ads or UI elements
                    if text and len(text) > 20:
                        paragraphs.append(text)

            # Extract author
            author_text = ""
            author_selectors = [
                ('span', {'class': 'last-byline'}),
                ('p', {'class': 'byline'}),
                ('span', {'itemprop': 'name'}),
                ('div', {'class': 'author'}),
            ]

            for tag, attrs in author_selectors:
                author = soup.find(tag, attrs)
                if author:
                    author_text = author.get_text(strip=True)
                    # Clean up common prefixes
                    author_text = author_text.replace('By ', '').replace('by ', '')
                    break

            # Extract date
            date_elem = soup.find('time')
            date_text = ""
            if date_elem:
                date_text = date_elem.get('datetime', '')
                if not date_text:
                    date_text = date_elem.get_text(strip=True)

            if not paragraphs:
                logger.warning(f"No content found for article: {headline_text}")
                return None

            return {
                'headline': headline_text,
                'author': author_text,
                'date': date_text,
                'content': '\n\n'.join(paragraphs),
                'url': url
            }

        except Exception as e:
            logger.error(f"Error fetching article content: {e}")
            return None

    def scrape(self, max_articles=10):
        """Main scraping function"""
        try:
            if not self.login():
                logger.error("Failed to login to NYT")
                return []

            # Get article list
            article_list = self.get_todays_articles(max_articles)

            # Fetch full content for each article
            articles_with_content = []
            for article_info in article_list:
                content = self.get_article_content(article_info['url'])
                if content:
                    articles_with_content.append(content)
                time.sleep(2)  # Be polite with rate limiting

            logger.info(f"Successfully scraped {len(articles_with_content)} NYT articles")
            return articles_with_content

        finally:
            # Always clean up the driver
            self.wm.quit()


if __name__ == "__main__":
    # Test the scraper
    import yaml

    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        scraper = NYTScraperSelenium(
            config['nyt']['email'],
            config['nyt']['password'],
            headless=False  # Set to False to see the browser
        )

        articles = scraper.scrape(max_articles=3)

        print(f"\nScraped {len(articles)} articles:")
        for article in articles:
            print(f"\n{'='*80}")
            print(f"Headline: {article['headline']}")
            print(f"Author: {article['author']}")
            print(f"Date: {article['date']}")
            print(f"Content preview: {article['content'][:200]}...")

    except FileNotFoundError:
        print("Please create config.yaml from config.example.yaml")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
