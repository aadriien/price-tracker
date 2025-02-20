###############################################################################
##  `main.py`                                                                ##
##                                                                           ##
##  Purpose: Orchestrate functionality at a high level                       ##
###############################################################################


from src.parser import check_emails # Message / text parsing logic
from src.tracker import track_prices # Price trend analysis logic
from src.scraper import update_log # Web scraping logic


def main():
    new_items = check_emails()
    if new_items:
        track_prices(new_items)
        update_log(new_items)

    # validate_items()

    


if __name__ == "__main__":
    main()

