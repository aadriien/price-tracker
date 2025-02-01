###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Orchestrate functionality at a high level                       ##
###############################################################################

from src.utils import connect_to_gmail, fetch_email_IDs # Email login
from src.parser import parse_emails  # Message / text parsing logic
from src.scraper import scrape_target  # Web scraping logic


def main():
    mail = connect_to_gmail()
    # Rest of the program logic
    # e.g., connecting to Gmail, parsing emails, etc.
    fetch_email_IDs(mail)
    


if __name__ == "__main__":
    main()

