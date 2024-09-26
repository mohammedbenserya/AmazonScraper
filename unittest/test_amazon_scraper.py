import unittest
from unittest.mock import patch, MagicMock
from amazon_scraper.scraper import AmazonScraper


class TestAmazonScraper(unittest.TestCase):

    @patch('amazon_scraper.scraper.AmazonScraper.fetch_page')
    def test_get_asins_by_link(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'<html></html>'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        asins, pagination_count = scraper.get_asins_by_link(url='http://example.com', check_pagination=True)

        self.assertIsInstance(asins, list)
        self.assertIsInstance(pagination_count, int)

    @patch('amazon_scraper.scraper.AmazonScraper.fetch_page')
    def test_get_products_brief(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.json.return_value = {'asin': 'B000123'}
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        product_info = scraper.get_products_brief(asins='B000123')

        self.assertIsInstance(product_info, dict)
        self.assertIn('asin', product_info)

    @patch('amazon_scraper.scraper.AmazonScraper.fetch_page')
    def test_get_asins_by_alias(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'{"data-search-metadata": {}, "search-result-": {}}'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        asins, pagination_count, src = scraper.get_asins_by_alias(alias='test-alias')

        self.assertIsInstance(asins, list)
        self.assertIsInstance(pagination_count, int)
        self.assertIsInstance(src, str)

    @patch('amazon_scraper.scraper.AmazonScraper.fetch_page')
    def test_get_asins_by_keyword(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'{"data-search-metadata": {}, "search-result-": {}}'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        asins, pagination_count, src = scraper.get_asins_by_keyword(keyword='test-keyword')

        self.assertIsInstance(asins, list)
        self.assertIsInstance(pagination_count, int)
        self.assertIsInstance(src, str)

    @patch('amazon_scraper.scraper.AmazonScraper.fetch_page')
    def test_extract_data_from_json(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'{"data-search-metadata": {}, "search-result-": {}}'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        data, pagination_count, src = scraper.extract_data_from_json(mock_response, 'http://example.com')

        self.assertIsInstance(data, list)
        self.assertIsInstance(pagination_count, int)
        self.assertIsInstance(src, str)

    @patch('amazon_scraper.scraper.AmazonScraper.fetch_page')
    def test_get_asins_by_link_no_pagination(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'<html></html>'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        asins, pagination_count = scraper.get_asins_by_link(url='http://example.com', check_pagination=False)

        self.assertIsInstance(asins, list)
        self.assertEqual(pagination_count, 1)

    @patch('amazon_scraper.scraper.AmazonScraper.fetch_page')
    def test_get_products_brief_empty_response(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        product_info = scraper.get_products_brief(asins='B000123')

        self.assertIsInstance(product_info, dict)
        self.assertEqual(product_info, {})


    @patch('amazon_scraper.scraper.AmazonScraper.fetch_page')
    def test_get_asins_by_keyword_special_characters(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'{"data-search-metadata": {}, "search-result-": {}}'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        asins, pagination_count, src = scraper.get_asins_by_keyword(keyword='test@keyword!')

        self.assertIsInstance(asins, list)
        self.assertIsInstance(pagination_count, int)
        self.assertIsInstance(src, str)

    @patch('amazon_scraper.scraper.AmazonScraper.fetch_page')
    def test_extract_data_from_json_invalid_json(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'invalid json'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        data, pagination_count, src = scraper.extract_data_from_json(mock_response, 'http://example.com')

        self.assertIsInstance(data, list)
        self.assertEqual(data, [])
        self.assertIsInstance(pagination_count, int)
        self.assertIsInstance(src, str)


if __name__ == '__main__':
    unittest.main()
