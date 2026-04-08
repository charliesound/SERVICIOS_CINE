import hashlib
import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteAuthStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    role TEXT NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_auth_sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    token_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    revoked_at TEXT,
                    last_used_at TEXT,
                    metadata TEXT NOT NULL DEFAULT '{}',
                    FOREIGN KEY (user_id) REFERENCES sequence_users(user_id)
                )
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_auth_sessions_user
                ON sequence_auth_sessions (user_id, created_at)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_auth_sessions_token
                ON sequence_auth_sessions (token_hash)
                """
            )
            conn.commit()

    def _row_to_user(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "user_id": str(row["user_id"] or ""),
            "email": str(row["email"] or ""),
            "password_hash": str(row["password_hash"] or ""),
            "role": str(row["role"] or "viewer"),
            "is_active": bool(int(row["is_active"] or 0)),
            "created_at": str(row["created_at"] or ""),
            "updated_at": str(row["updated_at"] or ""),
        }

    def _row_to_session(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "session_id": str(row["session_id"] or ""),
            "user_id": str(row["user_id"] or ""),
            "token_hash": str(row["token_hash"] or ""),
            "created_at": str(row["created_at"] or ""),
            "expires_at": str(row["expires_at"] or ""),
            "revoked_at": str(row["revoked_at"]) if row["revoked_at"] else None,
            "last_used_at": str(row["last_used_at"]) if row["last_used_at"] else None,
            "metadata": json.loads(row["metadata"] or "{}"),
        }

    def count_users(self) -> int:
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) AS count FROM sequence_users").fetchone()
        return int(row["count"] if row else 0)

    def list_users(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM sequence_users ORDER BY created_at ASC").fetchall()
        return [self._row_to_user(row) for row in rows]

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sequence_users (
                    user_id,
                    email,
                    password_hash,
                    role,
                    is_active,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_data["user_id"],
                    user_data["email"],
                    user_data["password_hash"],
                    user_data["role"],
                    1 if bool(user_data.get("is_active", True)) else 0,
                    user_data["created_at"],
                    user_data["updated_at"],
                ),
            )
            conn.commit()
        return self.get_user_by_email(str(user_data["email"])) or user_data

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        normalized_email = str(email or "").strip().lower()
        if not normalized_email:
            return None

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM sequence_users
                WHERE lower(email) = ?
                """,
                (normalized_email,),
            ).fetchone()
        return self._row_to_user(row) if row else None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        normalized_user_id = str(user_id or "").strip()
        if not normalized_user_id:
            return None

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM sequence_users
                WHERE user_id = ?
                """,
                (normalized_user_id,),
            ).fetchone()
        return self._row_to_user(row) if row else None

    def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sequence_auth_sessions (
                    session_id,
                    user_id,
                    token_hash,
                    created_at,
                    expires_at,
                    revoked_at,
                    last_used_at,
                    metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_data["session_id"],
                    session_data["user_id"],
                    session_data["token_hash"],
                    session_data["created_at"],
                    session_data["expires_at"],
                    session_data.get("revoked_at"),
                    session_data.get("last_used_at"),
                    json.dumps(session_data.get("metadata", {}), ensure_ascii=False),
                ),
            )
            conn.commit()
        return session_data

    def get_session_by_token_hash(self, token_hash: str) -> Optional[Dict[str, Any]]:
        normalized_token_hash = str(token_hash or "").strip()
        if not normalized_token_hash:
            return None

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM sequence_auth_sessions
                WHERE token_hash = ?
                """,
                (normalized_token_hash,),
            ).fetchone()
        return self._row_to_session(row) if row else None

    def update_session_last_used_at(self, token_hash: str, last_used_at: str) -> Optional[Dict[str, Any]]:
        normalized_token_hash = str(token_hash or "").strip()
        if not normalized_token_hash:
            return None

        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sequence_auth_sessions
                SET last_used_at = ?
                WHERE token_hash = ?
                """,
                (last_used_at, normalized_token_hash),
            )
            conn.commit()

        if cursor.rowcount == 0:
            return None
        return self.get_session_by_token_hash(normalized_token_hash)

    def revoke_session_by_token_hash(self, token_hash: str, revoked_at: str) -> Optional[Dict[str, Any]]:
        normalized_token_hash = str(token_hash or "").strip()
        if not normalized_token_hash:
            return None

        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sequence_auth_sessions
                SET revoked_at = ?
                WHERE token_hash = ?
                """,
                (revoked_at, normalized_token_hash),
            )
            conn.commit()

        if cursor.rowcount == 0:
            return None
        return self.get_session_by_token_hash(normalized_token_hash)
