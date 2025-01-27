###############################################################################
##  `utils.py`                                                               ##
##                                                                           ##
##  Purpose: Administers notifications, data exports, etc in accordance      ##
##           with user-specified flags & notice systems                      ##
###############################################################################


import imaplib
from email import policy
from email.parser import BytesParser

from encrypt import decrypt_data, load_key

FROM = "service@chewy.com"
SUBJECT = "Thanks for your Chewy order!"


# Connect to Gmail
def connect_to_gmail():
    credentials = decrypt_data(load_key())
    
    gmail_user = credentials["user"]
    gmail_password = credentials["password"]

    # Establish connection
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(gmail_user, gmail_password)
    return mail


# Fetch email IDs based on criteria
def fetch_email_IDs(mail, since_date=None):
    mail.select("inbox")

    search_criteria = f'(FROM "{FROM}" SUBJECT "{SUBJECT}")'
    if since_date:
        search_criteria += f' SINCE "{since_date}"'

    status, email_ids = mail.search(None, search_criteria)
    if status != "OK":
        raise Exception("Failed to search mailbox")
    
    return email_ids[0].split()  # List of email IDs


# Fetch a specific email by ID
def fetch_email(mail, email_id):
    status, data = mail.fetch(email_id, "(RFC822)") # Get entire message
    if status != "OK":
        raise Exception(f"Failed to fetch email ID {email_id}")
    
    raw_email = data[0][1]
    email_message = BytesParser(policy=policy.default).parsebytes(raw_email)
    return email_message


