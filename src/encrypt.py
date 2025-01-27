###############################################################################
##  `encrypt.py`                                                             ##
##                                                                           ##
##  Purpose: Handles encryption/decryption to protect email credentials      ##
###############################################################################


import os
import json
from cryptography.fernet import Fernet
from dotenv import load_dotenv


SECRETS_DIR = "secrets"
KEY_FILE = f"{SECRETS_DIR}/key.key"
CREDENTIALS_FILE = f"{SECRETS_DIR}/credentials.enc"

# Ensure the secrets directory exists
def ensure_secrets_dir():
    if not os.path.exists(SECRETS_DIR):
        os.makedirs(SECRETS_DIR)


# Setup encryption: Check files & generate if needed
def setup_encryption():
    ensure_secrets_dir()

    # Check if key exists; if not, generate one
    if not os.path.exists(KEY_FILE) or os.path.getsize(KEY_FILE) == 0:
        print(f"{KEY_FILE} missing or empty. Generating new key")
        generate_key()

    # Check if credentials file exists; if not, encrypt and save credentials
    if not os.path.exists(CREDENTIALS_FILE) or os.path.getsize(CREDENTIALS_FILE) == 0:
        print(f"{CREDENTIALS_FILE} missing or empty. Encrypting credentials")
        encrypt_data(load_env_vars(), load_key())


# Generate new encryption key & save to file
def generate_key(file_path=KEY_FILE):
    key = Fernet.generate_key()
    with open(file_path, "wb") as key_file:
        key_file.write(key)


# Load the encryption key from file
def load_key(file_path=KEY_FILE):
    with open(file_path, "rb") as key_file:
        return key_file.read()


# Load environment variables from .env
def load_env_vars():
    load_dotenv()
    gmail_user = os.getenv("GMAIL_USER")
    gmail_password = os.getenv("GMAIL_PASSWORD")

    if not (gmail_user and gmail_password):
        raise ValueError("GMAIL_USER and GMAIL_PASSWORD must be set in .env")
    return gmail_user, gmail_password


# Encrypt data and save it to file
def encrypt_data(data, key, output_file=CREDENTIALS_FILE):
    cipher = Fernet(key)
    encrypted_data = cipher.encrypt(json.dumps(data).encode())

    with open(output_file, "wb") as enc_file:
        enc_file.write(encrypted_data)


# Decrypt data from file
def decrypt_data(key, input_file=CREDENTIALS_FILE):
    cipher = Fernet(key)
    with open(input_file, "rb") as enc_file:
        encrypted_data = enc_file.read()

    decrypted_data = cipher.decrypt(encrypted_data).decode()
    return json.loads(decrypted_data)



