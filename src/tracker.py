###############################################################################
##  `tracker.py`                                                             ##
##                                                                           ##
##  Purpose: Manages price tracking, price thresholds, & price alerts,       ##
##           then analyzes & offers recommendations                          ##
###############################################################################


import pandas as pd
import numpy as np

from src.utils.data_utils import (
    csv_exists, read_purchases_prices_csv, update_price_tracker_scraper_csv,
    PURCHASES_FILE, PRICE_TRACKER_FILE
)

PURCHASES_COLUMNS_BRIEF = ["timestamp", "name", "quantity", "price"]
PRICES_COLUMNS_ANALYSIS = ["price", "prev_price", "price_change", "percent_change", "avg_price", "diff_from_avg"]
TRACKER_COLUMNS_FULL = ["timestamp", "name", "quantity", "price", "prev_price", "price_change", "percent_change", "avg_price", "diff_from_avg"]


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


def calculate_price_deltas(items):
    items = items.sort_values(by=["name", "timestamp"])
  
    # Remove $ sign & convert prices to float for math
    items["price"] = items["price"].replace(r"[\$,]", "", regex=True).astype(float)

    items["prev_price"] = items.groupby("name")["price"].shift(1) 
    items["prev_price"] = items["prev_price"].fillna(np.nan)

    items["price_change"] = items["price"] - items["prev_price"] 
    items["percent_change"] = (items["price_change"] / items["prev_price"]) * 100

    # Track rolling average (mean up until & including curr row, i.e.
    # disregard any future purchases, only focus on avg until this point)
    items["avg_price"] = (
        items.groupby("name")["price"]
        .expanding()
        .mean()
        .reset_index(level=0, drop=True)
    )
    items["diff_from_avg"] = items["price"] - items["avg_price"] 
    
    return format_price_log_for_display(items)


def track_prices(items):
    new_items = pd.DataFrame(items)
    
    # Automatically create datetime instances from CSV for sorting
    all_purchases = read_purchases_prices_csv(PURCHASES_FILE, PURCHASES_COLUMNS_BRIEF)
    items_to_update = all_purchases[all_purchases["name"].isin(new_items["name"])].copy()

    tracked_and_formatted = calculate_price_deltas(items_to_update)

    # If we already have price tracking data, combine updated with unchanged
    if csv_exists(PRICE_TRACKER_FILE):
        prev_tracked = read_purchases_prices_csv(PRICE_TRACKER_FILE, TRACKER_COLUMNS_FULL)
        unchanged_items = prev_tracked[~prev_tracked["name"].isin(new_items["name"])]

        all_tracked = pd.concat([unchanged_items, tracked_and_formatted], ignore_index=True)
    else:
        # No existing file, so just use the new formatted data
        all_tracked = tracked_and_formatted

    all_tracked = all_tracked.sort_values(by=["name", "timestamp"], ascending=[True, False]).reset_index(drop=True)
    update_price_tracker_scraper_csv(PRICE_TRACKER_FILE, all_tracked)

    
    
 




