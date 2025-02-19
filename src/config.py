###############################################################################
##  `config.py`                                                              ##
##                                                                           ##
##  Purpose: Manages setup and key constants                                 ##
###############################################################################


import os
from dotenv import load_dotenv


TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%B %d, %Y"
TIME_FORMAT = "%I:%M %p"


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

    if not ip_env and port_env:
        raise ValueError("IP and PORT must be set in .env to query site")

    return ip_env, port_env
    

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



