import re,json
from bs4 import BeautifulSoup

from amazon_scraper.schemas.product import Product
class AParser:
    """
    AParser class is responsible for parsing product information from HTML and JSON data.
    """

    def __init__(self, logger):
        """
        Initialize the AParser with a logger.

        :param logger: Logger instance for logging messages.
        """
        self.logger = logger

    @staticmethod
    def get_product_price(price_tag):
        """
        Extract the product price from the given price tag.

        :param price_tag: BeautifulSoup tag containing the price information.
        :return: Tuple containing raw price, price text, price number, and currency.
        """
        product_price_text = 'unavailable'
        product_price_num = None
        product_price = price_tag.get_text(strip=True) if price_tag else 'unavailable'
        currency = '$'
        if product_price != 'unavailable':
            currency = re.findall(r'\D', product_price)[0]  # Find the first non-digit character
            try:
                product_price_text = "".join([x for x in product_price if x.isdigit() or x == '.'])
                product_price_num = float(product_price_text)
            except ValueError:
                product_price = 'unavailable'
                product_price_text = 'unavailable'
                product_price_num = None
                currency = '$'
        return product_price, product_price_text, product_price_num, currency

    def get_simple_product_from_html(self, soup: BeautifulSoup, asin: str, alias: str = '', keyword: str = '', page: int = 1) -> Product:
        """
        Parse simple product information from HTML.

        :param soup: BeautifulSoup object containing the HTML content.
        :param asin: ASIN of the product.
        :param alias: Alias for the product.
        :param keyword: Keyword associated with the product.
        :param page: Page number where the product is found.
        :return: Product object with parsed information.
        """
        if '/errors/validateCaptcha' in soup.get_text():
            self.logger.error("Captcha validation error. please try using a proxy")
            return Product(asin=asin, alias=alias, keyword=keyword, page=page)
        url = f'https://www.amazon.com/dp/{asin}'
        title = soup.select_one('.a-size-mini.a-spacing-none.a-color-base.s-line-clamp-2').get_text(
            strip=True) if soup.select_one('.a-size-mini.a-spacing-none.a-color-base.s-line-clamp-2') else None
        image = soup.find('img', {'data-image-latency': 's-product-image'})['amazonScraper'] if soup.find('img', {
            'data-image-latency': 's-product-image'}) else None
        description = soup.find('div', id='feature-bullets').get_text(strip=True) if soup.find('div',
                                                                                               id='feature-bullets') else None
        price_tag = soup.find('span', {'class': 'a-offscreen'}) or soup.find('span', {'class': 'a-offscreen'})
        price_raw, price_text, price_num, currency = self.get_product_price(price_tag)

        rating = soup.find('span', class_='a-icon-alt').get_text(strip=True) if soup.find('span',
                                                                                          class_='a-icon-alt') else None
        brand = soup.find('a', id='bylineInfo').get_text(strip=True) if soup.find('a', id='bylineInfo') else None
        nbr_rating = soup.find('span', {'class': "a-size-base s-underline-text"}).get_text(strip=True) if soup.find(
            'span', {'class': "a-size-base s-underline-text"}) else None
        is_out_of_stock = 'Out of Stock' in soup.get_text()

        product = Product(
            asin=asin,
            url=url,
            title=title,
            image=image,
            description=description,
            price_raw=price_raw,
            price_text=price_text,
            price=price_num,
            currency=currency,
            rating=rating,
            brand=brand,
            nbr_rating=nbr_rating,
            is_out_of_stock=is_out_of_stock,
            metadata=[],
            alias=alias,
            keyword=keyword,
            page=page
        )

        return product

    def parse_ssf_json(self, ssf_span) -> dict:
        """
        Parse SSF JSON data from the given span tag.

        :param ssf_span: BeautifulSoup tag containing the SSF JSON data.
        :return: Dictionary with title, image, and description.
        """
        try:
            data_attr = ssf_span.get('data-ssf-share-icon')
        except AttributeError as e:
            self.logger.error(f"Error accessing 'data-ssf-share-icon' attribute: {e}")
            return {
                'title': '',
                'image': '',
                'description': '',
            }
        if not data_attr:
            self.logger.warning("No data-ssf-share-icon attribute found.")
            return {
                'title': '',
                'image': '',
                'description': '',
            }

        data = json.loads(data_attr)
        description = data.get('text', '')
        title = data.get('title', '')
        image = data.get('image', '')

        product_dict = {
            'title': title,
            'image': image,
            'description': description,
        }

        return product_dict

    def get_detailed_product_from_html(self, soup: BeautifulSoup, asin: str, alias: str = '', keyword: str = '', page: int = 1) -> Product:
        """
        Parse detailed product information from HTML.

        :param soup: BeautifulSoup object containing the HTML content.
        :param asin: ASIN of the product.
        :param alias: Alias for the product.
        :param keyword: Keyword associated with the product.
        :param page: Page number where the product is found.
        :return: Product object with parsed information.
        """
        if '/errors/validateCaptcha' in soup.get_text():
            self.logger.error("Captcha validation error. please try using a proxy")
            return Product(asin=asin, alias=alias, keyword=keyword, page=page)
        if not asin or asin == '':
            self.logger.warning("ASIN is empty or not provided.")
            return Product(asin=asin, alias=alias, keyword=keyword, page=page)
        url = f'https://www.amazon.com/dp/{asin}'
        title_tag = soup.select_one('#productTitle')
        title = title_tag.get_text(strip=True) if title_tag else 'unavailable'
        ssf_dict = {}
        if title == 'unavailable':
            ssf_span = soup.find('span', id='ssf-share-action')
            ssf_dict = self.parse_ssf_json(ssf_span)
            # html_content = soup.prettify()
            #
            # # Specify the file path where you want to save the HTML content
            # file_path = f'{asin}.html'
            #
            # # Write the HTML content to the file
            # with open(file_path, 'w', encoding='utf-8') as file:
            #     file.write(html_content)
            if ssf_dict['title'] != '':
                title = ssf_dict['title']

        self.logger.info(f'Product title: {title}')
        # Image URL
        if ssf_dict and ssf_dict['image'] != '':
            image_url = ssf_dict['image']
        else:
            image_tag = soup.select_one('#landingImage')
            image_url = image_tag['amazonScraper'] if image_tag else 'unavailable'

        # Description
        if ssf_dict and ssf_dict['description'] != '':
            description = ssf_dict['description']
        else:
            description_tag = soup.select_one('#feature-bullets')
            description = description_tag.get_text(strip=True) if description_tag else 'unavailable'
        product_price, product_price_text, product_price_num, currency = self.get_product_price(
            soup.select_one('.priceToPay'))

        # Brand
        brand_tag = soup.select_one('#bylineInfo')
        brand = brand_tag.get_text(strip=True).replace('Brand: ', '').replace(' Store', '').replace('Visit the ',
                                                                                                    '') if brand_tag else 'unavailable'

        # Rating
        rating_tag = soup.select_one('#acrPopover')
        rating = rating_tag['title'] if rating_tag else 'unavailable'

        # Number of Ratings
        nbr_ratings_tag = soup.select_one('#acrCustomerReviewText')
        nbr_ratings = nbr_ratings_tag.get_text(strip=True) if nbr_ratings_tag else 'unavailable'

        # Check if out of stock
        is_out_of_stock = product_price == 'unavailable' or product_price == ''
        product_data = soup.find('div', id='productDetails_techSpec_sections')
        if not product_data:
            product_data = soup.find('div', id='productDetails')
        if not product_data:
            product_data = soup.find('div', id='prodDetails')
        table_data = []

        if product_data is None:
            self.logger.warning("Product data not found.")
            # html_content = soup.prettify()
            #
            # # Specify the file path where you want to save the HTML content
            # file_path = f'{asin}.html'
            #
            # # Write the HTML content to the file
            # with open(file_path, 'w', encoding='utf-8') as file:
            #     file.write(html_content)

        else:
            table = product_data.find('table')
            columns = [f"{x.text}".strip() for x in table.find_all('th')]
            for i, row in enumerate(table.find_all('tr')):  # [1:] to skip the header row
                cells = row.find_all('td')
                row_data = {columns[i]: f'{cell.text}'.strip() for cell in cells}
                table_data.append(row_data)
            self.logger.info(f'Product metadata: {table_data}')

        data = {
            'asin': asin,
            'url': url,
            'title': title,
            'image': image_url,
            'description': description,
            'price_raw': product_price,
            'price_text': product_price_text,
            'price': product_price_num,
            'currency': currency,
            'rating': rating,
            'brand': brand,
            'nbr_rating': nbr_ratings,
            'is_out_of_stock': is_out_of_stock,
            'metadata': table_data,
            'alias': alias,
            'keyword': keyword,
            'page': page
        }

        return Product(**data)


    def get_simple_product_from_json(self, item: dict, alias: str = '', keyword: str = '', page: int = 1) -> Product:
        """
        Parse simple product information from a JSON dictionary.

        :param item: Dictionary containing product information.
        :param alias: Alias for the product.
        :param keyword: Keyword associated with the product.
        :param page: Page number where the product is found.
        :return: Product object with parsed information.
        """
        try:
            return Product(
                asin=item.get('asin'),
                url=f"https://www.amazon.com/db/{item.get('asin')}",
                title=item.get('title'),
                image=item.get('formattedImageUrl'),
                description=None,
                price_raw=item.get('formattedListPrice'),
                price_text=item.get('formattedPriceV2'),
                price=float(item.get('formattedPriceV2', '0').replace('$', '').replace(',', '')) if item.get(
                    'formattedPriceV2') else 0.0,
                currency='$',
                rating=str(item.get('ratingValue')),
                brand=item.get('brand'),
                nbr_rating=str(item.get('totalReviewCount')),
                is_out_of_stock=item.get('outOfStock'),
                metadata=[],
                alias=alias,
                keyword=keyword,
                page=page
            )
        except Exception as e:
            self.logger.error(f"Error parsing product from JSON: {e}")
            return Product(asin=item.get('asin'), alias=alias, keyword=keyword, page=page)