###############################################################################
##  `data_utils.py`                                                          ##
##                                                                           ##
##  Purpose: Handles pipelines for CSV processing                            ##
###############################################################################


import os
import csv
from datetime import datetime

PURCHASES_FILE = "data/purchase_tracker.csv"

PURCHASES_COLUMNS = ["email_id", "timestamp", "date", "time", "name", "quantity", "price", "url"]

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%B %d, %Y"
TIME_FORMAT = "%I:%M %p"


def purchases_csv_exists():
    # Extracts the 'data/' folder path
    folder = os.path.dirname(PURCHASES_FILE)  
    
    if not os.path.exists(folder):
        print(f"Folder '{folder}' not found. Creating it...")
        os.makedirs(folder)

    if os.path.exists(PURCHASES_FILE):
        return True

    print(f"{PURCHASES_FILE} not found. Creating new CSV...")
    with open(PURCHASES_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(PURCHASES_COLUMNS)

    return False


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



