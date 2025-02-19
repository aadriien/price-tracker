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
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from src.config import (
    load_IP_vars, load_test_URL_var, load_test_param_vars,
    TIMESTAMP_FORMAT
)


def get_page_source():
    ip, port = load_IP_vars()
    address = f"{ip}: {port}"

    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", address)
    options.add_argument("--disable-webrtc")
    options.add_argument("--incognito") 

    driver = webdriver.Chrome(options=options)

    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")

    url = load_test_URL_var()
    driver.get(url)

    actions = ActionChains(driver)
    actions.move_by_offset(100, 100).perform()
    time.sleep(2)

    return driver.page_source


def validate_items():
    # Get test parameters & parse
    page_source = get_page_source()
    test_param_1, test_param_2, test_param_3, test_param_4 = load_test_param_vars()

    pattern = re.findall(
        rf'"value":"(\d+) {test_param_1}".*?"{test_param_2}":"(.*?)".*?"{test_param_3}":"(\$[\d.]+)".*?"{test_param_4}":"(\$[\d.]+)"',
        page_source
    )
    
    # Convert results into structured list of dicts
    results = [
        {
            test_param_1: param_1,
            test_param_2: json.loads(f'"{param_2}"'),  # Decode special chars
            test_param_3: param_3,
            test_param_4: param_4
        }
        for param_1, param_2, param_3, param_4 in pattern
    ]

    curr_timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    print(f"\nCurr timestamp: {curr_timestamp}\n")

    for item in results:
        print(f"{test_param_1}: {item[test_param_1]}, {test_param_2}: {item[test_param_2]}, {test_param_3}: {item[test_param_3]}, {test_param_4}: {item[test_param_4]}")

    return results




