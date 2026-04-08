import json
import sqlite3
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_NOTIFICATION_ENABLED_TYPES = [
    "HEALTH_STATUS_CHANGED",
    "COLLECTION_ENTERED_RED",
    "MISSING_BEST_EXECUTION",
    "PENDING_REVIEW_HIGH",
    "OPERATIONAL_FAILURE_THRESHOLD",
]


class SQLiteSequencePlanRunsStore:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_plan_runs (
                    request_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    request_payload TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    prompt_comparisons TEXT NOT NULL DEFAULT '[]',
                    prompt_comparison_metrics TEXT NOT NULL DEFAULT '{}',
                    created_jobs TEXT NOT NULL,
                    job_ids TEXT NOT NULL,
                    shot_job_links TEXT NOT NULL,
                    job_count INTEGER NOT NULL,
                    is_favorite INTEGER NOT NULL DEFAULT 0,
                    tags TEXT NOT NULL DEFAULT '[]',
                    note TEXT NOT NULL DEFAULT '',
                    review_status TEXT NOT NULL DEFAULT 'pending_review',
                    review_note TEXT NOT NULL DEFAULT '',
                    reviewed_at TEXT
                )
                """
            )
            self._ensure_optional_columns(connection)
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_plan_runs_created_at
                ON sequence_plan_runs (created_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_plan_runs_updated_at
                ON sequence_plan_runs (updated_at)
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_plan_review_history (
                    history_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    previous_review_status TEXT NOT NULL,
                    new_review_status TEXT NOT NULL,
                    review_note TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (request_id)
                        REFERENCES sequence_plan_runs(request_id)
                        ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_plan_review_history_request
                ON sequence_plan_review_history (request_id, created_at)
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_execution_collections (
                    collection_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL DEFAULT '',
                    editorial_note TEXT NOT NULL DEFAULT '',
                    color TEXT NOT NULL DEFAULT '',
                    is_archived INTEGER NOT NULL DEFAULT 0,
                    best_request_id TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_execution_collection_items (
                    collection_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    is_highlighted INTEGER NOT NULL DEFAULT 0,
                    added_at TEXT NOT NULL,
                    PRIMARY KEY (collection_id, request_id),
                    FOREIGN KEY (collection_id)
                        REFERENCES sequence_execution_collections(collection_id)
                        ON DELETE CASCADE
                )
                """
            )
            self._ensure_collection_columns(connection)
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_execution_collections_updated_at
                ON sequence_execution_collections (updated_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_execution_collection_items_collection
                ON sequence_execution_collection_items (collection_id, added_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_execution_collection_items_request
                ON sequence_execution_collection_items (request_id)
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_collection_notifications (
                    notification_id TEXT PRIMARY KEY,
                    collection_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    is_read INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (collection_id)
                        REFERENCES sequence_execution_collections(collection_id)
                        ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_collection_notification_state (
                    collection_id TEXT PRIMARY KEY,
                    last_health_status TEXT NOT NULL DEFAULT 'green',
                    missing_best_active INTEGER NOT NULL DEFAULT 0,
                    pending_review_high_active INTEGER NOT NULL DEFAULT 0,
                    operational_risk_active INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (collection_id)
                        REFERENCES sequence_execution_collections(collection_id)
                        ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_collection_notifications_created
                ON sequence_collection_notifications (created_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_collection_notifications_collection
                ON sequence_collection_notifications (collection_id, created_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_collection_notifications_read
                ON sequence_collection_notifications (is_read, created_at)
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_notification_preferences (
                    preferences_id TEXT PRIMARY KEY,
                    notifications_enabled INTEGER NOT NULL DEFAULT 1,
                    min_severity TEXT NOT NULL DEFAULT 'info',
                    enabled_types TEXT NOT NULL DEFAULT '[]',
                    show_only_unread_by_default INTEGER NOT NULL DEFAULT 0,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT OR IGNORE INTO sequence_notification_preferences (
                    preferences_id,
                    notifications_enabled,
                    min_severity,
                    enabled_types,
                    show_only_unread_by_default,
                    updated_at
                ) VALUES ('default', 1, 'info', ?, 0, '')
                """,
                (json.dumps(DEFAULT_NOTIFICATION_ENABLED_TYPES, ensure_ascii=False),),
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_notification_webhooks (
                    webhook_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    is_enabled INTEGER NOT NULL DEFAULT 1,
                    auth_mode TEXT NOT NULL DEFAULT 'none',
                    secret_token TEXT,
                    min_severity TEXT NOT NULL DEFAULT 'info',
                    enabled_types TEXT NOT NULL DEFAULT '[]',
                    custom_headers TEXT NOT NULL DEFAULT '{}',
                    payload_template_mode TEXT NOT NULL DEFAULT 'default',
                    payload_template TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            self._ensure_webhook_columns(connection)
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_notification_webhooks_updated
                ON sequence_notification_webhooks (updated_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_notification_webhooks_enabled
                ON sequence_notification_webhooks (is_enabled, updated_at)
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_notification_webhook_deliveries (
                    delivery_id TEXT PRIMARY KEY,
                    webhook_id TEXT NOT NULL,
                    notification_id TEXT NOT NULL,
                    collection_id TEXT NOT NULL,
                    routing_rule_id TEXT,
                    routing_rule_name TEXT,
                    payload TEXT NOT NULL DEFAULT '{}',
                    delivery_status TEXT NOT NULL DEFAULT 'pending',
                    attempt_count INTEGER NOT NULL DEFAULT 1,
                    max_attempts INTEGER NOT NULL DEFAULT 4,
                    last_attempt_at TEXT,
                    next_retry_at TEXT,
                    final_failure_at TEXT,
                    is_test INTEGER NOT NULL DEFAULT 0,
                    template_mode TEXT NOT NULL DEFAULT 'default',
                    auth_mode TEXT NOT NULL DEFAULT 'none',
                    request_headers TEXT NOT NULL DEFAULT '{}',
                    signature_timestamp TEXT,
                    response_status_code INTEGER,
                    response_body TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    delivered_at TEXT,
                    FOREIGN KEY (webhook_id)
                        REFERENCES sequence_notification_webhooks(webhook_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (notification_id)
                        REFERENCES sequence_collection_notifications(notification_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (collection_id)
                        REFERENCES sequence_execution_collections(collection_id)
                        ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_notification_webhook_deliveries_created
                ON sequence_notification_webhook_deliveries (created_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_notification_webhook_deliveries_webhook
                ON sequence_notification_webhook_deliveries (webhook_id, created_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_notification_webhook_deliveries_notification
                ON sequence_notification_webhook_deliveries (notification_id)
                """
            )
            self._ensure_webhook_delivery_columns(connection)
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_notification_channels (
                    channel_id TEXT PRIMARY KEY,
                    channel_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    is_enabled INTEGER NOT NULL DEFAULT 1,
                    config TEXT NOT NULL DEFAULT '{}',
                    min_severity TEXT NOT NULL DEFAULT 'info',
                    enabled_types TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_notification_channels_updated
                ON sequence_notification_channels (updated_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_notification_channels_type_enabled
                ON sequence_notification_channels (channel_type, is_enabled, updated_at)
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_notification_channel_deliveries (
                    delivery_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    channel_type TEXT NOT NULL,
                    notification_id TEXT NOT NULL,
                    collection_id TEXT NOT NULL,
                    routing_rule_id TEXT,
                    routing_rule_name TEXT,
                    payload TEXT NOT NULL DEFAULT '{}',
                    message_text TEXT NOT NULL DEFAULT '',
                    delivery_status TEXT NOT NULL DEFAULT 'pending',
                    attempt_count INTEGER NOT NULL DEFAULT 1,
                    max_attempts INTEGER NOT NULL DEFAULT 4,
                    last_attempt_at TEXT,
                    next_retry_at TEXT,
                    final_failure_at TEXT,
                    is_test INTEGER NOT NULL DEFAULT 0,
                    response_status_code INTEGER,
                    response_body TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    delivered_at TEXT,
                    FOREIGN KEY (channel_id)
                        REFERENCES sequence_notification_channels(channel_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (notification_id)
                        REFERENCES sequence_collection_notifications(notification_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (collection_id)
                        REFERENCES sequence_execution_collections(collection_id)
                        ON DELETE CASCADE
                )
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_notification_channel_deliveries_created
                ON sequence_notification_channel_deliveries (created_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_notification_channel_deliveries_channel
                ON sequence_notification_channel_deliveries (channel_id, created_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_notification_channel_deliveries_notification
                ON sequence_notification_channel_deliveries (notification_id)
                """
            )
            self._ensure_notification_channel_delivery_columns(connection)
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sequence_alert_routing_rules (
                    rule_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    is_enabled INTEGER NOT NULL DEFAULT 1,
                    target_channel_id TEXT NOT NULL,
                    target_channel_kind TEXT NOT NULL DEFAULT 'notification_channel',
                    match_types TEXT NOT NULL DEFAULT '[]',
                    min_severity TEXT NOT NULL DEFAULT 'info',
                    match_collection_id TEXT,
                    match_health_status TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            self._ensure_alert_routing_rule_columns(connection)
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_alert_routing_rules_updated
                ON sequence_alert_routing_rules (updated_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_alert_routing_rules_enabled
                ON sequence_alert_routing_rules (is_enabled, updated_at)
                """
            )
            connection.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_sequence_alert_routing_rules_target
                ON sequence_alert_routing_rules (target_channel_kind, target_channel_id)
                """
            )
            connection.commit()

    def _ensure_optional_columns(self, connection: sqlite3.Connection) -> None:
        existing_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(sequence_plan_runs)").fetchall()
        }

        if "is_favorite" not in existing_columns:
            connection.execute(
                """
                ALTER TABLE sequence_plan_runs
                ADD COLUMN is_favorite INTEGER NOT NULL DEFAULT 0
                """
            )

        if "tags" not in existing_columns:
            connection.execute(
                """
                ALTER TABLE sequence_plan_runs
                ADD COLUMN tags TEXT NOT NULL DEFAULT '[]'
                """
            )

        if "note" not in existing_columns:
            connection.execute(
                """
                ALTER TABLE sequence_plan_runs
                ADD COLUMN note TEXT NOT NULL DEFAULT ''
                """
            )

        if "review_status" not in existing_columns:
            connection.execute(
                """
                ALTER TABLE sequence_plan_runs
                ADD COLUMN review_status TEXT NOT NULL DEFAULT 'pending_review'
                """
            )

        if "review_note" not in existing_columns:
            connection.execute(
                """
                ALTER TABLE sequence_plan_runs
                ADD COLUMN review_note TEXT NOT NULL DEFAULT ''
                """
            )

        if "reviewed_at" not in existing_columns:
            connection.execute(
                """
                ALTER TABLE sequence_plan_runs
                ADD COLUMN reviewed_at TEXT
                """
            )

        if "prompt_comparisons" not in existing_columns:
            connection.execute(
                """
                ALTER TABLE sequence_plan_runs
                ADD COLUMN prompt_comparisons TEXT NOT NULL DEFAULT '[]'
                """
            )

        if "prompt_comparison_metrics" not in existing_columns:
            connection.execute(
                """
                ALTER TABLE sequence_plan_runs
                ADD COLUMN prompt_comparison_metrics TEXT NOT NULL DEFAULT '{}'
                """
            )

    def _ensure_collection_columns(self, connection: sqlite3.Connection) -> None:
        collection_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(sequence_execution_collections)").fetchall()
        }

        if "editorial_note" not in collection_columns:
            connection.execute(
                """
                ALTER TABLE sequence_execution_collections
                ADD COLUMN editorial_note TEXT NOT NULL DEFAULT ''
                """
            )

        if "best_request_id" not in collection_columns:
            connection.execute(
                """
                ALTER TABLE sequence_execution_collections
                ADD COLUMN best_request_id TEXT
                """
            )

        item_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(sequence_execution_collection_items)").fetchall()
        }

        if "is_highlighted" not in item_columns:
            connection.execute(
                """
                ALTER TABLE sequence_execution_collection_items
                ADD COLUMN is_highlighted INTEGER NOT NULL DEFAULT 0
                """
            )

    def _ensure_webhook_columns(self, connection: sqlite3.Connection) -> None:
        webhook_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(sequence_notification_webhooks)").fetchall()
        }

        if "auth_mode" not in webhook_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhooks
                ADD COLUMN auth_mode TEXT NOT NULL DEFAULT 'none'
                """
            )

        if "secret_token" not in webhook_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhooks
                ADD COLUMN secret_token TEXT
                """
            )

        if "custom_headers" not in webhook_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhooks
                ADD COLUMN custom_headers TEXT NOT NULL DEFAULT '{}'
                """
            )

        if "payload_template_mode" not in webhook_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhooks
                ADD COLUMN payload_template_mode TEXT NOT NULL DEFAULT 'default'
                """
            )

        if "payload_template" not in webhook_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhooks
                ADD COLUMN payload_template TEXT
                """
            )

    def _ensure_webhook_delivery_columns(self, connection: sqlite3.Connection) -> None:
        delivery_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(sequence_notification_webhook_deliveries)").fetchall()
        }

        if "attempt_count" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN attempt_count INTEGER NOT NULL DEFAULT 1
                """
            )

        if "max_attempts" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN max_attempts INTEGER NOT NULL DEFAULT 4
                """
            )

        if "last_attempt_at" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN last_attempt_at TEXT
                """
            )

        if "next_retry_at" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN next_retry_at TEXT
                """
            )

        if "final_failure_at" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN final_failure_at TEXT
                """
            )

        if "is_test" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN is_test INTEGER NOT NULL DEFAULT 0
                """
            )

        if "template_mode" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN template_mode TEXT NOT NULL DEFAULT 'default'
                """
            )

        if "auth_mode" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN auth_mode TEXT NOT NULL DEFAULT 'none'
                """
            )

        if "request_headers" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN request_headers TEXT NOT NULL DEFAULT '{}'
                """
            )

        if "signature_timestamp" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN signature_timestamp TEXT
                """
            )

        if "routing_rule_id" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN routing_rule_id TEXT
                """
            )

        if "routing_rule_name" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_webhook_deliveries
                ADD COLUMN routing_rule_name TEXT
                """
            )

    def _ensure_notification_channel_delivery_columns(self, connection: sqlite3.Connection) -> None:
        delivery_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(sequence_notification_channel_deliveries)").fetchall()
        }

        if "routing_rule_id" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_channel_deliveries
                ADD COLUMN routing_rule_id TEXT
                """
            )

        if "routing_rule_name" not in delivery_columns:
            connection.execute(
                """
                ALTER TABLE sequence_notification_channel_deliveries
                ADD COLUMN routing_rule_name TEXT
                """
            )

    def _ensure_alert_routing_rule_columns(self, connection: sqlite3.Connection) -> None:
        rule_columns = {
            str(row["name"])
            for row in connection.execute("PRAGMA table_info(sequence_alert_routing_rules)").fetchall()
        }

        if "target_channel_kind" not in rule_columns:
            connection.execute(
                """
                ALTER TABLE sequence_alert_routing_rules
                ADD COLUMN target_channel_kind TEXT NOT NULL DEFAULT 'notification_channel'
                """
            )

        if "match_collection_id" not in rule_columns:
            connection.execute(
                """
                ALTER TABLE sequence_alert_routing_rules
                ADD COLUMN match_collection_id TEXT
                """
            )

        if "match_health_status" not in rule_columns:
            connection.execute(
                """
                ALTER TABLE sequence_alert_routing_rules
                ADD COLUMN match_health_status TEXT
                """
            )

    def _row_to_run(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "request_id": row["request_id"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
            "request_payload": json.loads(row["request_payload"] or "{}"),
            "plan": json.loads(row["plan"] or "{}"),
            "prompt_comparisons": json.loads(row["prompt_comparisons"] or "[]"),
            "prompt_comparison_metrics": json.loads(row["prompt_comparison_metrics"] or "{}"),
            "created_jobs": json.loads(row["created_jobs"] or "[]"),
            "job_ids": json.loads(row["job_ids"] or "[]"),
            "shot_job_links": json.loads(row["shot_job_links"] or "[]"),
            "job_count": int(row["job_count"] or 0),
            "is_favorite": bool(int(row["is_favorite"] or 0)),
            "tags": json.loads(row["tags"] or "[]"),
            "note": str(row["note"] or ""),
            "review_status": str(row["review_status"] or "pending_review"),
            "review_note": str(row["review_note"] or ""),
            "reviewed_at": str(row["reviewed_at"]) if row["reviewed_at"] else None,
        }

    def create_run(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sequence_plan_runs (
                    request_id,
                    created_at,
                    updated_at,
                    request_payload,
                    plan,
                    prompt_comparisons,
                    prompt_comparison_metrics,
                    created_jobs,
                    job_ids,
                    shot_job_links,
                    job_count,
                    is_favorite,
                    tags,
                    note,
                    review_status,
                    review_note,
                    reviewed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_data["request_id"],
                    run_data["created_at"],
                    run_data["updated_at"],
                    json.dumps(run_data.get("request_payload", {}), ensure_ascii=False),
                    json.dumps(run_data.get("plan", {}), ensure_ascii=False),
                    json.dumps(run_data.get("prompt_comparisons", []), ensure_ascii=False),
                    json.dumps(run_data.get("prompt_comparison_metrics", {}), ensure_ascii=False),
                    json.dumps(run_data.get("created_jobs", []), ensure_ascii=False),
                    json.dumps(run_data.get("job_ids", []), ensure_ascii=False),
                    json.dumps(run_data.get("shot_job_links", []), ensure_ascii=False),
                    int(run_data.get("job_count", 0)),
                    1 if bool(run_data.get("is_favorite", False)) else 0,
                    json.dumps(run_data.get("tags", []), ensure_ascii=False),
                    str(run_data.get("note", "") or ""),
                    str(run_data.get("review_status", "pending_review") or "pending_review"),
                    str(run_data.get("review_note", "") or ""),
                    str(run_data.get("reviewed_at")) if run_data.get("reviewed_at") else None,
                ),
            )
            connection.commit()

        return run_data

    def _row_to_review_history_entry(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "history_id": str(row["history_id"] or ""),
            "request_id": str(row["request_id"] or ""),
            "previous_review_status": str(row["previous_review_status"] or "pending_review"),
            "new_review_status": str(row["new_review_status"] or "pending_review"),
            "review_note": str(row["review_note"] or ""),
            "created_at": str(row["created_at"] or ""),
        }

    def _row_to_notification(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "notification_id": str(row["notification_id"] or ""),
            "collection_id": str(row["collection_id"] or ""),
            "type": str(row["type"] or ""),
            "severity": str(row["severity"] or "info"),
            "message": str(row["message"] or ""),
            "created_at": str(row["created_at"] or ""),
            "is_read": bool(int(row["is_read"] or 0)),
        }

    def create_review_history_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO sequence_plan_review_history (
                    history_id,
                    request_id,
                    previous_review_status,
                    new_review_status,
                    review_note,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    str(entry_data.get("history_id") or ""),
                    str(entry_data.get("request_id") or ""),
                    str(entry_data.get("previous_review_status") or "pending_review"),
                    str(entry_data.get("new_review_status") or "pending_review"),
                    str(entry_data.get("review_note") or ""),
                    str(entry_data.get("created_at") or ""),
                ),
            )
            connection.commit()

        return entry_data

    def list_review_history_for_request(self, request_id: str, limit: Optional[int] = 200) -> List[Dict[str, Any]]:
        query = """
            SELECT
                history_id,
                request_id,
                previous_review_status,
                new_review_status,
                review_note,
                created_at
            FROM sequence_plan_review_history
            WHERE request_id = ?
            ORDER BY created_at DESC
        """
        params: tuple[Any, ...]

        if limit is None:
            params = (request_id,)
        else:
            normalized_limit = max(1, min(int(limit), 500))
            query += " LIMIT ?"
            params = (request_id, normalized_limit)

        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()

        return [self._row_to_review_history_entry(row) for row in rows]

    def get_review_history_summary(self, request_id: str) -> Dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    COUNT(history_id) AS history_count,
                    MAX(created_at) AS latest_created_at
                FROM sequence_plan_review_history
                WHERE request_id = ?
                """,
                (request_id,),
            ).fetchone()

        if row is None:
            return {
                "history_count": 0,
                "latest_created_at": None,
            }

        return {
            "history_count": int(row["history_count"] or 0),
            "latest_created_at": str(row["latest_created_at"]) if row["latest_created_at"] else None,
        }

    def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO sequence_collection_notifications (
                    notification_id,
                    collection_id,
                    type,
                    severity,
                    message,
                    created_at,
                    is_read
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(notification_data.get("notification_id") or ""),
                    str(notification_data.get("collection_id") or ""),
                    str(notification_data.get("type") or ""),
                    str(notification_data.get("severity") or "info"),
                    str(notification_data.get("message") or ""),
                    str(notification_data.get("created_at") or ""),
                    1 if bool(notification_data.get("is_read", False)) else 0,
                ),
            )
            connection.commit()

        return notification_data

    def _row_to_notification_preferences(self, row: sqlite3.Row) -> Dict[str, Any]:
        raw_enabled_types = json.loads(row["enabled_types"] or "[]")
        enabled_types: List[str] = []
        seen = set()
        if isinstance(raw_enabled_types, list):
            for item in raw_enabled_types:
                if not isinstance(item, str):
                    continue
                trimmed = item.strip()
                if not trimmed:
                    continue
                if trimmed in seen:
                    continue
                seen.add(trimmed)
                enabled_types.append(trimmed)

        return {
            "notifications_enabled": bool(int(row["notifications_enabled"] or 0)),
            "min_severity": str(row["min_severity"] or "info"),
            "enabled_types": enabled_types,
            "show_only_unread_by_default": bool(int(row["show_only_unread_by_default"] or 0)),
            "updated_at": str(row["updated_at"] or ""),
        }

    def get_notification_preferences(self) -> Dict[str, Any]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    notifications_enabled,
                    min_severity,
                    enabled_types,
                    show_only_unread_by_default,
                    updated_at
                FROM sequence_notification_preferences
                WHERE preferences_id = 'default'
                """
            ).fetchone()

        if row is None:
            return {
                "notifications_enabled": True,
                "min_severity": "info",
                "enabled_types": deepcopy(DEFAULT_NOTIFICATION_ENABLED_TYPES),
                "show_only_unread_by_default": False,
                "updated_at": "",
            }

        return self._row_to_notification_preferences(row)

    def upsert_notification_preferences(self, preferences_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sequence_notification_preferences (
                    preferences_id,
                    notifications_enabled,
                    min_severity,
                    enabled_types,
                    show_only_unread_by_default,
                    updated_at
                ) VALUES ('default', ?, ?, ?, ?, ?)
                ON CONFLICT(preferences_id) DO UPDATE SET
                    notifications_enabled = excluded.notifications_enabled,
                    min_severity = excluded.min_severity,
                    enabled_types = excluded.enabled_types,
                    show_only_unread_by_default = excluded.show_only_unread_by_default,
                    updated_at = excluded.updated_at
                """,
                (
                    1 if bool(preferences_data.get("notifications_enabled", True)) else 0,
                    str(preferences_data.get("min_severity") or "info"),
                    json.dumps(preferences_data.get("enabled_types", []), ensure_ascii=False),
                    1 if bool(preferences_data.get("show_only_unread_by_default", False)) else 0,
                    str(preferences_data.get("updated_at") or ""),
                ),
            )
            connection.commit()

        return self.get_notification_preferences()

    def _row_to_webhook(self, row: sqlite3.Row) -> Dict[str, Any]:
        raw_enabled_types = json.loads(row["enabled_types"] or "[]")
        enabled_types: List[str] = []
        seen = set()
        if isinstance(raw_enabled_types, list):
            for item in raw_enabled_types:
                if not isinstance(item, str):
                    continue
                trimmed = item.strip()
                if not trimmed:
                    continue
                if trimmed in seen:
                    continue
                seen.add(trimmed)
                enabled_types.append(trimmed)

        raw_custom_headers = json.loads(row["custom_headers"] or "{}")
        custom_headers: Dict[str, str] = {}
        if isinstance(raw_custom_headers, dict):
            for raw_key, raw_value in raw_custom_headers.items():
                if not isinstance(raw_key, str):
                    continue
                key = raw_key.strip()
                if not key:
                    continue
                if isinstance(raw_value, str):
                    value = raw_value.strip()
                else:
                    value = str(raw_value).strip()
                if not value:
                    continue
                custom_headers[key] = value

        secret_token = str(row["secret_token"] or "").strip() if row["secret_token"] is not None else None
        if secret_token == "":
            secret_token = None

        payload_template_raw: Optional[Any] = None
        if row["payload_template"] is not None:
            try:
                payload_template_raw = json.loads(row["payload_template"])
            except Exception:
                payload_template_raw = None

        payload_template = payload_template_raw if isinstance(payload_template_raw, dict) else None

        return {
            "webhook_id": str(row["webhook_id"] or ""),
            "name": str(row["name"] or ""),
            "url": str(row["url"] or ""),
            "is_enabled": bool(int(row["is_enabled"] or 0)),
            "auth_mode": str(row["auth_mode"] or "none"),
            "secret_token": secret_token,
            "min_severity": str(row["min_severity"] or "info"),
            "enabled_types": enabled_types,
            "custom_headers": custom_headers,
            "payload_template_mode": str(row["payload_template_mode"] or "default"),
            "payload_template": payload_template,
            "created_at": str(row["created_at"] or ""),
            "updated_at": str(row["updated_at"] or ""),
        }

    def _row_to_webhook_delivery(self, row: sqlite3.Row) -> Dict[str, Any]:
        payload_raw = json.loads(row["payload"] or "{}")
        payload = payload_raw if isinstance(payload_raw, dict) else {}
        request_headers_raw = json.loads(row["request_headers"] or "{}")
        request_headers: Dict[str, str] = {}
        if isinstance(request_headers_raw, dict):
            for raw_key, raw_value in request_headers_raw.items():
                if not isinstance(raw_key, str):
                    continue
                key = raw_key.strip()
                if not key:
                    continue
                if isinstance(raw_value, str):
                    value = raw_value.strip()
                else:
                    value = str(raw_value).strip()
                if not value:
                    continue
                request_headers[key] = value

        return {
            "delivery_id": str(row["delivery_id"] or ""),
            "webhook_id": str(row["webhook_id"] or ""),
            "notification_id": str(row["notification_id"] or ""),
            "collection_id": str(row["collection_id"] or ""),
            "routing_rule_id": str(row["routing_rule_id"]) if row["routing_rule_id"] is not None else None,
            "routing_rule_name": str(row["routing_rule_name"]) if row["routing_rule_name"] is not None else None,
            "payload": payload,
            "delivery_status": str(row["delivery_status"] or "pending"),
            "attempt_count": int(row["attempt_count"] or 0),
            "max_attempts": int(row["max_attempts"] or 0),
            "last_attempt_at": str(row["last_attempt_at"]) if row["last_attempt_at"] is not None else None,
            "next_retry_at": str(row["next_retry_at"]) if row["next_retry_at"] is not None else None,
            "final_failure_at": str(row["final_failure_at"])
            if row["final_failure_at"] is not None
            else None,
            "is_test": bool(int(row["is_test"] or 0)),
            "template_mode": str(row["template_mode"] or "default"),
            "auth_mode": str(row["auth_mode"] or "none"),
            "request_headers": request_headers,
            "signature_timestamp": str(row["signature_timestamp"])
            if row["signature_timestamp"] is not None
            else None,
            "response_status_code": int(row["response_status_code"])
            if row["response_status_code"] is not None
            else None,
            "response_body": str(row["response_body"]) if row["response_body"] is not None else None,
            "error_message": str(row["error_message"]) if row["error_message"] is not None else None,
            "created_at": str(row["created_at"] or ""),
            "delivered_at": str(row["delivered_at"]) if row["delivered_at"] is not None else None,
        }

    def _row_to_notification_channel(self, row: sqlite3.Row) -> Dict[str, Any]:
        raw_enabled_types = json.loads(row["enabled_types"] or "[]")
        enabled_types: List[str] = []
        seen = set()
        if isinstance(raw_enabled_types, list):
            for item in raw_enabled_types:
                if not isinstance(item, str):
                    continue
                trimmed = item.strip()
                if not trimmed:
                    continue
                if trimmed in seen:
                    continue
                seen.add(trimmed)
                enabled_types.append(trimmed)

        config_raw = json.loads(row["config"] or "{}")
        config = config_raw if isinstance(config_raw, dict) else {}

        return {
            "channel_id": str(row["channel_id"] or ""),
            "channel_type": str(row["channel_type"] or "webhook"),
            "name": str(row["name"] or ""),
            "is_enabled": bool(int(row["is_enabled"] or 0)),
            "config": config,
            "min_severity": str(row["min_severity"] or "info"),
            "enabled_types": enabled_types,
            "created_at": str(row["created_at"] or ""),
            "updated_at": str(row["updated_at"] or ""),
        }

    def _row_to_notification_channel_delivery(self, row: sqlite3.Row) -> Dict[str, Any]:
        payload_raw = json.loads(row["payload"] or "{}")
        payload = payload_raw if isinstance(payload_raw, dict) else {}
        return {
            "delivery_id": str(row["delivery_id"] or ""),
            "channel_id": str(row["channel_id"] or ""),
            "channel_type": str(row["channel_type"] or "webhook"),
            "notification_id": str(row["notification_id"] or ""),
            "collection_id": str(row["collection_id"] or ""),
            "routing_rule_id": str(row["routing_rule_id"]) if row["routing_rule_id"] is not None else None,
            "routing_rule_name": str(row["routing_rule_name"]) if row["routing_rule_name"] is not None else None,
            "payload": payload,
            "message_text": str(row["message_text"] or ""),
            "delivery_status": str(row["delivery_status"] or "pending"),
            "attempt_count": int(row["attempt_count"] or 0),
            "max_attempts": int(row["max_attempts"] or 0),
            "last_attempt_at": str(row["last_attempt_at"]) if row["last_attempt_at"] is not None else None,
            "next_retry_at": str(row["next_retry_at"]) if row["next_retry_at"] is not None else None,
            "final_failure_at": str(row["final_failure_at"]) if row["final_failure_at"] is not None else None,
            "is_test": bool(int(row["is_test"] or 0)),
            "response_status_code": int(row["response_status_code"])
            if row["response_status_code"] is not None
            else None,
            "response_body": str(row["response_body"]) if row["response_body"] is not None else None,
            "error_message": str(row["error_message"]) if row["error_message"] is not None else None,
            "created_at": str(row["created_at"] or ""),
            "delivered_at": str(row["delivered_at"]) if row["delivered_at"] is not None else None,
        }

    def _row_to_alert_routing_rule(self, row: sqlite3.Row) -> Dict[str, Any]:
        raw_match_types = json.loads(row["match_types"] or "[]")
        match_types: List[str] = []
        seen = set()
        if isinstance(raw_match_types, list):
            for item in raw_match_types:
                if not isinstance(item, str):
                    continue
                trimmed = item.strip()
                if not trimmed or trimmed in seen:
                    continue
                seen.add(trimmed)
                match_types.append(trimmed)

        match_collection_id = str(row["match_collection_id"] or "").strip() if row["match_collection_id"] is not None else None
        if match_collection_id == "":
            match_collection_id = None

        match_health_status = str(row["match_health_status"] or "").strip().lower() if row["match_health_status"] is not None else None
        if match_health_status == "":
            match_health_status = None

        return {
            "rule_id": str(row["rule_id"] or ""),
            "name": str(row["name"] or ""),
            "is_enabled": bool(int(row["is_enabled"] or 0)),
            "target_channel_id": str(row["target_channel_id"] or ""),
            "target_channel_kind": str(row["target_channel_kind"] or "notification_channel"),
            "match_types": match_types,
            "min_severity": str(row["min_severity"] or "info"),
            "match_collection_id": match_collection_id,
            "match_health_status": match_health_status,
            "created_at": str(row["created_at"] or ""),
            "updated_at": str(row["updated_at"] or ""),
        }

    def list_webhooks(self, limit: int = 100, include_disabled: bool = True) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))
        query = """
            SELECT
                webhook_id,
                name,
                url,
                is_enabled,
                auth_mode,
                secret_token,
                min_severity,
                enabled_types,
                custom_headers,
                payload_template_mode,
                payload_template,
                created_at,
                updated_at
            FROM sequence_notification_webhooks
        """
        params: List[Any] = []
        if not include_disabled:
            query += " WHERE is_enabled = 1"
        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(normalized_limit)

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [self._row_to_webhook(row) for row in rows]

    def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    webhook_id,
                    name,
                    url,
                    is_enabled,
                    auth_mode,
                    secret_token,
                    min_severity,
                    enabled_types,
                    custom_headers,
                    payload_template_mode,
                    payload_template,
                    created_at,
                    updated_at
                FROM sequence_notification_webhooks
                WHERE webhook_id = ?
                """,
                (webhook_id,),
            ).fetchone()

        return self._row_to_webhook(row) if row else None

    def create_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sequence_notification_webhooks (
                    webhook_id,
                    name,
                    url,
                    is_enabled,
                    auth_mode,
                    secret_token,
                    min_severity,
                    enabled_types,
                    custom_headers,
                    payload_template_mode,
                    payload_template,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(webhook_data.get("webhook_id") or ""),
                    str(webhook_data.get("name") or ""),
                    str(webhook_data.get("url") or ""),
                    1 if bool(webhook_data.get("is_enabled", True)) else 0,
                    str(webhook_data.get("auth_mode") or "none"),
                    str(webhook_data.get("secret_token") or "").strip() if webhook_data.get("secret_token") is not None else None,
                    str(webhook_data.get("min_severity") or "info"),
                    json.dumps(webhook_data.get("enabled_types", []), ensure_ascii=False),
                    json.dumps(webhook_data.get("custom_headers", {}), ensure_ascii=False),
                    str(webhook_data.get("payload_template_mode") or "default"),
                    json.dumps(webhook_data.get("payload_template"), ensure_ascii=False)
                    if webhook_data.get("payload_template") is not None
                    else None,
                    str(webhook_data.get("created_at") or ""),
                    str(webhook_data.get("updated_at") or ""),
                ),
            )
            connection.commit()

        persisted = self.get_webhook(str(webhook_data.get("webhook_id") or ""))
        return persisted if persisted is not None else webhook_data

    def update_webhook(self, webhook_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = {
            "name",
            "url",
            "is_enabled",
            "auth_mode",
            "secret_token",
            "min_severity",
            "enabled_types",
            "custom_headers",
            "payload_template_mode",
            "payload_template",
            "updated_at",
        }

        set_clauses: List[str] = []
        values: List[Any] = []

        for key, value in updates.items():
            if key not in allowed_fields:
                continue

            set_clauses.append(f"{key} = ?")

            if key == "is_enabled":
                values.append(1 if bool(value) else 0)
            elif key == "enabled_types":
                values.append(json.dumps(value if isinstance(value, list) else [], ensure_ascii=False))
            elif key == "custom_headers":
                values.append(json.dumps(value if isinstance(value, dict) else {}, ensure_ascii=False))
            elif key == "payload_template":
                values.append(json.dumps(value, ensure_ascii=False) if isinstance(value, dict) else None)
            elif key == "secret_token":
                normalized_secret = str(value).strip() if value is not None else ""
                values.append(normalized_secret or None)
            else:
                values.append(str(value or ""))

        if not set_clauses:
            return self.get_webhook(webhook_id)

        values.append(webhook_id)

        with self._connect() as connection:
            cursor = connection.execute(
                f"""
                UPDATE sequence_notification_webhooks
                SET {", ".join(set_clauses)}
                WHERE webhook_id = ?
                """,
                tuple(values),
            )
            connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_webhook(webhook_id)

    def create_webhook_delivery(self, delivery_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO sequence_notification_webhook_deliveries (
                    delivery_id,
                    webhook_id,
                    notification_id,
                    collection_id,
                    routing_rule_id,
                    routing_rule_name,
                    payload,
                    delivery_status,
                    attempt_count,
                    max_attempts,
                    last_attempt_at,
                    next_retry_at,
                    final_failure_at,
                    is_test,
                    template_mode,
                    auth_mode,
                    request_headers,
                    signature_timestamp,
                    response_status_code,
                    response_body,
                    error_message,
                    created_at,
                    delivered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(delivery_data.get("delivery_id") or ""),
                    str(delivery_data.get("webhook_id") or ""),
                    str(delivery_data.get("notification_id") or ""),
                    str(delivery_data.get("collection_id") or ""),
                    str(delivery_data.get("routing_rule_id"))
                    if delivery_data.get("routing_rule_id") is not None
                    else None,
                    str(delivery_data.get("routing_rule_name"))
                    if delivery_data.get("routing_rule_name") is not None
                    else None,
                    json.dumps(delivery_data.get("payload", {}), ensure_ascii=False),
                    str(delivery_data.get("delivery_status") or "pending"),
                    int(delivery_data.get("attempt_count", 1)),
                    int(delivery_data.get("max_attempts", 4)),
                    str(delivery_data.get("last_attempt_at"))
                    if delivery_data.get("last_attempt_at") is not None
                    else None,
                    str(delivery_data.get("next_retry_at"))
                    if delivery_data.get("next_retry_at") is not None
                    else None,
                    str(delivery_data.get("final_failure_at"))
                    if delivery_data.get("final_failure_at") is not None
                    else None,
                    1 if bool(delivery_data.get("is_test", False)) else 0,
                    str(delivery_data.get("template_mode") or "default"),
                    str(delivery_data.get("auth_mode") or "none"),
                    json.dumps(delivery_data.get("request_headers", {}), ensure_ascii=False),
                    str(delivery_data.get("signature_timestamp"))
                    if delivery_data.get("signature_timestamp") is not None
                    else None,
                    int(delivery_data.get("response_status_code"))
                    if delivery_data.get("response_status_code") is not None
                    else None,
                    str(delivery_data.get("response_body")) if delivery_data.get("response_body") is not None else None,
                    str(delivery_data.get("error_message")) if delivery_data.get("error_message") is not None else None,
                    str(delivery_data.get("created_at") or ""),
                    str(delivery_data.get("delivered_at")) if delivery_data.get("delivered_at") is not None else None,
                ),
            )
            connection.commit()

        persisted = self.get_webhook_delivery(str(delivery_data.get("delivery_id") or ""))
        return persisted if persisted is not None else delivery_data

    def get_webhook_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    delivery_id,
                    webhook_id,
                    notification_id,
                    collection_id,
                    routing_rule_id,
                    routing_rule_name,
                    payload,
                    delivery_status,
                    attempt_count,
                    max_attempts,
                    last_attempt_at,
                    next_retry_at,
                    final_failure_at,
                    is_test,
                    template_mode,
                    auth_mode,
                    request_headers,
                    signature_timestamp,
                    response_status_code,
                    response_body,
                    error_message,
                    created_at,
                    delivered_at
                FROM sequence_notification_webhook_deliveries
                WHERE delivery_id = ?
                """,
                (delivery_id,),
            ).fetchone()

        return self._row_to_webhook_delivery(row) if row else None

    def update_webhook_delivery(self, delivery_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = {
            "delivery_status",
            "attempt_count",
            "max_attempts",
            "last_attempt_at",
            "next_retry_at",
            "final_failure_at",
            "is_test",
            "auth_mode",
            "request_headers",
            "signature_timestamp",
            "response_status_code",
            "response_body",
            "error_message",
            "delivered_at",
            "routing_rule_id",
            "routing_rule_name",
        }

        set_clauses: List[str] = []
        values: List[Any] = []

        for key, value in updates.items():
            if key not in allowed_fields:
                continue

            set_clauses.append(f"{key} = ?")

            if key == "response_status_code":
                values.append(int(value) if value is not None else None)
            elif key == "attempt_count":
                values.append(max(0, int(value)) if value is not None else 0)
            elif key == "max_attempts":
                values.append(max(1, int(value)) if value is not None else 1)
            elif key == "is_test":
                values.append(1 if bool(value) else 0)
            elif key == "request_headers":
                values.append(json.dumps(value if isinstance(value, dict) else {}, ensure_ascii=False))
            elif key in {
                "response_body",
                "error_message",
                "delivered_at",
                "last_attempt_at",
                "next_retry_at",
                "final_failure_at",
                "routing_rule_id",
                "routing_rule_name",
            }:
                values.append(str(value) if value is not None else None)
            else:
                values.append(str(value or "pending"))

        if not set_clauses:
            return self.get_webhook_delivery(delivery_id)

        values.append(delivery_id)

        with self._connect() as connection:
            cursor = connection.execute(
                f"""
                UPDATE sequence_notification_webhook_deliveries
                SET {", ".join(set_clauses)}
                WHERE delivery_id = ?
                """,
                tuple(values),
            )
            connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_webhook_delivery(delivery_id)

    def list_webhook_deliveries(
        self,
        limit: int = 100,
        webhook_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        notification_id: Optional[str] = None,
        is_test: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))
        query = """
            SELECT
                delivery_id,
                webhook_id,
                notification_id,
                collection_id,
                routing_rule_id,
                routing_rule_name,
                payload,
                delivery_status,
                attempt_count,
                max_attempts,
                last_attempt_at,
                next_retry_at,
                final_failure_at,
                is_test,
                template_mode,
                auth_mode,
                request_headers,
                signature_timestamp,
                response_status_code,
                response_body,
                error_message,
                created_at,
                delivered_at
            FROM sequence_notification_webhook_deliveries
        """

        where_clauses: List[str] = []
        params: List[Any] = []

        if isinstance(webhook_id, str) and webhook_id.strip():
            where_clauses.append("webhook_id = ?")
            params.append(webhook_id.strip())

        if isinstance(collection_id, str) and collection_id.strip():
            where_clauses.append("collection_id = ?")
            params.append(collection_id.strip())

        if isinstance(notification_id, str) and notification_id.strip():
            where_clauses.append("notification_id = ?")
            params.append(notification_id.strip())

        if isinstance(is_test, bool):
            where_clauses.append("is_test = ?")
            params.append(1 if is_test else 0)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(normalized_limit)

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [self._row_to_webhook_delivery(row) for row in rows]

    def list_webhook_deliveries_pending_retry(
        self,
        due_before: str,
        limit: int = 100,
        webhook_id: Optional[str] = None,
        collection_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))
        query = """
            SELECT
                delivery_id,
                webhook_id,
                notification_id,
                collection_id,
                routing_rule_id,
                routing_rule_name,
                payload,
                delivery_status,
                attempt_count,
                max_attempts,
                last_attempt_at,
                next_retry_at,
                final_failure_at,
                is_test,
                template_mode,
                auth_mode,
                request_headers,
                signature_timestamp,
                response_status_code,
                response_body,
                error_message,
                created_at,
                delivered_at
            FROM sequence_notification_webhook_deliveries
            WHERE delivery_status = 'failed'
                AND attempt_count < max_attempts
                AND final_failure_at IS NULL
                AND (next_retry_at IS NULL OR next_retry_at <= ?)
        """

        params: List[Any] = [str(due_before or "")]

        if isinstance(webhook_id, str) and webhook_id.strip():
            query += " AND webhook_id = ?"
            params.append(webhook_id.strip())

        if isinstance(collection_id, str) and collection_id.strip():
            query += " AND collection_id = ?"
            params.append(collection_id.strip())

        query += " ORDER BY COALESCE(next_retry_at, created_at) ASC, created_at ASC LIMIT ?"
        params.append(normalized_limit)

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [self._row_to_webhook_delivery(row) for row in rows]

    def list_webhook_delivery_stats_by_webhook(self) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    w.webhook_id AS webhook_id,
                    w.name AS name,
                    w.is_enabled AS is_enabled,
                    COUNT(d.delivery_id) AS total_deliveries,
                    SUM(CASE WHEN d.delivery_status = 'sent' THEN 1 ELSE 0 END) AS sent_deliveries,
                    SUM(CASE WHEN d.delivery_status = 'failed' THEN 1 ELSE 0 END) AS failed_deliveries,
                    SUM(CASE WHEN d.delivery_status = 'pending' THEN 1 ELSE 0 END) AS pending_deliveries,
                    SUM(
                        CASE
                            WHEN d.delivery_status = 'failed'
                                AND (d.final_failure_at IS NOT NULL OR d.attempt_count >= d.max_attempts)
                            THEN 1
                            ELSE 0
                        END
                    ) AS exhausted_deliveries,
                    SUM(CASE WHEN d.attempt_count > 1 THEN d.attempt_count - 1 ELSE 0 END) AS total_retries,
                    MAX(COALESCE(d.last_attempt_at, d.created_at)) AS last_delivery_at
                FROM sequence_notification_webhooks w
                LEFT JOIN sequence_notification_webhook_deliveries d
                    ON d.webhook_id = w.webhook_id
                GROUP BY w.webhook_id, w.name, w.is_enabled
                """
            ).fetchall()

        stats: List[Dict[str, Any]] = []
        for row in rows:
            stats.append(
                {
                    "webhook_id": str(row["webhook_id"] or ""),
                    "name": str(row["name"] or ""),
                    "is_enabled": bool(int(row["is_enabled"] or 0)),
                    "total_deliveries": int(row["total_deliveries"] or 0),
                    "sent_deliveries": int(row["sent_deliveries"] or 0),
                    "failed_deliveries": int(row["failed_deliveries"] or 0),
                    "pending_deliveries": int(row["pending_deliveries"] or 0),
                    "exhausted_deliveries": int(row["exhausted_deliveries"] or 0),
                    "total_retries": int(row["total_retries"] or 0),
                    "last_delivery_at": str(row["last_delivery_at"]) if row["last_delivery_at"] is not None else None,
                }
            )

        return stats

    def list_recent_webhook_delivery_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    d.delivery_id,
                    d.webhook_id,
                    COALESCE(w.name, '') AS webhook_name,
                    d.notification_id,
                    d.collection_id,
                    d.error_message,
                    d.attempt_count,
                    d.max_attempts,
                    d.is_test,
                    d.auth_mode,
                    d.template_mode,
                    d.created_at,
                    d.last_attempt_at
                FROM sequence_notification_webhook_deliveries d
                LEFT JOIN sequence_notification_webhooks w
                    ON w.webhook_id = d.webhook_id
                WHERE d.delivery_status = 'failed'
                    AND d.error_message IS NOT NULL
                    AND TRIM(d.error_message) <> ''
                ORDER BY COALESCE(d.last_attempt_at, d.created_at) DESC, d.created_at DESC
                LIMIT ?
                """,
                (normalized_limit,),
            ).fetchall()

        errors: List[Dict[str, Any]] = []
        for row in rows:
            errors.append(
                {
                    "delivery_id": str(row["delivery_id"] or ""),
                    "webhook_id": str(row["webhook_id"] or ""),
                    "webhook_name": str(row["webhook_name"] or ""),
                    "notification_id": str(row["notification_id"] or ""),
                    "collection_id": str(row["collection_id"] or ""),
                    "error_message": str(row["error_message"] or ""),
                    "attempt_count": int(row["attempt_count"] or 0),
                    "max_attempts": int(row["max_attempts"] or 0),
                    "is_test": bool(int(row["is_test"] or 0)),
                    "auth_mode": str(row["auth_mode"] or "none"),
                    "template_mode": str(row["template_mode"] or "default"),
                    "created_at": str(row["created_at"] or ""),
                    "last_attempt_at": str(row["last_attempt_at"]) if row["last_attempt_at"] is not None else None,
                }
            )

        return errors

    def list_notification_channels(
        self,
        limit: int = 100,
        include_disabled: bool = True,
        channel_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))
        query = """
            SELECT
                channel_id,
                channel_type,
                name,
                is_enabled,
                config,
                min_severity,
                enabled_types,
                created_at,
                updated_at
            FROM sequence_notification_channels
        """

        where_clauses: List[str] = []
        params: List[Any] = []

        if not include_disabled:
            where_clauses.append("is_enabled = 1")

        if isinstance(channel_type, str) and channel_type.strip():
            where_clauses.append("channel_type = ?")
            params.append(channel_type.strip().lower())

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(normalized_limit)

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [self._row_to_notification_channel(row) for row in rows]

    def get_notification_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    channel_id,
                    channel_type,
                    name,
                    is_enabled,
                    config,
                    min_severity,
                    enabled_types,
                    created_at,
                    updated_at
                FROM sequence_notification_channels
                WHERE channel_id = ?
                """,
                (channel_id,),
            ).fetchone()

        return self._row_to_notification_channel(row) if row else None

    def create_notification_channel(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sequence_notification_channels (
                    channel_id,
                    channel_type,
                    name,
                    is_enabled,
                    config,
                    min_severity,
                    enabled_types,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(channel_data.get("channel_id") or ""),
                    str(channel_data.get("channel_type") or "webhook"),
                    str(channel_data.get("name") or ""),
                    1 if bool(channel_data.get("is_enabled", True)) else 0,
                    json.dumps(channel_data.get("config", {}), ensure_ascii=False),
                    str(channel_data.get("min_severity") or "info"),
                    json.dumps(channel_data.get("enabled_types", []), ensure_ascii=False),
                    str(channel_data.get("created_at") or ""),
                    str(channel_data.get("updated_at") or ""),
                ),
            )
            connection.commit()

        persisted = self.get_notification_channel(str(channel_data.get("channel_id") or ""))
        return persisted if persisted is not None else channel_data

    def update_notification_channel(self, channel_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = {
            "channel_type",
            "name",
            "is_enabled",
            "config",
            "min_severity",
            "enabled_types",
            "updated_at",
        }

        set_clauses: List[str] = []
        values: List[Any] = []
        for key, value in updates.items():
            if key not in allowed_fields:
                continue

            set_clauses.append(f"{key} = ?")
            if key == "is_enabled":
                values.append(1 if bool(value) else 0)
            elif key == "config":
                values.append(json.dumps(value if isinstance(value, dict) else {}, ensure_ascii=False))
            elif key == "enabled_types":
                values.append(json.dumps(value if isinstance(value, list) else [], ensure_ascii=False))
            else:
                values.append(str(value or ""))

        if not set_clauses:
            return self.get_notification_channel(channel_id)

        values.append(channel_id)
        with self._connect() as connection:
            cursor = connection.execute(
                f"""
                UPDATE sequence_notification_channels
                SET {", ".join(set_clauses)}
                WHERE channel_id = ?
                """,
                tuple(values),
            )
            connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_notification_channel(channel_id)

    def create_notification_channel_delivery(self, delivery_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO sequence_notification_channel_deliveries (
                    delivery_id,
                    channel_id,
                    channel_type,
                    notification_id,
                    collection_id,
                    routing_rule_id,
                    routing_rule_name,
                    payload,
                    message_text,
                    delivery_status,
                    attempt_count,
                    max_attempts,
                    last_attempt_at,
                    next_retry_at,
                    final_failure_at,
                    is_test,
                    response_status_code,
                    response_body,
                    error_message,
                    created_at,
                    delivered_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(delivery_data.get("delivery_id") or ""),
                    str(delivery_data.get("channel_id") or ""),
                    str(delivery_data.get("channel_type") or "webhook"),
                    str(delivery_data.get("notification_id") or ""),
                    str(delivery_data.get("collection_id") or ""),
                    str(delivery_data.get("routing_rule_id"))
                    if delivery_data.get("routing_rule_id") is not None
                    else None,
                    str(delivery_data.get("routing_rule_name"))
                    if delivery_data.get("routing_rule_name") is not None
                    else None,
                    json.dumps(delivery_data.get("payload", {}), ensure_ascii=False),
                    str(delivery_data.get("message_text") or ""),
                    str(delivery_data.get("delivery_status") or "pending"),
                    int(delivery_data.get("attempt_count", 1)),
                    int(delivery_data.get("max_attempts", 4)),
                    str(delivery_data.get("last_attempt_at")) if delivery_data.get("last_attempt_at") is not None else None,
                    str(delivery_data.get("next_retry_at")) if delivery_data.get("next_retry_at") is not None else None,
                    str(delivery_data.get("final_failure_at"))
                    if delivery_data.get("final_failure_at") is not None
                    else None,
                    1 if bool(delivery_data.get("is_test", False)) else 0,
                    int(delivery_data.get("response_status_code"))
                    if delivery_data.get("response_status_code") is not None
                    else None,
                    str(delivery_data.get("response_body")) if delivery_data.get("response_body") is not None else None,
                    str(delivery_data.get("error_message")) if delivery_data.get("error_message") is not None else None,
                    str(delivery_data.get("created_at") or ""),
                    str(delivery_data.get("delivered_at")) if delivery_data.get("delivered_at") is not None else None,
                ),
            )
            connection.commit()

        persisted = self.get_notification_channel_delivery(str(delivery_data.get("delivery_id") or ""))
        return persisted if persisted is not None else delivery_data

    def get_notification_channel_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    delivery_id,
                    channel_id,
                    channel_type,
                    notification_id,
                    collection_id,
                    routing_rule_id,
                    routing_rule_name,
                    payload,
                    message_text,
                    delivery_status,
                    attempt_count,
                    max_attempts,
                    last_attempt_at,
                    next_retry_at,
                    final_failure_at,
                    is_test,
                    response_status_code,
                    response_body,
                    error_message,
                    created_at,
                    delivered_at
                FROM sequence_notification_channel_deliveries
                WHERE delivery_id = ?
                """,
                (delivery_id,),
            ).fetchone()

        return self._row_to_notification_channel_delivery(row) if row else None

    def update_notification_channel_delivery(self, delivery_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = {
            "delivery_status",
            "attempt_count",
            "max_attempts",
            "last_attempt_at",
            "next_retry_at",
            "final_failure_at",
            "is_test",
            "response_status_code",
            "response_body",
            "error_message",
            "delivered_at",
            "routing_rule_id",
            "routing_rule_name",
        }

        set_clauses: List[str] = []
        values: List[Any] = []
        for key, value in updates.items():
            if key not in allowed_fields:
                continue

            set_clauses.append(f"{key} = ?")
            if key == "response_status_code":
                values.append(int(value) if value is not None else None)
            elif key == "attempt_count":
                values.append(max(0, int(value)) if value is not None else 0)
            elif key == "max_attempts":
                values.append(max(1, int(value)) if value is not None else 1)
            elif key == "is_test":
                values.append(1 if bool(value) else 0)
            elif key in {
                "response_body",
                "error_message",
                "delivered_at",
                "last_attempt_at",
                "next_retry_at",
                "final_failure_at",
                "routing_rule_id",
                "routing_rule_name",
            }:
                values.append(str(value) if value is not None else None)
            else:
                values.append(str(value or "pending"))

        if not set_clauses:
            return self.get_notification_channel_delivery(delivery_id)

        values.append(delivery_id)
        with self._connect() as connection:
            cursor = connection.execute(
                f"""
                UPDATE sequence_notification_channel_deliveries
                SET {", ".join(set_clauses)}
                WHERE delivery_id = ?
                """,
                tuple(values),
            )
            connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_notification_channel_delivery(delivery_id)

    def list_notification_channel_deliveries(
        self,
        limit: int = 100,
        channel_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        notification_id: Optional[str] = None,
        channel_type: Optional[str] = None,
        is_test: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))
        query = """
            SELECT
                delivery_id,
                channel_id,
                channel_type,
                notification_id,
                collection_id,
                routing_rule_id,
                routing_rule_name,
                payload,
                message_text,
                delivery_status,
                attempt_count,
                max_attempts,
                last_attempt_at,
                next_retry_at,
                final_failure_at,
                is_test,
                response_status_code,
                response_body,
                error_message,
                created_at,
                delivered_at
            FROM sequence_notification_channel_deliveries
        """

        where_clauses: List[str] = []
        params: List[Any] = []

        if isinstance(channel_id, str) and channel_id.strip():
            where_clauses.append("channel_id = ?")
            params.append(channel_id.strip())

        if isinstance(collection_id, str) and collection_id.strip():
            where_clauses.append("collection_id = ?")
            params.append(collection_id.strip())

        if isinstance(notification_id, str) and notification_id.strip():
            where_clauses.append("notification_id = ?")
            params.append(notification_id.strip())

        if isinstance(channel_type, str) and channel_type.strip():
            where_clauses.append("channel_type = ?")
            params.append(channel_type.strip().lower())

        if isinstance(is_test, bool):
            where_clauses.append("is_test = ?")
            params.append(1 if is_test else 0)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(normalized_limit)

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [self._row_to_notification_channel_delivery(row) for row in rows]

    def list_notification_channel_deliveries_pending_retry(
        self,
        due_before: str,
        limit: int = 100,
        channel_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        channel_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))
        query = """
            SELECT
                delivery_id,
                channel_id,
                channel_type,
                notification_id,
                collection_id,
                routing_rule_id,
                routing_rule_name,
                payload,
                message_text,
                delivery_status,
                attempt_count,
                max_attempts,
                last_attempt_at,
                next_retry_at,
                final_failure_at,
                is_test,
                response_status_code,
                response_body,
                error_message,
                created_at,
                delivered_at
            FROM sequence_notification_channel_deliveries
            WHERE delivery_status = 'failed'
                AND attempt_count < max_attempts
                AND final_failure_at IS NULL
                AND (next_retry_at IS NULL OR next_retry_at <= ?)
        """

        params: List[Any] = [str(due_before or "")]

        if isinstance(channel_id, str) and channel_id.strip():
            query += " AND channel_id = ?"
            params.append(channel_id.strip())

        if isinstance(collection_id, str) and collection_id.strip():
            query += " AND collection_id = ?"
            params.append(collection_id.strip())

        if isinstance(channel_type, str) and channel_type.strip():
            query += " AND channel_type = ?"
            params.append(channel_type.strip().lower())

        query += " ORDER BY COALESCE(next_retry_at, created_at) ASC, created_at ASC LIMIT ?"
        params.append(normalized_limit)

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [self._row_to_notification_channel_delivery(row) for row in rows]

    def list_recent_notification_channel_delivery_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    d.delivery_id,
                    d.channel_id,
                    d.channel_type,
                    COALESCE(c.name, '') AS channel_name,
                    d.notification_id,
                    d.collection_id,
                    d.error_message,
                    d.attempt_count,
                    d.max_attempts,
                    d.is_test,
                    d.created_at,
                    d.last_attempt_at
                FROM sequence_notification_channel_deliveries d
                LEFT JOIN sequence_notification_channels c
                    ON c.channel_id = d.channel_id
                WHERE d.delivery_status = 'failed'
                    AND d.error_message IS NOT NULL
                    AND TRIM(d.error_message) <> ''
                ORDER BY COALESCE(d.last_attempt_at, d.created_at) DESC, d.created_at DESC
                LIMIT ?
                """,
                (normalized_limit,),
            ).fetchall()

        errors: List[Dict[str, Any]] = []
        for row in rows:
            errors.append(
                {
                    "delivery_id": str(row["delivery_id"] or ""),
                    "channel_id": str(row["channel_id"] or ""),
                    "channel_type": str(row["channel_type"] or "webhook"),
                    "channel_name": str(row["channel_name"] or ""),
                    "notification_id": str(row["notification_id"] or ""),
                    "collection_id": str(row["collection_id"] or ""),
                    "error_message": str(row["error_message"] or ""),
                    "attempt_count": int(row["attempt_count"] or 0),
                    "max_attempts": int(row["max_attempts"] or 0),
                    "is_test": bool(int(row["is_test"] or 0)),
                    "created_at": str(row["created_at"] or ""),
                    "last_attempt_at": str(row["last_attempt_at"]) if row["last_attempt_at"] is not None else None,
                }
            )

        return errors

    def list_alert_routing_rules(
        self,
        limit: int = 100,
        include_disabled: bool = True,
        target_channel_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))
        query = """
            SELECT
                rule_id,
                name,
                is_enabled,
                target_channel_id,
                target_channel_kind,
                match_types,
                min_severity,
                match_collection_id,
                match_health_status,
                created_at,
                updated_at
            FROM sequence_alert_routing_rules
        """

        where_clauses: List[str] = []
        params: List[Any] = []

        if not include_disabled:
            where_clauses.append("is_enabled = 1")

        if isinstance(target_channel_id, str) and target_channel_id.strip():
            where_clauses.append("target_channel_id = ?")
            params.append(target_channel_id.strip())

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY updated_at DESC LIMIT ?"
        params.append(normalized_limit)

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [self._row_to_alert_routing_rule(row) for row in rows]

    def get_alert_routing_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    rule_id,
                    name,
                    is_enabled,
                    target_channel_id,
                    target_channel_kind,
                    match_types,
                    min_severity,
                    match_collection_id,
                    match_health_status,
                    created_at,
                    updated_at
                FROM sequence_alert_routing_rules
                WHERE rule_id = ?
                """,
                (rule_id,),
            ).fetchone()

        return self._row_to_alert_routing_rule(row) if row else None

    def create_alert_routing_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sequence_alert_routing_rules (
                    rule_id,
                    name,
                    is_enabled,
                    target_channel_id,
                    target_channel_kind,
                    match_types,
                    min_severity,
                    match_collection_id,
                    match_health_status,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(rule_data.get("rule_id") or ""),
                    str(rule_data.get("name") or ""),
                    1 if bool(rule_data.get("is_enabled", True)) else 0,
                    str(rule_data.get("target_channel_id") or ""),
                    str(rule_data.get("target_channel_kind") or "notification_channel"),
                    json.dumps(rule_data.get("match_types", []), ensure_ascii=False),
                    str(rule_data.get("min_severity") or "info"),
                    str(rule_data.get("match_collection_id"))
                    if rule_data.get("match_collection_id") is not None
                    else None,
                    str(rule_data.get("match_health_status"))
                    if rule_data.get("match_health_status") is not None
                    else None,
                    str(rule_data.get("created_at") or ""),
                    str(rule_data.get("updated_at") or ""),
                ),
            )
            connection.commit()

        persisted = self.get_alert_routing_rule(str(rule_data.get("rule_id") or ""))
        return persisted if persisted is not None else rule_data

    def update_alert_routing_rule(self, rule_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = {
            "name",
            "is_enabled",
            "target_channel_id",
            "target_channel_kind",
            "match_types",
            "min_severity",
            "match_collection_id",
            "match_health_status",
            "updated_at",
        }

        set_clauses: List[str] = []
        values: List[Any] = []
        for key, value in updates.items():
            if key not in allowed_fields:
                continue

            set_clauses.append(f"{key} = ?")
            if key == "is_enabled":
                values.append(1 if bool(value) else 0)
            elif key == "match_types":
                values.append(json.dumps(value if isinstance(value, list) else [], ensure_ascii=False))
            elif key in {"match_collection_id", "match_health_status"}:
                values.append(str(value) if value is not None else None)
            else:
                values.append(str(value or ""))

        if not set_clauses:
            return self.get_alert_routing_rule(rule_id)

        values.append(rule_id)
        with self._connect() as connection:
            cursor = connection.execute(
                f"""
                UPDATE sequence_alert_routing_rules
                SET {", ".join(set_clauses)}
                WHERE rule_id = ?
                """,
                tuple(values),
            )
            connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_alert_routing_rule(rule_id)

    def delete_alert_routing_rule(self, rule_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                DELETE FROM sequence_alert_routing_rules
                WHERE rule_id = ?
                """,
                (rule_id,),
            )
            connection.commit()

        return cursor.rowcount > 0

    def list_notifications(
        self,
        limit: int = 50,
        collection_id: Optional[str] = None,
        is_read: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 200))
        query = """
            SELECT
                notification_id,
                collection_id,
                type,
                severity,
                message,
                created_at,
                is_read
            FROM sequence_collection_notifications
        """

        where_clauses: List[str] = []
        params: List[Any] = []

        if isinstance(collection_id, str) and collection_id.strip():
            where_clauses.append("collection_id = ?")
            params.append(collection_id.strip())

        if isinstance(is_read, bool):
            where_clauses.append("is_read = ?")
            params.append(1 if is_read else 0)

        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)

        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(normalized_limit)

        with self._connect() as connection:
            rows = connection.execute(query, tuple(params)).fetchall()

        return [self._row_to_notification(row) for row in rows]

    def get_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    notification_id,
                    collection_id,
                    type,
                    severity,
                    message,
                    created_at,
                    is_read
                FROM sequence_collection_notifications
                WHERE notification_id = ?
                """,
                (notification_id,),
            ).fetchone()

        return self._row_to_notification(row) if row else None

    def update_notification_read(self, notification_id: str, is_read: bool) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE sequence_collection_notifications
                SET is_read = ?
                WHERE notification_id = ?
                """,
                (1 if is_read else 0, notification_id),
            )
            connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_notification(notification_id)

    def get_collection_notification_state(self, collection_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    collection_id,
                    last_health_status,
                    missing_best_active,
                    pending_review_high_active,
                    operational_risk_active,
                    updated_at
                FROM sequence_collection_notification_state
                WHERE collection_id = ?
                """,
                (collection_id,),
            ).fetchone()

        if row is None:
            return None

        return {
            "collection_id": str(row["collection_id"] or ""),
            "last_health_status": str(row["last_health_status"] or "green"),
            "missing_best_active": bool(int(row["missing_best_active"] or 0)),
            "pending_review_high_active": bool(int(row["pending_review_high_active"] or 0)),
            "operational_risk_active": bool(int(row["operational_risk_active"] or 0)),
            "updated_at": str(row["updated_at"] or ""),
        }

    def upsert_collection_notification_state(self, collection_id: str, state_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "collection_id": collection_id,
            "last_health_status": str(state_data.get("last_health_status") or "green"),
            "missing_best_active": bool(state_data.get("missing_best_active", False)),
            "pending_review_high_active": bool(state_data.get("pending_review_high_active", False)),
            "operational_risk_active": bool(state_data.get("operational_risk_active", False)),
            "updated_at": str(state_data.get("updated_at") or ""),
        }

        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO sequence_collection_notification_state (
                    collection_id,
                    last_health_status,
                    missing_best_active,
                    pending_review_high_active,
                    operational_risk_active,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(collection_id) DO UPDATE SET
                    last_health_status = excluded.last_health_status,
                    missing_best_active = excluded.missing_best_active,
                    pending_review_high_active = excluded.pending_review_high_active,
                    operational_risk_active = excluded.operational_risk_active,
                    updated_at = excluded.updated_at
                """,
                (
                    payload["collection_id"],
                    payload["last_health_status"],
                    1 if payload["missing_best_active"] else 0,
                    1 if payload["pending_review_high_active"] else 0,
                    1 if payload["operational_risk_active"] else 0,
                    payload["updated_at"],
                ),
            )
            connection.commit()

        return payload

    def get_run(self, request_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT * FROM sequence_plan_runs
                WHERE request_id = ?
                """,
                (request_id,),
            ).fetchone()

        return self._row_to_run(row) if row else None

    def list_runs(self, limit: Optional[int] = 20) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM sequence_plan_runs
            ORDER BY updated_at DESC
        """
        parameters: tuple[Any, ...] = ()

        if limit is not None:
            normalized_limit = max(1, min(int(limit), 200))
            query += " LIMIT ?"
            parameters = (normalized_limit,)

        with self._connect() as connection:
            rows = connection.execute(query, parameters).fetchall()

        return [self._row_to_run(row) for row in rows]

    def update_run(self, request_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = {
            "updated_at",
            "request_payload",
            "plan",
            "prompt_comparisons",
            "prompt_comparison_metrics",
            "created_jobs",
            "job_ids",
            "shot_job_links",
            "job_count",
            "is_favorite",
            "tags",
            "note",
            "review_status",
            "review_note",
            "reviewed_at",
        }

        set_clauses = []
        values = []

        for key, value in updates.items():
            if key not in allowed_fields:
                continue

            set_clauses.append(f"{key} = ?")

            if key in {"request_payload", "plan", "prompt_comparisons", "prompt_comparison_metrics", "created_jobs", "job_ids", "shot_job_links"}:
                values.append(json.dumps(value, ensure_ascii=False))
            elif key == "job_count":
                values.append(int(value))
            elif key == "is_favorite":
                values.append(1 if bool(value) else 0)
            elif key == "tags":
                values.append(json.dumps(value if isinstance(value, list) else [], ensure_ascii=False))
            elif key == "note":
                values.append(str(value or ""))
            elif key == "review_status":
                values.append(str(value or "pending_review"))
            elif key == "review_note":
                values.append(str(value or ""))
            elif key == "reviewed_at":
                values.append(str(value) if value else None)
            else:
                values.append(value)

        if not set_clauses:
            return self.get_run(request_id)

        values.append(request_id)

        with self._connect() as connection:
            cursor = connection.execute(
                f"""
                UPDATE sequence_plan_runs
                SET {", ".join(set_clauses)}
                WHERE request_id = ?
                """,
                tuple(values),
            )
            connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_run(request_id)

    def _row_to_collection(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "collection_id": str(row["collection_id"]),
            "name": str(row["name"] or ""),
            "description": str(row["description"] or ""),
            "editorial_note": str(row["editorial_note"] or ""),
            "color": str(row["color"] or ""),
            "is_archived": bool(int(row["is_archived"] or 0)),
            "best_request_id": str(row["best_request_id"] or "") or None,
            "created_at": str(row["created_at"] or ""),
            "updated_at": str(row["updated_at"] or ""),
            "item_count": int(row["item_count"] or 0) if "item_count" in row.keys() else 0,
            "highlighted_count": int(row["highlighted_count"] or 0) if "highlighted_count" in row.keys() else 0,
        }

    def _row_to_collection_item(self, row: sqlite3.Row) -> Dict[str, Any]:
        return {
            "collection_id": str(row["collection_id"]),
            "request_id": str(row["request_id"]),
            "is_highlighted": bool(int(row["is_highlighted"] or 0)),
            "added_at": str(row["added_at"] or ""),
        }

    def create_collection(self, collection_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute(
                """
                INSERT INTO sequence_execution_collections (
                    collection_id,
                    name,
                    description,
                    editorial_note,
                    color,
                    is_archived,
                    best_request_id,
                    created_at,
                    updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    collection_data["collection_id"],
                    collection_data["name"],
                    str(collection_data.get("description") or ""),
                    str(collection_data.get("editorial_note") or ""),
                    str(collection_data.get("color") or ""),
                    1 if bool(collection_data.get("is_archived", False)) else 0,
                    str(collection_data.get("best_request_id") or "") or None,
                    collection_data["created_at"],
                    collection_data["updated_at"],
                ),
            )
            connection.commit()

        created = self.get_collection(str(collection_data["collection_id"]))
        return created if created is not None else collection_data

    def list_collections(self, limit: int = 100, include_archived: bool = False) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    c.collection_id,
                    c.name,
                    c.description,
                    c.editorial_note,
                    c.color,
                    c.is_archived,
                    c.best_request_id,
                    c.created_at,
                    c.updated_at,
                    COUNT(i.request_id) AS item_count,
                    SUM(CASE WHEN i.is_highlighted = 1 THEN 1 ELSE 0 END) AS highlighted_count
                FROM sequence_execution_collections c
                LEFT JOIN sequence_execution_collection_items i
                    ON c.collection_id = i.collection_id
                WHERE (? = 1 OR c.is_archived = 0)
                GROUP BY
                    c.collection_id,
                    c.name,
                    c.description,
                    c.editorial_note,
                    c.color,
                    c.is_archived,
                    c.best_request_id,
                    c.created_at,
                    c.updated_at
                ORDER BY c.updated_at DESC
                LIMIT ?
                """,
                (1 if include_archived else 0, normalized_limit),
            ).fetchall()

        return [self._row_to_collection(row) for row in rows]

    def get_collection(self, collection_id: str) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT
                    c.collection_id,
                    c.name,
                    c.description,
                    c.editorial_note,
                    c.color,
                    c.is_archived,
                    c.best_request_id,
                    c.created_at,
                    c.updated_at,
                    COUNT(i.request_id) AS item_count,
                    SUM(CASE WHEN i.is_highlighted = 1 THEN 1 ELSE 0 END) AS highlighted_count
                FROM sequence_execution_collections c
                LEFT JOIN sequence_execution_collection_items i
                    ON c.collection_id = i.collection_id
                WHERE c.collection_id = ?
                GROUP BY
                    c.collection_id,
                    c.name,
                    c.description,
                    c.editorial_note,
                    c.color,
                    c.is_archived,
                    c.best_request_id,
                    c.created_at,
                    c.updated_at
                """,
                (collection_id,),
            ).fetchone()

        return self._row_to_collection(row) if row else None

    def update_collection(self, collection_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = {
            "name",
            "description",
            "editorial_note",
            "color",
            "is_archived",
            "best_request_id",
            "updated_at",
        }

        set_clauses = []
        values = []
        for key, value in updates.items():
            if key not in allowed_fields:
                continue

            set_clauses.append(f"{key} = ?")
            if key == "is_archived":
                values.append(1 if bool(value) else 0)
            elif key == "best_request_id":
                values.append(str(value or "") or None)
            else:
                values.append(str(value or ""))

        if not set_clauses:
            return self.get_collection(collection_id)

        values.append(collection_id)

        with self._connect() as connection:
            cursor = connection.execute(
                f"""
                UPDATE sequence_execution_collections
                SET {", ".join(set_clauses)}
                WHERE collection_id = ?
                """,
                tuple(values),
            )
            connection.commit()

        if cursor.rowcount == 0:
            return None

        return self.get_collection(collection_id)

    def delete_collection(self, collection_id: str) -> bool:
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            cursor = connection.execute(
                """
                DELETE FROM sequence_execution_collections
                WHERE collection_id = ?
                """,
                (collection_id,),
            )
            connection.commit()

        return cursor.rowcount > 0

    def list_collection_items(self, collection_id: str) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT collection_id, request_id, is_highlighted, added_at
                FROM sequence_execution_collection_items
                WHERE collection_id = ?
                ORDER BY added_at DESC
                """,
                (collection_id,),
            ).fetchall()

        return [self._row_to_collection_item(row) for row in rows]

    def add_collection_items(
        self,
        collection_id: str,
        request_ids: List[str],
        added_at: str,
        updated_at: str,
    ) -> Dict[str, int]:
        inserted = 0

        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            for request_id in request_ids:
                cursor = connection.execute(
                    """
                    INSERT OR IGNORE INTO sequence_execution_collection_items (
                        collection_id,
                        request_id,
                        is_highlighted,
                        added_at
                    ) VALUES (?, ?, 0, ?)
                    """,
                    (collection_id, request_id, added_at),
                )
                if cursor.rowcount > 0:
                    inserted += 1

            connection.execute(
                """
                UPDATE sequence_execution_collections
                SET updated_at = ?
                WHERE collection_id = ?
                """,
                (updated_at, collection_id),
            )
            connection.commit()

        return {"inserted": inserted}

    def remove_collection_item(self, collection_id: str, request_id: str, updated_at: str) -> bool:
        with self._connect() as connection:
            connection.execute("PRAGMA foreign_keys = ON")
            cursor = connection.execute(
                """
                DELETE FROM sequence_execution_collection_items
                WHERE collection_id = ? AND request_id = ?
                """,
                (collection_id, request_id),
            )

            if cursor.rowcount > 0:
                connection.execute(
                    """
                    UPDATE sequence_execution_collections
                    SET
                        updated_at = ?,
                        best_request_id = CASE
                            WHEN best_request_id = ? THEN NULL
                            ELSE best_request_id
                        END
                    WHERE collection_id = ?
                    """,
                    (updated_at, request_id, collection_id),
                )

            connection.commit()

        return cursor.rowcount > 0

    def set_collection_item_highlight(
        self,
        collection_id: str,
        request_id: str,
        is_highlighted: bool,
        updated_at: str,
    ) -> Optional[Dict[str, Any]]:
        with self._connect() as connection:
            cursor = connection.execute(
                """
                UPDATE sequence_execution_collection_items
                SET is_highlighted = ?
                WHERE collection_id = ? AND request_id = ?
                """,
                (1 if is_highlighted else 0, collection_id, request_id),
            )

            if cursor.rowcount > 0:
                connection.execute(
                    """
                    UPDATE sequence_execution_collections
                    SET updated_at = ?
                    WHERE collection_id = ?
                    """,
                    (updated_at, collection_id),
                )

            connection.commit()

        if cursor.rowcount == 0:
            return None

        items = self.list_collection_items(collection_id)
        for item in items:
            if item["request_id"] == request_id:
                return item

        return None

    def list_collections_for_request(self, request_id: str) -> List[Dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    c.collection_id,
                    c.name,
                    c.best_request_id,
                    i.is_highlighted,
                    i.added_at
                FROM sequence_execution_collection_items i
                INNER JOIN sequence_execution_collections c
                    ON c.collection_id = i.collection_id
                WHERE i.request_id = ?
                ORDER BY c.updated_at DESC
                """,
                (request_id,),
            ).fetchall()

        return [
            {
                "collection_id": str(row["collection_id"]),
                "name": str(row["name"] or ""),
                "is_highlighted": bool(int(row["is_highlighted"] or 0)),
                "is_best": bool(str(row["best_request_id"] or "") == request_id),
                "added_at": str(row["added_at"] or ""),
            }
            for row in rows
        ]
