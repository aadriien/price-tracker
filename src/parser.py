###############################################################################
##  `parser.py`                                                              ##
##                                                                           ##
##  Purpose: Routinely checks email for updates in product purchase history  ##
##           (diff of existing vs new), then parses text to extract details  ##
##           around item, price, date, etc                                   ##
###############################################################################


from xml.dom import ValidationErr
from src.utils import (
    connect_to_gmail, fetch_email_IDs, fetch_email, 
    get_latest_date, append_to_csv 
)
from datetime import datetime
from bs4 import BeautifulSoup, Comment
import pytz
import base64
import re


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

    body_data_html = None
    body_data_plain = None
    
    if "body" in payload and "data" in payload["body"]:
        # Assume it's HTML since there's no MIME type indicator
        body_data = payload["body"]["data"]
        html_body = base64.urlsafe_b64decode(body_data).decode("utf-8", errors="ignore")
    else:
        # If body not directly available, check inside "parts"
        parts = payload.get("parts", [])
        if not parts:
            raise ValueError("Error, could not find email body")

        for part in parts:
            if part.get("mimeType") == "text/html": 
                body_data_html = part["body"].get("data", "")
            elif part.get("mimeType") == "text/plain":
                body_data_plain = part["body"].get("data", "")

        # Decode base64-encoded email body
        html_body = (
            base64.urlsafe_b64decode(body_data_html).decode("utf-8", errors="ignore") 
            if body_data_html else None
        )
        plain_body = (
            base64.urlsafe_b64decode(body_data_plain).decode("utf-8", errors="ignore") 
            if body_data_plain else None
        )
    
    return {"html": html_body, "plain": plain_body}


# Assuming HTML structure (e.g. table row), to extract name, we look for  
# the <a> tag, from the parent <td> or other container, which holds text
def extract_item_names(soup):
    names = []

    for td in soup.find_all("td", class_="copy"):
        # Find the <a> tag, which connects to product name text
        name_link = td.find("a")  
        if name_link:
            name_text = name_link.text.strip() 
            if name_text and ".com" not in name_text:
                names.append(name_text) 

    return names


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


def get_item_names_URLs_prices_quantities(html_body):
    soup = BeautifulSoup(html_body, "html.parser")

    names = extract_item_names(soup)
    URLs = extract_item_URLs(soup)
    prices = extract_item_prices(soup)
    quantities = extract_item_quantities(soup)

    # Zip all item info into dicts
    items = [
        {"name": name, "URL": link, "price": price, "quantity": qty}
        for name, link, price, qty in zip(names, URLs, prices, quantities)
    ]
    return items


def extract_from_plaintext(plain_body):
    lines = plain_body.split("\n")

    # Flag to start capturing lines
    extracting_products = False 
    plaintext_items = []

    for line in lines:
        if "Order Items" in line:
            extracting_products = True
            continue 
        
        if extracting_products:
            # Stop when empty line is reached, then append
            if line.strip() == "":  
                break

            match = re.match(r"(\d+) x (.+) - (\d+\.\d{2})", line)
            if match:
                quantity, name, price = match.groups()
                plaintext_items.append({
                    "name": name.strip(),
                    "price": f"${price}",
                    "quantity": int(quantity)
                })

    return plaintext_items


def remove_free_promo_items(items):
    filtered_items = []

    for item in items:
        if item["price"] not in ("FREE", "$0.00"):
            if "Promo" and "Free" not in item["name"]:
                filtered_items.append(item)

    return filtered_items


def validate_HTML_with_plaintext(html_items, plain_items):
    html_items.sort(key=lambda x: x["name"])
    plain_items.sort(key=lambda x: x["name"])
    
    # Cannot compare/check URL since only HTML has it (not plaintext)
    def filter_fields(item):
        return (item["name"], item["quantity"], item["price"]) 

    html_set = {filter_fields(item) for item in html_items}
    plain_set = {filter_fields(item) for item in plain_items}

    return html_set == plain_set


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
        html_body, plain_body = payload["html"], payload["plain"]

        # Extract details from HTML, then compare to plaintext to confirm
        html_items = get_item_names_URLs_prices_quantities(html_body)
        plain_items = extract_from_plaintext(plain_body)

        html_purchases = remove_free_promo_items(html_items)
        plain_purchases = remove_free_promo_items(plain_items)

        if not validate_HTML_with_plaintext(html_purchases, plain_purchases):
            raise ValidationErr("Error, HTML does not match plaintext")

        email_data = {
            "id": email_ID,
            "timestamp": timestamp,
            "items": html_purchases
        }
        append_to_csv(email_data)

        
        




