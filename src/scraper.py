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
import pandas as pd
from rapidfuzz import fuzz
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from src.config import (
    load_IP_vars, load_test_URL_vars, load_test_param_vars, launch_chrome, close_chrome, clear_cache_and_hard_reload,
    TIMESTAMP_FORMAT, 
)

from src.utils.data_utils import (
    csv_exists, read_unique_items_csv, update_price_tracker_scraper_csv,
    UNIQUE_ITEMS_FILE
)

UNIQUE_ITEMS_COLUMNS = ["name", "url"]


def update_log(items):
    new_items = pd.DataFrame(items)

    # Integrate new items with existing
    if csv_exists(UNIQUE_ITEMS_FILE, UNIQUE_ITEMS_COLUMNS):
        existing_items = read_unique_items_csv()
        all_items = pd.concat([existing_items, new_items], ignore_index=True)
    else:
        all_items = new_items

    # Ensure unique & sort
    unique_items = all_items.drop_duplicates(subset=["name"])
    unique_items = unique_items.sort_values(by="name", ascending=True).reset_index(drop=True)

    update_price_tracker_scraper_csv(UNIQUE_ITEMS_FILE, unique_items)


def get_page_source(url):
    ip, port = load_IP_vars()
    address = f"{ip}: {port}"

    # Now set up web driver
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", address)
    options.add_argument("--disable-webrtc")

    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Refresh / clean out everything
    clear_cache_and_hard_reload(driver)

    driver.execute_script("document.body.style.zoom='100%'") 
    time.sleep(2)

    actions = ActionChains(driver)
    actions.move_by_offset(100, 100).perform()
    time.sleep(2)

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



def ping_urls():
    # Launch Chrome instance before pinging URL
    launch_chrome()
    
    items = read_unique_items_csv()

    for _, row in items.iterrows():
        print(row["name"], row["url"])

        timestamp, results = scrape_page(row["url"])
        matching_item = find_match(results, row["name"])

        # print(f"\nTimestamp: {timestamp}")
        print(f"Item: {matching_item}\n")

    # Close Chrome instance after pinging URLs & retrieving page sources
    close_chrome()



