###############################################################################
##  `parser.py`                                                              ##
##                                                                           ##
##  Purpose: Routinely checks email for updates in product purchase history  ##
##           (diff of existing vs new), then parses text to extract details  ##
##           around item, price, date, etc                                   ##
###############################################################################


from utils import connect_to_gmail, fetch_email

def parse_emails():
    mail = connect_to_gmail()





