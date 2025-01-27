###############################################################################
##  `scraper.py`                                                             ##
##                                                                           ##
##  Purpose: Dynamically scrapes product URLs from listing pages             ##
##           (by category), then scrapes those individual product            ##
##           pages for prices                                                ##
###############################################################################


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

import time




def scrape_target(url):
    # Automatically download and manage ChromeDriver
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # Open the URL
        driver.get(url)

        # Wait for the page to load completely (adjust time if needed)
        driver.implicitly_wait(5)

        # Initialize variables
        all_product_containers = []
        previous_product_count = 0
        scroll_pause_time = 1  # Time to wait for content to load
        max_products = 100 # Limit to top 100 bestselling (based on URL)

        # Scroll the page until no more products are loaded
        while len(all_product_containers) < max_products:
            # Get the current page source after scrolling
            html = driver.page_source

            # Parse the HTML with BeautifulSoup only once after scrolling
            soup = BeautifulSoup(html, "lxml")

            # Find all product containers
            product_containers = soup.select(".styles_ndsRow__iT6yG")
            all_product_containers.extend(product_containers)

            # Check if new products were loaded
            if len(all_product_containers) == previous_product_count:
                break  # Exit loop if no new products were loaded

            # Update the previous product count
            previous_product_count = len(all_product_containers)

            # Scroll down to load more products
            driver.execute_script("window.scrollBy(0, window.innerHeight);")
            time.sleep(scroll_pause_time)  # Wait for new content to load

        all_product_containers = all_product_containers[:max_products]
        
        # Print the final product count
        print(f"Total products found: {len(all_product_containers)}")

    finally:
        # Always close the browser
        driver.quit()

# Example usage
# scrape_target("https://www.target.com/c/nintendo-switch-games-video/-/N-p86ax")
scrape_target("https://www.target.com/c/nintendo-switch-games-video/-/N-p86ax?sortBy=bestselling&moveTo=product-list-grid")







# import requests
# import json
# from bs4 import BeautifulSoup


# # Fetch HTML content of page
# url = "https://www.target.com/c/nintendo-switch-games-video/-/N-p86ax"
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
# }

# response = requests.get(url, headers=headers)

# # Print status & content (first 500 chars of HTML)
# # print(f"Status Code: {response.status_code}")
# # print(response.text[:500]) 


# # Parse HTML content using lxml (for speed, if installed) otherwise default
# def get_soup(html):
#     try:
#         return BeautifulSoup(html, "lxml")
#     except Exception as e:
#         print(f"lxml not available, defaulting to html.parser: {e}")
#         return BeautifulSoup(html, "html.parser")

# soup = get_soup(response.text)


# # Print the title of the page
# page_title = soup.title.string
# # print(f"Page Title: {page_title}")




# # Find product containers
# # product_containers = soup.select(".styles_ndsRow__iT6yG")
# product_containers = soup.find_all('div', class_='styles_ndsRow__iT6yG')
# # product_containers = soup.find_all('div', {'data-test': '@web/ProductCard/body'})
# print(f"Found {len(product_containers)} products")







