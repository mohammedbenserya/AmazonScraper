import unittest
from unittest.mock import MagicMock
from bs4 import BeautifulSoup
from AmazonSmartScraper.managers.parser import AParser
from AmazonSmartScraper.schemas.product import Product
from AmazonSmartScraper.schemas.custom_errors import ParsingError

class TestAParser(unittest.TestCase):

    def setUp(self):
        self.logger = MagicMock()
        self.parser = AParser(self.logger)

    def test_get_product_price(self):
        price_tag = BeautifulSoup('<span class="a-offscreen">$19.99</span>', 'html.parser').find('span')
        result = self.parser.get_product_price(price_tag)
        self.assertEqual(result, ('$19.99', '19.99', 19.99, '$'))

    def test_get_simple_product_from_html(self):
        html_content = '''
        <div>
            <span class="a-size-mini a-spacing-none a-color-base s-line-clamp-2">Test Product</span>
            <img data-image-latency="s-product-image" src="https://example.com/image.jpg"/>
            <div id="feature-bullets">Test Description</div>
            <span class="a-offscreen">$19.99</span>
            <span class="a-icon-alt">4.5 out of 5 stars</span>
            <a id="bylineInfo">Test Brand</a>
            <span class="a-size-base s-underline-text">100</span>
        </div>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        product = self.parser.get_simple_product_from_html(soup, 'B000123456')
        self.assertIsInstance(product, Product)
        self.assertEqual(product.title, 'Test Product')
        self.assertEqual(product.price, 19.99)

    def test_get_simple_product_from_html_captcha(self):
        html_content = '<div>/errors/validateCaptcha</div>'
        soup = BeautifulSoup(html_content, 'html.parser')
        with self.assertRaises(ParsingError):
            self.parser.get_simple_product_from_html(soup, 'B000123456')

    def test_get_detailed_product_from_html(self):
        html_content = '''
        <div>
            <span id="productTitle">Detailed Product</span>
            <span id="ssf-share-action" data-ssf-share-icon='{"title": "Detailed Product", "image": "http://example.com/image.jpg", "text": "Detailed Description"}'></span>
            <span class="priceToPay">$29.99</span>
            <a id="bylineInfo">Brand: Detailed Brand</a>
            <span id="acrPopover" title="4.0 out of 5 stars"></span>
            <span id="acrCustomerReviewText">200 ratings</span>
        </div>
        '''
        soup = BeautifulSoup(html_content, 'html.parser')
        product = self.parser.get_detailed_product_from_html(soup, 'B000654321')
        self.assertIsInstance(product, Product)
        self.assertEqual(product.title, 'Detailed Product')
        self.assertEqual(product.price, 29.99)

    def test_get_detailed_product_from_html_captcha(self):
        html_content = '<div>/errors/validateCaptcha</div>'
        soup = BeautifulSoup(html_content, 'html.parser')
        with self.assertRaises(ParsingError):
            self.parser.get_detailed_product_from_html(soup, 'B000654321')

    def test_get_simple_product_from_json(self):
        item = {
            'asin': 'B000789012',
            'title': 'JSON Product',
            'formattedImageUrl': 'http://example.com/image.jpg',
            'formattedListPrice': '$39.99',
            'formattedPriceV2': '$39.99',
            'ratingValue': '4.5',
            'brand': 'JSON Brand',
            'totalReviewCount': '300',
            'outOfStock': False
        }
        product = self.parser.get_simple_product_from_json(item)
        self.assertIsInstance(product, Product)
        self.assertEqual(product.title, 'JSON Product')
        self.assertEqual(product.price, 39.99)

if __name__ == '__main__':
    unittest.main()