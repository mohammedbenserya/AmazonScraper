from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
from selenium import webdriver
import os
from fake_useragent import UserAgent
from pyvirtualdisplay import Display
import traceback
import platform
from AmazonSmartScraper.config import set_custom_log_level, logger

class SessionBuilder:
    """
    A class to build and manage a Selenium WebDriver session for web scraping.
    """

    def __init__(self, url: str = 'https://google.com') -> None:
        """
        Initialize the SessionBuilder with a URL and set up the driver.

        :param url: The URL to be used for the session. Defaults to 'https://google.com'.
        """
        self.driver = None
        self.url = url
        self.headers = {}
        set_custom_log_level()
        self.__logger = logger
        self.log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log")
        os.makedirs(self.log_dir, exist_ok=True)
        self.__setup_driver()

    def __setup_driver(self) -> None:
        """
        Set up the Selenium WebDriver with the necessary options and configurations.
        """
        try:
            chrome_options = Options()
            ua = UserAgent()
            user_agent = ua.chrome
            chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
            chrome_options.add_experimental_option("useAutomationExtension", False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--log-level=3")
            chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.page_load_strategy = "normal"
            chrome_options.add_argument("disable-infobars")
            current_dir = os.getcwd()
            chrome_options.add_argument(f'--user-data-dir={current_dir}/selenium')

            if platform.system() != "Windows":
                display = Display(visible=False, size=(1920, 1080))
                display.start()
                chrome_options.add_argument(f"user-agent={user_agent}")
                chrome_options.add_argument("--headless")
            # Add this line to fix headless mode issue
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_window_size(1200, 900)
            self.driver.execute_cdp_cmd(
                "Network.setUserAgentOverride",
                {
                    "userAgent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36"
                },
            )
            self.driver.execute_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
        except Exception as e:
            self.__logger.error(f"Error setting up driver: {str(e)}")
            traceback.print_exc()

    def get_driver(self) -> webdriver.Chrome:
        """
        Retrieve the Selenium WebDriver instance.

        :return: The Selenium WebDriver instance.
        """
        return self.driver

    def close_driver(self) -> None:
        """
        Close the Selenium WebDriver instance.
        """
        try:
            self.driver.quit()
        except Exception as e:
            self.__logger.error(f"Error closing driver: {str(e)}")
            traceback.print_exc()

    def __process_browser_log_entry(self, entry):
        """
        Process a single browser log entry.

        :param entry: The log entry to process.
        :return: The processed log entry as a dictionary.
        """
        try:
            response = json.loads(entry['message'])['message']
            return response
        except Exception as e:
            self.__logger.error(f"Error processing browser log entry: {str(e)}")
            traceback.print_exc()

    def get_headers(self) -> dict:
        """
        Retrieve the headers from the browser's performance log.

        :return: A dictionary of headers.
        """
        try:
            self.driver.get(self.url)
            browser_log = self.driver.get_log('performance')
            events = [self.__process_browser_log_entry(entry) for entry in browser_log]
            headers = {}
            for event in events:
                if 'Network.requestWillBeSentExtraInfo' in event['method']:
                    headersObj = event['params']['headers']
                    headers = {key: value for key, value in headersObj.items() if key[0] != ":"}
                    break

            # input("Press Enter to continue...")
            return headers
        except Exception as e:
            self.__logger.error(f"Error getting headers: {str(e)}")
            traceback.print_exc()

    def session(self) -> requests.Session:
        """
        Create a requests session with the headers retrieved from the browser.

        :return: A requests.Session object with updated headers.
        """
        try:
            session = requests.Session()
            session.headers.update(self.get_headers())
            return session
        except Exception as e:
            self.__logger.error(f"Error creating session: {str(e)}")
            traceback.print_exc()

    def make_request(self) -> str:
        """
        Make a GET request to the specified URL using the session headers.

        :return: The response text from the GET request.
        """
        try:
            headers = self.get_headers()
            session = requests.Session()
            response = session.get(self.url, headers=headers)

            self.__logger.info("\nResponse Content:")
            self.__logger.info(response.text)
            return response.text
        except Exception as e:
            self.__logger.error(f"Error making request: {str(e)}")
            traceback.print_exc()

            return ''

# Usage example
