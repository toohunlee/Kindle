"""
WebDriver Manager
Handles Selenium WebDriver setup and configuration
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebDriverManager:
    def __init__(self, headless=True):
        """
        Initialize WebDriver Manager

        Args:
            headless: Run browser in headless mode (no GUI)
        """
        self.headless = headless
        self.driver = None

    def create_driver(self):
        """Create and configure Chrome WebDriver"""
        try:
            logger.info("Setting up Chrome WebDriver...")

            # Configure Chrome options
            chrome_options = Options()

            if self.headless:
                chrome_options.add_argument('--headless=new')  # New headless mode
                logger.info("Running in headless mode")

            # Additional options for stability and anti-detection
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--start-maximized')

            # More anti-detection measures
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            # Add realistic browser preferences
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2,
                "profile.managed_default_content_settings.images": 1,
            })

            # User agent to appear as normal browser - updated to match current Chrome
            chrome_options.add_argument(
                'user-agent=Mozilla/5.0 (X11; Linux x86_64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7499.169 Safari/537.36'
            )

            # Suppress logging
            chrome_options.add_argument('--log-level=3')

            # Setup Chrome driver with webdriver-manager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)

            # Remove automation indicators
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.7499.169 Safari/537.36'
            })

            # Enhanced anti-detection scripts
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # Add additional navigator properties to appear more legitimate
            self.driver.execute_script("""
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
            """)

            # Set timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(30)

            logger.info("WebDriver setup complete")
            return self.driver

        except Exception as e:
            logger.error(f"Error setting up WebDriver: {e}")
            raise

    def get_driver(self):
        """Get existing driver or create new one"""
        if self.driver is None:
            return self.create_driver()
        return self.driver

    def quit(self):
        """Quit the driver and clean up"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
            finally:
                self.driver = None

    def wait_for_element(self, by, value, timeout=10):
        """
        Wait for element to be present

        Args:
            by: Selenium By type (e.g., By.ID, By.XPATH)
            value: Element selector
            timeout: Max wait time in seconds

        Returns:
            WebElement or None
        """
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            logger.warning(f"Element not found: {value}")
            return None

    def wait_for_clickable(self, by, value, timeout=10):
        """Wait for element to be clickable"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except Exception as e:
            logger.warning(f"Element not clickable: {value}")
            return None

    def scroll_to_bottom(self, pause_time=2):
        """Scroll to bottom of page to load dynamic content"""
        import time

        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_time)

            # Calculate new scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break

            last_height = new_height

    def take_screenshot(self, filename):
        """Take a screenshot (useful for debugging)"""
        try:
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False

    def __enter__(self):
        """Context manager entry"""
        self.create_driver()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.quit()


if __name__ == "__main__":
    # Test the WebDriver
    print("Testing WebDriver setup...")

    try:
        with WebDriverManager(headless=False) as wm:
            driver = wm.get_driver()

            print("Navigating to Google...")
            driver.get("https://www.google.com")

            print(f"Page title: {driver.title}")

            import time
            time.sleep(3)

            print("WebDriver test successful!")

    except Exception as e:
        print(f"WebDriver test failed: {e}")
        print("\nMake sure Chrome browser is installed on your system.")
