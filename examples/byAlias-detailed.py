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
    product_briefs=res[0]
    for asin in product_briefs:
        print(asin['asin'])
        if any(product['asin'] == asin['asin'] for product in all_products):
            continue
        soup=scraper.get_soup_from_asin(asin['asin'])
        product_details = scraper.generate_product.get_detailed_product_from_html(soup=soup,asin= asin['asin'],keyword=alias,page=page)
        print(product_details)
        all_products.append(product_details.dict())
        df = pd.DataFrame(all_products)
        df.to_csv(csv_file, index=False, encoding='utf-8')