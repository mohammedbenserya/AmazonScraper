import re, json
from bs4 import BeautifulSoup
from AmazonSmartScraper.schemas.custom_errors import ParsingError
from AmazonSmartScraper.schemas.product import Product


class AParser:
    """
    AParser class is responsible for parsing product information from HTML and JSON data.
    """

    def __init__(self, logger):
        """
        Initialize the AParser with a logger.

        :param logger: Logger instance for logging messages.
        """
        self.__logger = logger

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

    def get_simple_product_from_html(self, soup: BeautifulSoup, asin: str, alias: str = '', keyword: str = '',
                                     page: int = 1) -> Product:
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
            raise ParsingError("Captcha validation error. Please try using a proxy", element="Captcha")
        url = f'https://www.amazon.com/dp/{asin}'
        title = soup.select_one('.a-size-mini.a-spacing-none.a-color-base.s-line-clamp-2').get_text(
            strip=True) if soup.select_one('.a-size-mini.a-spacing-none.a-color-base.s-line-clamp-2') else None
        image = soup.find('img', {'data-image-latency': 's-product-image'})['src'] if soup.find('img', {
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

    def __parse_ssf_json(self, ssf_span) -> dict:
        """
        Parse SSF JSON data from the given span tag.

        :param ssf_span: BeautifulSoup tag containing the SSF JSON data.
        :return: Dictionary with title, image, and description.
        """
        try:
            data_attr = ssf_span.get('data-ssf-share-icon')
        except AttributeError as e:
            self.__logger.error(f"Error accessing 'data-ssf-share-icon' attribute: {e}")
            return {
                'title': '',
                'image': '',
                'description': '',
            }
        if not data_attr:
            self.__logger.warning("No data-ssf-share-icon attribute found.")
            return {
                'title': '',
                'image': '',
                'description': '',
            }

        data = json.loads(data_attr)
        description = data.get('text', '')
        title = data.get('title', '')
        image = data.get('image', '')
        self.__logger.debug(f"SSF JSON data: {data}")
        product_dict = {
            'title': title,
            'image': image,
            'description': description,
        }

        return product_dict
    def __get_titles(self, soup: BeautifulSoup,ssf_dict : dict) -> str:
        """
        Get the title of the product from the HTML content.

        :param soup: BeautifulSoup object containing the HTML content.
        :param ssf_dict: Dictionary containing SSF JSON data.

        :return: Title of the product.
        """
        title_tag = soup.select_one('#productTitle')
        prod_title = title_tag.get_text(strip=True) if title_tag else ssf_dict.get('title', 'unavailable')

        self.__logger.info(f'Product title: {prod_title}')
        return prod_title
    @staticmethod
    def __get_img( soup: BeautifulSoup,ssf_dict : dict) -> str:
        """
        Get the title of the product from the HTML content.

        :param soup: BeautifulSoup object containing the HTML content.
        :param ssf_dict: Dictionary containing SSF JSON data.
        :return: Title of the product.
        """
        image_tag = soup.select_one('#landingImage') or soup.select_one('#imgTagWrapperId img')
        image_url = image_tag.get('amazonScraper',
                                  image_tag.get('data-old-hires', 'unavailable')) if image_tag else ssf_dict.get(
            'image', 'unavailable')
        return image_url
    @staticmethod
    def __get_description( soup: BeautifulSoup,ssf_dict : dict) -> str:
        """
        Get the description of the product from the HTML content.

        :param soup: BeautifulSoup object containing the HTML content.
        :param ssf_dict: Dictionary containing SSF JSON data.
        :return: Description of the product.
        """
        # Description
        description_tag = soup.select_one('#feature-bullets')
        description = description_tag.get_text(strip=True) if description_tag else ssf_dict.get('description',
                                                                                                'unavailable')
        return description
    def get_detailed_product_from_html(self, soup: BeautifulSoup, asin: str, alias: str = '', keyword: str = '',
                                       page: int = 1) -> Product:
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
            raise ParsingError("Captcha validation error. Please try using a proxy", element="Captcha")
        if not asin or asin == '':
            self.__logger.warning("ASIN is empty or not provided.")
            return Product(asin=asin, alias=alias, keyword=keyword, page=page)
        url = f'https://www.amazon.com/dp/{asin}'
        ssf_span = soup.find('span', id='ssf-share-action')
        ssf_dict = self.__parse_ssf_json(ssf_span) if ssf_span else {}





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
            self.__logger.warning("Product data not found.")

        else:
            table = product_data.find('table')
            columns = [f"{x.text}".strip() for x in table.find_all('th')]
            for i, row in enumerate(table.find_all('tr')):  # [1:] to skip the header row
                cells = row.find_all('td')
                row_data = {columns[i]: f'{cell.text}'.strip() for cell in cells}
                table_data.append(row_data)
            self.__logger.info(f'Product metadata: {table_data}')

        data = {
            'asin': asin,
            'url': url,
            'title': self.__get_titles(soup,ssf_dict),
            'image': self.__get_img(soup,ssf_dict),
            'description': self.__get_description(soup,ssf_dict),
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
            self.__logger.error(f"Error parsing product from JSON: {e}")
            return Product(asin=item.get('asin'), alias=alias, keyword=keyword, page=page)
