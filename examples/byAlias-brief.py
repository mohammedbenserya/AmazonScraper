from AmazonSmartScraper.scraper import AmazonScraper

import pandas as pd
# Initialize the AmazonScraper with Selenium headers
scraper = AmazonScraper(use_selenium_headers=True)

# set the proxy
scraper.set_proxy('91.228.216.36',10047)

# Alias for the product category
alias = 'specialty-aps'

# Get the initial ASINs and total pages for the given alias
res = scraper.get_asins_by_alias(alias)

# List to store all product details
all_products = []

# CSV file name to save the results
csv_file = f'{alias}.csv'

# First loop to get all ASINs
all_asins = []
total_pages = res[1]
print(total_pages)

for page in range(1, total_pages + 1):
    print(page)
    res = scraper.get_asins_by_alias(alias, page)

    # Extract new ASINs that are not already in the list
    new_asins = [asin['asin'] for asin in res[0] if asin['asin'] not in all_asins]
    all_asins.extend(new_asins)

    if not new_asins:
        break

    # Join ASINs into a comma-separated string
    asins = ','.join(new_asins)

    # Get brief product details for the ASINs
    product_briefs = scraper.get_products_brief(asins)

    for asin in product_briefs:
        if asin['asin'] in all_asins:
            continue

        # Generate simple product details from JSON
        product_details = scraper.generate_product.get_simple_product_from_json(item=asin, alias=alias, page=page)
        all_products.append(product_details.dict())

    # Save the product details to a CSV file
    df = pd.DataFrame(all_products)
    df.to_csv(csv_file, index=False, encoding='utf-8')