###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Orchestrate functionality at a high level                       ##
###############################################################################


from src.email_utils import load_env_vars # Filter & connection logic
from src.parser import check_emails # Message / text parsing logic
from src.tracker import track_prices # Price trend analysis logic
from src.scraper import scrape_target # Web scraping logic


def main():
    load_env_vars()

    new_items = check_emails()
    if new_items:
        track_prices(new_items)


    


if __name__ == "__main__":
    main()

