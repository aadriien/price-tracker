###############################################################################
##  `data_utils.py`                                                          ##
##                                                                           ##
##  Purpose: Handles pipelines for CSV processing                            ##
###############################################################################


import os
import csv
import pandas as pd
from datetime import datetime

from src.config import (
    format_date_time, shorten_url,
    TIMESTAMP_FORMAT
)

UNIQUE_ITEMS_FILE = "data/unique_items.csv"

PURCHASES_FILE = "data/purchase_tracker.csv"
FREE_PROMO_FILE = "data/free_promo_tracker.csv"

PRICE_TRACKER_FILE = "data/price_tracker.csv"
PRICE_SCRAPER_FILE = "data/price_scraper.csv"


def csv_exists(csv_file, create_header=None):
    # Extracts the 'data/' folder path
    folder = os.path.dirname(csv_file)  
    
    if not os.path.exists(folder):
        print(f"Folder '{folder}' not found. Creating it...")
        os.makedirs(folder)

    if os.path.exists(csv_file):
        return True

    # Provide option to create CSV (with columns) if doesn't yet exist
    if create_header:
        create_csv(csv_file, create_header)
    
    return False


def create_csv(csv_file, header):
    if csv_exists(csv_file):
        raise ValueError("Error, {csv_file} already exists")
    if not header:
        raise ValueError("Error, missing CSV header columns")

    # If CSV doesn't yet exist, then create & populate with header columns
    print(f"{csv_file} not found. Creating new CSV...")
    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)


def get_latest_date(csv_file):
    if not csv_file:
        raise ValueError("Error, missing CSV file")

    timestamps = []

    with open(csv_file, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        # Loop through rows, extracting timestamps
        for row in reader:
            timestamp = row["timestamp"].strip()  
            if timestamp:
                timestamps.append(timestamp)

    if not timestamps:
        return None

    # Convert strs to datetime objects & find most recent
    try:
        most_recent = max(datetime.strptime(timestamp, TIMESTAMP_FORMAT) for timestamp in timestamps)
        return most_recent.strftime(TIMESTAMP_FORMAT) 
    except ValueError:
        print("Warning: Invalid date format in CSV")
        return None


def append_to_purchases_free_promo_csv(csv_file, data):
    # Can handle purchase / free / promo items log
    item_names_urls = []

    with open(csv_file, mode="a", newline="") as file:
        writer = csv.writer(file)

        email_ID = data["id"]
        timestamp = data["timestamp"]
        date, time = format_date_time(timestamp)

        # New row for each item, based on email contents (data)
        for item in data["items"]:
            name = item["name"]
            url = item["URL"]
            price = item["price"]
            quantity = item["quantity"]
            
            row = [email_ID, timestamp, date, time, name, quantity, price, shorten_url(url)]
            writer.writerow(row)

            item_names_urls.append({
                "name": name, 
                "url": shorten_url(url) # Can adjust long vs short URL return
            })

    # Return the new products we've just added
    return item_names_urls


def read_purchases_prices_csv(csv_file, columns):
    # Can handle any purchase/price file with timestamp
    if not csv_exists(csv_file):
        raise ValueError("Error, missing CSV file")
    if not columns:
        raise ValueError("Error, missing columns")

    return pd.read_csv(csv_file, parse_dates=["timestamp"], usecols=columns)


def read_unique_items_csv():
    if not csv_exists(UNIQUE_ITEMS_FILE):
        raise ValueError("Error, missing CSV file")

    return pd.read_csv(UNIQUE_ITEMS_FILE)


def update_price_tracker_scraper_csv(csv_file, sorted_items):
    if sorted_items.empty:
        raise ValueError("Error, missing tracked items, cannot update")

    sorted_items.to_csv(csv_file, index=False)



