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
    # Load email filter parameters
    load_dotenv()

    ip_env = os.getenv("IP")
    port_env = os.getenv("PORT")

    if not ip_env and port_env:
        raise ValueError("IP and PORT must be set in .env to query site")

    return ip_env, port_env



