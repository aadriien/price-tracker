###############################################################################
##  `test_utils.py`                                                          ##
##                                                                           ##
##  Purpose: Tests notifications, data exports, etc in accordance            ##
##           with user-specified flags & notice systems                      ##
###############################################################################


import pytest
from unittest.mock import patch, MagicMock
from email.message import EmailMessage
from cryptography.fernet import Fernet

from src.utils import (
    connect_to_gmail, 
    fetch_email_IDs, 
    fetch_email
)


@pytest.fixture
def mock_mail():
    # Create mock IMAP4_SSL connection w/ fake email IDs
    mock_mail = MagicMock()
    mock_mail.search.return_value = ("OK", [b"1 2 3"]) 
    return mock_mail


@patch("src.utils.decrypt_data", return_value = {"GMAIL_USER": "test@example.com", "GMAIL_PASSWORD": "securepassword"})
@patch("src.utils.load_key", return_value = Fernet.generate_key())
@patch("src.utils.imaplib.IMAP4_SSL")
def test_connect_to_gmail(mock_imap, mock_load_key, mock_decrypt_data):
    # Confirm valid mail connection w/ mocked IMAP instance
    mock_instance = mock_imap.return_value
    mock_instance.login.return_value = ("OK", b"Logged in")

    mail = connect_to_gmail()

    mock_imap.assert_called_once_with("imap.gmail.com")
    mock_instance.login.assert_called_once_with("test@example.com", "securepassword")
    assert mail == mock_instance


def test_fetch_email_IDs(mock_mail):
    # Simulate selecting inbox
    mock_mail.select.return_value = ("OK", b"") 
    email_ids = fetch_email_IDs(mock_mail)

    assert email_ids == [b"1", b"2", b"3"]


def test_fetch_email(mock_mail):
    sample_email_content = b"Subject: Test Email\n\nThis is a test."
    sample_fetch_response = ("OK", [(b"1", sample_email_content)])

    mock_mail.fetch.return_value = sample_fetch_response

    email_message = fetch_email(mock_mail, b"1")

    assert isinstance(email_message, EmailMessage)
    assert email_message["Subject"] == "Test Email"

