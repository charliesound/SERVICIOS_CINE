from __future__ import annotations

import base64
import hashlib
import os

from cryptography.fernet import Fernet, InvalidToken

from config import config


class EncryptionService:
    def __init__(self) -> None:
        secret = (
            os.getenv("INTEGRATION_TOKEN_ENCRYPTION_KEY")
            or os.getenv("APP_SECRET_KEY")
            or str(config.get("app", {}).get("secret_key", ""))
            or os.getenv("AUTH_SECRET_KEY")
            or str(config.get("auth", {}).get("secret_key", ""))
        )
        if not secret:
            raise RuntimeError("Missing integration encryption secret")
        derived_key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode("utf-8")).digest())
        self._fernet = Fernet(derived_key)

    def encrypt(self, value: str | None) -> str | None:
        if value is None:
            return None
        return self._fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, value: str | None) -> str | None:
        if value is None:
            return None
        try:
            return self._fernet.decrypt(value.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise RuntimeError("Encrypted token could not be decrypted") from exc


encryption_service = EncryptionService()
