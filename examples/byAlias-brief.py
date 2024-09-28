from AmazonSmartScraper.scraper import AmazonScraper

import pandas as pd
scraper = AmazonScraper(use_selenium_headers=True)
alias = 'specialty-aps'
res = scraper.get_asins_by_alias(alias)
all_products = []
csv_file = f'{alias}.csv'
# First loop to get all ASINs
all_asins = []
print(res[1])
for page in range(1, res[1] + 1):
    print(page)
    res = scraper.get_asins_by_alias(alias, page)
    all_asins = [asin['asin'] for asin in res[0] if not any(product['asin'] == asin['asin'] for product in all_products)]
    asins = ','.join([asin for asin in all_asins])
    if len(all_asins) == 0:
        break
    product_briefs = scraper.get_products_brief(asins)
    for asin in product_briefs:
        print(asin['asin'])
        if any(product['asin'] == asin['asin'] for product in all_products):
            continue
        product_details = scraper.generate_product.get_simple_product_from_json(item=asin, alias=alias, page=page)
        print(product_details)
        all_products.append(product_details.dict())
        df = pd.DataFrame(all_products)
        df.to_csv(csv_file, index=False, encoding='utf-8')