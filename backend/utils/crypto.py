from cryptography.fernet import Fernet
import os
import logging

logger = logging.getLogger(__name__)

def get_cipher():
    """Get or generate Fernet cipher for encryption."""
    key = os.getenv("ENCRYPTION_KEY")

    if not key:
        logger.warning("ENCRYPTION_KEY not found in environment. Generating a new key.")
        logger.warning("THIS KEY WILL NOT PERSIST ACROSS RESTARTS!")
        logger.warning("Please set ENCRYPTION_KEY in your .env file to persist encrypted data.")
        key = Fernet.generate_key().decode()

    # Ensure key is bytes
    if isinstance(key, str):
        key = key.encode()

    return Fernet(key)

def encrypt_credential(value: str) -> str:
    """Encrypt a credential string."""
    if not value:
        return ""

    cipher = get_cipher()
    encrypted = cipher.encrypt(value.encode())
    return encrypted.decode()

def decrypt_credential(encrypted: str) -> str:
    """Decrypt a credential string."""
    if not encrypted:
        return ""

    cipher = get_cipher()
    decrypted = cipher.decrypt(encrypted.encode())
    return decrypted.decode()
