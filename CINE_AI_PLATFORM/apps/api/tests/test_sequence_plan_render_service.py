from __future__ import annotations

import unittest
import hashlib
import hmac
import json
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.error import URLError
from unittest.mock import patch

from src.schemas.sequence_plan import SequencePlanRequest
from src.services.sequence_plan_render_service import (
    WEBHOOK_TEST_COLLECTION_ID,
    SequenceAlertRoutingRuleNotFoundError,
    SequenceCollectionNotFoundError,
    SequenceNotificationNotFoundError,
    SequencePlanRenderService,
    SequencePlanRunNotFoundError,
    SequenceShotNotFoundError,
    SequenceWebhookDeliveryNotFoundError,
)
from src.services.sequence_planner_service import SequencePlannerService


class StubRenderJobsService:
    def __init__(self) -> None:
        self.calls: List[Dict[str, Any]] = []
        self.jobs: Dict[str, Dict[str, Any]] = {}

    def create_job_from_client_payload(
        self,
        request_payload: Dict[str, Any],
        render_context: Optional[Any] = None,
        parent_job_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        index = len(self.calls) + 1
        now = "2026-01-01T00:00:00+00:00"
        payload = request_payload if isinstance(request_payload, dict) else {}

        self.calls.append(
            {
                "request_payload": payload,
                "render_context": render_context,
                "parent_job_id": parent_job_id,
            }
        )

        job = {
            "job_id": f"job_{index:03d}",
            "created_at": now,
            "updated_at": now,
            "status": "queued",
            "request_payload": payload,
            "parent_job_id": parent_job_id,
            "comfyui_prompt_id": None,
            "result": None,
            "error": None,
            "duration_ms": None,
        }
        self.jobs[job["job_id"]] = deepcopy(job)
        return deepcopy(job)

    def execute_job(self, job_id: str) -> None:
        return None

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.jobs.get(job_id)
        if job is None:
            return None
        return deepcopy(job)

    def set_job_status(self, job_id: str, status: str) -> None:
        if job_id in self.jobs:
            self.jobs[job_id]["status"] = status


class FakeWebhookHTTPResponse:
    def __init__(self, status_code: int = 200, body: str = "ok") -> None:
        self._status_code = status_code
        self._body = body.encode("utf-8")

    def __enter__(self) -> "FakeWebhookHTTPResponse":
        return self

    def __exit__(self, exc_type, exc, traceback) -> bool:
        return False

    def getcode(self) -> int:
        return self._status_code

    def read(self) -> bytes:
        return self._body


class InMemorySequencePlanRunsRepository:
    def __init__(self) -> None:
        self._records: Dict[str, Dict[str, Any]] = {}
        self._collections: Dict[str, Dict[str, Any]] = {}
        self._collection_items: Dict[str, Dict[str, Dict[str, Any]]] = {}
        self._review_history: Dict[str, List[Dict[str, Any]]] = {}
        self._notifications: Dict[str, Dict[str, Any]] = {}
        self._notification_state: Dict[str, Dict[str, Any]] = {}
        self._webhooks: Dict[str, Dict[str, Any]] = {}
        self._webhook_deliveries: Dict[str, Dict[str, Any]] = {}
        self._notification_channels: Dict[str, Dict[str, Any]] = {}
        self._notification_channel_deliveries: Dict[str, Dict[str, Any]] = {}
        self._alert_routing_rules: Dict[str, Dict[str, Any]] = {}
        self._notification_preferences: Dict[str, Any] = {
            "notifications_enabled": True,
            "min_severity": "info",
            "enabled_types": [
                "HEALTH_STATUS_CHANGED",
                "COLLECTION_ENTERED_RED",
                "MISSING_BEST_EXECUTION",
                "PENDING_REVIEW_HIGH",
                "OPERATIONAL_FAILURE_THRESHOLD",
            ],
            "show_only_unread_by_default": False,
            "updated_at": "",
        }

    def create(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        self._records[str(run_data["request_id"])] = deepcopy(run_data)
        return deepcopy(run_data)

    def get(self, request_id: str) -> Optional[Dict[str, Any]]:
        record = self._records.get(request_id)
        if record is None:
            return None
        return deepcopy(record)

    def update(self, request_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self._records.get(request_id)
        if current is None:
            return None

        merged = {**current, **deepcopy(updates)}
        self._records[request_id] = merged
        return deepcopy(merged)

    def list_recent(self, limit: Optional[int] = 20) -> List[Dict[str, Any]]:
        values = [deepcopy(value) for value in self._records.values()]
        values.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        if limit is None:
            return values

        normalized_limit = max(1, min(int(limit), 200))
        return values[:normalized_limit]

    def create_review_history_entry(self, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        request_id = str(entry_data.get("request_id") or "")
        bucket = self._review_history.setdefault(request_id, [])
        bucket.append(deepcopy(entry_data))
        return deepcopy(entry_data)

    def list_review_history_for_request(self, request_id: str, limit: Optional[int] = 200) -> List[Dict[str, Any]]:
        values = [deepcopy(item) for item in self._review_history.get(request_id, [])]
        values.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        if limit is None:
            return values

        normalized_limit = max(1, min(int(limit), 500))
        return values[:normalized_limit]

    def get_review_history_summary(self, request_id: str) -> Dict[str, Any]:
        items = self._review_history.get(request_id, [])
        if not items:
            return {"history_count": 0, "latest_created_at": None}

        latest = max(str(item.get("created_at") or "") for item in items)
        return {
            "history_count": len(items),
            "latest_created_at": latest or None,
        }

    def create_notification(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        notification_id = str(notification_data.get("notification_id") or "")
        self._notifications[notification_id] = deepcopy(notification_data)
        return deepcopy(notification_data)

    def list_notifications(
        self,
        limit: int = 50,
        collection_id: Optional[str] = None,
        is_read: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        values = [deepcopy(item) for item in self._notifications.values()]

        if collection_id is not None:
            values = [item for item in values if str(item.get("collection_id") or "") == collection_id]

        if isinstance(is_read, bool):
            values = [item for item in values if bool(item.get("is_read", False)) == is_read]

        values.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        normalized_limit = max(1, min(int(limit), 200))
        return values[:normalized_limit]

    def get_notification(self, notification_id: str) -> Optional[Dict[str, Any]]:
        notification = self._notifications.get(notification_id)
        if notification is None:
            return None
        return deepcopy(notification)

    def update_notification_read(self, notification_id: str, is_read: bool) -> Optional[Dict[str, Any]]:
        notification = self._notifications.get(notification_id)
        if notification is None:
            return None

        notification["is_read"] = bool(is_read)
        return deepcopy(notification)

    def get_collection_notification_state(self, collection_id: str) -> Optional[Dict[str, Any]]:
        state = self._notification_state.get(collection_id)
        if state is None:
            return None
        return deepcopy(state)

    def upsert_collection_notification_state(self, collection_id: str, state_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "collection_id": collection_id,
            "last_health_status": str(state_data.get("last_health_status") or "green"),
            "missing_best_active": bool(state_data.get("missing_best_active", False)),
            "pending_review_high_active": bool(state_data.get("pending_review_high_active", False)),
            "operational_risk_active": bool(state_data.get("operational_risk_active", False)),
            "updated_at": str(state_data.get("updated_at") or ""),
        }
        self._notification_state[collection_id] = payload
        return deepcopy(payload)

    def get_notification_preferences(self) -> Dict[str, Any]:
        return deepcopy(self._notification_preferences)

    def upsert_notification_preferences(self, preferences_data: Dict[str, Any]) -> Dict[str, Any]:
        updated = {
            **self._notification_preferences,
            **deepcopy(preferences_data),
        }
        if not isinstance(updated.get("enabled_types"), list):
            updated["enabled_types"] = []
        self._notification_preferences = updated
        return deepcopy(self._notification_preferences)

    def list_webhooks(self, limit: int = 100, include_disabled: bool = True) -> List[Dict[str, Any]]:
        values = [deepcopy(item) for item in self._webhooks.values()]
        if not include_disabled:
            values = [item for item in values if bool(item.get("is_enabled", True))]
        values.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        normalized_limit = max(1, min(int(limit), 500))
        return values[:normalized_limit]

    def get_webhook(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        webhook = self._webhooks.get(webhook_id)
        if webhook is None:
            return None
        return deepcopy(webhook)

    def create_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        webhook_id = str(webhook_data.get("webhook_id") or "")
        payload = deepcopy(webhook_data)
        payload.setdefault("payload_template_mode", "default")
        payload.setdefault("payload_template", None)
        self._webhooks[webhook_id] = payload
        return deepcopy(payload)

    def update_webhook(self, webhook_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        webhook = self._webhooks.get(webhook_id)
        if webhook is None:
            return None
        merged = {**webhook, **deepcopy(updates)}
        self._webhooks[webhook_id] = merged
        return deepcopy(merged)

    def create_webhook_delivery(self, delivery_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = deepcopy(delivery_data)
        payload.setdefault("attempt_count", 1)
        payload.setdefault("max_attempts", 4)
        payload.setdefault("last_attempt_at", payload.get("created_at"))
        payload.setdefault("next_retry_at", None)
        payload.setdefault("final_failure_at", None)
        payload.setdefault("is_test", False)
        payload.setdefault("template_mode", "default")
        payload.setdefault("auth_mode", "none")
        payload.setdefault("request_headers", {})
        payload.setdefault("signature_timestamp", None)
        payload.setdefault("routing_rule_id", None)
        payload.setdefault("routing_rule_name", None)
        delivery_id = str(delivery_data.get("delivery_id") or "")
        self._webhook_deliveries[delivery_id] = payload
        return deepcopy(payload)

    def get_webhook_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        delivery = self._webhook_deliveries.get(delivery_id)
        if delivery is None:
            return None
        return deepcopy(delivery)

    def update_webhook_delivery(self, delivery_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        delivery = self._webhook_deliveries.get(delivery_id)
        if delivery is None:
            return None
        merged = {**delivery, **deepcopy(updates)}
        self._webhook_deliveries[delivery_id] = merged
        return deepcopy(merged)

    def list_webhook_deliveries(
        self,
        limit: int = 100,
        webhook_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        notification_id: Optional[str] = None,
        is_test: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        values = [deepcopy(item) for item in self._webhook_deliveries.values()]

        if webhook_id is not None:
            values = [item for item in values if str(item.get("webhook_id") or "") == webhook_id]
        if collection_id is not None:
            values = [item for item in values if str(item.get("collection_id") or "") == collection_id]
        if notification_id is not None:
            values = [item for item in values if str(item.get("notification_id") or "") == notification_id]
        if isinstance(is_test, bool):
            values = [item for item in values if bool(item.get("is_test", False)) == is_test]

        values.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        normalized_limit = max(1, min(int(limit), 500))
        return values[:normalized_limit]

    def list_webhook_deliveries_pending_retry(
        self,
        due_before: str,
        limit: int = 100,
        webhook_id: Optional[str] = None,
        collection_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        due_dt = self._parse_iso(due_before)
        values = [deepcopy(item) for item in self._webhook_deliveries.values()]

        filtered: List[Dict[str, Any]] = []
        for item in values:
            if str(item.get("delivery_status") or "").strip().lower() != "failed":
                continue

            attempt_count = int(item.get("attempt_count") or 0)
            max_attempts = max(1, int(item.get("max_attempts") or 1))
            if attempt_count >= max_attempts:
                continue
            if item.get("final_failure_at") is not None:
                continue

            next_retry_at = item.get("next_retry_at")
            if next_retry_at is not None and due_dt is not None:
                next_retry_dt = self._parse_iso(str(next_retry_at))
                if next_retry_dt is not None and next_retry_dt > due_dt:
                    continue

            if webhook_id is not None and str(item.get("webhook_id") or "") != webhook_id:
                continue
            if collection_id is not None and str(item.get("collection_id") or "") != collection_id:
                continue

            filtered.append(item)

        filtered.sort(
            key=lambda entry: (
                str(entry.get("next_retry_at") or entry.get("created_at") or ""),
                str(entry.get("created_at") or ""),
            )
        )
        normalized_limit = max(1, min(int(limit), 500))
        return filtered[:normalized_limit]

    def list_webhook_delivery_stats_by_webhook(self) -> List[Dict[str, Any]]:
        stats: List[Dict[str, Any]] = []
        for webhook in self._webhooks.values():
            webhook_id = str(webhook.get("webhook_id") or "")
            deliveries = [
                item
                for item in self._webhook_deliveries.values()
                if str(item.get("webhook_id") or "") == webhook_id
            ]

            total_deliveries = len(deliveries)
            sent_deliveries = sum(
                1 for item in deliveries if str(item.get("delivery_status") or "").strip().lower() == "sent"
            )
            failed_deliveries = sum(
                1 for item in deliveries if str(item.get("delivery_status") or "").strip().lower() == "failed"
            )
            pending_deliveries = sum(
                1 for item in deliveries if str(item.get("delivery_status") or "").strip().lower() == "pending"
            )
            exhausted_deliveries = sum(
                1
                for item in deliveries
                if str(item.get("delivery_status") or "").strip().lower() == "failed"
                and (
                    item.get("final_failure_at") is not None
                    or int(item.get("attempt_count") or 0) >= max(1, int(item.get("max_attempts") or 1))
                )
            )
            total_retries = sum(max(0, int(item.get("attempt_count") or 0) - 1) for item in deliveries)

            last_delivery_at = None
            for item in deliveries:
                candidate = str(item.get("last_attempt_at") or item.get("created_at") or "")
                if not candidate:
                    continue
                if last_delivery_at is None or candidate > last_delivery_at:
                    last_delivery_at = candidate

            stats.append(
                {
                    "webhook_id": webhook_id,
                    "name": str(webhook.get("name") or ""),
                    "is_enabled": bool(webhook.get("is_enabled", True)),
                    "total_deliveries": total_deliveries,
                    "sent_deliveries": sent_deliveries,
                    "failed_deliveries": failed_deliveries,
                    "pending_deliveries": pending_deliveries,
                    "exhausted_deliveries": exhausted_deliveries,
                    "total_retries": total_retries,
                    "last_delivery_at": last_delivery_at,
                }
            )

        stats.sort(key=lambda item: str(item.get("last_delivery_at") or ""), reverse=True)
        return stats

    def list_recent_webhook_delivery_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))
        errors: List[Dict[str, Any]] = []
        for delivery in self._webhook_deliveries.values():
            status = str(delivery.get("delivery_status") or "").strip().lower()
            if status != "failed":
                continue

            error_message = str(delivery.get("error_message") or "").strip()
            if not error_message:
                continue

            webhook_id = str(delivery.get("webhook_id") or "")
            webhook = self._webhooks.get(webhook_id) or {}
            errors.append(
                {
                    "delivery_id": str(delivery.get("delivery_id") or ""),
                    "webhook_id": webhook_id,
                    "webhook_name": str(webhook.get("name") or ""),
                    "notification_id": str(delivery.get("notification_id") or ""),
                    "collection_id": str(delivery.get("collection_id") or ""),
                    "error_message": error_message,
                    "attempt_count": int(delivery.get("attempt_count") or 0),
                    "max_attempts": int(delivery.get("max_attempts") or 0),
                    "is_test": bool(delivery.get("is_test", False)),
                    "auth_mode": str(delivery.get("auth_mode") or "none"),
                    "template_mode": str(delivery.get("template_mode") or "default"),
                    "created_at": str(delivery.get("created_at") or ""),
                    "last_attempt_at": str(delivery.get("last_attempt_at"))
                    if delivery.get("last_attempt_at") is not None
                    else None,
                }
            )

        errors.sort(
            key=lambda item: (
                str(item.get("last_attempt_at") or item.get("created_at") or ""),
                str(item.get("created_at") or ""),
            ),
            reverse=True,
        )
        return errors[:normalized_limit]

    def list_notification_channels(
        self,
        limit: int = 100,
        include_disabled: bool = True,
        channel_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        values = [deepcopy(item) for item in self._notification_channels.values()]
        if not include_disabled:
            values = [item for item in values if bool(item.get("is_enabled", True))]
        if channel_type is not None:
            normalized_channel_type = str(channel_type or "").strip().lower()
            values = [
                item
                for item in values
                if str(item.get("channel_type") or "").strip().lower() == normalized_channel_type
            ]
        values.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        normalized_limit = max(1, min(int(limit), 500))
        return values[:normalized_limit]

    def get_notification_channel(self, channel_id: str) -> Optional[Dict[str, Any]]:
        channel = self._notification_channels.get(channel_id)
        if channel is None:
            return None
        return deepcopy(channel)

    def create_notification_channel(self, channel_data: Dict[str, Any]) -> Dict[str, Any]:
        channel_id = str(channel_data.get("channel_id") or "")
        payload = deepcopy(channel_data)
        self._notification_channels[channel_id] = payload
        return deepcopy(payload)

    def update_notification_channel(self, channel_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        channel = self._notification_channels.get(channel_id)
        if channel is None:
            return None
        merged = {**channel, **deepcopy(updates)}
        self._notification_channels[channel_id] = merged
        return deepcopy(merged)

    def create_notification_channel_delivery(self, delivery_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = deepcopy(delivery_data)
        payload.setdefault("attempt_count", 0)
        payload.setdefault("max_attempts", 4)
        payload.setdefault("last_attempt_at", None)
        payload.setdefault("next_retry_at", None)
        payload.setdefault("final_failure_at", None)
        payload.setdefault("is_test", False)
        payload.setdefault("response_status_code", None)
        payload.setdefault("response_body", None)
        payload.setdefault("error_message", None)
        payload.setdefault("delivered_at", None)
        payload.setdefault("routing_rule_id", None)
        payload.setdefault("routing_rule_name", None)
        delivery_id = str(delivery_data.get("delivery_id") or "")
        self._notification_channel_deliveries[delivery_id] = payload
        return deepcopy(payload)

    def get_notification_channel_delivery(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        delivery = self._notification_channel_deliveries.get(delivery_id)
        if delivery is None:
            return None
        return deepcopy(delivery)

    def update_notification_channel_delivery(self, delivery_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        delivery = self._notification_channel_deliveries.get(delivery_id)
        if delivery is None:
            return None
        merged = {**delivery, **deepcopy(updates)}
        self._notification_channel_deliveries[delivery_id] = merged
        return deepcopy(merged)

    def list_notification_channel_deliveries(
        self,
        limit: int = 100,
        channel_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        notification_id: Optional[str] = None,
        channel_type: Optional[str] = None,
        is_test: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        values = [deepcopy(item) for item in self._notification_channel_deliveries.values()]

        if channel_id is not None:
            values = [item for item in values if str(item.get("channel_id") or "") == channel_id]
        if collection_id is not None:
            values = [item for item in values if str(item.get("collection_id") or "") == collection_id]
        if notification_id is not None:
            values = [item for item in values if str(item.get("notification_id") or "") == notification_id]
        if channel_type is not None:
            normalized_channel_type = str(channel_type or "").strip().lower()
            values = [
                item
                for item in values
                if str(item.get("channel_type") or "").strip().lower() == normalized_channel_type
            ]
        if isinstance(is_test, bool):
            values = [item for item in values if bool(item.get("is_test", False)) == is_test]

        values.sort(key=lambda item: str(item.get("created_at") or ""), reverse=True)
        normalized_limit = max(1, min(int(limit), 500))
        return values[:normalized_limit]

    def list_notification_channel_deliveries_pending_retry(
        self,
        due_before: str,
        limit: int = 100,
        channel_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        channel_type: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        due_dt = self._parse_iso(due_before)
        values = [deepcopy(item) for item in self._notification_channel_deliveries.values()]

        filtered: List[Dict[str, Any]] = []
        for item in values:
            if str(item.get("delivery_status") or "").strip().lower() != "failed":
                continue

            attempt_count = int(item.get("attempt_count") or 0)
            max_attempts = max(1, int(item.get("max_attempts") or 1))
            if attempt_count >= max_attempts:
                continue
            if item.get("final_failure_at") is not None:
                continue

            next_retry_at = item.get("next_retry_at")
            if next_retry_at is not None and due_dt is not None:
                next_retry_dt = self._parse_iso(str(next_retry_at))
                if next_retry_dt is not None and next_retry_dt > due_dt:
                    continue

            if channel_id is not None and str(item.get("channel_id") or "") != channel_id:
                continue
            if collection_id is not None and str(item.get("collection_id") or "") != collection_id:
                continue
            if channel_type is not None:
                normalized_channel_type = str(channel_type or "").strip().lower()
                if str(item.get("channel_type") or "").strip().lower() != normalized_channel_type:
                    continue

            filtered.append(item)

        filtered.sort(
            key=lambda entry: (
                str(entry.get("next_retry_at") or entry.get("created_at") or ""),
                str(entry.get("created_at") or ""),
            )
        )
        normalized_limit = max(1, min(int(limit), 500))
        return filtered[:normalized_limit]

    def list_recent_notification_channel_delivery_errors(self, limit: int = 10) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 500))
        errors: List[Dict[str, Any]] = []
        for delivery in self._notification_channel_deliveries.values():
            status = str(delivery.get("delivery_status") or "").strip().lower()
            if status != "failed":
                continue

            error_message = str(delivery.get("error_message") or "").strip()
            if not error_message:
                continue

            channel_id = str(delivery.get("channel_id") or "")
            channel = self._notification_channels.get(channel_id) or {}
            errors.append(
                {
                    "delivery_id": str(delivery.get("delivery_id") or ""),
                    "channel_id": channel_id,
                    "channel_type": str(delivery.get("channel_type") or "webhook"),
                    "channel_name": str(channel.get("name") or ""),
                    "notification_id": str(delivery.get("notification_id") or ""),
                    "collection_id": str(delivery.get("collection_id") or ""),
                    "error_message": error_message,
                    "attempt_count": int(delivery.get("attempt_count") or 0),
                    "max_attempts": int(delivery.get("max_attempts") or 0),
                    "is_test": bool(delivery.get("is_test", False)),
                    "created_at": str(delivery.get("created_at") or ""),
                    "last_attempt_at": str(delivery.get("last_attempt_at"))
                    if delivery.get("last_attempt_at") is not None
                    else None,
                }
            )

        errors.sort(
            key=lambda item: (
                str(item.get("last_attempt_at") or item.get("created_at") or ""),
                str(item.get("created_at") or ""),
            ),
            reverse=True,
        )
        return errors[:normalized_limit]

    def list_alert_routing_rules(
        self,
        limit: int = 100,
        include_disabled: bool = True,
        target_channel_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        values = [deepcopy(item) for item in self._alert_routing_rules.values()]
        if not include_disabled:
            values = [item for item in values if bool(item.get("is_enabled", True))]
        if target_channel_id is not None:
            values = [item for item in values if str(item.get("target_channel_id") or "") == target_channel_id]
        values.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        normalized_limit = max(1, min(int(limit), 500))
        return values[:normalized_limit]

    def get_alert_routing_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        rule = self._alert_routing_rules.get(rule_id)
        if rule is None:
            return None
        return deepcopy(rule)

    def create_alert_routing_rule(self, rule_data: Dict[str, Any]) -> Dict[str, Any]:
        rule_id = str(rule_data.get("rule_id") or "")
        payload = deepcopy(rule_data)
        payload.setdefault("target_channel_kind", "notification_channel")
        payload.setdefault("match_types", [])
        payload.setdefault("match_collection_id", None)
        payload.setdefault("match_health_status", None)
        self._alert_routing_rules[rule_id] = payload
        return deepcopy(payload)

    def update_alert_routing_rule(self, rule_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        rule = self._alert_routing_rules.get(rule_id)
        if rule is None:
            return None
        merged = {**rule, **deepcopy(updates)}
        self._alert_routing_rules[rule_id] = merged
        return deepcopy(merged)

    def delete_alert_routing_rule(self, rule_id: str) -> bool:
        return self._alert_routing_rules.pop(rule_id, None) is not None

    def _parse_iso(self, value: str) -> Optional[datetime]:
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    def create_collection(self, collection_data: Dict[str, Any]) -> Dict[str, Any]:
        collection_id = str(collection_data["collection_id"])
        payload = {
            **deepcopy(collection_data),
            "best_request_id": collection_data.get("best_request_id"),
            "item_count": 0,
            "highlighted_count": 0,
        }
        self._collections[collection_id] = payload
        if collection_id not in self._collection_items:
            self._collection_items[collection_id] = {}
        return deepcopy(payload)

    def list_collections(self, limit: int = 100, include_archived: bool = False) -> List[Dict[str, Any]]:
        values: List[Dict[str, Any]] = []
        for collection in self._collections.values():
            if not include_archived and bool(collection.get("is_archived", False)):
                continue
            values.append(deepcopy(collection))

        values.sort(key=lambda item: str(item.get("updated_at") or ""), reverse=True)
        normalized_limit = max(1, min(int(limit), 500))
        return values[:normalized_limit]

    def get_collection(self, collection_id: str) -> Optional[Dict[str, Any]]:
        collection = self._collections.get(collection_id)
        if collection is None:
            return None
        return deepcopy(collection)

    def update_collection(self, collection_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        current = self._collections.get(collection_id)
        if current is None:
            return None

        merged = {**current, **deepcopy(updates)}
        self._collections[collection_id] = merged
        return deepcopy(merged)

    def delete_collection(self, collection_id: str) -> bool:
        existed = collection_id in self._collections
        self._collections.pop(collection_id, None)
        self._collection_items.pop(collection_id, None)
        self._notification_state.pop(collection_id, None)
        for notification_id in [
            key
            for key, value in self._notifications.items()
            if str(value.get("collection_id") or "") == collection_id
        ]:
            self._notifications.pop(notification_id, None)

        self._webhook_deliveries = {
            key: value
            for key, value in self._webhook_deliveries.items()
            if str(value.get("collection_id") or "") != collection_id
        }
        self._notification_channel_deliveries = {
            key: value
            for key, value in self._notification_channel_deliveries.items()
            if str(value.get("collection_id") or "") != collection_id
        }
        return existed

    def list_collection_items(self, collection_id: str) -> List[Dict[str, Any]]:
        values = list((self._collection_items.get(collection_id) or {}).values())
        values.sort(key=lambda item: str(item.get("added_at") or ""), reverse=True)
        return [deepcopy(value) for value in values]

    def _refresh_collection_counts(self, collection_id: str) -> None:
        collection = self._collections.get(collection_id)
        if collection is None:
            return

        items = list((self._collection_items.get(collection_id) or {}).values())
        collection["item_count"] = len(items)
        collection["highlighted_count"] = sum(1 for item in items if bool(item.get("is_highlighted", False)))

    def add_collection_items(
        self,
        collection_id: str,
        request_ids: List[str],
        added_at: str,
        updated_at: str,
    ) -> Dict[str, int]:
        bucket = self._collection_items.setdefault(collection_id, {})
        inserted = 0
        for request_id in request_ids:
            if request_id in bucket:
                continue
            bucket[request_id] = {
                "collection_id": collection_id,
                "request_id": request_id,
                "is_highlighted": False,
                "added_at": added_at,
            }
            inserted += 1

        if collection_id in self._collections:
            self._collections[collection_id]["updated_at"] = updated_at
        self._refresh_collection_counts(collection_id)
        return {"inserted": inserted}

    def remove_collection_item(self, collection_id: str, request_id: str, updated_at: str) -> bool:
        bucket = self._collection_items.get(collection_id)
        if bucket is None:
            return False
        removed = bucket.pop(request_id, None) is not None
        if removed and collection_id in self._collections:
            self._collections[collection_id]["updated_at"] = updated_at
            if self._collections[collection_id].get("best_request_id") == request_id:
                self._collections[collection_id]["best_request_id"] = None
            self._refresh_collection_counts(collection_id)
        return removed

    def set_collection_item_highlight(
        self,
        collection_id: str,
        request_id: str,
        is_highlighted: bool,
        updated_at: str,
    ) -> Optional[Dict[str, Any]]:
        bucket = self._collection_items.get(collection_id)
        if bucket is None:
            return None

        item = bucket.get(request_id)
        if item is None:
            return None

        item["is_highlighted"] = bool(is_highlighted)
        if collection_id in self._collections:
            self._collections[collection_id]["updated_at"] = updated_at
        self._refresh_collection_counts(collection_id)
        return deepcopy(item)

    def list_collections_for_request(self, request_id: str) -> List[Dict[str, Any]]:
        memberships: List[Dict[str, Any]] = []
        for collection_id, items_by_request in self._collection_items.items():
            item = items_by_request.get(request_id)
            if item is None:
                continue

            collection = self._collections.get(collection_id)
            if collection is None:
                continue

            memberships.append(
                {
                    "collection_id": collection_id,
                    "name": str(collection.get("name") or ""),
                    "is_highlighted": bool(item.get("is_highlighted", False)),
                    "is_best": str(collection.get("best_request_id") or "") == request_id,
                    "added_at": str(item.get("added_at") or ""),
                    "updated_at": str(collection.get("updated_at") or ""),
                }
            )

        memberships.sort(key=lambda row: row["updated_at"], reverse=True)
        for row in memberships:
            row.pop("updated_at", None)

        return memberships


class SequencePlanRenderServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.planner_service = SequencePlannerService()
        self.render_jobs_service = StubRenderJobsService()
        self.runs_repository = InMemorySequencePlanRunsRepository()
        self.service = SequencePlanRenderService(
            planner_service=self.planner_service,
            render_jobs_service=self.render_jobs_service,
            runs_repository=self.runs_repository,
        )

    def _set_execution_status(self, execution: Dict[str, Any], status: str) -> None:
        for job_id in execution.get("job_ids", []):
            if isinstance(job_id, str):
                self.render_jobs_service.set_job_status(job_id, status)

    def test_plan_and_create_jobs_returns_expected_contract(self) -> None:
        payload = SequencePlanRequest(
            script_text=(
                "INT. CASA - NOCHE. ANA entra al salon y se detiene frente a LUIS. "
                "LUIS responde con calma mientras la tension crece."
            ),
            project_id="project_001",
            sequence_id="seq_101",
            continuity_mode="strict",
        )

        result = self.service.plan_and_create_jobs(payload)

        self.assertTrue(result["ok"])
        self.assertIn("plan", result)
        self.assertIn("request_id", result)
        self.assertIn("created_jobs", result)
        self.assertIn("job_count", result)
        self.assertIn("job_ids", result)
        self.assertIn("shot_job_links", result)
        self.assertIn("status_summary", result)
        self.assertIn("is_favorite", result)
        self.assertIn("tags", result)
        self.assertIn("note", result)
        self.assertIn("review_status", result)
        self.assertIn("review_note", result)
        self.assertIn("reviewed_at", result)
        self.assertIn("review_history_summary", result)
        self.assertIn("collections", result)
        self.assertTrue(result["request_id"])

        self.assertGreater(result["job_count"], 0)
        self.assertEqual(result["job_count"], len(result["created_jobs"]))
        self.assertEqual(result["job_count"], len(result["job_ids"]))
        self.assertEqual(result["job_count"], len(result["shot_job_links"]))

        persisted = self.runs_repository.get(result["request_id"])
        self.assertIsNotNone(persisted)
        assert persisted is not None
        self.assertIn("request_payload", persisted)
        self.assertIn("plan", persisted)
        self.assertIn("created_jobs", persisted)
        self.assertIn("job_ids", persisted)
        self.assertIn("shot_job_links", persisted)
        self.assertIn("job_count", persisted)
        self.assertIn("created_at", persisted)
        self.assertIn("updated_at", persisted)
        self.assertIn("is_favorite", persisted)
        self.assertIn("tags", persisted)
        self.assertIn("note", persisted)
        self.assertIn("review_status", persisted)
        self.assertIn("review_note", persisted)
        self.assertIn("reviewed_at", persisted)

    def test_plan_and_create_jobs_links_shots_with_jobs(self) -> None:
        payload = SequencePlanRequest(
            script_text="EXT. CALLE - DIA. ANA camina. LUIS la sigue a distancia.",
            sequence_id="seq_102",
            continuity_mode="balanced",
        )

        result = self.service.plan_and_create_jobs(payload)

        shot_ids_in_plan = {shot["shot_id"] for shot in result["plan"]["shots"]}
        links = result["shot_job_links"]
        self.assertGreater(len(links), 0)

        job_ids = set(result["job_ids"])
        linked_shot_ids = set()
        for link in links:
            self.assertIn("shot_id", link)
            self.assertIn("job_id", link)
            self.assertIn(link["job_id"], job_ids)
            linked_shot_ids.add(link["shot_id"])

        self.assertEqual(shot_ids_in_plan, linked_shot_ids)

    def test_get_plan_and_render_request_returns_saved_execution(self) -> None:
        payload = SequencePlanRequest(
            script_text="INT. OFICINA - TARDE. ANA se detiene. LUIS responde.",
            sequence_id="seq_103",
            continuity_mode="strict",
        )

        created = self.service.plan_and_create_jobs(payload)
        self.assertGreater(len(created["job_ids"]), 0)

        first_job_id = created["job_ids"][0]
        self.render_jobs_service.set_job_status(first_job_id, "running")

        loaded = self.service.get_plan_and_render_request(created["request_id"])
        self.assertIsNotNone(loaded)
        assert loaded is not None

        self.assertEqual(loaded["request_id"], created["request_id"])
        self.assertEqual(loaded["job_count"], len(loaded["created_jobs"]))
        self.assertIn("status_summary", loaded)
        self.assertIn("by_status", loaded["status_summary"])
        self.assertGreaterEqual(loaded["status_summary"]["by_status"].get("running", 0), 1)
        self.assertIn("review_status", loaded)
        self.assertIn("review_note", loaded)
        self.assertIn("reviewed_at", loaded)
        self.assertIn("review_history_summary", loaded)
        self.assertEqual(loaded["review_history_summary"]["history_count"], 0)
        self.assertIn("collections", loaded)
        self.assertEqual(loaded["collections"], [])

    def test_get_plan_and_render_request_returns_none_when_missing(self) -> None:
        loaded = self.service.get_plan_and_render_request("missing_request_id")
        self.assertIsNone(loaded)

    def test_retry_shot_creates_child_job_and_updates_links(self) -> None:
        payload = SequencePlanRequest(
            script_text="INT. CASA - NOCHE. ANA entra al salon. LUIS la observa.",
            sequence_id="seq_retry_001",
            continuity_mode="strict",
        )
        created = self.service.plan_and_create_jobs(payload)

        first_link = created["shot_job_links"][0]
        shot_id = first_link["shot_id"]
        parent_job_id = first_link["job_id"]

        retry_result = self.service.retry_shot(
            request_id=created["request_id"],
            shot_id=shot_id,
            override_prompt="updated prompt for retry",
            override_negative_prompt="updated negative",
            override_render_context={"character_id": "char_ana", "use_ipadapter": True},
            reason="manual qa retry",
        )

        self.assertTrue(retry_result["ok"])
        self.assertEqual(retry_result["request_id"], created["request_id"])
        self.assertEqual(retry_result["shot_id"], shot_id)
        self.assertEqual(retry_result["parent_job_id"], parent_job_id)
        self.assertEqual(retry_result["retry_index"], 1)
        self.assertEqual(retry_result["status"], "queued")

        loaded = self.service.get_plan_and_render_request(created["request_id"])
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded["job_count"], created["job_count"] + 1)
        self.assertIn(retry_result["new_job_id"], loaded["job_ids"])

        matching_links = [
            link
            for link in loaded["shot_job_links"]
            if link.get("shot_id") == shot_id and link.get("job_id") == retry_result["new_job_id"]
        ]
        self.assertEqual(len(matching_links), 1)
        self.assertEqual(matching_links[0].get("parent_job_id"), parent_job_id)
        self.assertEqual(matching_links[0].get("retry_index"), 1)

    def test_retry_shot_raises_when_request_missing(self) -> None:
        with self.assertRaises(SequencePlanRunNotFoundError):
            self.service.retry_shot(
                request_id="missing_request",
                shot_id="shot_001",
            )

    def test_retry_shot_raises_when_shot_missing(self) -> None:
        payload = SequencePlanRequest(
            script_text="INT. CASA - NOCHE. ANA entra al salon.",
            sequence_id="seq_retry_002",
        )
        created = self.service.plan_and_create_jobs(payload)

        with self.assertRaises(SequenceShotNotFoundError):
            self.service.retry_shot(
                request_id=created["request_id"],
                shot_id="shot_not_found",
            )

    def test_list_recent_requests_returns_ordered_summary_with_limit(self) -> None:
        first = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. OFICINA - DIA. ANA mira el monitor.",
                project_id="project_alpha",
                sequence_id="seq_alpha",
            )
        )
        second = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="EXT. CALLE - NOCHE. LUIS camina bajo la lluvia.",
                project_id="project_beta",
                sequence_id="seq_beta",
            )
        )

        recent = self.service.list_recent_requests(limit=1)

        self.assertTrue(recent["ok"])
        self.assertEqual(recent["limit"], 1)
        self.assertEqual(recent["count"], 1)
        self.assertEqual(len(recent["executions"]), 1)

        item = recent["executions"][0]
        self.assertEqual(item["request_id"], second["request_id"])
        self.assertEqual(item["sequence_id"], "seq_beta")
        self.assertEqual(item["project_id"], "project_beta")
        self.assertIn("sequence_summary", item)
        self.assertIn("status_summary", item)
        self.assertIn("job_count", item)
        self.assertIn("success_ratio", item)
        self.assertIn("total_retries", item)
        self.assertIn("is_favorite", item)
        self.assertIn("tags", item)
        self.assertIn("note", item)
        self.assertIn("review_status", item)
        self.assertIn("review_note", item)
        self.assertIn("reviewed_at", item)
        self.assertIn("collection_candidate", item)
        self.assertIn("collection_added_at", item)
        self.assertIn("collection_best", item)
        self.assertGreaterEqual(item["job_count"], 1)
        self.assertIn("by_status", item["status_summary"])

        # Ensure first record still appears when limit allows.
        expanded = self.service.list_recent_requests(limit=10)
        returned_ids = [item["request_id"] for item in expanded["executions"]]
        self.assertIn(first["request_id"], returned_ids)
        self.assertIn(second["request_id"], returned_ids)

    def test_list_recent_requests_supports_q_project_sequence_and_status_filters(self) -> None:
        first = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. OFICINA - DIA. ANA mira el monitor.",
                project_id="project_filter_alpha",
                sequence_id="seq_filter_alpha",
            )
        )
        second = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="EXT. CALLE - NOCHE. LUIS camina bajo la lluvia.",
                project_id="project_filter_beta",
                sequence_id="seq_filter_beta",
            )
        )

        self._set_execution_status(first, "succeeded")
        self._set_execution_status(second, "failed")

        by_project = self.service.list_recent_requests(limit=10, project_id="project_filter_beta")
        self.assertEqual(by_project["count"], 1)
        self.assertEqual(by_project["executions"][0]["request_id"], second["request_id"])

        by_sequence = self.service.list_recent_requests(limit=10, sequence_id="seq_filter_alpha")
        self.assertEqual(by_sequence["count"], 1)
        self.assertEqual(by_sequence["executions"][0]["request_id"], first["request_id"])

        by_status = self.service.list_recent_requests(limit=10, status="failed")
        self.assertEqual(by_status["count"], 1)
        self.assertEqual(by_status["executions"][0]["request_id"], second["request_id"])

        by_q_request = self.service.list_recent_requests(limit=10, q=first["request_id"][:8])
        self.assertEqual(by_q_request["count"], 1)
        self.assertEqual(by_q_request["executions"][0]["request_id"], first["request_id"])

        by_q_project = self.service.list_recent_requests(limit=10, q="project_filter_beta")
        self.assertEqual(by_q_project["count"], 1)
        self.assertEqual(by_q_project["executions"][0]["request_id"], second["request_id"])

    def test_update_run_meta_updates_get_and_recent_payload(self) -> None:
        created = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. CASA - NOCHE. ANA revisa tomas en monitor.",
                project_id="project_meta",
                sequence_id="seq_meta",
            )
        )

        updated = self.service.update_run_meta(
            request_id=created["request_id"],
            is_favorite=True,
            tags=["revision", "v2", "revision"],
            note="  Revisar prompt del close up  ",
        )

        self.assertTrue(updated["is_favorite"])
        self.assertEqual(updated["tags"], ["revision", "v2"])
        self.assertEqual(updated["note"], "Revisar prompt del close up")

        loaded = self.service.get_plan_and_render_request(created["request_id"])
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertTrue(loaded["is_favorite"])
        self.assertEqual(loaded["tags"], ["revision", "v2"])
        self.assertEqual(loaded["note"], "Revisar prompt del close up")

        recent = self.service.list_recent_requests(limit=10, q=created["request_id"])
        self.assertEqual(recent["count"], 1)
        self.assertTrue(recent["executions"][0]["is_favorite"])
        self.assertEqual(recent["executions"][0]["tags"], ["revision", "v2"])
        self.assertEqual(recent["executions"][0]["note"], "Revisar prompt del close up")

    def test_update_run_review_updates_get_and_recent_payload(self) -> None:
        created = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. QA - NOCHE. ANA evalua versión final.",
                project_id="project_review",
                sequence_id="seq_review",
            )
        )

        initial = self.service.get_plan_and_render_request(created["request_id"])
        self.assertIsNotNone(initial)
        assert initial is not None
        self.assertEqual(initial["review_status"], "pending_review")
        self.assertEqual(initial["review_note"], "")
        self.assertIsNone(initial["reviewed_at"])

        updated = self.service.update_run_review(
            request_id=created["request_id"],
            review_status="approved",
            review_note="Aprobada por consistencia visual",
        )
        self.assertEqual(updated["review_status"], "approved")
        self.assertEqual(updated["review_note"], "Aprobada por consistencia visual")
        self.assertIsNotNone(updated["reviewed_at"])
        self.assertEqual(updated["review_history_summary"]["history_count"], 1)
        self.assertIsNotNone(updated["review_history_summary"]["latest_created_at"])

        loaded = self.service.get_plan_and_render_request(created["request_id"])
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded["review_status"], "approved")
        self.assertEqual(loaded["review_note"], "Aprobada por consistencia visual")
        self.assertIsNotNone(loaded["reviewed_at"])
        self.assertEqual(loaded["review_history_summary"]["history_count"], 1)

        recent = self.service.list_recent_requests(limit=10, q=created["request_id"])
        self.assertEqual(recent["count"], 1)
        self.assertEqual(recent["executions"][0]["review_status"], "approved")
        self.assertEqual(recent["executions"][0]["review_note"], "Aprobada por consistencia visual")
        self.assertIsNotNone(recent["executions"][0]["reviewed_at"])

        history = self.service.list_run_review_history(created["request_id"], limit=50)
        self.assertTrue(history["ok"])
        self.assertEqual(history["request_id"], created["request_id"])
        self.assertEqual(history["count"], 1)
        self.assertEqual(len(history["history"]), 1)
        self.assertEqual(history["history"][0]["previous_review_status"], "pending_review")
        self.assertEqual(history["history"][0]["new_review_status"], "approved")
        self.assertEqual(history["history"][0]["review_note"], "Aprobada por consistencia visual")

    def test_update_run_review_note_only_creates_history_entry(self) -> None:
        created = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. QA - DIA. ANA deja feedback de nota.",
                project_id="project_review_note",
                sequence_id="seq_review_note",
            )
        )

        updated = self.service.update_run_review(
            request_id=created["request_id"],
            review_note="Pendiente por ajustar color grading",
        )
        self.assertEqual(updated["review_status"], "pending_review")
        self.assertEqual(updated["review_note"], "Pendiente por ajustar color grading")
        self.assertEqual(updated["review_history_summary"]["history_count"], 1)

        history = self.service.list_run_review_history(created["request_id"], limit=50)
        self.assertEqual(history["count"], 1)
        self.assertEqual(history["history"][0]["previous_review_status"], "pending_review")
        self.assertEqual(history["history"][0]["new_review_status"], "pending_review")
        self.assertEqual(history["history"][0]["review_note"], "Pendiente por ajustar color grading")

    def test_update_run_review_without_relevant_change_does_not_create_history_entry(self) -> None:
        created = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. QA - DIA. ANA mantiene estado sin cambios.",
                project_id="project_review_same",
                sequence_id="seq_review_same",
            )
        )

        first_update = self.service.update_run_review(
            request_id=created["request_id"],
            review_status="approved",
            review_note="Aprobada",
        )
        self.assertEqual(first_update["review_history_summary"]["history_count"], 1)

        second_update = self.service.update_run_review(
            request_id=created["request_id"],
            review_status="approved",
            review_note="Aprobada",
        )
        self.assertEqual(second_update["review_history_summary"]["history_count"], 1)

        history = self.service.list_run_review_history(created["request_id"], limit=50)
        self.assertEqual(history["count"], 1)

    def test_list_run_review_history_raises_when_request_missing(self) -> None:
        with self.assertRaises(SequencePlanRunNotFoundError):
            self.service.list_run_review_history("missing_request_id", limit=20)

    def test_list_recent_requests_supports_favorite_and_tag_filters(self) -> None:
        favorite_execution = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. SET - DIA. ANA revisa continuidad en monitor.",
                project_id="project_editorial",
                sequence_id="seq_editorial_fav",
            )
        )
        regular_execution = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="EXT. PARQUE - TARDE. LUIS practica blocking.",
                project_id="project_editorial",
                sequence_id="seq_editorial_regular",
            )
        )

        self.service.update_run_meta(
            request_id=favorite_execution["request_id"],
            is_favorite=True,
            tags=["revision", "hero"],
        )
        self.service.update_run_meta(
            request_id=regular_execution["request_id"],
            is_favorite=False,
            tags=["baseline"],
        )

        favorites_only = self.service.list_recent_requests(limit=10, is_favorite=True)
        self.assertEqual(favorites_only["count"], 1)
        self.assertEqual(favorites_only["executions"][0]["request_id"], favorite_execution["request_id"])

        by_tag = self.service.list_recent_requests(limit=10, tag="revision")
        self.assertEqual(by_tag["count"], 1)
        self.assertEqual(by_tag["executions"][0]["request_id"], favorite_execution["request_id"])

        by_tag_case_insensitive = self.service.list_recent_requests(limit=10, tag="REVISION")
        self.assertEqual(by_tag_case_insensitive["count"], 1)
        self.assertEqual(by_tag_case_insensitive["executions"][0]["request_id"], favorite_execution["request_id"])

        combined = self.service.list_recent_requests(limit=10, is_favorite=True, tag="hero")
        self.assertEqual(combined["count"], 1)
        self.assertEqual(combined["executions"][0]["request_id"], favorite_execution["request_id"])

    def test_list_recent_requests_supports_operational_rankings(self) -> None:
        stable_execution = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. EDIT - DIA. ANA aprueba corte final.",
                project_id="project_rank",
                sequence_id="seq_rank_stable",
            )
        )
        problematic_execution = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="EXT. RODAJE - NOCHE. LUIS repite toma con errores.",
                project_id="project_rank",
                sequence_id="seq_rank_problem",
            )
        )
        retry_heavy_execution = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. SET - TARDE. ANA ajusta continuidad en múltiples intentos.",
                project_id="project_rank",
                sequence_id="seq_rank_retry",
            )
        )

        self._set_execution_status(stable_execution, "succeeded")
        self._set_execution_status(problematic_execution, "failed")

        retry_shot_id = retry_heavy_execution["shot_job_links"][0]["shot_id"]
        self.service.retry_shot(request_id=retry_heavy_execution["request_id"], shot_id=retry_shot_id)
        self.service.retry_shot(request_id=retry_heavy_execution["request_id"], shot_id=retry_shot_id)
        self.service.retry_shot(request_id=retry_heavy_execution["request_id"], shot_id=retry_shot_id)

        most_stable = self.service.list_recent_requests(limit=10, ranking="most_stable")
        self.assertGreaterEqual(most_stable["count"], 3)
        self.assertEqual(most_stable["executions"][0]["request_id"], stable_execution["request_id"])

        most_problematic = self.service.list_recent_requests(limit=10, ranking="most_problematic")
        self.assertGreaterEqual(most_problematic["count"], 3)
        self.assertEqual(most_problematic["executions"][0]["request_id"], problematic_execution["request_id"])

        most_retries = self.service.list_recent_requests(limit=10, ranking="most_retries")
        self.assertGreaterEqual(most_retries["count"], 3)
        self.assertEqual(most_retries["executions"][0]["request_id"], retry_heavy_execution["request_id"])
        self.assertGreaterEqual(most_retries["executions"][0]["total_retries"], 3)

        highest_success_ratio = self.service.list_recent_requests(limit=10, ranking="highest_success_ratio")
        self.assertGreaterEqual(highest_success_ratio["count"], 3)
        self.assertEqual(highest_success_ratio["executions"][0]["request_id"], stable_execution["request_id"])
        self.assertGreaterEqual(highest_success_ratio["executions"][0]["success_ratio"], 1.0)

    def test_collection_review_flow_supports_items_highlight_and_editorial_note(self) -> None:
        first = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. STUDIO - DIA. ANA revisa la primera versión.",
                project_id="project_collection",
                sequence_id="seq_collection_001",
            )
        )
        second = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. STUDIO - DIA. LUIS propone variante de iluminación.",
                project_id="project_collection",
                sequence_id="seq_collection_002",
            )
        )

        created_collection = self.service.create_collection(
            name="Coleccion QA Creativa",
            description="Revision editorial semanal",
            editorial_note="Priorizar consistencia de personaje",
            color="#0ea5e9",
        )
        collection_id = created_collection["collection"]["collection_id"]
        self.assertTrue(collection_id)

        add_items = self.service.add_collection_items(collection_id, [first["request_id"], second["request_id"]])
        self.assertEqual(add_items["collection"]["item_count"], 2)

        highlighted = self.service.set_collection_item_highlight(
            collection_id=collection_id,
            request_id=first["request_id"],
            is_highlighted=True,
        )
        self.assertTrue(highlighted["collection"]["highlighted_count"] >= 1)

        updated_collection = self.service.update_collection(
            collection_id=collection_id,
            editorial_note="Candidata final: request con mejor estabilidad",
        )
        self.assertEqual(
            updated_collection["collection"]["editorial_note"],
            "Candidata final: request con mejor estabilidad",
        )

        review = self.service.get_collection_review(collection_id=collection_id, ranking="most_stable", limit=20)
        self.assertTrue(review["ok"])
        self.assertEqual(review["collection"]["collection_id"], collection_id)
        self.assertEqual(review["count"], 2)
        self.assertIn("summary", review)
        self.assertIn("highlighted_count", review["summary"])

        review_request_ids = [item["request_id"] for item in review["executions"]]
        self.assertIn(first["request_id"], review_request_ids)
        self.assertIn(second["request_id"], review_request_ids)

        first_item = next(item for item in review["executions"] if item["request_id"] == first["request_id"])
        self.assertTrue(first_item.get("collection_candidate"))

    def test_list_recent_requests_supports_collection_filter(self) -> None:
        first = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. PASILLO - NOCHE. ANA espera señal.",
                project_id="project_collection_filter",
                sequence_id="seq_collection_filter_001",
            )
        )
        second = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. PASILLO - NOCHE. LUIS entra en cuadro.",
                project_id="project_collection_filter",
                sequence_id="seq_collection_filter_002",
            )
        )

        collection = self.service.create_collection(name="Coleccion filtro")
        collection_id = collection["collection"]["collection_id"]

        self.service.add_collection_items(collection_id, [first["request_id"]])
        self.service.set_collection_best_request(collection_id, first["request_id"])

        filtered = self.service.list_recent_requests(limit=50, collection_id=collection_id)
        self.assertEqual(filtered["count"], 1)
        self.assertEqual(filtered["executions"][0]["request_id"], first["request_id"])
        self.assertNotEqual(filtered["executions"][0]["request_id"], second["request_id"])
        self.assertTrue(filtered["executions"][0]["collection_best"])

    def test_collection_best_request_flow(self) -> None:
        first = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. SALA - DIA. ANA prueba primera versión.",
                project_id="project_best",
                sequence_id="seq_best_001",
            )
        )
        second = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. SALA - DIA. LUIS prueba segunda versión.",
                project_id="project_best",
                sequence_id="seq_best_002",
            )
        )

        collection = self.service.create_collection(name="Coleccion Best")
        collection_id = collection["collection"]["collection_id"]

        self.service.add_collection_items(collection_id, [first["request_id"], second["request_id"]])

        marked = self.service.set_collection_best_request(collection_id, first["request_id"])
        self.assertEqual(marked["collection"]["best_request_id"], first["request_id"])

        review = self.service.get_collection_review(collection_id=collection_id, ranking=None, limit=20)
        first_item = next(item for item in review["executions"] if item["request_id"] == first["request_id"])
        second_item = next(item for item in review["executions"] if item["request_id"] == second["request_id"])
        self.assertTrue(first_item.get("collection_best"))
        self.assertFalse(second_item.get("collection_best"))

        cleared = self.service.set_collection_best_request(collection_id, None)
        self.assertIsNone(cleared["collection"].get("best_request_id"))

    def test_get_plan_and_render_request_includes_collection_membership(self) -> None:
        created = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. QA - TARDE. ANA valida pertenencia en colecciones.",
                project_id="project_membership",
                sequence_id="seq_membership_001",
            )
        )

        collection = self.service.create_collection(name="Coleccion membership")
        collection_id = collection["collection"]["collection_id"]
        self.service.add_collection_items(collection_id, [created["request_id"]])
        self.service.set_collection_item_highlight(collection_id, created["request_id"], True)
        self.service.set_collection_best_request(collection_id, created["request_id"])

        loaded = self.service.get_plan_and_render_request(created["request_id"])
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(len(loaded["collections"]), 1)

        membership = loaded["collections"][0]
        self.assertEqual(membership["collection_id"], collection_id)
        self.assertEqual(membership["name"], "Coleccion membership")
        self.assertTrue(membership["is_highlighted"])
        self.assertTrue(membership["is_best"])
        self.assertTrue(membership["added_at"])

    def test_get_collection_audit_returns_editorial_and_operational_kpis(self) -> None:
        approved_execution = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. AUDIT - DIA. ANA aprueba versión estable.",
                project_id="project_audit",
                sequence_id="seq_audit_approved",
            )
        )
        rejected_execution = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. AUDIT - DIA. LUIS rechaza versión con error.",
                project_id="project_audit",
                sequence_id="seq_audit_rejected",
            )
        )
        pending_execution = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. AUDIT - DIA. Tercera ejecución pendiente.",
                project_id="project_audit",
                sequence_id="seq_audit_pending",
            )
        )

        self._set_execution_status(approved_execution, "succeeded")
        self._set_execution_status(rejected_execution, "failed")
        self._set_execution_status(pending_execution, "timeout")

        self.service.update_run_meta(request_id=approved_execution["request_id"], is_favorite=True)
        self.service.update_run_review(
            request_id=approved_execution["request_id"],
            review_status="approved",
            review_note="Aprobada",
        )
        self.service.update_run_review(
            request_id=rejected_execution["request_id"],
            review_status="rejected",
            review_note="Rechazada por artifacts",
        )

        collection = self.service.create_collection(name="Coleccion Audit")
        collection_id = collection["collection"]["collection_id"]
        self.service.add_collection_items(
            collection_id,
            [
                approved_execution["request_id"],
                rejected_execution["request_id"],
                pending_execution["request_id"],
            ],
        )
        self.service.set_collection_best_request(collection_id, approved_execution["request_id"])

        audit = self.service.get_collection_audit(collection_id)
        self.assertTrue(audit["ok"])
        self.assertEqual(audit["collection_id"], collection_id)
        self.assertEqual(audit["total_executions"], 3)
        self.assertEqual(audit["approved_count"], 1)
        self.assertEqual(audit["rejected_count"], 1)
        self.assertEqual(audit["pending_review_count"], 1)
        self.assertEqual(audit["favorite_count"], 1)
        self.assertEqual(audit["best_request_id"], approved_execution["request_id"])
        self.assertEqual(audit["executions_without_review"], 1)

        self.assertGreater(audit["total_jobs"], 0)
        self.assertGreaterEqual(audit["total_retries"], 0)
        self.assertGreaterEqual(audit["failed_count"], 1)
        self.assertGreaterEqual(audit["timeout_count"], 1)
        self.assertEqual(audit["success_ratio_summary"]["total_jobs"], audit["total_jobs"])
        self.assertGreaterEqual(audit["success_ratio_summary"]["ratio"], 0.0)
        self.assertLessEqual(audit["success_ratio_summary"]["ratio"], 1.0)

        self.assertIn("editorial_summary", audit)
        self.assertIn("operational_summary", audit)
        self.assertEqual(audit["health_status"], "red")
        self.assertIsInstance(audit.get("alerts"), list)
        self.assertGreaterEqual(len(audit["alerts"]), 1)
        self.assertIsInstance(audit.get("signals"), list)
        self.assertGreaterEqual(len(audit["signals"]), 1)

    def test_get_collection_audit_marks_yellow_when_pending_and_no_best(self) -> None:
        first = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. AUDIT - DIA. Primera pendiente.",
                project_id="project_audit_yellow",
                sequence_id="seq_audit_yellow_001",
            )
        )
        second = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. AUDIT - DIA. Segunda pendiente.",
                project_id="project_audit_yellow",
                sequence_id="seq_audit_yellow_002",
            )
        )

        collection = self.service.create_collection(name="Coleccion Audit Yellow")
        collection_id = collection["collection"]["collection_id"]
        self.service.add_collection_items(collection_id, [first["request_id"], second["request_id"]])

        audit = self.service.get_collection_audit(collection_id)
        self.assertEqual(audit["health_status"], "yellow")
        self.assertGreaterEqual(len(audit["alerts"]), 1)

    def test_get_collection_audit_marks_green_when_collection_is_stable(self) -> None:
        stable_execution = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. AUDIT - DIA. Ejecución estable aprobada.",
                project_id="project_audit_green",
                sequence_id="seq_audit_green",
            )
        )

        self._set_execution_status(stable_execution, "succeeded")
        self.service.update_run_review(
            request_id=stable_execution["request_id"],
            review_status="approved",
            review_note="Aprobada y estable",
        )

        collection = self.service.create_collection(name="Coleccion Audit Green")
        collection_id = collection["collection"]["collection_id"]
        self.service.add_collection_items(collection_id, [stable_execution["request_id"]])
        self.service.set_collection_best_request(collection_id, stable_execution["request_id"])

        audit = self.service.get_collection_audit(collection_id)
        self.assertEqual(audit["health_status"], "green")
        self.assertEqual(audit["alerts"], [])

    def test_get_collection_audit_raises_when_collection_missing(self) -> None:
        with self.assertRaises(SequenceCollectionNotFoundError):
            self.service.get_collection_audit("missing_collection_id")

    def test_get_collections_dashboard_returns_global_kpis_and_featured_lists(self) -> None:
        red_a = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. DASHBOARD - DIA. Red A.",
                project_id="project_dashboard",
                sequence_id="seq_dashboard_red_a",
            )
        )
        red_b = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. DASHBOARD - DIA. Red B.",
                project_id="project_dashboard",
                sequence_id="seq_dashboard_red_b",
            )
        )
        red_c = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. DASHBOARD - DIA. Red C.",
                project_id="project_dashboard",
                sequence_id="seq_dashboard_red_c",
            )
        )

        self._set_execution_status(red_a, "succeeded")
        self._set_execution_status(red_b, "failed")
        self._set_execution_status(red_c, "timeout")
        self.service.update_run_review(red_a["request_id"], review_status="approved", review_note="ok")
        self.service.update_run_review(red_b["request_id"], review_status="rejected", review_note="nok")

        red_collection = self.service.create_collection(name="Coleccion Dashboard Red")
        red_collection_id = red_collection["collection"]["collection_id"]
        self.service.add_collection_items(red_collection_id, [red_a["request_id"], red_b["request_id"], red_c["request_id"]])
        self.service.set_collection_best_request(red_collection_id, red_a["request_id"])

        yellow_execution = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. DASHBOARD - DIA. Yellow pending.",
                project_id="project_dashboard",
                sequence_id="seq_dashboard_yellow",
            )
        )
        yellow_shot_id = yellow_execution["shot_job_links"][0]["shot_id"]
        self.service.retry_shot(yellow_execution["request_id"], yellow_shot_id)
        self.service.retry_shot(yellow_execution["request_id"], yellow_shot_id)

        yellow_collection = self.service.create_collection(name="Coleccion Dashboard Yellow")
        yellow_collection_id = yellow_collection["collection"]["collection_id"]
        self.service.add_collection_items(yellow_collection_id, [yellow_execution["request_id"]])

        green_execution = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. DASHBOARD - DIA. Green stable.",
                project_id="project_dashboard",
                sequence_id="seq_dashboard_green",
            )
        )
        self._set_execution_status(green_execution, "succeeded")
        self.service.update_run_review(green_execution["request_id"], review_status="approved", review_note="stable")

        green_collection = self.service.create_collection(name="Coleccion Dashboard Green")
        green_collection_id = green_collection["collection"]["collection_id"]
        self.service.add_collection_items(green_collection_id, [green_execution["request_id"]])
        self.service.set_collection_best_request(green_collection_id, green_execution["request_id"])

        dashboard = self.service.get_collections_dashboard(limit=200, include_archived=False, top_limit=5)
        self.assertTrue(dashboard["ok"])
        self.assertEqual(dashboard["total_collections"], 3)
        self.assertGreaterEqual(dashboard["collections_red"], 1)
        self.assertGreaterEqual(dashboard["collections_yellow"], 1)
        self.assertGreaterEqual(dashboard["collections_green"], 1)

        top_by_executions = dashboard["top_collections_by_executions"]
        self.assertGreaterEqual(len(top_by_executions), 1)
        self.assertEqual(top_by_executions[0]["collection_id"], red_collection_id)

        top_by_retries = dashboard["top_collections_by_retries"]
        self.assertGreaterEqual(len(top_by_retries), 1)
        self.assertEqual(top_by_retries[0]["collection_id"], yellow_collection_id)

        without_best_ids = {item["collection_id"] for item in dashboard["collections_without_best_execution"]}
        self.assertIn(yellow_collection_id, without_best_ids)

        with_pending_ids = {item["collection_id"] for item in dashboard["collections_with_pending_review"]}
        self.assertIn(yellow_collection_id, with_pending_ids)

        highlighted_ids = [item["collection_id"] for item in dashboard["highlighted_collections"]]
        self.assertIn(red_collection_id, highlighted_ids)

    def test_collection_notifications_generated_and_marked_as_read(self) -> None:
        first = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. NOTIF - DIA. Primera ejecución pendiente.",
                project_id="project_notifications",
                sequence_id="seq_notifications_001",
            )
        )
        second = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. NOTIF - DIA. Segunda ejecución pendiente.",
                project_id="project_notifications",
                sequence_id="seq_notifications_002",
            )
        )

        collection = self.service.create_collection(name="Coleccion Notificaciones")
        collection_id = collection["collection"]["collection_id"]
        self.service.add_collection_items(collection_id, [first["request_id"], second["request_id"]])

        audit = self.service.get_collection_audit(collection_id)
        self.assertIn(audit["health_status"], {"yellow", "red"})

        notifications = self.service.list_notifications(limit=100, collection_id=collection_id)
        self.assertTrue(notifications["ok"])
        self.assertGreaterEqual(notifications["count"], 1)

        first_notification = notifications["notifications"][0]
        self.assertEqual(first_notification["collection_id"], collection_id)
        self.assertFalse(first_notification["is_read"])

        marked = self.service.mark_notification_read(first_notification["notification_id"], is_read=True)
        self.assertTrue(marked["ok"])
        self.assertTrue(marked["notification"]["is_read"])

    def test_collection_notifications_do_not_duplicate_without_state_change(self) -> None:
        first = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. NOTIF - DIA. Estado estable de alertas.",
                project_id="project_notifications_dup",
                sequence_id="seq_notifications_dup",
            )
        )

        collection = self.service.create_collection(name="Coleccion Notificaciones Dedupe")
        collection_id = collection["collection"]["collection_id"]
        self.service.add_collection_items(collection_id, [first["request_id"]])

        self.service.get_collection_audit(collection_id)
        first_batch = self.service.list_notifications(limit=100, collection_id=collection_id)
        self.assertGreaterEqual(first_batch["count"], 1)

        self.service.get_collection_audit(collection_id)
        second_batch = self.service.list_notifications(limit=100, collection_id=collection_id)
        self.assertEqual(second_batch["count"], first_batch["count"])

    def test_mark_notification_read_raises_for_missing_notification(self) -> None:
        with self.assertRaises(SequenceNotificationNotFoundError):
            self.service.mark_notification_read("missing_notification_id", is_read=True)

    def test_get_and_update_notification_preferences(self) -> None:
        current = self.service.get_notification_preferences()
        self.assertTrue(current["ok"])
        self.assertTrue(current["preferences"]["notifications_enabled"])
        self.assertEqual(current["preferences"]["min_severity"], "info")
        self.assertIsInstance(current["preferences"]["enabled_types"], list)

        updated = self.service.update_notification_preferences(
            notifications_enabled=True,
            min_severity="warning",
            enabled_types=["COLLECTION_ENTERED_RED", "PENDING_REVIEW_HIGH"],
            show_only_unread_by_default=True,
        )
        self.assertTrue(updated["ok"])
        self.assertEqual(updated["preferences"]["min_severity"], "warning")
        self.assertEqual(
            updated["preferences"]["enabled_types"],
            ["COLLECTION_ENTERED_RED", "PENDING_REVIEW_HIGH"],
        )
        self.assertTrue(updated["preferences"]["show_only_unread_by_default"])

    def test_notifications_disabled_prevents_new_notifications(self) -> None:
        self.service.update_notification_preferences(notifications_enabled=False)

        first = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. NOTIF PREF - DIA. Primera ejecución.",
                project_id="project_notifications_pref",
                sequence_id="seq_notifications_pref_001",
            )
        )
        second = self.service.plan_and_create_jobs(
            SequencePlanRequest(
                script_text="INT. NOTIF PREF - DIA. Segunda ejecución.",
                project_id="project_notifications_pref",
                sequence_id="seq_notifications_pref_002",
            )
        )

        collection = self.service.create_collection(name="Coleccion Notificaciones Off")
        collection_id = collection["collection"]["collection_id"]
        self.service.add_collection_items(collection_id, [first["request_id"], second["request_id"]])
        self.service.get_collection_audit(collection_id)

        notifications = self.service.list_notifications(limit=100, collection_id=collection_id)
        self.assertTrue(notifications["ok"])
        self.assertEqual(notifications["count"], 0)

    def test_create_list_and_update_webhooks(self) -> None:
        created = self.service.create_webhook(
            name="Ops Alerts",
            url="https://example.test/hooks/ops",
            is_enabled=True,
            min_severity="warning",
            enabled_types=["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
        )
        self.assertTrue(created["ok"])
        webhook_id = created["webhook"]["webhook_id"]
        self.assertTrue(webhook_id)
        self.assertEqual(created["webhook"].get("payload_template_mode"), "default")
        self.assertIsNone(created["webhook"].get("payload_template"))
        self.assertEqual(created["webhook"].get("health_status"), "green")
        self.assertEqual(created["webhook"].get("alerts"), [])

        listed = self.service.list_webhooks(limit=100, include_disabled=True)
        self.assertTrue(listed["ok"])
        ids = [item["webhook_id"] for item in listed["webhooks"]]
        self.assertIn(webhook_id, ids)
        listed_item = next(item for item in listed["webhooks"] if item["webhook_id"] == webhook_id)
        self.assertIn("health_status", listed_item)
        self.assertIn("alerts", listed_item)

        updated = self.service.update_webhook(
            webhook_id=webhook_id,
            name="Ops Alerts Updated",
            is_enabled=False,
            min_severity="critical",
            enabled_types=["COLLECTION_ENTERED_RED"],
        )
        self.assertTrue(updated["ok"])
        self.assertEqual(updated["webhook"]["name"], "Ops Alerts Updated")
        self.assertFalse(updated["webhook"]["is_enabled"])
        self.assertEqual(updated["webhook"]["min_severity"], "critical")
        self.assertEqual(updated["webhook"]["enabled_types"], ["COLLECTION_ENTERED_RED"])
        self.assertEqual(updated["webhook"].get("payload_template_mode"), "default")

        enabled_only = self.service.list_webhooks(limit=100, include_disabled=False)
        enabled_ids = [item["webhook_id"] for item in enabled_only["webhooks"]]
        self.assertNotIn(webhook_id, enabled_ids)

    def test_get_webhook_health_returns_operational_summary_and_signals(self) -> None:
        created = self.service.create_webhook(
            name="Webhook Health",
            url="https://example.test/hooks/health",
            is_enabled=True,
        )
        webhook_id = created["webhook"]["webhook_id"]

        for index in range(1, 11):
            exhausted = index <= 3
            attempt_count = 4 if exhausted else 2
            self.runs_repository.create_webhook_delivery(
                {
                    "delivery_id": f"delivery_health_failed_{index}",
                    "webhook_id": webhook_id,
                    "notification_id": f"notif_health_failed_{index}",
                    "collection_id": "collection_health",
                    "payload": {"type": "HEALTH_STATUS_CHANGED", "index": index},
                    "delivery_status": "failed",
                    "attempt_count": attempt_count,
                    "max_attempts": 4,
                    "last_attempt_at": f"2026-01-01T10:{index:02d}:00+00:00",
                    "next_retry_at": None if exhausted else f"2026-01-01T11:{index:02d}:00+00:00",
                    "final_failure_at": f"2026-01-01T10:{index:02d}:00+00:00" if exhausted else None,
                    "is_test": False,
                    "template_mode": "default",
                    "auth_mode": "none",
                    "request_headers": {},
                    "response_status_code": 500,
                    "response_body": "error",
                    "error_message": f"Health failure #{index}",
                    "created_at": f"2026-01-01T10:{index:02d}:00+00:00",
                    "delivered_at": None,
                }
            )

        health = self.service.get_webhook_health(webhook_id=webhook_id, recent_limit=40, signals_limit=10)
        self.assertTrue(health["ok"])
        self.assertEqual(health["health_status"], "red")
        self.assertGreaterEqual(len(health["alerts"]), 1)

        summary = health["operational_summary"]
        self.assertEqual(summary["total_deliveries"], 10)
        self.assertEqual(summary["failed_deliveries"], 10)
        self.assertGreaterEqual(summary["exhausted_deliveries"], 3)
        self.assertGreater(summary["failure_ratio"], 0.9)
        self.assertEqual(summary["recent_failed_deliveries"], 10)

        signals = health["recent_signals"]
        self.assertGreaterEqual(len(signals), 1)
        first_signal = signals[0]
        self.assertIn("code", first_signal)
        self.assertIn("severity", first_signal)
        self.assertIn("message", first_signal)

    def test_get_webhooks_dashboard_includes_health_counters_and_active_alerts(self) -> None:
        risky = self.service.create_webhook(
            name="Webhook Dashboard Risky",
            url="https://example.test/hooks/dashboard-risky",
            is_enabled=True,
        )
        risky_id = risky["webhook"]["webhook_id"]

        healthy = self.service.create_webhook(
            name="Webhook Dashboard Healthy",
            url="https://example.test/hooks/dashboard-healthy",
            is_enabled=True,
        )
        healthy_id = healthy["webhook"]["webhook_id"]

        for index in range(1, 9):
            self.runs_repository.create_webhook_delivery(
                {
                    "delivery_id": f"delivery_dashboard_failed_{index}",
                    "webhook_id": risky_id,
                    "notification_id": f"notif_dashboard_failed_{index}",
                    "collection_id": "collection_dashboard",
                    "payload": {"index": index},
                    "delivery_status": "failed",
                    "attempt_count": 3,
                    "max_attempts": 4,
                    "last_attempt_at": f"2026-01-01T12:{index:02d}:00+00:00",
                    "next_retry_at": f"2026-01-01T13:{index:02d}:00+00:00",
                    "final_failure_at": None,
                    "is_test": False,
                    "template_mode": "default",
                    "auth_mode": "none",
                    "request_headers": {},
                    "response_status_code": 500,
                    "response_body": "error",
                    "error_message": f"Dashboard failure #{index}",
                    "created_at": f"2026-01-01T12:{index:02d}:00+00:00",
                    "delivered_at": None,
                }
            )

        self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": "delivery_dashboard_sent_001",
                "webhook_id": healthy_id,
                "notification_id": "notif_dashboard_sent_001",
                "collection_id": "collection_dashboard",
                "payload": {"status": "ok"},
                "delivery_status": "sent",
                "attempt_count": 1,
                "max_attempts": 4,
                "last_attempt_at": "2026-01-01T12:30:00+00:00",
                "next_retry_at": None,
                "final_failure_at": None,
                "is_test": False,
                "template_mode": "default",
                "auth_mode": "none",
                "request_headers": {},
                "response_status_code": 200,
                "response_body": "ok",
                "error_message": None,
                "created_at": "2026-01-01T12:30:00+00:00",
                "delivered_at": "2026-01-01T12:30:01+00:00",
            }
        )

        dashboard = self.service.get_webhooks_dashboard(top_limit=5, errors_limit=10)
        self.assertTrue(dashboard["ok"])
        self.assertEqual(dashboard["total_webhooks"], 2)
        self.assertGreaterEqual(dashboard["webhooks_red"], 1)
        self.assertGreaterEqual(dashboard["webhooks_green"], 1)
        self.assertIn("active_alerts", dashboard)
        self.assertGreaterEqual(len(dashboard["active_alerts"]), 1)

        alert_webhook_ids = {item["webhook_id"] for item in dashboard["active_alerts"]}
        self.assertIn(risky_id, alert_webhook_ids)

    def test_send_test_webhook_event_without_auth_registers_test_delivery(self) -> None:
        webhook = self.service.create_webhook(
            name="Webhook Test No Auth",
            url="https://example.test/hooks/test-no-auth",
            is_enabled=True,
            auth_mode="none",
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        captured_request: Dict[str, Any] = {}

        def fake_urlopen(request_obj: Any, timeout: int = 0) -> FakeWebhookHTTPResponse:
            captured_request["request"] = request_obj
            return FakeWebhookHTTPResponse(status_code=200, body="ok")

        with patch("src.services.sequence_plan_render_service.urlopen", side_effect=fake_urlopen):
            result = self.service.send_test_webhook_event(webhook_id)

        self.assertTrue(result["ok"])
        delivery = result["delivery"]
        self.assertTrue(delivery["is_test"])
        self.assertEqual(delivery["template_mode"], "default")
        self.assertEqual(delivery["collection_id"], WEBHOOK_TEST_COLLECTION_ID)

        payload = delivery["payload"]
        self.assertEqual(payload.get("event_type"), "test_event")
        self.assertEqual(payload.get("webhook_id"), webhook_id)
        self.assertEqual(payload.get("webhook_name"), "Webhook Test No Auth")
        self.assertEqual(payload.get("message"), "This is a test webhook event")
        self.assertTrue(payload.get("created_at"))

        request_obj = captured_request.get("request")
        self.assertIsNotNone(request_obj)
        assert request_obj is not None
        request_headers = {key.lower(): value for key, value in request_obj.header_items()}
        self.assertNotIn("authorization", request_headers)
        self.assertNotIn("x-webhook-signature", request_headers)
        self.assertNotIn("x-webhook-timestamp", request_headers)

        body_bytes = request_obj.data if isinstance(request_obj.data, bytes) else b"{}"
        sent_payload = json.loads(body_bytes.decode("utf-8"))
        self.assertEqual(sent_payload, payload)

    def test_send_test_webhook_event_with_hmac_applies_signature(self) -> None:
        secret = "test-hmac-secret"
        webhook = self.service.create_webhook(
            name="Webhook Test HMAC",
            url="https://example.test/hooks/test-hmac",
            is_enabled=True,
            auth_mode="hmac_sha256",
            secret_token=secret,
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        captured_request: Dict[str, Any] = {}

        def fake_urlopen(request_obj: Any, timeout: int = 0) -> FakeWebhookHTTPResponse:
            captured_request["request"] = request_obj
            return FakeWebhookHTTPResponse(status_code=200, body="ok")

        with patch("src.services.sequence_plan_render_service.urlopen", side_effect=fake_urlopen):
            result = self.service.send_test_webhook_event(webhook_id)

        self.assertTrue(result["ok"])
        delivery = result["delivery"]
        self.assertTrue(delivery["is_test"])
        self.assertEqual(delivery["auth_mode"], "hmac_sha256")

        request_obj = captured_request.get("request")
        self.assertIsNotNone(request_obj)
        assert request_obj is not None
        request_headers = {key.lower(): value for key, value in request_obj.header_items()}
        timestamp = request_headers.get("x-webhook-timestamp")
        signature = request_headers.get("x-webhook-signature")
        self.assertIsNotNone(timestamp)
        self.assertIsNotNone(signature)
        self.assertEqual(request_headers.get("x-webhook-id"), webhook_id)

        body_bytes = request_obj.data if isinstance(request_obj.data, bytes) else b""
        body_text = body_bytes.decode("utf-8")
        expected_signature = "sha256=" + hmac.new(
            secret.encode("utf-8"),
            f"{timestamp}.{body_text}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        self.assertEqual(signature, expected_signature)

        self.assertEqual(delivery.get("signature_timestamp"), timestamp)

    def test_send_test_webhook_event_applies_custom_payload_template(self) -> None:
        webhook = self.service.create_webhook(
            name="Webhook Test Custom",
            url="https://example.test/hooks/test-custom",
            is_enabled=True,
            payload_template_mode="custom",
            payload_template={
                "event": "{{event_type}}",
                "target": "{{webhook_name}}",
                "summary": "{{message}}",
            },
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        with patch(
            "src.services.sequence_plan_render_service.urlopen",
            return_value=FakeWebhookHTTPResponse(status_code=200, body="ok"),
        ):
            result = self.service.send_test_webhook_event(webhook_id)

        self.assertTrue(result["ok"])
        delivery = result["delivery"]
        self.assertTrue(delivery["is_test"])
        self.assertEqual(delivery["template_mode"], "custom")
        self.assertEqual(
            delivery["payload"],
            {
                "event": "test_event",
                "target": "Webhook Test Custom",
                "summary": "This is a test webhook event",
            },
        )

    def test_preview_webhook_payload_default_mode_does_not_send_http(self) -> None:
        webhook = self.service.create_webhook(
            name="Webhook Preview Default",
            url="https://example.test/hooks/preview-default",
            is_enabled=True,
            payload_template_mode="default",
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        with patch("src.services.sequence_plan_render_service.urlopen") as mocked_urlopen:
            preview = self.service.preview_webhook_payload(webhook_id=webhook_id)

        self.assertTrue(preview["ok"])
        self.assertEqual(preview["webhook_id"], webhook_id)
        self.assertEqual(preview["auth_mode"], "none")
        self.assertEqual(preview["payload_template_mode"], "default")
        self.assertEqual(preview["signature_preview"], None)
        payload = preview["rendered_payload"]
        self.assertEqual(payload.get("event_type"), "test_event")
        self.assertEqual(payload.get("webhook_id"), webhook_id)
        self.assertEqual(payload.get("message"), "This is a test webhook event")
        self.assertIn("Content-Type", preview["rendered_headers"])
        self.assertIn("User-Agent", preview["rendered_headers"])
        mocked_urlopen.assert_not_called()

    def test_preview_webhook_payload_compact_mode_uses_reduced_payload(self) -> None:
        webhook = self.service.create_webhook(
            name="Webhook Preview Compact",
            url="https://example.test/hooks/preview-compact",
            is_enabled=True,
            payload_template_mode="compact",
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        preview = self.service.preview_webhook_payload(
            webhook_id=webhook_id,
            event_type="health_ping",
            sample_data={
                "custom_debug": "ignore_me",
                "message": "Compact preview message",
            },
        )

        self.assertTrue(preview["ok"])
        self.assertEqual(preview["payload_template_mode"], "compact")
        payload = preview["rendered_payload"]
        self.assertEqual(payload.get("event_type"), "health_ping")
        self.assertEqual(payload.get("message"), "Compact preview message")
        self.assertNotIn("custom_debug", payload)

    def test_preview_webhook_payload_with_bearer_shows_authorization_header(self) -> None:
        webhook = self.service.create_webhook(
            name="Webhook Preview Bearer",
            url="https://example.test/hooks/preview-bearer",
            is_enabled=True,
            auth_mode="bearer",
            secret_token="preview-bearer-secret",
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        preview = self.service.preview_webhook_payload(webhook_id=webhook_id)

        self.assertTrue(preview["ok"])
        self.assertEqual(preview["auth_mode"], "bearer")
        headers = preview["rendered_headers"]
        self.assertEqual(headers.get("Authorization"), "Bearer ***")
        self.assertIsNone(preview["signature_preview"])

    def test_preview_webhook_payload_with_hmac_shows_signature_preview(self) -> None:
        webhook = self.service.create_webhook(
            name="Webhook Preview HMAC",
            url="https://example.test/hooks/preview-hmac",
            is_enabled=True,
            auth_mode="hmac_sha256",
            secret_token="preview-hmac-secret",
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        preview = self.service.preview_webhook_payload(webhook_id=webhook_id)

        self.assertTrue(preview["ok"])
        self.assertEqual(preview["auth_mode"], "hmac_sha256")
        headers = preview["rendered_headers"]
        self.assertTrue(headers.get("X-Webhook-Timestamp"))
        self.assertEqual(headers.get("X-Webhook-Id"), webhook_id)
        self.assertTrue(preview.get("signature_preview"))
        self.assertEqual(headers.get("X-Webhook-Signature"), preview.get("signature_preview"))

    def test_list_webhook_deliveries_filters_is_test(self) -> None:
        webhook = self.service.create_webhook(
            name="Webhook Deliveries Test Filter",
            url="https://example.test/hooks/deliveries-filter",
            is_enabled=True,
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": "delivery_filter_test",
                "webhook_id": webhook_id,
                "notification_id": "notif_filter_test",
                "collection_id": "collection_filter",
                "payload": {"event_type": "test_event"},
                "delivery_status": "sent",
                "is_test": True,
                "template_mode": "default",
                "auth_mode": "none",
                "request_headers": {},
                "created_at": "2026-01-01T10:00:00+00:00",
                "delivered_at": "2026-01-01T10:00:01+00:00",
            }
        )
        self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": "delivery_filter_notification",
                "webhook_id": webhook_id,
                "notification_id": "notif_filter_notification",
                "collection_id": "collection_filter",
                "payload": {"type": "HEALTH_STATUS_CHANGED"},
                "delivery_status": "sent",
                "is_test": False,
                "template_mode": "default",
                "auth_mode": "none",
                "request_headers": {},
                "created_at": "2026-01-01T10:00:02+00:00",
                "delivered_at": "2026-01-01T10:00:03+00:00",
            }
        )

        tests_only = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id, is_test=True)
        self.assertTrue(tests_only["ok"])
        self.assertEqual(tests_only["count"], 1)
        self.assertTrue(tests_only["deliveries"][0]["is_test"])

        notifications_only = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id, is_test=False)
        self.assertTrue(notifications_only["ok"])
        self.assertEqual(notifications_only["count"], 1)
        self.assertFalse(notifications_only["deliveries"][0]["is_test"])

    def test_compare_webhook_deliveries_returns_payload_and_headers_diff(self) -> None:
        webhook = self.service.create_webhook(
            name="Webhook Compare",
            url="https://example.test/hooks/compare",
            is_enabled=True,
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": "delivery_compare_left",
                "webhook_id": webhook_id,
                "notification_id": "notif_compare",
                "collection_id": "collection_compare",
                "payload": {"event": "alpha", "stable": 1, "left_only": True},
                "delivery_status": "sent",
                "is_test": False,
                "template_mode": "default",
                "auth_mode": "none",
                "request_headers": {"Content-Type": "application/json", "X-Left": "left"},
                "created_at": "2026-01-01T11:00:00+00:00",
                "delivered_at": "2026-01-01T11:00:01+00:00",
            }
        )
        self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": "delivery_compare_right",
                "webhook_id": webhook_id,
                "notification_id": "notif_compare",
                "collection_id": "collection_compare",
                "payload": {"event": "beta", "stable": 1, "right_only": 99},
                "delivery_status": "sent",
                "is_test": True,
                "template_mode": "compact",
                "auth_mode": "hmac_sha256",
                "request_headers": {"Content-Type": "application/json", "X-Right": "right"},
                "created_at": "2026-01-01T11:00:02+00:00",
                "delivered_at": "2026-01-01T11:00:03+00:00",
            }
        )

        compared = self.service.compare_webhook_deliveries(
            left_delivery_id="delivery_compare_left",
            right_delivery_id="delivery_compare_right",
        )

        self.assertTrue(compared["ok"])
        self.assertEqual(compared["left_delivery_id"], "delivery_compare_left")
        self.assertEqual(compared["right_delivery_id"], "delivery_compare_right")
        self.assertEqual(compared["auth_mode_left"], "none")
        self.assertEqual(compared["auth_mode_right"], "hmac_sha256")
        self.assertEqual(compared["payload_template_mode_left"], "default")
        self.assertEqual(compared["payload_template_mode_right"], "compact")

        payload_diff = compared["payload_diff"]
        self.assertEqual(payload_diff["removed"].get("left_only"), True)
        self.assertEqual(payload_diff["added"].get("right_only"), 99)
        self.assertEqual(payload_diff["changed"].get("event"), {"left": "alpha", "right": "beta"})
        self.assertEqual(payload_diff["unchanged_count"], 1)

        headers_diff = compared["headers_diff"]
        self.assertEqual(headers_diff["removed"].get("X-Left"), "left")
        self.assertEqual(headers_diff["added"].get("X-Right"), "right")

    def test_webhook_delivery_sent_when_notification_emitted(self) -> None:
        webhook = self.service.create_webhook(
            name="Delivery Sent",
            url="https://example.test/hooks/sent",
            is_enabled=True,
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        with patch(
            "src.services.sequence_plan_render_service.urlopen",
            return_value=FakeWebhookHTTPResponse(status_code=200, body="accepted"),
        ) as mocked_urlopen:
            execution = self.service.plan_and_create_jobs(
                SequencePlanRequest(
                    script_text="INT. WEBHOOK - DIA. Trigger sent delivery.",
                    project_id="project_webhook_sent",
                    sequence_id="seq_webhook_sent_001",
                )
            )
            collection = self.service.create_collection(name="Coleccion Webhook Sent")
            collection_id = collection["collection"]["collection_id"]
            self.service.add_collection_items(collection_id, [execution["request_id"]])
            self.service.get_collection_audit(collection_id)

        request_obj = mocked_urlopen.call_args[0][0]
        request_headers = {key.lower(): value for key, value in request_obj.header_items()}
        self.assertNotIn("authorization", request_headers)
        self.assertNotIn("x-webhook-signature", request_headers)
        self.assertNotIn("x-webhook-timestamp", request_headers)

        request_body_bytes = request_obj.data if isinstance(request_obj.data, bytes) else b"{}"
        request_payload = json.loads(request_body_bytes.decode("utf-8"))

        deliveries = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id)
        self.assertTrue(deliveries["ok"])
        self.assertGreaterEqual(deliveries["count"], 1)

        first_delivery = deliveries["deliveries"][0]
        self.assertEqual(first_delivery["delivery_status"], "sent")
        self.assertEqual(first_delivery["attempt_count"], 1)
        self.assertIsNotNone(first_delivery["last_attempt_at"])
        self.assertFalse(first_delivery["is_test"])
        self.assertEqual(first_delivery["auth_mode"], "none")
        self.assertEqual(first_delivery["template_mode"], "default")
        self.assertIsNone(first_delivery["signature_timestamp"])
        self.assertNotIn("Authorization", first_delivery["request_headers"])
        self.assertEqual(first_delivery["response_status_code"], 200)
        self.assertIsNone(first_delivery["error_message"])
        self.assertEqual(first_delivery["payload"], request_payload)

        payload = first_delivery["payload"]
        self.assertIn("notification_id", payload)
        self.assertIn("collection_id", payload)
        self.assertIn("collection_name", payload)
        self.assertIn("type", payload)
        self.assertIn("severity", payload)
        self.assertIn("message", payload)
        self.assertIn("created_at", payload)
        self.assertIn("health_status", payload)

    def test_webhook_compact_template_sends_reduced_payload(self) -> None:
        webhook = self.service.create_webhook(
            name="Delivery Compact",
            url="https://example.test/hooks/compact",
            is_enabled=True,
            payload_template_mode="compact",
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        captured_request: Dict[str, Any] = {}

        def fake_urlopen(request_obj: Any, timeout: int = 0) -> FakeWebhookHTTPResponse:
            captured_request["request"] = request_obj
            return FakeWebhookHTTPResponse(status_code=200, body="accepted")

        with patch("src.services.sequence_plan_render_service.urlopen", side_effect=fake_urlopen):
            execution = self.service.plan_and_create_jobs(
                SequencePlanRequest(
                    script_text="INT. WEBHOOK - DIA. Trigger compact payload.",
                    project_id="project_webhook_compact",
                    sequence_id="seq_webhook_compact_001",
                )
            )
            collection = self.service.create_collection(name="Coleccion Webhook Compact")
            collection_id = collection["collection"]["collection_id"]
            self.service.add_collection_items(collection_id, [execution["request_id"]])
            self.service.get_collection_audit(collection_id)

        request_obj = captured_request.get("request")
        self.assertIsNotNone(request_obj)
        assert request_obj is not None
        body_bytes = request_obj.data if isinstance(request_obj.data, bytes) else b"{}"
        sent_payload = json.loads(body_bytes.decode("utf-8"))

        self.assertEqual(
            set(sent_payload.keys()),
            {
                "notification_id",
                "collection_id",
                "type",
                "severity",
                "message",
                "created_at",
                "health_status",
            },
        )
        self.assertNotIn("collection_name", sent_payload)

        deliveries = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id)
        self.assertTrue(deliveries["ok"])
        self.assertGreaterEqual(deliveries["count"], 1)
        first_delivery = deliveries["deliveries"][0]
        self.assertEqual(first_delivery["template_mode"], "compact")
        self.assertEqual(first_delivery["payload"], sent_payload)

    def test_webhook_custom_template_interpolates_and_saves_final_payload(self) -> None:
        webhook = self.service.create_webhook(
            name="Delivery Custom",
            url="https://example.test/hooks/custom",
            is_enabled=True,
            payload_template_mode="custom",
            payload_template={
                "event": "{{type}}",
                "level": "{{severity}}",
                "notification": {
                    "id": "{{notification_id}}",
                    "collection": "{{collection_id}}",
                    "health": "{{health_status}}",
                },
                "summary": "[{{severity}}] {{message}}",
                "webhook": "{{webhook_id}}",
            },
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        captured_request: Dict[str, Any] = {}

        def fake_urlopen(request_obj: Any, timeout: int = 0) -> FakeWebhookHTTPResponse:
            captured_request["request"] = request_obj
            return FakeWebhookHTTPResponse(status_code=200, body="accepted")

        with patch("src.services.sequence_plan_render_service.urlopen", side_effect=fake_urlopen):
            execution = self.service.plan_and_create_jobs(
                SequencePlanRequest(
                    script_text="INT. WEBHOOK - DIA. Trigger custom payload.",
                    project_id="project_webhook_custom",
                    sequence_id="seq_webhook_custom_001",
                )
            )
            collection = self.service.create_collection(name="Coleccion Webhook Custom")
            collection_id = collection["collection"]["collection_id"]
            self.service.add_collection_items(collection_id, [execution["request_id"]])
            self.service.get_collection_audit(collection_id)

        request_obj = captured_request.get("request")
        self.assertIsNotNone(request_obj)
        assert request_obj is not None
        body_bytes = request_obj.data if isinstance(request_obj.data, bytes) else b"{}"
        sent_payload = json.loads(body_bytes.decode("utf-8"))

        self.assertIn("event", sent_payload)
        self.assertIn("level", sent_payload)
        self.assertIn("notification", sent_payload)
        self.assertIn("summary", sent_payload)
        self.assertIn("webhook", sent_payload)
        self.assertEqual(sent_payload["webhook"], webhook_id)
        self.assertEqual(sent_payload["event"], "HEALTH_STATUS_CHANGED")

        deliveries = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id)
        self.assertTrue(deliveries["ok"])
        self.assertGreaterEqual(deliveries["count"], 1)
        first_delivery = deliveries["deliveries"][0]
        self.assertEqual(first_delivery["template_mode"], "custom")
        self.assertEqual(first_delivery["payload"], sent_payload)

    def test_webhook_delivery_failed_when_destination_unreachable(self) -> None:
        webhook = self.service.create_webhook(
            name="Delivery Failed",
            url="https://example.test/hooks/failed",
            is_enabled=True,
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        with patch(
            "src.services.sequence_plan_render_service.urlopen",
            side_effect=URLError("connection refused"),
        ):
            execution = self.service.plan_and_create_jobs(
                SequencePlanRequest(
                    script_text="INT. WEBHOOK - DIA. Trigger failed delivery.",
                    project_id="project_webhook_failed",
                    sequence_id="seq_webhook_failed_001",
                )
            )
            collection = self.service.create_collection(name="Coleccion Webhook Failed")
            collection_id = collection["collection"]["collection_id"]
            self.service.add_collection_items(collection_id, [execution["request_id"]])
            self.service.get_collection_audit(collection_id)

        deliveries = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id)
        self.assertTrue(deliveries["ok"])
        self.assertGreaterEqual(deliveries["count"], 1)

        first_delivery = deliveries["deliveries"][0]
        self.assertEqual(first_delivery["delivery_status"], "failed")
        self.assertEqual(first_delivery["attempt_count"], 1)
        self.assertIsNotNone(first_delivery["last_attempt_at"])
        self.assertFalse(first_delivery["is_test"])
        self.assertIsNotNone(first_delivery["error_message"])
        self.assertIn("connection refused", str(first_delivery["error_message"]).lower())

    def test_webhook_bearer_auth_sends_authorization_header(self) -> None:
        secret = "bearer-token-123"
        webhook = self.service.create_webhook(
            name="Delivery Bearer",
            url="https://example.test/hooks/bearer",
            is_enabled=True,
            auth_mode="bearer",
            secret_token=secret,
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        captured_request: Dict[str, Any] = {}

        def fake_urlopen(request_obj: Any, timeout: int = 0) -> FakeWebhookHTTPResponse:
            captured_request["request"] = request_obj
            return FakeWebhookHTTPResponse(status_code=200, body="accepted")

        with patch("src.services.sequence_plan_render_service.urlopen", side_effect=fake_urlopen):
            execution = self.service.plan_and_create_jobs(
                SequencePlanRequest(
                    script_text="INT. WEBHOOK - DIA. Bearer header expected.",
                    project_id="project_webhook_bearer",
                    sequence_id="seq_webhook_bearer_001",
                )
            )
            collection = self.service.create_collection(name="Coleccion Webhook Bearer")
            collection_id = collection["collection"]["collection_id"]
            self.service.add_collection_items(collection_id, [execution["request_id"]])
            self.service.get_collection_audit(collection_id)

        request_obj = captured_request.get("request")
        self.assertIsNotNone(request_obj)
        assert request_obj is not None
        request_headers = {key.lower(): value for key, value in request_obj.header_items()}
        self.assertEqual(request_headers.get("authorization"), f"Bearer {secret}")

        deliveries = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id)
        self.assertTrue(deliveries["ok"])
        self.assertGreaterEqual(deliveries["count"], 1)
        first_delivery = deliveries["deliveries"][0]
        self.assertEqual(first_delivery["auth_mode"], "bearer")
        self.assertEqual(first_delivery["request_headers"].get("Authorization"), "Bearer ***")
        self.assertIsNone(first_delivery["signature_timestamp"])

    def test_webhook_hmac_sha256_generates_valid_signature_headers(self) -> None:
        secret = "hmac-secret-xyz"
        webhook = self.service.create_webhook(
            name="Delivery HMAC",
            url="https://example.test/hooks/hmac",
            is_enabled=True,
            auth_mode="hmac_sha256",
            secret_token=secret,
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        captured_request: Dict[str, Any] = {}

        def fake_urlopen(request_obj: Any, timeout: int = 0) -> FakeWebhookHTTPResponse:
            captured_request["request"] = request_obj
            return FakeWebhookHTTPResponse(status_code=200, body="accepted")

        with patch("src.services.sequence_plan_render_service.urlopen", side_effect=fake_urlopen):
            execution = self.service.plan_and_create_jobs(
                SequencePlanRequest(
                    script_text="INT. WEBHOOK - DIA. HMAC signature expected.",
                    project_id="project_webhook_hmac",
                    sequence_id="seq_webhook_hmac_001",
                )
            )
            collection = self.service.create_collection(name="Coleccion Webhook HMAC")
            collection_id = collection["collection"]["collection_id"]
            self.service.add_collection_items(collection_id, [execution["request_id"]])
            self.service.get_collection_audit(collection_id)

        request_obj = captured_request.get("request")
        self.assertIsNotNone(request_obj)
        assert request_obj is not None
        request_headers = {key.lower(): value for key, value in request_obj.header_items()}
        timestamp = request_headers.get("x-webhook-timestamp")
        signature = request_headers.get("x-webhook-signature")
        self.assertIsNotNone(timestamp)
        self.assertIsNotNone(signature)
        self.assertEqual(request_headers.get("x-webhook-id"), webhook_id)

        body_bytes = request_obj.data if isinstance(request_obj.data, bytes) else b""
        body_text = body_bytes.decode("utf-8")
        expected_signature = "sha256=" + hmac.new(
            secret.encode("utf-8"),
            f"{timestamp}.{body_text}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        self.assertEqual(signature, expected_signature)

        deliveries = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id)
        self.assertTrue(deliveries["ok"])
        self.assertGreaterEqual(deliveries["count"], 1)
        first_delivery = deliveries["deliveries"][0]
        self.assertEqual(first_delivery["auth_mode"], "hmac_sha256")
        self.assertEqual(first_delivery["signature_timestamp"], timestamp)
        self.assertEqual(first_delivery["request_headers"].get("X-Webhook-Signature"), signature)

    def test_webhook_filters_prevent_non_matching_deliveries(self) -> None:
        webhook = self.service.create_webhook(
            name="Critical Only",
            url="https://example.test/hooks/critical",
            is_enabled=True,
            min_severity="critical",
            enabled_types=["COLLECTION_ENTERED_RED"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        with patch(
            "src.services.sequence_plan_render_service.urlopen",
            return_value=FakeWebhookHTTPResponse(status_code=200, body="accepted"),
        ) as mocked_urlopen:
            execution = self.service.plan_and_create_jobs(
                SequencePlanRequest(
                    script_text="INT. WEBHOOK - DIA. Only warning notifications expected.",
                    project_id="project_webhook_filter",
                    sequence_id="seq_webhook_filter_001",
                )
            )
            collection = self.service.create_collection(name="Coleccion Webhook Filter")
            collection_id = collection["collection"]["collection_id"]
            self.service.add_collection_items(collection_id, [execution["request_id"]])
            self.service.get_collection_audit(collection_id)

        deliveries = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id)
        self.assertTrue(deliveries["ok"])
        self.assertEqual(deliveries["count"], 0)
        mocked_urlopen.assert_not_called()

    def test_retry_webhook_delivery_increments_attempt_count(self) -> None:
        webhook = self.service.create_webhook(
            name="Retry Delivery",
            url="https://example.test/hooks/retry",
            is_enabled=True,
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        with patch(
            "src.services.sequence_plan_render_service.urlopen",
            side_effect=URLError("connection refused"),
        ):
            execution = self.service.plan_and_create_jobs(
                SequencePlanRequest(
                    script_text="INT. WEBHOOK - DIA. Initial failed delivery for retry.",
                    project_id="project_webhook_retry",
                    sequence_id="seq_webhook_retry_001",
                )
            )
            collection = self.service.create_collection(name="Coleccion Webhook Retry")
            collection_id = collection["collection"]["collection_id"]
            self.service.add_collection_items(collection_id, [execution["request_id"]])
            self.service.get_collection_audit(collection_id)

        deliveries = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id)
        self.assertTrue(deliveries["ok"])
        self.assertGreaterEqual(deliveries["count"], 1)
        failed_delivery = deliveries["deliveries"][0]
        self.assertEqual(failed_delivery["delivery_status"], "failed")
        self.assertEqual(failed_delivery["attempt_count"], 1)

        with patch(
            "src.services.sequence_plan_render_service.urlopen",
            return_value=FakeWebhookHTTPResponse(status_code=200, body="accepted"),
        ):
            retried = self.service.retry_webhook_delivery(failed_delivery["delivery_id"])

        self.assertTrue(retried["ok"])
        self.assertEqual(retried["delivery"]["delivery_status"], "sent")
        self.assertEqual(retried["delivery"]["attempt_count"], 2)
        self.assertEqual(retried["delivery"]["response_status_code"], 200)
        self.assertIsNone(retried["delivery"]["error_message"])
        self.assertIsNotNone(retried["delivery"]["last_attempt_at"])

    def test_webhook_retry_timestamps_follow_backoff_policy_and_exhaustion(self) -> None:
        first = self.service._calculate_webhook_retry_timestamps(
            attempt_count=1,
            max_attempts=4,
            attempt_at="2026-01-01T00:00:00+00:00",
        )
        self.assertEqual(first["next_retry_at"], "2026-01-01T00:01:00+00:00")
        self.assertIsNone(first["final_failure_at"])

        second = self.service._calculate_webhook_retry_timestamps(
            attempt_count=2,
            max_attempts=4,
            attempt_at="2026-01-01T00:00:00+00:00",
        )
        self.assertEqual(second["next_retry_at"], "2026-01-01T00:05:00+00:00")
        self.assertIsNone(second["final_failure_at"])

        third = self.service._calculate_webhook_retry_timestamps(
            attempt_count=3,
            max_attempts=4,
            attempt_at="2026-01-01T00:00:00+00:00",
        )
        self.assertEqual(third["next_retry_at"], "2026-01-01T00:15:00+00:00")
        self.assertIsNone(third["final_failure_at"])

        exhausted = self.service._calculate_webhook_retry_timestamps(
            attempt_count=4,
            max_attempts=4,
            attempt_at="2026-01-01T00:00:00+00:00",
        )
        self.assertIsNone(exhausted["next_retry_at"])
        self.assertEqual(exhausted["final_failure_at"], "2026-01-01T00:00:00+00:00")

    def test_process_webhook_delivery_retries_processes_only_due_eligible_deliveries(self) -> None:
        webhook = self.service.create_webhook(
            name="Batch Retry",
            url="https://example.test/hooks/process",
            is_enabled=True,
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        base_now = "2026-01-01T10:00:00+00:00"
        due_delivery = self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": "delivery_due_001",
                "webhook_id": webhook_id,
                "notification_id": "notif_due",
                "collection_id": "collection_due",
                "payload": {"message": "due"},
                "delivery_status": "failed",
                "attempt_count": 1,
                "max_attempts": 4,
                "last_attempt_at": "2026-01-01T09:50:00+00:00",
                "next_retry_at": "2026-01-01T09:55:00+00:00",
                "final_failure_at": None,
                "auth_mode": "none",
                "request_headers": {},
                "signature_timestamp": None,
                "response_status_code": None,
                "response_body": None,
                "error_message": "initial failure",
                "created_at": "2026-01-01T09:45:00+00:00",
                "delivered_at": None,
            }
        )
        self.assertEqual(due_delivery["delivery_id"], "delivery_due_001")

        self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": "delivery_not_due_001",
                "webhook_id": webhook_id,
                "notification_id": "notif_not_due",
                "collection_id": "collection_due",
                "payload": {"message": "not-due"},
                "delivery_status": "failed",
                "attempt_count": 1,
                "max_attempts": 4,
                "last_attempt_at": "2026-01-01T09:50:00+00:00",
                "next_retry_at": "2026-01-01T10:30:00+00:00",
                "final_failure_at": None,
                "auth_mode": "none",
                "request_headers": {},
                "signature_timestamp": None,
                "response_status_code": None,
                "response_body": None,
                "error_message": "initial failure",
                "created_at": "2026-01-01T09:46:00+00:00",
                "delivered_at": None,
            }
        )

        with patch("src.services.sequence_plan_render_service.urlopen", return_value=FakeWebhookHTTPResponse(status_code=200, body="ok")):
            with patch.object(self.service, "_now_iso", return_value=base_now):
                processed = self.service.process_webhook_delivery_retries(limit=100)

        self.assertTrue(processed["ok"])
        self.assertEqual(processed["processed_count"], 1)
        self.assertEqual(processed["sent_count"], 1)
        self.assertEqual(processed["failed_count"], 0)
        self.assertEqual(processed["exhausted_count"], 0)
        self.assertEqual(processed["deliveries"][0]["delivery_id"], "delivery_due_001")
        self.assertEqual(processed["deliveries"][0]["delivery_status"], "sent")
        self.assertEqual(processed["deliveries"][0]["attempt_count"], 2)

        untouched = self.runs_repository.get_webhook_delivery("delivery_not_due_001")
        self.assertIsNotNone(untouched)
        assert untouched is not None
        self.assertEqual(untouched["attempt_count"], 1)

    def test_process_webhook_delivery_retries_does_not_reprocess_ineligible_deliveries(self) -> None:
        webhook = self.service.create_webhook(
            name="Batch Retry Ineligible",
            url="https://example.test/hooks/process-ineligible",
            is_enabled=True,
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": "delivery_sent_001",
                "webhook_id": webhook_id,
                "notification_id": "notif_sent",
                "collection_id": "collection_x",
                "payload": {"message": "already sent"},
                "delivery_status": "sent",
                "attempt_count": 1,
                "max_attempts": 4,
                "last_attempt_at": "2026-01-01T10:00:00+00:00",
                "next_retry_at": None,
                "final_failure_at": None,
                "auth_mode": "none",
                "request_headers": {},
                "signature_timestamp": None,
                "response_status_code": 200,
                "response_body": "ok",
                "error_message": None,
                "created_at": "2026-01-01T09:00:00+00:00",
                "delivered_at": "2026-01-01T10:00:00+00:00",
            }
        )

        self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": "delivery_exhausted_001",
                "webhook_id": webhook_id,
                "notification_id": "notif_exhausted",
                "collection_id": "collection_x",
                "payload": {"message": "exhausted"},
                "delivery_status": "failed",
                "attempt_count": 4,
                "max_attempts": 4,
                "last_attempt_at": "2026-01-01T10:00:00+00:00",
                "next_retry_at": None,
                "final_failure_at": "2026-01-01T10:00:00+00:00",
                "auth_mode": "none",
                "request_headers": {},
                "signature_timestamp": None,
                "response_status_code": None,
                "response_body": None,
                "error_message": "final failure",
                "created_at": "2026-01-01T09:00:00+00:00",
                "delivered_at": None,
            }
        )

        with patch("src.services.sequence_plan_render_service.urlopen") as mocked_urlopen:
            processed = self.service.process_webhook_delivery_retries(limit=100)

        self.assertTrue(processed["ok"])
        self.assertEqual(processed["processed_count"], 0)
        self.assertEqual(processed["deliveries"], [])
        mocked_urlopen.assert_not_called()

    def test_process_webhook_delivery_retries_marks_delivery_exhausted_at_max_attempts(self) -> None:
        webhook = self.service.create_webhook(
            name="Batch Retry Exhaust",
            url="https://example.test/hooks/process-exhaust",
            is_enabled=True,
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": "delivery_exhaust_me",
                "webhook_id": webhook_id,
                "notification_id": "notif_exhaust_me",
                "collection_id": "collection_exhaust",
                "payload": {"message": "will exhaust"},
                "delivery_status": "failed",
                "attempt_count": 1,
                "max_attempts": 2,
                "last_attempt_at": "2026-01-01T09:00:00+00:00",
                "next_retry_at": "2026-01-01T09:01:00+00:00",
                "final_failure_at": None,
                "auth_mode": "none",
                "request_headers": {},
                "signature_timestamp": None,
                "response_status_code": None,
                "response_body": None,
                "error_message": "first failure",
                "created_at": "2026-01-01T08:59:00+00:00",
                "delivered_at": None,
            }
        )

        with patch(
            "src.services.sequence_plan_render_service.urlopen",
            side_effect=URLError("still unreachable"),
        ):
            with patch.object(self.service, "_now_iso", return_value="2026-01-01T10:00:00+00:00"):
                processed = self.service.process_webhook_delivery_retries(limit=100)

        self.assertEqual(processed["processed_count"], 1)
        self.assertEqual(processed["sent_count"], 0)
        self.assertEqual(processed["failed_count"], 1)
        self.assertEqual(processed["exhausted_count"], 1)

        delivery = processed["deliveries"][0]
        self.assertEqual(delivery["delivery_id"], "delivery_exhaust_me")
        self.assertEqual(delivery["delivery_status"], "failed")
        self.assertEqual(delivery["attempt_count"], 2)
        self.assertEqual(delivery["max_attempts"], 2)
        self.assertIsNone(delivery["next_retry_at"])
        self.assertEqual(delivery["final_failure_at"], "2026-01-01T10:00:00+00:00")

    def test_retry_webhook_delivery_requires_failed_status(self) -> None:
        webhook = self.service.create_webhook(
            name="Retry Sent Not Allowed",
            url="https://example.test/hooks/retry-not-allowed",
            is_enabled=True,
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED", "MISSING_BEST_EXECUTION"],
        )
        webhook_id = webhook["webhook"]["webhook_id"]

        with patch(
            "src.services.sequence_plan_render_service.urlopen",
            return_value=FakeWebhookHTTPResponse(status_code=200, body="accepted"),
        ):
            execution = self.service.plan_and_create_jobs(
                SequencePlanRequest(
                    script_text="INT. WEBHOOK - DIA. Sent delivery cannot retry.",
                    project_id="project_webhook_sent_retry",
                    sequence_id="seq_webhook_sent_retry_001",
                )
            )
            collection = self.service.create_collection(name="Coleccion Webhook Sent Retry")
            collection_id = collection["collection"]["collection_id"]
            self.service.add_collection_items(collection_id, [execution["request_id"]])
            self.service.get_collection_audit(collection_id)

        deliveries = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id)
        self.assertTrue(deliveries["ok"])
        self.assertGreaterEqual(deliveries["count"], 1)
        sent_delivery = deliveries["deliveries"][0]
        self.assertEqual(sent_delivery["delivery_status"], "sent")

        with self.assertRaises(ValueError):
            self.service.retry_webhook_delivery(sent_delivery["delivery_id"])

    def test_retry_webhook_delivery_raises_when_missing(self) -> None:
        with self.assertRaises(SequenceWebhookDeliveryNotFoundError):
            self.service.retry_webhook_delivery("missing-webhook-delivery-id")

    def test_alert_routing_rules_crud_lifecycle(self) -> None:
        channel = self.service.create_notification_channel(
            channel_type="slack",
            name="Routing Slack",
            config={"webhook_url": "https://hooks.slack.com/services/T123/B123/C123"},
        )
        channel_id = str(channel["channel"]["channel_id"])

        created = self.service.create_alert_routing_rule(
            name="Warn to Slack",
            target_channel_id=channel_id,
            target_channel_kind="notification_channel",
            match_types=["HEALTH_STATUS_CHANGED"],
            min_severity="warning",
            is_enabled=True,
            match_collection_id=None,
            match_health_status="yellow",
        )
        self.assertTrue(created["ok"])
        rule = created["rule"]
        rule_id = str(rule["rule_id"])
        self.assertTrue(rule_id)
        self.assertEqual(rule["target_channel_id"], channel_id)
        self.assertEqual(rule["target_channel_kind"], "notification_channel")
        self.assertEqual(rule["match_types"], ["HEALTH_STATUS_CHANGED"])

        listed = self.service.list_alert_routing_rules(limit=100, include_disabled=True)
        self.assertTrue(listed["ok"])
        self.assertIn(rule_id, [item["rule_id"] for item in listed["rules"]])

        updated = self.service.update_alert_routing_rule(
            rule_id=rule_id,
            name="Warn to Slack Updated",
            is_enabled=False,
            min_severity="critical",
            match_collection_id="collection_abc",
            match_health_status="red",
        )
        self.assertTrue(updated["ok"])
        self.assertEqual(updated["rule"]["name"], "Warn to Slack Updated")
        self.assertFalse(updated["rule"]["is_enabled"])
        self.assertEqual(updated["rule"]["min_severity"], "critical")
        self.assertEqual(updated["rule"]["match_collection_id"], "collection_abc")
        self.assertEqual(updated["rule"]["match_health_status"], "red")

        deleted = self.service.delete_alert_routing_rule(rule_id)
        self.assertTrue(deleted["ok"])
        self.assertTrue(deleted["deleted"])

        listed_after_delete = self.service.list_alert_routing_rules(limit=100, include_disabled=True)
        self.assertNotIn(rule_id, [item["rule_id"] for item in listed_after_delete["rules"]])

        with self.assertRaises(SequenceAlertRoutingRuleNotFoundError):
            self.service.delete_alert_routing_rule(rule_id)

    def test_alert_routing_rules_route_and_dedupe_notification_channel_deliveries(self) -> None:
        slack_channel = self.service.create_notification_channel(
            channel_type="slack",
            name="Slack Routed",
            config={"webhook_url": "https://hooks.slack.com/services/T999/B999/RULE"},
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED"],
        )
        slack_channel_id = str(slack_channel["channel"]["channel_id"])

        telegram_channel = self.service.create_notification_channel(
            channel_type="telegram",
            name="Telegram Routed",
            config={"bot_token": "token-xyz", "chat_id": "chat-xyz"},
            min_severity="critical",
            enabled_types=["COLLECTION_ENTERED_RED"],
        )
        telegram_channel_id = str(telegram_channel["channel"]["channel_id"])

        first_rule = self.service.create_alert_routing_rule(
            name="Rule A",
            target_channel_id=slack_channel_id,
            target_channel_kind="notification_channel",
            match_types=["HEALTH_STATUS_CHANGED"],
            min_severity="info",
        )
        second_rule = self.service.create_alert_routing_rule(
            name="Rule B duplicate destination",
            target_channel_id=slack_channel_id,
            target_channel_kind="notification_channel",
            match_types=["HEALTH_STATUS_CHANGED"],
            min_severity="info",
        )
        self.service.create_alert_routing_rule(
            name="Rule C unmatched",
            target_channel_id=telegram_channel_id,
            target_channel_kind="notification_channel",
            match_types=["COLLECTION_ENTERED_RED"],
            min_severity="critical",
        )

        collection = self.service.create_collection(name="Routing Collection")
        collection_id = str(collection["collection"]["collection_id"])

        with patch(
            "src.services.sequence_plan_render_service.urlopen",
            return_value=FakeWebhookHTTPResponse(status_code=200, body="ok"),
        ):
            self.service._emit_collection_notifications(
                collection_id=collection_id,
                health_status="yellow",
                best_request_id="best_request_001",
                total_executions=1,
                pending_review_count=0,
                failed_count=0,
                timeout_count=0,
                failed_red_threshold=2,
                timeout_red_threshold=2,
            )

        deliveries = self.service.list_notification_channel_deliveries(
            limit=100,
            channel_id=slack_channel_id,
        )
        self.assertTrue(deliveries["ok"])
        self.assertEqual(deliveries["count"], 1)
        routed_delivery = deliveries["deliveries"][0]
        self.assertEqual(routed_delivery["channel_id"], slack_channel_id)
        self.assertIn(routed_delivery.get("routing_rule_id"), {
            first_rule["rule"]["rule_id"],
            second_rule["rule"]["rule_id"],
        })
        self.assertEqual(routed_delivery.get("delivery_status"), "sent")

        unmatched = self.service.list_notification_channel_deliveries(
            limit=100,
            channel_id=telegram_channel_id,
        )
        self.assertEqual(unmatched["count"], 0)

    def test_alert_routing_rules_support_webhook_target_delivery_trace(self) -> None:
        webhook = self.service.create_webhook(
            name="Routing Webhook",
            url="https://example.test/routing-webhook",
            is_enabled=True,
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED"],
        )
        webhook_id = str(webhook["webhook"]["webhook_id"])

        rule = self.service.create_alert_routing_rule(
            name="Webhook Route",
            target_channel_id=webhook_id,
            target_channel_kind="webhook",
            match_types=["HEALTH_STATUS_CHANGED"],
            min_severity="info",
        )

        collection = self.service.create_collection(name="Routing Webhook Collection")
        collection_id = str(collection["collection"]["collection_id"])

        with patch(
            "src.services.sequence_plan_render_service.urlopen",
            return_value=FakeWebhookHTTPResponse(status_code=200, body="ok"),
        ):
            self.service._emit_collection_notifications(
                collection_id=collection_id,
                health_status="yellow",
                best_request_id="best_request_002",
                total_executions=1,
                pending_review_count=0,
                failed_count=0,
                timeout_count=0,
                failed_red_threshold=2,
                timeout_red_threshold=2,
            )

        deliveries = self.service.list_webhook_deliveries(limit=100, webhook_id=webhook_id)
        self.assertTrue(deliveries["ok"])
        self.assertEqual(deliveries["count"], 1)
        delivery = deliveries["deliveries"][0]
        self.assertEqual(delivery.get("routing_rule_id"), rule["rule"]["rule_id"])
        self.assertEqual(delivery.get("routing_rule_name"), "Webhook Route")

    def test_create_alert_routing_rule_requires_existing_target(self) -> None:
        with self.assertRaises(ValueError):
            self.service.create_alert_routing_rule(
                name="Invalid Target",
                target_channel_id="missing-target-id",
                target_channel_kind="notification_channel",
                match_types=["HEALTH_STATUS_CHANGED"],
                min_severity="info",
            )

    def test_create_update_and_list_notification_channels(self) -> None:
        created = self.service.create_notification_channel(
            channel_type="slack",
            name="Ops Slack",
            config={"webhook_url": "https://hooks.slack.com/services/T000/B000/XXXXX"},
            min_severity="warning",
            enabled_types=["HEALTH_STATUS_CHANGED", "COLLECTION_ENTERED_RED"],
        )
        self.assertTrue(created["ok"])
        channel = created["channel"]
        channel_id = str(channel["channel_id"])
        self.assertEqual(channel["channel_type"], "slack")
        self.assertTrue(channel["config"].get("has_webhook_url"))

        listed = self.service.list_notification_channels(limit=100, include_disabled=True)
        self.assertTrue(listed["ok"])
        ids = [item["channel_id"] for item in listed["channels"]]
        self.assertIn(channel_id, ids)

        updated = self.service.update_notification_channel(
            channel_id=channel_id,
            name="Ops Slack Disabled",
            is_enabled=False,
            min_severity="critical",
        )
        self.assertTrue(updated["ok"])
        self.assertEqual(updated["channel"]["name"], "Ops Slack Disabled")
        self.assertFalse(updated["channel"]["is_enabled"])
        self.assertEqual(updated["channel"]["min_severity"], "critical")

    def test_send_test_notification_channel_event_telegram(self) -> None:
        created = self.service.create_notification_channel(
            channel_type="telegram",
            name="Ops Telegram",
            config={"bot_token": "bot-token-123", "chat_id": "chat-42"},
            min_severity="info",
            enabled_types=["HEALTH_STATUS_CHANGED"],
        )
        channel_id = str(created["channel"]["channel_id"])

        captured_requests: List[Any] = []

        def fake_urlopen(request_obj: Any, timeout: int = 0) -> FakeWebhookHTTPResponse:
            captured_requests.append(request_obj)
            return FakeWebhookHTTPResponse(status_code=200, body='{"ok":true}')

        with patch("src.services.sequence_plan_render_service.urlopen", side_effect=fake_urlopen):
            result = self.service.send_test_notification_channel_event(channel_id)

        self.assertTrue(result["ok"])
        self.assertEqual(result["delivery"]["delivery_status"], "sent")
        self.assertEqual(result["delivery"]["response_status_code"], 200)
        self.assertEqual(result["delivery"]["channel_type"], "telegram")
        self.assertEqual(len(captured_requests), 1)

        request_obj = captured_requests[0]
        self.assertIn("/botbot-token-123/sendMessage", str(request_obj.full_url))
        body = json.loads(request_obj.data.decode("utf-8"))
        self.assertEqual(body["chat_id"], "chat-42")
        self.assertIn("Severity:", str(body.get("text") or ""))

    def test_process_notification_channel_delivery_retries_handles_delivery_attempt_errors(self) -> None:
        created = self.service.create_notification_channel(
            channel_type="slack",
            name="Broken Slack",
            config={"webhook_url": "https://hooks.slack.com/services/T111/B111/ZZZZZ"},
        )
        channel_id = str(created["channel"]["channel_id"])
        self.runs_repository.update_notification_channel(
            channel_id,
            {
                "config": {"webhook_url": ""},
                "updated_at": "2026-01-01T10:00:00+00:00",
            },
        )

        self.runs_repository.create_notification_channel_delivery(
            {
                "delivery_id": "channel_retry_001",
                "channel_id": channel_id,
                "channel_type": "slack",
                "notification_id": "notif_channel_retry_001",
                "collection_id": "collection_channel_retry",
                "payload": {"message": "Retry me"},
                "message_text": "Retry me",
                "delivery_status": "failed",
                "attempt_count": 1,
                "max_attempts": 3,
                "last_attempt_at": "2026-01-01T09:00:00+00:00",
                "next_retry_at": "2026-01-01T09:01:00+00:00",
                "final_failure_at": None,
                "is_test": False,
                "response_status_code": None,
                "response_body": None,
                "error_message": "first failure",
                "created_at": "2026-01-01T08:59:00+00:00",
                "delivered_at": None,
            }
        )

        with patch.object(self.service, "_now_iso", return_value="2026-01-01T10:00:00+00:00"):
            processed = self.service.process_notification_channel_delivery_retries(limit=50)

        self.assertTrue(processed["ok"])
        self.assertEqual(processed["processed_count"], 1)
        self.assertEqual(processed["failed_count"], 1)
        self.assertEqual(processed["sent_count"], 0)
        delivery = processed["deliveries"][0]
        self.assertEqual(delivery["delivery_id"], "channel_retry_001")
        self.assertEqual(delivery["delivery_status"], "failed")
        self.assertEqual(delivery["attempt_count"], 2)
        self.assertIn("destination url is required", str(delivery.get("error_message") or ""))


if __name__ == "__main__":
    unittest.main()
