import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class SQLiteFollowUpQueueStore:
    """SQLite-backed queue store for follow-up processing.

    Extends the follow_ups table with queue-specific fields:
    - queue_status: queued | processing | sent | failed | skipped | cancelled
    - attempts_count
    - max_attempts
    - last_attempt_at
    - next_attempt_at
    - priority: hot | warm | cold
    - sequence_key
    - sequence_step
    - scheduled_for
    - eligible_at
    - generation_mode: manual | automatic
    - terminal_reason
    - processing_lock_token
    - provider
    - provider_message_id
    - delivery_mode
    - delivery_details_json
    - recipient_email
    - from_email
    """

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
                CREATE TABLE IF NOT EXISTS follow_ups (
                    id TEXT PRIMARY KEY,
                    lead_id TEXT NOT NULL,
                    campaign_key TEXT NOT NULL DEFAULT 'cid_storyboard_ia',
                    template_key TEXT NOT NULL DEFAULT 'cid_storyboard_ia_initial',
                    channel TEXT NOT NULL DEFAULT 'email',
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'draft',
                    scheduled_at TEXT,
                    sent_at TEXT,
                    last_error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            # V3 queue fields
            self._ensure_column(conn, "queue_status", "TEXT DEFAULT 'queued'")
            self._ensure_column(conn, "attempts_count", "INTEGER DEFAULT 0")
            self._ensure_column(conn, "max_attempts", "INTEGER DEFAULT 3")
            self._ensure_column(conn, "last_attempt_at", "TEXT")
            self._ensure_column(conn, "next_attempt_at", "TEXT")
            self._ensure_column(conn, "priority", "TEXT DEFAULT 'warm'")
            self._ensure_column(conn, "sequence_key", "TEXT")
            self._ensure_column(conn, "sequence_step", "INTEGER")
            self._ensure_column(conn, "scheduled_for", "TEXT")
            self._ensure_column(conn, "eligible_at", "TEXT")
            self._ensure_column(conn, "generation_mode", "TEXT DEFAULT 'manual'")
            self._ensure_column(conn, "terminal_reason", "TEXT")
            self._ensure_column(conn, "processing_lock_token", "TEXT")
            self._ensure_column(conn, "provider", "TEXT")
            self._ensure_column(conn, "provider_message_id", "TEXT")
            self._ensure_column(conn, "delivery_mode", "TEXT")
            self._ensure_column(conn, "delivery_details_json", "TEXT")
            self._ensure_column(conn, "recipient_email", "TEXT")
            self._ensure_column(conn, "from_email", "TEXT")

            # Indexes for queue processing
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_follow_ups_lead_id
                ON follow_ups (lead_id)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_follow_ups_queue_status
                ON follow_ups (queue_status)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_follow_ups_priority
                ON follow_ups (priority)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_follow_ups_next_attempt
                ON follow_ups (next_attempt_at)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_follow_ups_campaign
                ON follow_ups (campaign_key)
                """
            )
            conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_follow_ups_sequence
                ON follow_ups (sequence_key, sequence_step)
                """
            )
            conn.commit()

    def _ensure_column(self, conn: sqlite3.Connection, column_name: str, column_type: str) -> None:
        rows = conn.execute("PRAGMA table_info(follow_ups)").fetchall()
        current_columns = {row[1] for row in rows}
        if column_name in current_columns:
            return
        conn.execute(f"ALTER TABLE follow_ups ADD COLUMN {column_name} {column_type}")

    def _row_to_followup(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "id": row["id"],
            "lead_id": row["lead_id"],
            "campaign_key": row["campaign_key"],
            "template_key": row["template_key"],
            "channel": row["channel"],
            "subject": row["subject"],
            "body": row["body"],
            "status": row["status"],
            "scheduled_at": row["scheduled_at"],
            "sent_at": row["sent_at"],
            "last_error": row["last_error"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            # V3 fields
            "queue_status": row.get("queue_status", "queued"),
            "attempts_count": row.get("attempts_count", 0),
            "max_attempts": row.get("max_attempts", 3),
            "last_attempt_at": row.get("last_attempt_at"),
            "next_attempt_at": row.get("next_attempt_at"),
            "priority": row.get("priority", "warm"),
            "sequence_key": row.get("sequence_key"),
            "sequence_step": row.get("sequence_step"),
            "scheduled_for": row.get("scheduled_for"),
            "eligible_at": row.get("eligible_at"),
            "generation_mode": row.get("generation_mode", "manual"),
            "terminal_reason": row.get("terminal_reason"),
            "processing_lock_token": row.get("processing_lock_token"),
            "provider": row.get("provider"),
            "provider_message_id": row.get("provider_message_id"),
            "delivery_mode": row.get("delivery_mode"),
            "delivery_details_json": row.get("delivery_details_json"),
            "recipient_email": row.get("recipient_email"),
            "from_email": row.get("from_email"),
        }

    def create(self, followup: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO follow_ups (
                    id, lead_id, campaign_key, template_key, channel,
                    subject, body, status, scheduled_at, sent_at,
                    last_error, created_at, updated_at,
                    queue_status, attempts_count, max_attempts,
                    last_attempt_at, next_attempt_at, priority,
                    sequence_key, sequence_step, scheduled_for, eligible_at,
                    generation_mode, terminal_reason, processing_lock_token,
                    provider, provider_message_id, delivery_mode,
                    delivery_details_json, recipient_email, from_email
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    followup["id"],
                    followup["lead_id"],
                    followup.get("campaign_key", "cid_storyboard_ia"),
                    followup.get("template_key", "cid_storyboard_ia_initial"),
                    followup.get("channel", "email"),
                    followup["subject"],
                    followup["body"],
                    followup.get("status", "draft"),
                    followup.get("scheduled_at"),
                    followup.get("sent_at"),
                    followup.get("last_error"),
                    followup["created_at"],
                    followup["updated_at"],
                    followup.get("queue_status", "queued"),
                    followup.get("attempts_count", 0),
                    followup.get("max_attempts", 3),
                    followup.get("last_attempt_at"),
                    followup.get("next_attempt_at"),
                    followup.get("priority", "warm"),
                    followup.get("sequence_key"),
                    followup.get("sequence_step"),
                    followup.get("scheduled_for"),
                    followup.get("eligible_at"),
                    followup.get("generation_mode", "manual"),
                    followup.get("terminal_reason"),
                    followup.get("processing_lock_token"),
                    followup.get("provider"),
                    followup.get("provider_message_id"),
                    followup.get("delivery_mode"),
                    followup.get("delivery_details_json"),
                    followup.get("recipient_email"),
                    followup.get("from_email"),
                ),
            )
            conn.commit()
        return self.get(followup["id"])

    def get(self, followup_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM follow_ups WHERE id = ?", (followup_id,)
            ).fetchone()
            return self._row_to_followup(row) if row else None

    def list(
        self,
        lead_id: Optional[str] = None,
        campaign_key: Optional[str] = None,
        status: Optional[str] = None,
        queue_status: Optional[str] = None,
        priority: Optional[str] = None,
        sequence_key: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            query = "SELECT * FROM follow_ups WHERE 1=1"
            params: list = []

            if lead_id:
                query += " AND lead_id = ?"
                params.append(lead_id)
            if campaign_key:
                query += " AND campaign_key = ?"
                params.append(campaign_key)
            if status:
                query += " AND status = ?"
                params.append(status)
            if queue_status:
                query += " AND queue_status = ?"
                params.append(queue_status)
            if priority:
                query += " AND priority = ?"
                params.append(priority)
            if sequence_key:
                query += " AND sequence_key = ?"
                params.append(sequence_key)

            query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            rows = conn.execute(query, params).fetchall()
            return [self._row_to_followup(row) for row in rows]

    def update(self, followup_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = {
            "status", "sent_at", "last_error", "subject", "body",
            "scheduled_at", "template_key", "campaign_key", "channel",
            "queue_status", "attempts_count", "max_attempts",
            "last_attempt_at", "next_attempt_at", "priority",
            "sequence_key", "sequence_step", "scheduled_for", "eligible_at",
            "generation_mode", "terminal_reason", "processing_lock_token",
            "provider", "provider_message_id", "delivery_mode",
            "delivery_details_json", "recipient_email", "from_email",
        }
        filtered = {k: v for k, v in updates.items() if k in allowed_fields}
        if not filtered:
            return self.get(followup_id)

        filtered["updated_at"] = updates.get("updated_at")

        set_clause = ", ".join(f"{k} = ?" for k in filtered.keys())
        values = list(filtered.values()) + [followup_id]

        with self._connect() as conn:
            conn.execute(
                f"UPDATE follow_ups SET {set_clause} WHERE id = ?",
                values,
            )
            conn.commit()

        return self.get(followup_id)

    def count(
        self,
        lead_id: Optional[str] = None,
        campaign_key: Optional[str] = None,
        status: Optional[str] = None,
        queue_status: Optional[str] = None,
        priority: Optional[str] = None,
        sequence_key: Optional[str] = None,
    ) -> int:
        with self._connect() as conn:
            query = "SELECT COUNT(*) as cnt FROM follow_ups WHERE 1=1"
            params: list = []

            if lead_id:
                query += " AND lead_id = ?"
                params.append(lead_id)
            if campaign_key:
                query += " AND campaign_key = ?"
                params.append(campaign_key)
            if status:
                query += " AND status = ?"
                params.append(status)
            if queue_status:
                query += " AND queue_status = ?"
                params.append(queue_status)
            if priority:
                query += " AND priority = ?"
                params.append(priority)
            if sequence_key:
                query += " AND sequence_key = ?"
                params.append(sequence_key)

            row = conn.execute(query, params).fetchone()
            return row["cnt"] if row else 0

    def get_queue_items(
        self,
        batch_size: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get follow-ups ready for processing, ordered by priority and age.

        Priority order: hot > warm > cold.
        Within same priority, older items first.
        Only returns items where:
        - queue_status is 'queued'
        - next_attempt_at is NULL or <= now
        """
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM follow_ups
                WHERE queue_status = 'queued'
                  AND (next_attempt_at IS NULL OR next_attempt_at <= datetime('now'))
                ORDER BY
                  CASE priority
                    WHEN 'hot' THEN 1
                    WHEN 'warm' THEN 2
                    WHEN 'cold' THEN 3
                    ELSE 4
                  END,
                  created_at ASC
                LIMIT ?
                """,
                (batch_size,),
            ).fetchall()
            return [self._row_to_followup(row) for row in rows]

    def claim_for_processing(self, followup_id: str, lock_token: str) -> Optional[Dict[str, Any]]:
        """Atomically claim a follow-up for processing.

        Returns the follow-up if successfully claimed, None if already processing.
        """
        now = "datetime('now')"
        with self._connect() as conn:
            cursor = conn.execute(
                """
                UPDATE follow_ups
                SET queue_status = 'processing',
                    processing_lock_token = ?,
                    last_attempt_at = {now},
                    updated_at = {now}
                WHERE id = ? AND queue_status = 'queued'
                  AND (next_attempt_at IS NULL OR next_attempt_at <= {now})
                """.format(now=now),
                (lock_token, followup_id),
            )
            conn.commit()
            if cursor.rowcount == 0:
                return None
            return self.get(followup_id)

    def get_queue_summary(self) -> Dict[str, Any]:
        """Return summary counts by queue_status and priority."""
        with self._connect() as conn:
            status_rows = conn.execute(
                "SELECT queue_status, COUNT(*) as cnt FROM follow_ups GROUP BY queue_status"
            ).fetchall()
            priority_rows = conn.execute(
                "SELECT priority, COUNT(*) as cnt FROM follow_ups GROUP BY priority"
            ).fetchall()
            retry_pending = conn.execute(
                "SELECT COUNT(*) as cnt FROM follow_ups WHERE queue_status = 'failed' AND next_attempt_at IS NOT NULL AND next_attempt_at <= datetime('now')"
            ).fetchone()

            return {
                "by_status": {row["queue_status"]: row["cnt"] for row in status_rows},
                "by_priority": {row["priority"]: row["cnt"] for row in priority_rows},
                "retry_pending": retry_pending["cnt"] if retry_pending else 0,
            }

    def get_by_lead_and_sequence(
        self, lead_id: str, sequence_key: str
    ) -> List[Dict[str, Any]]:
        """Get all follow-ups for a lead in a specific sequence, ordered by step."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM follow_ups
                WHERE lead_id = ? AND sequence_key = ?
                ORDER BY sequence_step ASC, created_at ASC
                """,
                (lead_id, sequence_key),
            ).fetchall()
            return [self._row_to_followup(row) for row in rows]

    def exists_for_lead_and_step(self, lead_id: str, sequence_key: str, step: int) -> bool:
        """Check if a follow-up already exists for a specific lead/sequence/step."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) as cnt FROM follow_ups
                WHERE lead_id = ? AND sequence_key = ? AND sequence_step = ?
                """,
                (lead_id, sequence_key, step),
            ).fetchone()
            return row["cnt"] > 0 if row else False
