import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()


class SecretCrypto:
    def __init__(self):
        self.key = os.getenv("FERNET_KEY").encode()
        self.cipher = Fernet(self.key)

    def encrypt(self, secret: str) -> bytes:
        return self.cipher.encrypt(secret.encode())

    def decrypt(self, encrypted_data: bytes) -> str:
        return self.cipher.decrypt(encrypted_data).decode()

    def get_all_keys(self, pattern="*") -> list:
        return self.client.keys(pattern)