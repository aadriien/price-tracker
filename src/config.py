###############################################################################
##  `config.py`                                                              ##
##                                                                           ##
##  Purpose: Manages setup and key constants                                 ##
###############################################################################


import os
import sys
import time
import requests
import subprocess
from datetime import datetime
from dotenv import load_dotenv


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%B %d, %Y"
TIME_FORMAT = "%I:%M %p"


def format_date_time(timestamp):
    try:
        dt = datetime.strptime(timestamp, TIMESTAMP_FORMAT)
        formatted_date = dt.strftime(DATE_FORMAT) 
        formatted_time = dt.strftime(TIME_FORMAT)  
        return formatted_date, formatted_time
    except ValueError:
        return timestamp, timestamp


def shorten_url(url):
    # Utilize TinyURL to condense link
    api_url = f"http://tinyurl.com/api-create.php?url={url}"
    response = requests.get(api_url)
    return response.text if response.status_code == 200 else None


def load_email_vars():
    # Load email filter parameters
    load_dotenv()

    from_env = os.getenv("GMAIL_FROM")
    subject_env = os.getenv("GMAIL_SUBJECT")

    if not from_env and subject_env:
        raise ValueError("GMAIL_FROM and GMAIL_SUBJECT must be set in .env to filter")

    return from_env, subject_env


def load_IP_vars():
    # Load IP & port parameters
    load_dotenv()

    ip_env = os.getenv("IP")
    port_env = os.getenv("PORT")
    main_url_env = os.getenv("MAIN_URL")

    if not ip_env and port_env and main_url_env:
        raise ValueError("IP, PORT, MAIN_URL must be set in .env to query site")

    return ip_env, port_env, main_url_env
    

def load_test_URL_vars():
    # Load test URL & name parameters
    load_dotenv()

    test_url_env = os.getenv("TEST_URL")
    test_name_env = os.getenv("TEST_NAME")

    if not test_url_env and test_name_env:
        raise ValueError("TEST_URL and TEST_NAME must be set in .env to query site")

    return test_url_env, test_name_env


def load_test_param_vars():
    # Load test parameter vars
    load_dotenv()

    test_param_1_env = os.getenv("TEST_PARAM_1")
    test_param_2_env = os.getenv("TEST_PARAM_2")
    test_param_3_env = os.getenv("TEST_PARAM_3")
    test_param_4_env = os.getenv("TEST_PARAM_4")

    if not test_param_1_env and test_param_2_env and test_param_3_env and test_param_4_env:
        raise ValueError("TEST_PARAMS_ 1, 2, 3, 4 must be set in .env")

    return test_param_1_env, test_param_2_env, test_param_3_env, test_param_4_env


def launch_chrome():
    # Launch Chrome as independent process 
    subprocess.Popen([
        # -g flag to open in background (specific to macOS)
        "open", "-g", "-a", "Google Chrome", 
        "--args",
        "--remote-debugging-port=9222",
        "--user-data-dir=/tmp/chrome-debug-new1",
        "--disable-gpu",
        "--disable-webrtc",
        "--disable-software-rasterizer",
        "--disable-background-networking",
        "--disable-blink-features=AutomationControlled",
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "--no-default-browser-check",
        "--disable-logging",
        "--log-level=3"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)  

    time.sleep(5)


def close_chrome():
    # Close Chrome after task finished (specific to macOS)
    if sys.platform == "darwin":
        subprocess.call(["pkill", "Google Chrome"])
        subprocess.call(["pkill", "chromedriver"])


def clear_cache_and_hard_reload(driver):
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")


