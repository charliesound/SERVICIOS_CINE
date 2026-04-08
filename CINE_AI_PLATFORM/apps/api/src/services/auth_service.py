import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, Optional
from uuid import uuid4

from src.schemas.auth import AuthRole
from src.settings import Settings
from src.storage.sqlite_auth_store import SQLiteAuthStore


class AuthService:
    def __init__(self, store: SQLiteAuthStore, settings: Settings):
        self.store = store
        self.settings = settings
        self._seed_bootstrap_users()

    def _now(self) -> datetime:
        return datetime.now(timezone.utc)

    def _now_iso(self) -> str:
        return self._now().isoformat()

    def _normalize_email(self, value: str) -> str:
        return str(value or "").strip().lower()

    def _normalize_role(self, value: str) -> str:
        normalized = str(value or "").strip().lower()
        if normalized not in {"admin", "editor", "reviewer", "viewer"}:
            raise ValueError("role must be one of admin, editor, reviewer or viewer")
        return normalized

    def _hash_password(self, password: str) -> str:
        normalized_password = str(password or "")
        if not normalized_password:
            raise ValueError("password is required")

        iterations = 310000
        salt = secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", normalized_password.encode("utf-8"), salt, iterations)
        return "pbkdf2_sha256${}${}${}".format(
            iterations,
            base64.urlsafe_b64encode(salt).decode("ascii").rstrip("="),
            base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        )

    def _verify_password(self, password: str, password_hash: str) -> bool:
        try:
            algorithm, iterations_raw, salt_raw, hash_raw = password_hash.split("$", 3)
        except ValueError:
            return False

        if algorithm != "pbkdf2_sha256":
            return False

        try:
            iterations = int(iterations_raw)
        except ValueError:
            return False

        salt_padding = "=" * (-len(salt_raw) % 4)
        hash_padding = "=" * (-len(hash_raw) % 4)
        try:
            salt = base64.urlsafe_b64decode(f"{salt_raw}{salt_padding}")
            expected = base64.urlsafe_b64decode(f"{hash_raw}{hash_padding}")
        except Exception:
            return False

        actual = hashlib.pbkdf2_hmac("sha256", str(password or "").encode("utf-8"), salt, iterations)
        return hmac.compare_digest(actual, expected)

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def _public_user(self, user: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "user_id": str(user.get("user_id") or ""),
            "email": str(user.get("email") or ""),
            "role": str(user.get("role") or "viewer"),
            "is_active": bool(user.get("is_active", True)),
            "created_at": str(user.get("created_at") or ""),
            "updated_at": str(user.get("updated_at") or ""),
        }

    def _seed_bootstrap_users(self) -> None:
        if self.store.count_users() > 0:
            return

        bootstrap_users = str(getattr(self.settings, "auth_bootstrap_users", "") or "").strip()
        if not bootstrap_users:
            return

        now = self._now_iso()
        for item in bootstrap_users.split(","):
            chunk = item.strip()
            if not chunk:
                continue
            parts = [part.strip() for part in chunk.split(":", 2)]
            if len(parts) != 3:
                continue

            email, password, role = parts
            normalized_email = self._normalize_email(email)
            if not normalized_email or not password:
                continue

            try:
                normalized_role = self._normalize_role(role)
            except ValueError:
                continue

            if self.store.get_user_by_email(normalized_email) is not None:
                continue

            self.store.create_user(
                {
                    "user_id": str(uuid4()),
                    "email": normalized_email,
                    "password_hash": self._hash_password(password),
                    "role": normalized_role,
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                }
            )

    def login(self, email: str, password: str) -> Dict[str, Any]:
        normalized_email = self._normalize_email(email)
        if not normalized_email or not password:
            raise ValueError("email and password are required")

        user = self.store.get_user_by_email(normalized_email)
        if user is None or not bool(user.get("is_active", True)):
            raise ValueError("Invalid email or password")

        password_hash = str(user.get("password_hash") or "")
        if not self._verify_password(password, password_hash):
            raise ValueError("Invalid email or password")

        token = secrets.token_urlsafe(32)
        now = self._now()
        expires_at = now + timedelta(days=max(1, int(getattr(self.settings, "auth_session_ttl_days", 30) or 30)))
        token_hash = self._hash_token(token)

        self.store.create_session(
            {
                "session_id": str(uuid4()),
                "user_id": str(user.get("user_id") or ""),
                "token_hash": token_hash,
                "created_at": now.isoformat(),
                "expires_at": expires_at.isoformat(),
                "revoked_at": None,
                "last_used_at": now.isoformat(),
                "metadata": {},
            }
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "user": self._public_user(user),
        }

    def get_authenticated_context(self, token: str) -> Optional[Dict[str, Any]]:
        normalized_token = str(token or "").strip()
        if not normalized_token:
            return None

        token_hash = self._hash_token(normalized_token)
        session = self.store.get_session_by_token_hash(token_hash)
        if session is None:
            return None

        if session.get("revoked_at"):
            return None

        try:
            expires_at = datetime.fromisoformat(str(session.get("expires_at") or ""))
        except ValueError:
            return None

        if expires_at <= self._now():
            return None

        user = self.store.get_user_by_id(str(session.get("user_id") or ""))
        if user is None or not bool(user.get("is_active", True)):
            return None

        self.store.update_session_last_used_at(token_hash, self._now_iso())
        return {
            "token": normalized_token,
            "token_hash": token_hash,
            "session": session,
            "user": self._public_user(user),
        }

    def revoke_token(self, token: str) -> bool:
        normalized_token = str(token or "").strip()
        if not normalized_token:
            return False
        token_hash = self._hash_token(normalized_token)
        revoked = self.store.revoke_session_by_token_hash(token_hash, self._now_iso())
        return revoked is not None
