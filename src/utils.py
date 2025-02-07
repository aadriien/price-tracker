###############################################################################
##  `utils.py`                                                               ##
##                                                                           ##
##  Purpose: Administers notifications, data exports, etc in accordance      ##
##           with user-specified flags & notice systems                      ##
###############################################################################


import os
import base64

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = "secrets/token.json"
CREDENTIALS_FILE = "secrets/client_secret_gmail.json"
PURCHASES_FILE = "data/purchase_tracker.csv"

GMAIL_TIMESTAMP_FORMAT = "%Y/%m/%d"
TIMESTAMP_FORMAT = "%m-%d-%Y %H:%M:%S"
DATE_FORMAT = "%B %d, %Y"
TIME_FORMAT = "%I:%M %p"


FROM = "service@chewy.com"
SUBJECT = "Thanks for your Chewy order!"


def generate_oauth2_string(email, access_token):
    auth_string = f"user={email}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")


def authenticate_gmail():
    creds = None

    # Load token from file if it exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # Check if creds valid, refresh if expired
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())  
                print("Token refreshed successfully")

            else:
                raise Exception("No valid refresh token available")

            # Save refreshed token
            with open(TOKEN_FILE, "w") as token_file:
                token_file.write(creds.to_json())

        except Exception as e:
            print(f"Token refresh failed: {e}")
            print("Deleting token file and re-authenticating...")

            # Remove invalid JSON token file & restart authentication
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)

            # Run OAuth flow to get new token
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

            with open(TOKEN_FILE, "w") as token_file:
                token_file.write(creds.to_json())

    return creds


# Connect to Gmail w/ OAuth2 (return API service)
def connect_to_gmail():
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)

    print("OAuth login successful")
    return service


def format_date_for_gmail(date_str):
    # 'MM-DD-YYYY HH:MM:SS' --> 'YYYY/MM/DD' for Gmail search
    dt = datetime.strptime(date_str, TIMESTAMP_FORMAT)
    return dt.strftime(GMAIL_TIMESTAMP_FORMAT)


# Fetch emails based on criteria
def fetch_email_IDs(mail, since_date=None):
    search_criteria = f'(FROM "{FROM}" subject:{SUBJECT})'

    if since_date:
        formatted_date = format_date_for_gmail(since_date)
        search_criteria += f' SINCE {formatted_date}'

    results = mail.users().messages().list(userId="me", q=search_criteria).execute()
    
    email_IDs = []
    while "messages" in results:
        email_IDs.extend(results["messages"])
        if "nextPageToken" in results:
            results = mail.users().messages().list(
                userId="me", q=search_criteria, pageToken=results["nextPageToken"]
            ).execute()
        else:
            break

    if not email_IDs:
        print(f"No emails found since date/time: {since_date}")
        return []

    print(f"Found {len(email_IDs)} emails since date/time: {since_date}")
    return [email["id"] for email in email_IDs]


# Fetch a specific email by ID
def fetch_email(mail, email_ID):
    try:
        return mail.users().messages().get(userId="me", id=email_ID, format="full").execute()
    except HttpError as error:
        if error.resp.status == 404:
            print(f"Error: Email ID {email_ID} not found")
        else:
            print(f"An error occurred: {error}")
        return None 




##############################
###    CSV / data steps    ###
##############################

import os
import csv
from datetime import datetime

COLUMNS = ["email_id", "timestamp", "date", "time", "quantity", "price", "url"]


def csv_exists(file_path=PURCHASES_FILE):
    # Extracts the 'data/' folder path
    folder = os.path.dirname(file_path)  
    
    if not os.path.exists(folder):
        print(f"Folder '{folder}' not found. Creating it...")
        os.makedirs(folder)

    if os.path.exists(file_path):
        return True

    print(f"{file_path} not found. Creating new CSV...")
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(COLUMNS)

    return False


def get_latest_date(file_path=PURCHASES_FILE):
    # Check if we already have data entries
    if not csv_exists(file_path):
        return None 

    timestamps = []

    with open(file_path, mode="r", newline="") as file:
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


def append_to_csv(data, file_path=PURCHASES_FILE):
    with open(file_path, mode="a", newline="") as file:
        writer = csv.writer(file)

        email_ID = data["id"]
        timestamp = data["timestamp"]
        date, time = format_date_time(timestamp)

        # New row for each item, based on email contents (data)
        for item in data["items"]:
            url = item["URL"]
            price = item["price"]
            quantity = item["quantity"]
            
            row = [email_ID, timestamp, date, time, quantity, price, url]
            writer.writerow(row)



