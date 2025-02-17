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
    TIMESTAMP_FORMAT, DATE_FORMAT, TIME_FORMAT
)

PURCHASES_FILE = "data/purchase_tracker.csv"
PRICE_TRACKER_FILE = "data/price_tracker.csv"


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


def format_date_time(timestamp):
    try:
        dt = datetime.strptime(timestamp, TIMESTAMP_FORMAT)
        formatted_date = dt.strftime(DATE_FORMAT) 
        formatted_time = dt.strftime(TIME_FORMAT)  
        return formatted_date, formatted_time
    except ValueError:
        return timestamp, timestamp


def append_to_purchases_csv(data):
    item_names = []

    with open(PURCHASES_FILE, mode="a", newline="") as file:
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
            
            row = [email_ID, timestamp, date, time, name, quantity, price, url]
            writer.writerow(row)

            item_names.append(name)

    # Return the new products we've just added
    return item_names


def read_purchases_prices_csv(csv_file, columns):
    if not csv_exists(csv_file):
        raise ValueError("Error, missing CSV file")
    if not columns:
        raise ValueError("Error, missing columns")

    return pd.read_csv(csv_file, parse_dates=["timestamp"], usecols=columns)


def update_purchases_csv(tracked_items):
    if tracked_items.empty:
        raise ValueError("Error, missing tracked items, cannot update")

    tracked_items = tracked_items.sort_values(by=["name", "timestamp"], ascending=[True, False])
    tracked_items.to_csv(PRICE_TRACKER_FILE, index=False)



