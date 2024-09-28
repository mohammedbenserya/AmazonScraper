from AmazonSmartScraper.scraper import AmazonScraper

import pandas as pd
scraper = AmazonScraper(use_selenium_headers=True)

# scraper.set_proxy('149.14.243.178',10361)
# res = scraper.get_asins_by_keyword('phones')

# res = scraper.get_asins_by_alias('computers-intl-ship')
url = 'https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A1292115011'
res = scraper.get_asins_by_link(url=url,check_pagination=True)
all_products = []
csv_file = '../by-url-detailed.csv'
# First loop to get all ASINs
all_asins = []
print(res[1])
for page in range(1, res[1] + 1):
    print(page)
    res = scraper.get_asins_by_link(url=url, check_pagination=True)
    all_asins = [asin for asin in res[0] if not any(product['asin'] == asin for product in all_products)]
    asins = ','.join([asin for asin in all_asins])
    #product_briefs = scraper.get_products_brief(asins)
    for asin in res[0]:
        print(asin)
        if any(product['asin'] == asin for product in all_products):
            continue
        #product_details = scraper.generate_product.get_simple_product_from_json(asin)
        soup=scraper.get_soup_from_asin(asin)
        product_details = scraper.generate_product.get_detailed_product_from_html(soup=soup,asin= asin,keyword=url,page=page)
        print(product_details)
        all_products.append(product_details.dict())
        df = pd.DataFrame(all_products)
        df.to_csv(csv_file, index=False, encoding='utf-8')