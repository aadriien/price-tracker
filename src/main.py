###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Orchestrate functionality at a high level                       ##
###############################################################################

from encrypt import setup_encryption  # Initialize encryption, env vars, etc
from parser import parse_emails  # Email parsing logic
from scraper import scrape_target  # Web scraping logic


def main():
    setup_encryption()
    # Rest of the program logic
    # e.g., connecting to Gmail, parsing emails, etc.


if __name__ == "__main__":
    main()

    