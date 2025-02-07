###############################################################################
##  `parser.py`                                                              ##
##                                                                           ##
##  Purpose: Routinely checks email for updates in product purchase history  ##
##           (diff of existing vs new), then parses text to extract details  ##
##           around item, price, date, etc                                   ##
###############################################################################


from src.utils import (
    connect_to_gmail, fetch_email_IDs, fetch_email, 
    get_latest_date, append_to_csv 
)
from datetime import datetime
from bs4 import BeautifulSoup, Comment
import pytz
import base64


def get_email_date(email, timezone="America/New_York"):
    internal_date = email.get("internalDate", None)
    if not internal_date:
        raise ValueError("Error with email timestamp")
    
    timestamp = int(internal_date) / 1000
    utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    local_time = utc_time.astimezone(pytz.timezone(timezone))

    return local_time.strftime("%m-%d-%Y %H:%M:%S")


def get_email_body(email):
    payload = email.get("payload", {})
    if not payload:
        raise ValueError("Error with email payload")
    
    if "body" in payload and "data" in payload["body"]:
        body_data = payload["body"]["data"]
    else:
        # If body not directly available, check inside "parts"
        parts = payload.get("parts", [])
        if not parts:
            raise ValueError("Error, could not find email body")

        for part in parts:
            if part.get("mimeType") == "text/html": 
                body_data = part["body"].get("data", "")
                break

    # Decode base64-encoded email body
    decoded_body = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
    return decoded_body


# Assuming HTML structure (e.g. table row), to extract URL, we look for  
# the <!--ITEM IMAGE--> comment, from the parent <td> or other container
def extract_item_URLs(soup):
    URLs = []
    
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if "ITEM IMAGE" in comment:
            parent = comment.find_parent(["td", "tr", "div"])  

            if parent:
                # Find the first <a> tag within that block
                item_link = parent.find("a", href=True)    

                if item_link:
                    link = item_link["href"]
                    URLs.append(link)
    return URLs


# Assuming HTML structure (e.g. table row), to extract price, we look for  
# the <!--IF SHOW PRICE--> comment, from the parent <td> or other container
def extract_item_prices(soup):
    prices = []

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if "IF SHOW PRICE" in comment:
            parent = comment.find_parent(["td", "tr", "div"])  

            if parent:
                item_price = parent.find("td", class_="price-mobile")

                if item_price:
                    price = item_price.get_text(strip=True) 
                    prices.append(price)
    
    # Since each price gets embedded twice in the HTML (due to individual
    # item price AND order total summary), drop every other instance
    clean_prices = prices[::2]
    return clean_prices


# Assuming HTML structure (e.g. table row), to extract quantity, we look for  
# the <!--IF SHOW QTY--> comment, from the parent <td> or other container
def extract_item_quantities(soup):
    quantities = []
    
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if "IF SHOW QTY" in comment:
            parent = comment.find_parent(["td", "tr", "div"])  

            if parent:
                qty_td = parent.find("td", class_="copy")  

                if qty_td:
                    qty_text = qty_td.get_text(strip=True)
                    qty = int(qty_text.replace("Qty: ", "")) if "Qty: " in qty_text else 1
                    quantities.append(qty)

    return quantities


def get_item_URLs_prices_quantities(html_body):
    soup = BeautifulSoup(html_body, "html.parser")

    URLs = extract_item_URLs(soup)
    prices = extract_item_prices(soup)
    quantities = extract_item_quantities(soup)

    # Zip all item info into dicts
    items = [
        {"URL": link, "price": price, "quantity": qty}
        for link, price, qty in zip(URLs, prices, quantities)
    ]
    return items


def parse_emails():
    mail = connect_to_gmail()

    # Only retrieve new emails (not yet logged)
    latest_date = get_latest_date()
    email_IDs = fetch_email_IDs(mail, latest_date)

    for ID in email_IDs:
        email = fetch_email(mail, ID)

        email_ID = email.get("id", "Unknown ID")
        timestamp = get_email_date(email)

        payload = get_email_body(email)
        items = get_item_URLs_prices_quantities(payload)

        email_data = {
            "id": email_ID,
            "timestamp": timestamp,
            "items": items
        }
        append_to_csv(email_data)

        
        




