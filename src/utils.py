###############################################################################
##  `utils.py`                                                               ##
##                                                                           ##
##  Purpose: Administers notifications, data exports, etc in accordance      ##
##           with user-specified flags & notice systems                      ##
###############################################################################


import os
import base64
from email.parser import BytesParser

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
TOKEN_FILE = "secrets/token.json"
CREDENTIALS_FILE = "secrets/client_secret_gmail.json"

FROM = "service@chewy.com"
SUBJECT = "Thanks for your Chewy order!"


def generate_oauth2_string(email, access_token):
    auth_string = f"user={email}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")


def authenticate_gmail():
    creds = None

    # Load token from file if exists - otherwise refresh / get new creds
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  
        else:
            # Run OAuth flow if no valid token
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0, access_type="offline", prompt="consent")

        # Save updated token
        with open(TOKEN_FILE, "w") as token_file:
            token_file.write(creds.to_json())

    return creds


# Connect to Gmail w/ OAuth2 (return API service)
def connect_to_gmail():
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)

    print("OAuth login successful")
    return service


# Fetch emails based on criteria
def fetch_email_IDs(mail, since_date=None):
    search_criteria = f'(FROM "{FROM}" subject:{SUBJECT})'
    if since_date:
        search_criteria += f' SINCE "{since_date}"'

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
        print("No emails found")
        return []

    print(f"Found {len(email_IDs)} emails")
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


