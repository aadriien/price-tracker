###############################################################################
##  `scraper.py`                                                             ##
##                                                                           ##
##  Purpose: Dynamically scrapes product URLs from listing pages             ##
##           (by category), then scrapes those individual product            ##
##           pages for prices                                                ##
###############################################################################


import re
import json
import time
import random

import pandas as pd
from rapidfuzz import fuzz
from datetime import datetime

from multiprocessing import Pool
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from src.tracker import calculate_price_deltas

from src.config import (
    load_IP_vars, load_test_URL_vars, load_test_param_vars, launch_chrome, close_chrome, clear_cache_and_hard_reload,
    TIMESTAMP_FORMAT, 
)

from src.utils.data_utils import (
    csv_exists, read_purchases_prices_csv, read_unique_items_csv, update_price_tracker_scraper_csv,
    UNIQUE_ITEMS_FILE, PRICE_SCRAPER_FILE
)

UNIQUE_ITEMS_COLUMNS = ["name", "url"]
SCRAPED_COLUMNS_BRIEF = ["timestamp", "name", "matching_name", "price"]


def update_log(items):
    new_items = pd.DataFrame(items)

    # Integrate new items with existing
    if csv_exists(UNIQUE_ITEMS_FILE):
        existing_items = read_unique_items_csv()
        all_items = pd.concat([existing_items, new_items], ignore_index=True)
    else:
        all_items = new_items

    # Ensure unique & sort
    unique_items = all_items.drop_duplicates(subset=["name"])
    unique_items = unique_items.sort_values(by="name", ascending=True).reset_index(drop=True)

    update_price_tracker_scraper_csv(UNIQUE_ITEMS_FILE, unique_items)


def track_scraped(items):
    new_scraped = pd.DataFrame(items)

    # If we already have scraped data, combine updated with unchanged
    if csv_exists(PRICE_SCRAPER_FILE):
        prev_scraped = read_purchases_prices_csv(PRICE_SCRAPER_FILE, SCRAPED_COLUMNS_BRIEF)
        all_scraped = pd.concat([prev_scraped, new_scraped], ignore_index=True)
    else:
        # No existing file, so just use the new formatted data
        all_scraped = new_scraped

    tracked_and_formatted = calculate_price_deltas(all_scraped)

    tracked_and_formatted = tracked_and_formatted.sort_values(by=["name", "timestamp"], ascending=[True, False]).reset_index(drop=True)
    update_price_tracker_scraper_csv(PRICE_SCRAPER_FILE, tracked_and_formatted)


def get_page_source(url):
    ip, port = load_IP_vars()
    address = f"{ip}:{port}"

    # Now set up web driver
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", address)
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-webrtc")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Refresh / clean out everything
    clear_cache_and_hard_reload(driver)

    driver.execute_script("document.body.style.zoom='100%'") 
    time.sleep(random.uniform(1, 3))

    actions = ActionChains(driver)
    actions.move_by_offset(100, 100).perform()
    time.sleep(random.uniform(1, 3))

    return driver.page_source


def scrape_page(url):
    page_source = get_page_source(url)
    _, test_param_2, test_param_3, _ = load_test_param_vars()

    pattern = rf'"__typename":"Item".*?"{test_param_2}":"(.*?)".*?"{test_param_3}":"(\$[\d.]+)"'
    # patternOld = rf'"value":"(\d+) {test_param_1}".*?"{test_param_2}":"(.*?)".*?"{test_param_3}":"(\$[\d.]+)".*?"{test_param_4}":"(\$[\d.]+)"'
    matches = re.findall(pattern, page_source)
    
    # Convert results into structured list of dicts
    results = [
        {
            # test_param_1: param_1,
            test_param_2: json.loads(f'"{param_2}"'),  # Decode special chars
            test_param_3: param_3,
            # test_param_4: param_4
        }
        # for param_1, param_2, param_3, param_4 in matches
        for param_2, param_3 in matches
    ]

    curr_timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)

    return curr_timestamp, results


def find_match(potential_matches, name):
    matching_item = None
    max_match_score = 0

    for item in potential_matches:
        # Scores 0-100 based on text match (e.g. 85% logical similarity, 90%, etc)
        similarity_score = fuzz.ratio(item["name"], name)  

        if similarity_score > max_match_score:
            matching_item = item
            max_match_score = similarity_score

    return matching_item


def ping_url(row):
    name, url = row["name"], row["url"]
    _, test_param_2, test_param_3, _ = load_test_param_vars()

    timestamp, results = scrape_page(url)
    matching_item = find_match(results, name)

    if not matching_item:
        print(f"Skipping {name}: No matching item found.")
        return None

    # print(f"\nTimestamp: {timestamp}")
    # print(f"\nItem: {matching_item}")

    return {
        "timestamp": timestamp,
        "name": name,
        "matching_name": matching_item["name"],
        "price": matching_item[test_param_3]
    }


# def ping_urls():
#     # Launch Chrome instance before pinging URL
#     launch_chrome()

#     # test_url, test_name = load_test_URL_vars()
#     # # proxy_url = "https://cors-anywhere.herokuapp.com/"
#     # # test_url = proxy_url + test_url

#     # timestamp, results = scrape_page(test_url)
#     # matching_item = find_match(results, test_url)

#     # # close_chrome()

#     # return
    
#     items = read_unique_items_csv()

#     for _, row in items.iterrows():
#         print(row["name"], row["url"])

#         timestamp, results = scrape_page(row["url"])
#         matching_item = find_match(results, row["name"])

#         # print(f"\nTimestamp: {timestamp}")
#         print(f"Item: {matching_item}\n")
#         return

#     # Close Chrome instance after pinging URLs & retrieving page sources
#     close_chrome()


def scrape():
    # ping_urls()


    items_df = read_unique_items_csv()
    items_list = items_df.to_dict(orient="records")

    # Launch Chrome before pinging URLs 
    launch_chrome()
    
    latest_batch = []
    for row in items_list:
        latest_batch.append(ping_url(row))

    # Close Chrome instance after pinging URLs & retrieving page sources
    close_chrome()

    track_scraped(latest_batch)




