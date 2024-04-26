# encryption_utils.py
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet
import base64

def derive_key(password: str) -> bytes:
    """Derive a cryptographic key from the user's password."""
    # Normally, a salt would be used here, but for simplicity, we're omitting it
    # This is NOT recommended for real applications due to security implications
    salt = b"unused_salt"  # In a real scenario, use a proper salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

def encrypt_data(data: str, password: str) -> str:
    """Encrypt the given data using the derived key."""
    key = derive_key(password)
    fernet = Fernet(key)
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(token: str, password: str) -> str:
    """Decrypt the given token using the derived key."""
    key = derive_key(password)
    fernet = Fernet(key)
    return fernet.decrypt(token.encode()).decode()
