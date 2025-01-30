###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Orchestrate functionality at a high level                       ##
###############################################################################

from src.encrypt import setup_encryption  # Initialize encryption, env vars, etc
from src.utils import connect_to_gmail # Email login
from src.parser import parse_emails  # Message / text parsing logic
from src.scraper import scrape_target  # Web scraping logic


def main():
    setup_encryption()
    # Rest of the program logic
    # e.g., connecting to Gmail, parsing emails, etc.
    connect_to_gmail()


if __name__ == "__main__":
    main()

