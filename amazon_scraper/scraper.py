from amazon_scraper.managers.fetcher import AFetcher
from amazon_scraper.managers.parser import AParser

class AmazonScraper(AFetcher):
    """
    AmazonScraper is a class that extends AFetcher to scrape product data from Amazon.

    Attributes:
        proxies (None): Placeholder for proxy settings.
        use_selenium_headers (bool): Flag to determine if Selenium headers should be used.
    """

    def __init__(self, use_selenium_headers: bool = True):
        """
        Initializes the AmazonScraper with optional Selenium headers.

        Args:
            use_selenium_headers (bool): Whether to use Selenium headers. Defaults to True.
        """
        self.proxies = None
        self.use_selenium_headers = use_selenium_headers
        super().__init__(self.use_selenium_headers, self.proxies)
        self.logger.info('AmazonScraper initialized')

    @property
    def generate_product(self) -> AParser:
        """
        Generates an AParser instance for parsing product data.

        Returns:
            AParser: An instance of AParser.
        """
        return AParser(self.logger)

