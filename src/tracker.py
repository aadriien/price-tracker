###############################################################################
##  `tracker.py`                                                             ##
##                                                                           ##
##  Purpose: Manages price tracking, price thresholds, & price alerts,       ##
##           then analyzes & offers recommendations                          ##
###############################################################################


import os
import pandas as pd

from src.utils import (
    get_latest_date,
    PURCHASES_FILE,
    PRICE_TRACKER_FILE,
    PURCHASES_COLUMNS_BRIEF,
    PRICES_COLUMNS_ANALYSIS
)


def format_price(price):
    return f"${price:,.2f}" if pd.notna(price) else "N/A"


def format_percentage(percentage):
    return f"{percentage:,.2f}%" if pd.notna(percentage) else "N/A"


def format_price_log_for_display(price_log):
    # Restore $ sign, % sign, etc only for export/display
    price_log_display = price_log.copy()

    for col in PRICES_COLUMNS_ANALYSIS:
        if col == "percent_change":
            price_log_display[col] = price_log_display[col].apply(format_percentage)
        else:
            price_log_display[col] = price_log_display[col].apply(format_price)

    return price_log_display


def track_price_changes(since=None):
    # Automatically create datetime instances form CSV for sorting
    price_log = pd.read_csv(PURCHASES_FILE, parse_dates=["timestamp"], usecols=PURCHASES_COLUMNS_BRIEF)
    
    if since:
        price_log = price_log[price_log["timestamp"] > pd.to_datetime(since)]
    
    price_log = price_log.sort_values(by=["name", "timestamp"]) 

    # Remove $ sign & convert prices to float for math
    price_log["price"] = price_log["price"].replace(r"[\$,]", "", regex=True).astype(float)

    price_log["prev_price"] = price_log.groupby("name")["price"].shift(1) 
    price_log["price_change"] = price_log["price"] - price_log["prev_price"] 
    price_log["percent_change"] = (price_log["price_change"] / price_log["prev_price"]) * 100

    # Track rolling average (mean up until & including curr row, i.e.
    # disregard any future purchases, only focus on avg until this point)
    price_log["avg_price"] = (
        price_log.groupby("name")["price"]
        .expanding()
        .mean()
        .reset_index(level=0, drop=True)
    )
    price_log["diff_from_avg"] = price_log["price"] - price_log["avg_price"] 
    
    return price_log


def update_price_tracker(csv_file=PRICE_TRACKER_FILE):
    # If the file doesn't exist, create it with headers & populate with logs
    if not os.path.exists(csv_file):
        new_price_logs = track_price_changes().sort_values(by=["name", "timestamp"], ascending=[True, False])
        format_price_log_for_display(new_price_logs).to_csv(csv_file, index=False)
    else:
        # Find where we left off, then add new data without loading full file
        latest_date = get_latest_date(csv_file)
        new_price_logs = track_price_changes(latest_date)

        format_price_log_for_display(new_price_logs).to_csv(csv_file, mode="a", header=False, index=False)
        
        # Now load, sort, and overwrite for proper organization
        sorted_price_logs = pd.read_csv(csv_file, parse_dates=["timestamp"])
        sorted_price_logs = sorted_price_logs.sort_values(by=["name", "timestamp"], ascending=[True, False])
        sorted_price_logs.to_csv(csv_file, index=False)


def track_prices():
    update_price_tracker()




