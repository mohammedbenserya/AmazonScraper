import unittest
from unittest.mock import patch, MagicMock
from AmazonSmartScraper.managers.fetcher import AFetcher
from AmazonSmartScraper.schemas.custom_errors import FetchPageError, ParsingError
from bs4 import BeautifulSoup
import requests

class TestAFetcher(unittest.TestCase):

    @patch('AmazonSmartScraper.managers.fetcher.ChromeSessionManager')
    def setUp(self, MockChromeSessionManager):
        self.mock_session_manager = MockChromeSessionManager.return_value
        self.fetcher = AFetcher(use_selenium_headers=True, proxies={'http': 'http://proxy.com'})

    @patch('AmazonSmartScraper.managers.fetcher.requests.Response')
    def test_fetch_page_success(self, MockResponse):
        mock_response = MockResponse.return_value
        mock_response.status_code = 200
        self.mock_session_manager.session.get.return_value = mock_response

        response = self.fetcher._fetch_page('https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A1292115011')
        self.assertEqual(response.status_code, 200)

    @patch('AmazonSmartScraper.managers.fetcher.requests.Response')
    def test_fetch_page_failure(self, MockResponse):
        mock_response = MockResponse.return_value
        mock_response.status_code = 404
        self.mock_session_manager.session.get.return_value = mock_response

        with self.assertRaises(FetchPageError):
            self.fetcher._fetch_page('http://invalid-url.com')

    @patch('AmazonSmartScraper.managers.fetcher.requests.Response')
    def test_get_soup_from_asin(self, MockResponse):
        mock_response = MockResponse.return_value
        mock_response.status_code = 200
        mock_response.content = '<html></html>'
        self.mock_session_manager.session.get.return_value = mock_response

        soup = self.fetcher.get_soup_from_asin('B07WJ5D3H4')
        self.assertIsInstance(soup, BeautifulSoup)

    @patch('AmazonSmartScraper.managers.fetcher.requests.Response')
    def test_parse_page_success(self, MockResponse):
        mock_response = MockResponse.return_value
        mock_response.content = '<div data-component-type="s-search-result" data-asin="B07WJ5D3H4"></div>'
        asins = self.fetcher._AFetcher__parse_page(mock_response)
        self.assertIn('B07WJ5D3H4', asins)

    @patch('AmazonSmartScraper.managers.fetcher.requests.Response')
    def test_parse_page_failure(self, MockResponse):
        mock_response = MockResponse.return_value
        mock_response.content = '<div></div>'
        with self.assertRaises(ParsingError):
            self.fetcher._AFetcher__parse_page(mock_response)

    def test_set_proxy(self):
        self.fetcher.set_proxy('proxy.com', 8080, 'user', 'pass')
        self.mock_session_manager.proxy_manager.set_proxy.assert_called_with('proxy.com', 8080, 'user', 'pass')

    def test_get_headers(self):
        headers = self.fetcher.get_headers()
        self.assertEqual(headers, self.mock_session_manager.headers)

    def test_set_headers(self):
        headers = {'User-Agent': 'test-agent'}
        self.fetcher.set_headers(headers)
        self.assertEqual(self.mock_session_manager.headers, headers)

    def test_get_session(self):
        session = self.fetcher.get_session()
        self.assertEqual(session, self.mock_session_manager.session)

    def test_set_session(self):
        new_session = requests.Session()
        self.fetcher.set_session(new_session)
        self.assertEqual(self.mock_session_manager.session, new_session)



    @patch('AmazonSmartScraper.managers.fetcher.requests.Response')
    def test_get_products_brief(self, MockResponse):
        mock_response = MockResponse.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {'product': 'info'}
        self.mock_session_manager.session.get.return_value = mock_response

        product_info = self.fetcher.get_products_brief('B07WJ5D3H4')
        self.assertEqual(product_info, {'product': 'info'})


if __name__ == '__main__':
    unittest.main()