###############################################################################
##  `test_utils.py`                                                          ##
##                                                                           ##
##  Purpose: Tests notifications, data exports, etc in accordance            ##
##           with user-specified flags & notice systems                      ##
###############################################################################


import pytest
from unittest.mock import MagicMock
from src.email_utils import fetch_email_IDs, fetch_email 


@pytest.fixture
def mock_mail():
    return MagicMock()


@pytest.fixture
def mock_email_ids():
    return [{"id": "1"}, {"id": "2"}, {"id": "3"}]


@pytest.fixture
def email_body():
    return "This is a test email"


@pytest.fixture
def mock_email_payload(email_body):
    return {
        "payload": {
            "body": {
                "data": email_body
            }
        }
    }


def test_fetch_email_IDs(mock_mail, mock_email_ids):
    mock_mail.users().messages().list().execute.return_value = {"messages": mock_email_ids}

    email_ids = fetch_email_IDs(mock_mail)    
    assert email_ids == [message["id"] for message in mock_email_ids]


def test_fetch_email(mock_mail, mock_email_payload, email_body):
    mock_mail.users().messages().get().execute.return_value = mock_email_payload

    email_message = fetch_email(mock_mail, "1")

    assert email_message is not None
    assert email_message["payload"]["body"]["data"] == email_body

