import requests

from fake_useragent import UserAgent
from .proxy import ProxyManager

from AmazonSmartScraper.helpers.session_builder import SessionBuilder
from AmazonSmartScraper.config import set_custom_log_level,logger

class ChromeSessionManager:
    """
    Manages a Chrome session for web scraping, with optional proxy support and custom headers.
    """

    def __init__(self, use_selenium_headers: bool, proxies: dict = None):
        """
        Initializes the ChromeSessionManager.

        :param use_selenium_headers: Whether to use headers that mimic Selenium.
        :param proxies: Optional dictionary of proxies to use.
        """
        self.__use_selenium_headers = use_selenium_headers
        self.__proxies = proxies
        self.headers = {}
        self.session = None
        self.__init_session()
        set_custom_log_level()
        self.__logger = logger

        self.proxy_manager = ProxyManager(logger=self.__logger, session=self.session)
        self.__logger.info('ChromeSessionManager initialized')

    def __init_chrome_session(self, url: str = 'https://www.amazon.co.uk') -> None:
        """
        Initializes a Chrome session with headers and session from SessionBuilder.

        :param url: The URL to initialize the session with.
        """
        web_scraper = SessionBuilder(url)
        self.headers = web_scraper.get_headers()
        self.session = web_scraper.session()
        web_scraper.close_driver()
        if self.__proxies:
            self.proxy_manager.update_proxy()

    def __init_session(self) -> None:
        """
        Initializes the session based on whether Selenium headers are used.
        """
        if self.__use_selenium_headers:
            self.__init_chrome_session()
        else:
            self.headers = {
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'en-US,en;q=0.9',
                'priority': 'u=0, i',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'none',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
            }

            ua = UserAgent()
            self.headers['user-agent'] = ua.chrome
            self.session = requests.Session()