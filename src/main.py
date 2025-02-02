###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Orchestrate functionality at a high level                       ##
###############################################################################

from src.parser import parse_emails  # Message / text parsing logic
from src.scraper import scrape_target  # Web scraping logic


def main():
    parse_emails()


    


if __name__ == "__main__":
    main()

