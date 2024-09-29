import requests,json
from bs4 import BeautifulSoup

from AmazonSmartScraper.managers.session import ChromeSessionManager
from typing import List, Tuple, Any
from lxml import html
from AmazonSmartScraper.config import set_custom_log_level, logger
from AmazonSmartScraper.schemas.custom_errors import FetchPageError, ParsingError


class AFetcher:
    """
    AFetcher is responsible for fetching and parsing Amazon product pages.
    """

    def __init__(self, use_selenium_headers: bool, proxies: dict = None):
        """
        Initialize the AFetcher instance.

        :param use_selenium_headers: Boolean indicating whether to use Selenium headers.
        :param proxies: Dictionary of proxies to use for the session.
        """
        self.__use_selenium_headers = use_selenium_headers
        set_custom_log_level()
        self._logger = logger
        self.proxies = proxies
        self.__chrome_session = ChromeSessionManager(use_selenium_headers, self._logger, self.proxies)
        self._logger.info('AParser initialized')



    def _fetch_page(self, url: str) -> requests.Response:
        """
        Fetch a page using the Chrome session.

        :param url: The URL of the page to fetch.
        :return: The response object from the request.
        """
        self._logger.info(f"Fetching page: {url}")
        response = self.__chrome_session.session.get(url, headers=self.__chrome_session.headers, proxies=self.proxies)
        if response.status_code != 200:
            self._logger.warning(f"Response code {response.status_code} received. Reinitiating session.")
            self.__chrome_session = ChromeSessionManager(use_selenium_headers=self.__use_selenium_headers, proxies=self.proxies)
            response = self.__chrome_session.session.get(url, headers=self.__chrome_session.headers, proxies=self.proxies)
            if response.status_code != 200:
                raise FetchPageError("Failed to fetch page", url=url, status_code=response.status_code)
        response.raise_for_status()
        return response

    def get_soup_from_asin(self, asin: str) -> BeautifulSoup:
        """
        Get BeautifulSoup object from an ASIN.

        :param asin: The ASIN of the product.
        :return: BeautifulSoup object of the product page.
        """
        self._logger.info("Getting soup from response.")
        url = f'https://www.amazon.com/dp/{asin}'
        response = self._fetch_page(url)
        return BeautifulSoup(response.content, 'lxml')

    def __parse_page(self, page_content: requests.Response) -> List[str]:
        """
        Parse the page content to extract ASINs.

        :param page_content: The response object containing the page content.
        :return: List of ASINs extracted from the page.
        :raises ParsingError: If no ASIN elements are found.
        """
        self._logger.info("Parsing page content.")
        tree = html.fromstring(page_content.content)
        data = tree.xpath('//div[@data-component-type="s-search-result"]/@data-asin')
        if not data:
            raise ParsingError("No ASIN elements found",
                               element='//div[@data-component-type="s-search-result"]/@data-asin')
        return data

    def set_proxy(self, host: str, port: int, user: str = None, password: str = None) -> None:
        """
        Set the proxy for the Chrome session.

        :param host: Proxy host address.
        :param port: Proxy port number.
        :param user: (Optional) Username for proxy authentication.
        :param password: (Optional) Password for proxy authentication.
        """
        self.__chrome_session.proxy_manager.set_proxy(host, port, user, password)

    def get_headers(self) -> dict:
        """
        Get the headers used in the Chrome session.

        :return: Dictionary of headers.
        """
        return self.__chrome_session.headers

    def set_headers(self, headers: dict) -> None:
        """
        Set the headers for the Chrome session.

        :param headers: Dictionary of headers to set.
        """
        self.__chrome_session.headers = headers

    def get_session(self) -> requests.Session:
        """
        Get the current requests session.

        :return: The current requests.Session object.
        """
        return self.__chrome_session.session

    def set_session(self, session: requests.Session) -> None:
        """
        Set a new requests session.

        :param session: The new requests.Session object to set.
        """
        self.__use_selenium_headers = False
        self.__chrome_session.session = session

    def __get_pagination_count(self, tree: html.HtmlElement) -> int:
        """
        Get the pagination count from the HTML tree.

        :param tree: The HTML tree of the page.
        :return: The number of pages in the pagination.
        """
        self._logger.info("Getting pagination count.")
        pagination_strip = tree.xpath('//span[@class="s-pagination-strip"]')
        if not pagination_strip:
            return 1

        pagination_items = pagination_strip[0].xpath(
            './/*[contains(@class, "s-pagination-item") and not(contains(., "Next"))]/text()')

        if not pagination_items:
            return 1

        return int(pagination_items[-1])


    def get_asins_by_link(self, url: str = '', check_pagination: bool = False, page_content: requests.Response = None) -> \
    Tuple[List[str], int]:
        """
        Get ASINs from a given URL.

        :param url: The URL to fetch ASINs from.
        :param check_pagination: Whether to check for pagination.
        :param page_content: The page content if already fetched.
        :return: A tuple containing a list of ASINs and the pagination count.
        """
        self._logger.info(f"Getting ASINs by link: {url}")
        if page_content is None:
            page_content = self._fetch_page(url)
        tree = html.fromstring(page_content.content)
        data = self.__parse_page(page_content)
        if check_pagination:
            pagination_count = self.__get_pagination_count(tree)
            return data, pagination_count
        else:
            return data, 1


    def get_products_brief(self, asins: str) -> dict:
        """
        Get brief product information for given ASINs.

        :param asins: The ASINs to fetch product information for.
        :return: A dictionary containing product information.
        """
        try:
            url = f"https://d2in0p32vp1pij.cloudfront.net/ajax/carousel/products?asin={asins}&locale=en_US"
            response = self._fetch_page(url)
            return response.json()
        except Exception as e:
            raise FetchPageError(f"Error sending ASINs request: {str(e)}")


    def get_asins_by_alias(self, alias: str = '', page: int = 1) -> tuple[list[dict[str, Any]], int, str]:
        """
        Get ASINs by alias.

        :param alias: The alias to search for.
        :param page: The page number to fetch.
        :return: A tuple containing a list of ASINs, the pagination count, and the source URL.
        """
        url = f'https://www.amazon.com/s/query?i={alias}&page={page}'
        self._logger.info(f"Getting ASINs by keyword: {alias}, page: {page}")
        page_content = self._fetch_page(url)
        return self.__extract_data_from_json(page_content, f'https://www.amazon.com/s?i={alias}&page={page}')


    def get_asins_by_keyword(self, keyword: str = '', page: int = 1) -> tuple[list[dict[str, Any]], int, str]:
        """
        Get ASINs by keyword.

        :param keyword: The keyword to search for.
        :param page: The page number to fetch.
        :return: A tuple containing a list of ASINs, the pagination count, and the source URL.
        """
        url = f'https://www.amazon.com/s/query?k={keyword}&page={page}'
        self._logger.info(f"Getting ASINs by keyword: {keyword}, page: {page}")
        page_content = self._fetch_page(url)
        return self.__extract_data_from_json(page_content, f'https://www.amazon.com/s?k={keyword}&page={page}')


    def __extract_data_from_json(self, page_content, src) -> tuple[list[dict[str, Any]], int, str]:
        """
        Extract data from JSON content.

        :param page_content: The page content containing JSON data.
        :param src: The source URL.
        :return: A tuple containing a list of data dictionaries, the pagination count, and the source URL.
        """
        page_content_str = page_content.content.decode('utf-8')
        items = page_content_str.split('&&&')
        data = []
        pagination_count = 1
        for item in items:
            try:
                if 'data-search-metadata' in item:
                    json_item = json.loads(item)
                    if len(json_item) > 2 and  'metadata' in json_item[2]:
                        metadata = json_item[2]['metadata']
                        try:
                            pagination_count = int(metadata['totalResultCount'] / metadata['asinOnPageCount']) - 1
                        except ZeroDivisionError:
                            self._logger.error(f"Error calculating pagination count: {metadata}")
                            pagination_count = 1

                    else:
                        self._logger.error(f"Metadata not found in JSON: {json_item}")
                if 'search-result-' in item:
                    json_item = json.loads(item)
                    if len(json_item) > 2  and 'html' in json_item[2] and 'asin' in json_item[2]:
                        data.append({'html': json_item[2]['html'], 'asin': json_item[2]['asin']})
                    else:
                        self._logger.error(f"ASIN not found in JSON: {json_item}")
            except json.decoder.JSONDecodeError as e:
                self._logger.error(f"Error decoding JSON: {e}")
        return data, pagination_count, src