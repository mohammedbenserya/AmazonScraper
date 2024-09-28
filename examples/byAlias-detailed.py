from AmazonSmartScraper.scraper import AmazonScraper
import pandas as pd

scraper = AmazonScraper(use_selenium_headers=True)

# set the proxy
scraper.set_proxy('185.76.11.212',10096)


alias = 'specialty-aps'
res = scraper.get_asins_by_alias(alias)
all_products = []
csv_file = f'{alias}.csv'

# Get total pages from the initial response
total_pages = res[1]
print(total_pages)

# Loop through all pages to get ASINs
for page in range(1, total_pages + 1):
    print(page)
    res = scraper.get_asins_by_alias(alias, page)

    # Extract new ASINs that are not already in the list
    new_asins = [asin['asin'] for asin in res[0] if asin['asin'] not in all_products]

    if not new_asins:
        break

    # Get brief product details for the new ASINs
    for asin in new_asins:
        print(asin)
        soup = scraper.get_soup_from_asin(asin)
        product_details = scraper.generate_product.get_detailed_product_from_html(soup=soup, asin=asin, keyword=alias, page=page)
        print(product_details)
        all_products.append(product_details.dict())

    # Save the product details to a CSV file
    df = pd.DataFrame(all_products)
    df.to_csv(csv_file, index=False, encoding='utf-8')