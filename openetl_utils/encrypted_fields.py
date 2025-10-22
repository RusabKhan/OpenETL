import json
import os
from sqlalchemy import Text
from sqlalchemy.types import TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from cryptography.fernet import Fernet
from typing import Any, Optional

Base = declarative_base()


class EncryptedJSON(TypeDecorator):
    """
    Encrypted JSON column type that automatically encrypts/decrypts data.

    Uses Fernet (symmetric encryption) from cryptography library.
    Stores encrypted data as TEXT in the database.
    """

    impl = Text
    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Get encryption key from environment variable
        key = os.getenv('DB_ENCRYPTION_KEY')

        if not key:
            raise ValueError(
                "DB_ENCRYPTION_KEY environment variable must be set. "
                "Generate one using: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )

        self.fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def process_bind_param(self, value: Optional[Any], dialect) -> Optional[str]:
        """Encrypt data before storing in database"""
        if value is None:
            return None

        # Convert to JSON string
        json_str = json.dumps(value)

        # Encrypt
        encrypted = self.fernet.encrypt(json_str.encode())

        # Return as string for TEXT column
        return encrypted.decode()

    def process_result_value(self, value: Optional[str], dialect) -> Optional[Any]:
        """Decrypt data when reading from database"""
        if value is None:
            return None

        try:
            # Decrypt
            decrypted = self.fernet.decrypt(value.encode())

            # Parse JSON
            return json.loads(decrypted.decode())
        except Exception as e:
            raise ValueError(f"Failed to decrypt data: {str(e)}")
