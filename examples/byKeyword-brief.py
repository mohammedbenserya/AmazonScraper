from AmazonSmartScraper.scraper import AmazonScraper
import pandas as pd

scraper = AmazonScraper(use_selenium_headers=False)

# set the proxy
# scraper.set_proxy('185.76.11.212',10096)


keyword = 'phones'
res = scraper.get_asins_by_keyword(keyword)

all_products = []
csv_file = f'{keyword}.csv'

# Get total pages from the initial response
total_pages = res[1]

# Loop through all pages to get ASINs
for page in range(1, total_pages + 1):
    res = scraper.get_asins_by_keyword(keyword, page)

    # Extract new ASINs that are not already in the list
    new_asins = [asin['asin'] for asin in res[0] if not any(product['asin'] == asin['asin'] for product in all_products)]

    if not new_asins:
        break

    asins = ','.join(new_asins)
    product_briefs = scraper.get_products_brief(asins)

    for asin in product_briefs:
        if any(product['asin'] == asin['asin'] for product in all_products):
            continue
        product_details = scraper.generate_product.get_simple_product_from_json(item=asin, keyword=keyword, page=page)
        print(product_details)
        all_products.append(product_details.dict())

# Save the product details to a CSV file
df = pd.DataFrame(all_products)
df.to_csv(csv_file, index=False, encoding='utf-8')