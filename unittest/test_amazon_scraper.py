import unittest
from unittest.mock import patch, MagicMock

from AmazonSmartScraper.schemas.product import Product
from AmazonSmartScraper.scraper import AmazonScraper
from bs4 import BeautifulSoup


class TestAmazonScraper(unittest.TestCase):



    def __init__(self, methodName: str = "runTest"):
        super().__init__(methodName)
        self.parser = None

    @patch('AmazonSmartScraper.scraper.AmazonScraper.generate_product')
    def test_get_detailed_product_from_html(self, mock_generate_product):
        html_content = """
        <html>
        <head><title>Test Product</title></head>
        <body>
            <span id="productTitle">Test Product Title</span>
            <span id="ssf-share-action" data-ssf-share-icon='{"title": "SSF Title", "image": "SSF Image", "text": "SSF Description"}'></span>
            <img id="landingImage"/>
            <div id="feature-bullets">Test Description</div>
            <span class="priceToPay">$19.99</span>
            <a id="bylineInfo">Test Brand</a>
            <span id="acrPopover" title="4.5 out of 5 stars"></span>
            <span id="acrCustomerReviewText">123 ratings</span>
            <div id="productDetails_techSpec_sections">
                <table>
                    <tr><th>Key</th><td>Value</td></tr>
                </table>
            </div>
        </body>
        </html>
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        asin = 'B000123456'

        # Mock the return value of generate_product
        mock_generate_product.get_detailed_product_from_html.return_value = Product(
            asin=asin,
            url='',
            title='Test Product Title',
            image='unavailable',
            description='Test Description',
            price_raw='',
            price_text='',
            price=19.99,
            currency='$',
            rating='4.5 out of 5 stars',
            brand='Test Brand',
            nbr_rating='123 ratings',
            is_out_of_stock=False,
            metadata=[{'Key': 'Value'}],
            alias='',
            keyword='',
            page=1
        )

        product = mock_generate_product.get_detailed_product_from_html(soup, asin)

        self.assertEqual(product.asin, asin)
        self.assertEqual(product.title, 'Test Product Title')
        self.assertEqual(product.image, 'unavailable')
        self.assertEqual(product.description, 'Test Description')
        self.assertEqual(product.price, 19.99)
        self.assertEqual(product.currency, '$')
        self.assertEqual(product.rating, '4.5 out of 5 stars')
        self.assertEqual(product.brand, 'Test Brand')
        self.assertEqual(product.nbr_rating, '123 ratings')
        self.assertFalse(product.is_out_of_stock)
        self.assertEqual(product.metadata, [{'Key': 'Value'}])
    @patch('AmazonSmartScraper.scraper.AmazonScraper.fetch_page')
    def test_get_asins_by_link(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'<html></html>'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        asins, pagination_count = scraper.get_asins_by_link(url='http://example.com', check_pagination=True)

        self.assertIsInstance(asins, list)
        self.assertIsInstance(pagination_count, int)

    @patch('AmazonSmartScraper.scraper.AmazonScraper.fetch_page')
    def test_get_products_brief(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.json.return_value = {'asin': 'B000123'}
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        product_info = scraper.get_products_brief(asins='B000123')

        self.assertIsInstance(product_info, dict)
        self.assertIn('asin', product_info)

    @patch('AmazonSmartScraper.scraper.AmazonScraper.fetch_page')
    def test_get_asins_by_alias(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'{"data-search-metadata": {}, "search-result-": {}}'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        asins, pagination_count, src = scraper.get_asins_by_alias(alias='test-alias')

        self.assertIsInstance(asins, list)
        self.assertIsInstance(pagination_count, int)
        self.assertIsInstance(src, str)

    @patch('AmazonSmartScraper.scraper.AmazonScraper.fetch_page')
    def test_get_asins_by_keyword(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'{"data-search-metadata": {}, "search-result-": {}}'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        asins, pagination_count, src = scraper.get_asins_by_keyword(keyword='test-keyword')

        self.assertIsInstance(asins, list)
        self.assertIsInstance(pagination_count, int)
        self.assertIsInstance(src, str)

    @patch('AmazonSmartScraper.scraper.AmazonScraper.fetch_page')
    def test_extract_data_from_json(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'{"data-search-metadata": {}, "search-result-": {}}'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        data, pagination_count, src = scraper.__extract_data_from_json(mock_response, 'http://example.com')

        self.assertIsInstance(data, list)
        self.assertIsInstance(pagination_count, int)
        self.assertIsInstance(src, str)

    @patch('AmazonSmartScraper.scraper.AmazonScraper.fetch_page')
    def test_get_asins_by_link_no_pagination(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'<html></html>'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        asins, pagination_count = scraper.get_asins_by_link(url='http://example.com', check_pagination=False)

        self.assertIsInstance(asins, list)
        self.assertEqual(pagination_count, 1)

    @patch('AmazonSmartScraper.scraper.AmazonScraper.fetch_page')
    def test_get_products_brief_empty_response(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        product_info = scraper.get_products_brief(asins='B000123')

        self.assertIsInstance(product_info, dict)
        self.assertEqual(product_info, {})


    @patch('AmazonSmartScraper.scraper.AmazonScraper.fetch_page')
    def test_get_asins_by_keyword_special_characters(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'{"data-search-metadata": {}, "search-result-": {}}'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        asins, pagination_count, src = scraper.get_asins_by_keyword(keyword='test@keyword!')

        self.assertIsInstance(asins, list)
        self.assertIsInstance(pagination_count, int)
        self.assertIsInstance(src, str)

    @patch('AmazonSmartScraper.scraper.AmazonScraper.fetch_page')
    def test_extract_data_from_json_invalid_json(self, mock_fetch_page):
        mock_response = MagicMock()
        mock_response.content = b'invalid json'
        mock_fetch_page.return_value = mock_response

        scraper = AmazonScraper()
        data, pagination_count, src = scraper.__extract_data_from_json(mock_response, 'http://example.com')

        self.assertIsInstance(data, list)
        self.assertEqual(data, [])
        self.assertIsInstance(pagination_count, int)
        self.assertIsInstance(src, str)


if __name__ == '__main__':
    unittest.main()
