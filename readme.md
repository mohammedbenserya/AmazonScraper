# Amazon Smart Scraper Package

## Overview

The Amazon Smart Scraper package is designed to facilitate the extraction of product information from Amazon. It uses the Amazon exposed APIs for mass extraction and supports various functionalities such as retrieving ASINs by keyword, alias, or URL, and parsing detailed product information from responses. It's smart enough to use Selenium to build the sessions for the requests library without the need to search for valid headers, etc., for your scraping session. Additionally, it supports using proxies. All these options are optional.
## Features

- **Retrieve ASINs by Keyword**: Search for products on Amazon using specific keywords and retrieve their ASINs.
- **Retrieve ASINs by Alias**: Fetch ASINs based on predefined aliases for product categories.
- **Retrieve ASINs by URL**: Extract ASINs from a given Amazon URL, with optional pagination support.
- **Parse Product Information**: Convert JSON responses into structured product data, including details like title, price, rating, and more.

## Prerequisites

- Python 3.10 or higher


## Installation

To install the package, use the following command:

```sh
pip install AmazonSmartScraper
```

## Usage

For usage examples, refer to the `examples` directory or visit the [GitHub repository](https://github.com/mohammedbenserya/AmazonScraper/tree/main/examples).


## Contact Information

For issues, questions, or suggestions, please open an issue on the [GitHub repository](https://github.com/mohammedbenserya/AmazonScraper) or contact the author at benseryamohammed1@gmail.com.