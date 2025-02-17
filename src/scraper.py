###############################################################################
##  `scraper.py`                                                             ##
##                                                                           ##
##  Purpose: Dynamically scrapes product URLs from listing pages             ##
##           (by category), then scrapes those individual product            ##
##           pages for prices                                                ##
###############################################################################


import re
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

from src.config import load_IP_vars, load_test_URL_var, load_test_param_vars


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
    test_param_1, test_param_2, test_param_3 = load_test_param_vars()

    pattern = re.findall(
        rf'"value":"(\d+) {test_param_1}".*?"{test_param_2}":"(\$[\d.]+)".*?"{test_param_3}":"(\$[\d.]+)"',
        page_source
    )
    
    # Convert results into structured list of dicts
    results = [{"{test_param_1}": param_1, "{test_param_2}": param_2, "{test_param_3}": param_3} for param_1, param_2, param_3 in pattern]

    for item in results:
        print(f"{test_param_1}: {item['{test_param_1}']}, {test_param_2}: {item['{test_param_2}']}, {test_param_3}: {item['{test_param_3}']}")


