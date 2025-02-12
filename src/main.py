###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Orchestrate functionality at a high level                       ##
###############################################################################

from src.parser import parse_emails # Message / text parsing logic
from src.tracker import track_prices # Price trend analysis logic
from src.scraper import scrape_target # Web scraping logic


def main():
    new_emails = parse_emails()
    if new_emails:
        track_prices()


    


if __name__ == "__main__":
    main()

