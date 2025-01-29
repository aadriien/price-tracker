###############################################################################
##  `test_encrypt.py`                                                        ##
##                                                                           ##
##  Purpose: Tests encryption/decryption                                     ##
###############################################################################


import os
import pytest
from cryptography.fernet import Fernet
from src.encrypt import (
    generate_key,
    load_key,
    encrypt_data,
    decrypt_data,
    KEY_FILE,
    CREDENTIALS_FILE,
)


@pytest.fixture
def temp_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)
    yield key
    os.remove(KEY_FILE)


@pytest.fixture
def sample_data():
    return {
        "GMAIL_USER": "test@example.com", 
        "GMAIL_PASSWORD": "securepassword"
        }


def test_generate_key():
    generate_key()
    assert os.path.exists(KEY_FILE) and os.path.getsize(KEY_FILE) > 0

    # Validate that key is a proper Fernet key (44 bytes)
    with open(KEY_FILE, "rb") as f:
        key = f.read()
    assert isinstance(key, bytes) and len(key) == 44
    os.remove(KEY_FILE)



def test_load_key(temp_key):
    key = load_key()
    assert key == temp_key


def test_encrypt_decrypt(temp_key, sample_data):
    encrypt_data(sample_data, temp_key)
    assert os.path.exists(CREDENTIALS_FILE)
    decrypted = decrypt_data(temp_key)
    assert decrypted == sample_data
    os.remove(CREDENTIALS_FILE)


