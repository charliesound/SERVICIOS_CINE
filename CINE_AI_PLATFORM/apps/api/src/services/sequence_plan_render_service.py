from __future__ import annotations

import hashlib
import hmac
import json
import re
import time
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
from uuid import uuid4

from src.schemas.sequence_plan import SequencePlanRequest
from src.services.render_jobs_service import RenderJobsService
from src.services.sequence_planner_service import SequencePlannerService
from src.storage.sequence_plan_runs_repository import SequencePlanRunsRepository


RECENT_STATUS_FILTER_VALUES = {"queued", "running", "succeeded", "failed", "timeout"}
RECENT_RANKING_FILTER_VALUES = {"most_stable", "most_problematic", "most_retries", "highest_success_ratio"}
REVIEW_STATUS_VALUES = {"pending_review", "approved", "rejected"}
NOTIFICATION_SEVERITY_VALUES = {"info", "warning", "critical"}
DEFAULT_NOTIFICATION_ENABLED_TYPES = [
    "HEALTH_STATUS_CHANGED",
    "COLLECTION_ENTERED_RED",
    "MISSING_BEST_EXECUTION",
    "PENDING_REVIEW_HIGH",
    "OPERATIONAL_FAILURE_THRESHOLD",
]
WEBHOOK_REQUEST_TIMEOUT_SECONDS = 1
WEBHOOK_RESPONSE_BODY_MAX_CHARS = 4000
WEBHOOK_AUTH_MODE_VALUES = {"none", "bearer", "hmac_sha256"}
WEBHOOK_PAYLOAD_TEMPLATE_MODE_VALUES = {"default", "compact", "custom"}
WEBHOOK_DELIVERY_DEFAULT_MAX_ATTEMPTS = 4
WEBHOOK_RETRY_BACKOFF_SECONDS = [60, 300, 900]
WEBHOOK_TEMPLATE_TOKEN_PATTERN = re.compile(r"\{\{\s*([a-zA-Z0-9_]+)\s*\}\}")
WEBHOOK_TEST_COLLECTION_ID = "__webhook_test_events__"
WEBHOOK_HEALTH_MIN_DELIVERIES_FOR_RATIO = 5
WEBHOOK_HEALTH_RED_FAILED_THRESHOLD = 8
WEBHOOK_HEALTH_RED_EXHAUSTED_THRESHOLD = 3
WEBHOOK_HEALTH_RED_FAILURE_RATIO_THRESHOLD = 0.60
WEBHOOK_HEALTH_YELLOW_FAILURE_RATIO_THRESHOLD = 0.30
WEBHOOK_HEALTH_YELLOW_RECENT_ERRORS_THRESHOLD = 3
WEBHOOK_HEALTH_YELLOW_RETRY_THRESHOLD = 6
WEBHOOK_HEALTH_RECENT_ERRORS_LOOKBACK_LIMIT = 250
NOTIFICATION_CHANNEL_TYPE_VALUES = {"webhook", "slack", "telegram"}
NOTIFICATION_CHANNEL_DELIVERY_DEFAULT_MAX_ATTEMPTS = 4
TELEGRAM_API_BASE_URL = "https://api.telegram.org"
ALERT_ROUTING_TARGET_KIND_VALUES = {"notification_channel", "webhook"}
COLLECTION_HEALTH_STATUS_VALUES = {"green", "yellow", "red"}


class SequencePlanRunNotFoundError(Exception):
    pass


class SequenceShotNotFoundError(Exception):
    pass


class SequenceCollectionNotFoundError(Exception):
    pass


class SequenceNotificationNotFoundError(Exception):
    pass


class SequenceWebhookNotFoundError(Exception):
    pass


class SequenceWebhookDeliveryNotFoundError(Exception):
    pass


class SequenceNotificationChannelNotFoundError(Exception):
    pass


class SequenceNotificationChannelDeliveryNotFoundError(Exception):
    pass


class SequenceAlertRoutingRuleNotFoundError(Exception):
    pass


class SequencePlanRenderService:
    def __init__(
        self,
        planner_service: SequencePlannerService,
        render_jobs_service: RenderJobsService,
        runs_repository: SequencePlanRunsRepository,
    ):
        self.planner_service = planner_service
        self.render_jobs_service = render_jobs_service
        self.runs_repository = runs_repository

    def plan_and_create_jobs(self, payload: SequencePlanRequest) -> Dict[str, Any]:
        plan = self.planner_service.plan_sequence(payload)
        request_id = str(uuid4())

        created_jobs: List[Dict[str, Any]] = []
        shot_job_links: List[Dict[str, Any]] = []
        job_ids: List[str] = []
        prompt_comparisons: List[Dict[str, Any]] = []

        render_inputs = plan.get("render_inputs") if isinstance(plan.get("render_inputs"), dict) else {}
        jobs_to_create = render_inputs.get("jobs") if isinstance(render_inputs.get("jobs"), list) else []

        for index, job_input in enumerate(jobs_to_create, start=1):
            if not isinstance(job_input, dict):
                continue

            request_payload = job_input.get("request_payload") if isinstance(job_input.get("request_payload"), dict) else {}
            render_context = job_input.get("render_context") if isinstance(job_input.get("render_context"), dict) else None

            created_job = self.render_jobs_service.create_job_from_client_payload(
                request_payload=request_payload,
                render_context=render_context,
            )

            shot_id = job_input.get("shot_id")
            if not isinstance(shot_id, str) or not shot_id.strip():
                shot_id = f"shot_{index:03d}"

            created_jobs.append(created_job)
            job_id = str(created_job.get("job_id"))
            job_ids.append(job_id)
            shot_job_link = {
                "shot_id": shot_id,
                "job_id": job_id,
                "request_id": request_id,
                "parent_job_id": None,
                "retry_index": 0,
                "reason": None,
            }
            shot_job_links.append(shot_job_link)
            prompt_comparison = self._build_prompt_comparison_entry(
                request_id=request_id,
                shot_id=shot_id,
                job_id=job_id,
                retry_index=0,
                job_input=job_input,
            )
            if prompt_comparison is not None:
                prompt_comparisons.append(prompt_comparison)

        now = self._now_iso()
        prompt_comparison_metrics = self._build_prompt_comparison_metrics(prompt_comparisons)
        run_record = {
            "request_id": request_id,
            "created_at": now,
            "updated_at": now,
            "request_payload": payload.model_dump(),
            "plan": plan,
            "prompt_comparisons": prompt_comparisons,
            "prompt_comparison_metrics": prompt_comparison_metrics,
            "created_jobs": created_jobs,
            "job_ids": job_ids,
            "shot_job_links": shot_job_links,
            "job_count": len(created_jobs),
            "is_favorite": False,
            "tags": [],
            "note": "",
            "review_status": "pending_review",
            "review_note": "",
            "reviewed_at": None,
        }
        persisted_record = self.runs_repository.create(run_record)

        return self._build_public_response(persisted_record)

    def retry_shot(
        self,
        request_id: str,
        shot_id: str,
        override_prompt: Optional[str] = None,
        override_negative_prompt: Optional[str] = None,
        override_render_context: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        run_record = self.runs_repository.get(request_id)
        if run_record is None:
            raise SequencePlanRunNotFoundError(f"Sequence plan-and-render request not found: {request_id}")

        normalized_shot_id = shot_id.strip()
        if not normalized_shot_id:
            raise ValueError("shot_id is required")

        shot_links = self._shot_links_for_shot(run_record, normalized_shot_id)
        if not shot_links:
            raise SequenceShotNotFoundError(f"Shot not found in request: {normalized_shot_id}")

        parent_link = shot_links[-1]
        parent_job_id = str(parent_link.get("job_id") or "").strip()
        if not parent_job_id:
            raise ValueError(f"No parent job found for shot_id={normalized_shot_id}")

        parent_job = self._resolve_job_by_id(run_record, parent_job_id)
        if parent_job is None:
            raise ValueError(f"Parent job data not found for job_id={parent_job_id}")

        request_payload = deepcopy(parent_job.get("request_payload") if isinstance(parent_job.get("request_payload"), dict) else {})
        if override_prompt:
            self._apply_prompt_override(request_payload, override_prompt)
        if override_negative_prompt:
            self._apply_negative_prompt_override(request_payload, override_negative_prompt)

        retry_index = len(shot_links)
        retry_context = override_render_context if isinstance(override_render_context, dict) else self._resolve_render_context(
            run_record,
            normalized_shot_id,
            parent_job,
        )
        trace_reason = reason.strip() if isinstance(reason, str) and reason.strip() else None

        self._inject_retry_trace_metadata(
            request_payload=request_payload,
            request_id=request_id,
            shot_id=normalized_shot_id,
            parent_job_id=parent_job_id,
            retry_index=retry_index,
            reason=trace_reason,
        )

        new_job = self.render_jobs_service.create_job_from_client_payload(
            request_payload=request_payload,
            render_context=retry_context,
            parent_job_id=parent_job_id,
        )
        new_job_id = str(new_job.get("job_id"))

        existing_created_jobs = run_record.get("created_jobs") if isinstance(run_record.get("created_jobs"), list) else []
        updated_created_jobs = [item for item in existing_created_jobs if isinstance(item, dict)] + [new_job]

        existing_job_ids = run_record.get("job_ids") if isinstance(run_record.get("job_ids"), list) else []
        updated_job_ids = [str(item) for item in existing_job_ids if isinstance(item, str)] + [new_job_id]

        existing_links = run_record.get("shot_job_links") if isinstance(run_record.get("shot_job_links"), list) else []
        updated_links = [item for item in existing_links if isinstance(item, dict)]
        updated_links.append(
            {
                "shot_id": normalized_shot_id,
                "job_id": new_job_id,
                "request_id": request_id,
                "parent_job_id": parent_job_id,
                "retry_index": retry_index,
                "reason": trace_reason,
            }
        )

        existing_prompt_comparisons = run_record.get("prompt_comparisons") if isinstance(run_record.get("prompt_comparisons"), list) else []
        updated_prompt_comparisons = [item for item in existing_prompt_comparisons if isinstance(item, dict)]
        updated_prompt_comparisons.append(
            {
                "request_id": request_id,
                "shot_id": normalized_shot_id,
                "job_id": new_job_id,
                "retry_index": retry_index,
                "prompt_base": self._resolve_retry_prompt_base(run_record, normalized_shot_id, request_payload),
                "prompt_enriched": self._extract_positive_prompt_text(request_payload),
                "semantic_summary_used": None,
                "semantic_enrichment_applied": False,
                "source": "retry",
            }
        )
        updated_prompt_comparison_metrics = self._build_prompt_comparison_metrics(updated_prompt_comparisons)

        self.runs_repository.update(
            request_id,
            {
                "updated_at": self._now_iso(),
                "prompt_comparisons": updated_prompt_comparisons,
                "prompt_comparison_metrics": updated_prompt_comparison_metrics,
                "created_jobs": updated_created_jobs,
                "job_ids": updated_job_ids,
                "shot_job_links": updated_links,
                "job_count": len(updated_created_jobs),
            },
        )

        return {
            "ok": True,
            "request_id": request_id,
            "shot_id": normalized_shot_id,
            "parent_job_id": parent_job_id,
            "new_job_id": new_job_id,
            "retry_index": retry_index,
            "status": str(new_job.get("status") or "queued"),
        }

    def update_run_meta(
        self,
        request_id: str,
        is_favorite: Optional[bool] = None,
        tags: Optional[List[str]] = None,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        run_record = self.runs_repository.get(request_id)
        if run_record is None:
            raise SequencePlanRunNotFoundError(f"Sequence plan-and-render request not found: {request_id}")

        if is_favorite is None and tags is None and note is None:
            raise ValueError("At least one meta field is required: is_favorite, tags or note")

        updates: Dict[str, Any] = {
            "updated_at": self._now_iso(),
        }

        if is_favorite is not None:
            updates["is_favorite"] = bool(is_favorite)

        if tags is not None:
            updates["tags"] = self._normalize_meta_tags(tags)

        if note is not None:
            updates["note"] = note.strip() if isinstance(note, str) else ""

        updated_record = self.runs_repository.update(request_id, updates)
        if updated_record is None:
            raise SequencePlanRunNotFoundError(f"Sequence plan-and-render request not found: {request_id}")

        return self._build_public_response(updated_record)

    def update_run_review(
        self,
        request_id: str,
        review_status: Optional[str] = None,
        review_note: Optional[str] = None,
    ) -> Dict[str, Any]:
        run_record = self.runs_repository.get(request_id)
        if run_record is None:
            raise SequencePlanRunNotFoundError(f"Sequence plan-and-render request not found: {request_id}")

        if review_status is None and review_note is None:
            raise ValueError("At least one review field is required: review_status or review_note")

        current_status = str(run_record.get("review_status") or "pending_review").strip().lower() or "pending_review"
        current_note = str(run_record.get("review_note") or "")

        next_status = current_status
        if review_status is not None:
            normalized_status = review_status.strip().lower()
            if normalized_status not in REVIEW_STATUS_VALUES:
                raise ValueError("review_status must be one of pending_review, approved, rejected")
            next_status = normalized_status

        next_note = current_note
        if review_note is not None:
            next_note = review_note.strip()

        status_changed = next_status != current_status
        note_changed = review_note is not None and next_note != current_note
        has_relevant_change = status_changed or note_changed

        now = self._now_iso()
        updates: Dict[str, Any] = {
            "updated_at": now,
        }

        if review_status is not None:
            updates["review_status"] = next_status
            if status_changed:
                updates["reviewed_at"] = now

        if review_note is not None:
            updates["review_note"] = next_note

        updated_record = self.runs_repository.update(request_id, updates)
        if updated_record is None:
            raise SequencePlanRunNotFoundError(f"Sequence plan-and-render request not found: {request_id}")

        if has_relevant_change:
            self.runs_repository.create_review_history_entry(
                {
                    "history_id": str(uuid4()),
                    "request_id": request_id,
                    "previous_review_status": current_status,
                    "new_review_status": next_status,
                    "review_note": next_note,
                    "created_at": now,
                }
            )

        return self._build_public_response(updated_record)

    def list_run_review_history(self, request_id: str, limit: int = 200) -> Dict[str, Any]:
        run_record = self.runs_repository.get(request_id)
        if run_record is None:
            raise SequencePlanRunNotFoundError(f"Sequence plan-and-render request not found: {request_id}")

        normalized_limit = max(1, min(int(limit), 500))
        history_entries = self.runs_repository.list_review_history_for_request(
            request_id=request_id,
            limit=normalized_limit,
        )

        return {
            "ok": True,
            "request_id": request_id,
            "history": [
                {
                    "history_id": str(item.get("history_id") or ""),
                    "request_id": str(item.get("request_id") or request_id),
                    "previous_review_status": str(item.get("previous_review_status") or "pending_review"),
                    "new_review_status": str(item.get("new_review_status") or "pending_review"),
                    "review_note": str(item.get("review_note") or ""),
                    "created_at": str(item.get("created_at") or ""),
                }
                for item in history_entries
                if isinstance(item, dict)
            ],
            "limit": normalized_limit,
            "count": len(history_entries),
        }

    def create_collection(
        self,
        name: str,
        description: Optional[str] = None,
        color: Optional[str] = None,
        editorial_note: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_name = (name or "").strip()
        if not normalized_name:
            raise ValueError("name is required")

        now = self._now_iso()
        collection = self.runs_repository.create_collection(
            {
                "collection_id": str(uuid4()),
                "name": normalized_name,
                "description": (description or "").strip(),
                "editorial_note": (editorial_note or "").strip(),
                "color": (color or "").strip(),
                "is_archived": False,
                "best_request_id": None,
                "created_at": now,
                "updated_at": now,
            }
        )

        return {
            "ok": True,
            "collection": self._build_collection_public_response(collection),
        }

    def list_collections(self, limit: int = 100, include_archived: bool = False) -> Dict[str, Any]:
        normalized_limit = max(1, min(int(limit), 500))
        collections = self.runs_repository.list_collections(
            limit=normalized_limit,
            include_archived=include_archived,
        )

        payload_collections: List[Dict[str, Any]] = []
        for item in collections:
            base_payload = self._build_collection_public_response(item)
            payload_collections.append(self._attach_collection_health_summary(base_payload))

        return {
            "ok": True,
            "collections": payload_collections,
            "limit": normalized_limit,
            "count": len(collections),
        }

    def get_collections_dashboard(
        self,
        limit: int = 200,
        include_archived: bool = False,
        top_limit: int = 5,
    ) -> Dict[str, Any]:
        normalized_limit = max(1, min(int(limit), 500))
        normalized_top_limit = max(1, min(int(top_limit), 20))

        collections = self.runs_repository.list_collections(
            limit=normalized_limit,
            include_archived=include_archived,
        )

        dashboard_items: List[Dict[str, Any]] = []
        for collection in collections:
            collection_payload = self._build_collection_public_response(collection)
            collection_id = str(collection_payload.get("collection_id") or "")
            if not collection_id:
                continue

            audit = self.get_collection_audit(collection_id, emit_notifications=False)
            dashboard_items.append(self._build_collection_dashboard_item(collection_payload, audit))

        total_collections = len(dashboard_items)
        collections_green = sum(1 for item in dashboard_items if item.get("health_status") == "green")
        collections_yellow = sum(1 for item in dashboard_items if item.get("health_status") == "yellow")
        collections_red = sum(1 for item in dashboard_items if item.get("health_status") == "red")

        top_collections_by_executions = self._sort_collection_dashboard_items(
            dashboard_items,
            key="total_executions",
            limit=normalized_top_limit,
        )
        top_collections_by_retries = self._sort_collection_dashboard_items(
            dashboard_items,
            key="total_retries",
            limit=normalized_top_limit,
        )

        collections_without_best_execution = [
            item
            for item in dashboard_items
            if not self._safe_optional_text(item.get("best_request_id")) and int(item.get("total_executions") or 0) > 0
        ]
        collections_without_best_execution = self._sort_collection_dashboard_items(
            collections_without_best_execution,
            key="total_executions",
            limit=normalized_top_limit,
        )

        collections_with_pending_review = [
            item for item in dashboard_items if int(item.get("pending_review_count") or 0) > 0
        ]
        collections_with_pending_review = self._sort_collection_dashboard_items(
            collections_with_pending_review,
            key="pending_review_count",
            limit=normalized_top_limit,
        )

        highlighted_collections = sorted(
            [deepcopy(item) for item in dashboard_items],
            key=lambda item: (
                self._health_rank(str(item.get("health_status") or "green")),
                len(item.get("alerts") if isinstance(item.get("alerts"), list) else []),
                int(item.get("total_executions") or 0),
                str(item.get("updated_at") or ""),
            ),
            reverse=True,
        )[:normalized_top_limit]

        return {
            "ok": True,
            "total_collections": total_collections,
            "collections_green": collections_green,
            "collections_yellow": collections_yellow,
            "collections_red": collections_red,
            "top_collections_by_executions": top_collections_by_executions,
            "top_collections_by_retries": top_collections_by_retries,
            "collections_without_best_execution": collections_without_best_execution,
            "collections_with_pending_review": collections_with_pending_review,
            "highlighted_collections": highlighted_collections,
        }

    def list_notifications(
        self,
        limit: int = 50,
        collection_id: Optional[str] = None,
        is_read: Optional[bool] = None,
    ) -> Dict[str, Any]:
        normalized_limit = max(1, min(int(limit), 200))
        normalized_collection_id = self._safe_optional_text(collection_id)

        notifications = self.runs_repository.list_notifications(
            limit=normalized_limit,
            collection_id=normalized_collection_id,
            is_read=is_read,
        )

        return {
            "ok": True,
            "notifications": [self._build_notification_public_response(item) for item in notifications],
            "limit": normalized_limit,
            "count": len(notifications),
        }

    def get_notification_preferences(self) -> Dict[str, Any]:
        preferences = self.runs_repository.get_notification_preferences()
        return {
            "ok": True,
            "preferences": self._build_notification_preferences_public_response(preferences),
        }

    def update_notification_preferences(
        self,
        notifications_enabled: Optional[bool] = None,
        min_severity: Optional[str] = None,
        enabled_types: Optional[List[str]] = None,
        show_only_unread_by_default: Optional[bool] = None,
    ) -> Dict[str, Any]:
        if (
            notifications_enabled is None
            and min_severity is None
            and enabled_types is None
            and show_only_unread_by_default is None
        ):
            raise ValueError(
                "At least one preference field is required: notifications_enabled, min_severity, enabled_types or show_only_unread_by_default"
            )

        current = self.runs_repository.get_notification_preferences()
        updates: Dict[str, Any] = {
            "notifications_enabled": bool(current.get("notifications_enabled", True)),
            "min_severity": str(current.get("min_severity") or "info"),
            "enabled_types": self._normalize_notification_enabled_types(current.get("enabled_types")),
            "show_only_unread_by_default": bool(current.get("show_only_unread_by_default", False)),
            "updated_at": self._now_iso(),
        }

        if notifications_enabled is not None:
            updates["notifications_enabled"] = bool(notifications_enabled)

        if min_severity is not None:
            normalized_min_severity = min_severity.strip().lower()
            if normalized_min_severity not in NOTIFICATION_SEVERITY_VALUES:
                raise ValueError("min_severity must be one of info, warning, critical")
            updates["min_severity"] = normalized_min_severity

        if enabled_types is not None:
            updates["enabled_types"] = self._normalize_notification_enabled_types(enabled_types)

        if show_only_unread_by_default is not None:
            updates["show_only_unread_by_default"] = bool(show_only_unread_by_default)

        updated = self.runs_repository.upsert_notification_preferences(updates)
        return {
            "ok": True,
            "preferences": self._build_notification_preferences_public_response(updated),
        }

    def list_webhooks(self, limit: int = 100, include_disabled: bool = True) -> Dict[str, Any]:
        normalized_limit = max(1, min(int(limit), 500))
        webhooks = self.runs_repository.list_webhooks(limit=normalized_limit, include_disabled=include_disabled)
        webhook_stats = self.runs_repository.list_webhook_delivery_stats_by_webhook()
        stats_by_webhook = self._index_webhook_stats_by_id(webhook_stats)

        recent_errors = self.runs_repository.list_recent_webhook_delivery_errors(
            limit=WEBHOOK_HEALTH_RECENT_ERRORS_LOOKBACK_LIMIT
        )
        recent_error_counts = self._count_recent_errors_by_webhook(recent_errors)

        payload_webhooks: List[Dict[str, Any]] = []
        for webhook in webhooks:
            webhook_id = str(webhook.get("webhook_id") or "")
            stats = stats_by_webhook.get(webhook_id)
            recent_error_count = int(recent_error_counts.get(webhook_id) or 0)
            health_summary = self._build_webhook_health_summary(
                webhook=webhook,
                stats=stats,
                recent_error_count=recent_error_count,
            )

            public_webhook = self._build_webhook_public_response(webhook)
            public_webhook["health_status"] = str(health_summary.get("health_status") or "green")
            public_webhook["alerts"] = [
                str(item)
                for item in (health_summary.get("alerts") if isinstance(health_summary.get("alerts"), list) else [])
                if isinstance(item, str) and item.strip()
            ]
            payload_webhooks.append(public_webhook)

        return {
            "ok": True,
            "webhooks": payload_webhooks,
            "limit": normalized_limit,
            "count": len(webhooks),
        }

    def get_webhooks_dashboard(
        self,
        top_limit: int = 5,
        errors_limit: int = 10,
    ) -> Dict[str, Any]:
        normalized_top_limit = max(1, min(int(top_limit), 20))
        normalized_errors_limit = max(1, min(int(errors_limit), 50))

        stats = self.runs_repository.list_webhook_delivery_stats_by_webhook()
        recent_errors_for_health = self.runs_repository.list_recent_webhook_delivery_errors(
            limit=max(normalized_errors_limit, WEBHOOK_HEALTH_RECENT_ERRORS_LOOKBACK_LIMIT)
        )
        recent_error_counts = self._count_recent_errors_by_webhook(recent_errors_for_health)

        dashboard_items = [
            self._build_webhook_dashboard_item(
                item,
                recent_error_count=int(recent_error_counts.get(str(item.get("webhook_id") or "")) or 0),
            )
            for item in stats
        ]

        total_webhooks = len(dashboard_items)
        active_webhooks = sum(1 for item in dashboard_items if bool(item.get("is_enabled", True)))
        inactive_webhooks = max(0, total_webhooks - active_webhooks)
        webhooks_green = sum(1 for item in dashboard_items if str(item.get("health_status") or "green") == "green")
        webhooks_yellow = sum(1 for item in dashboard_items if str(item.get("health_status") or "green") == "yellow")
        webhooks_red = sum(1 for item in dashboard_items if str(item.get("health_status") or "green") == "red")

        total_deliveries = sum(int(item.get("total_deliveries") or 0) for item in dashboard_items)
        sent_deliveries = sum(int(item.get("sent_deliveries") or 0) for item in dashboard_items)
        failed_deliveries = sum(int(item.get("failed_deliveries") or 0) for item in dashboard_items)
        pending_deliveries = sum(int(item.get("pending_deliveries") or 0) for item in dashboard_items)

        with_volume = [item for item in dashboard_items if int(item.get("total_deliveries") or 0) > 0]
        with_failures = [item for item in dashboard_items if int(item.get("failed_deliveries") or 0) > 0]
        with_retries = [item for item in dashboard_items if int(item.get("total_retries") or 0) > 0]

        top_webhooks_by_volume = sorted(
            [deepcopy(item) for item in with_volume],
            key=lambda item: (
                int(item.get("total_deliveries") or 0),
                int(item.get("failed_deliveries") or 0),
                int(item.get("total_retries") or 0),
                self._health_rank(str(item.get("health_status") or "green")),
                str(item.get("last_delivery_at") or ""),
            ),
            reverse=True,
        )[:normalized_top_limit]

        top_webhooks_by_failures = sorted(
            [deepcopy(item) for item in with_failures],
            key=lambda item: (
                int(item.get("failed_deliveries") or 0),
                int(item.get("total_deliveries") or 0),
                int(item.get("total_retries") or 0),
                self._health_rank(str(item.get("health_status") or "green")),
                str(item.get("last_delivery_at") or ""),
            ),
            reverse=True,
        )[:normalized_top_limit]

        top_webhooks_by_retries = sorted(
            [deepcopy(item) for item in with_retries],
            key=lambda item: (
                int(item.get("total_retries") or 0),
                int(item.get("total_deliveries") or 0),
                int(item.get("failed_deliveries") or 0),
                self._health_rank(str(item.get("health_status") or "green")),
                str(item.get("last_delivery_at") or ""),
            ),
            reverse=True,
        )[:normalized_top_limit]

        recent_errors_raw = recent_errors_for_health[:normalized_errors_limit]
        recent_delivery_errors = [self._build_webhook_dashboard_error_item(item) for item in recent_errors_raw]

        active_alerts = sorted(
            [
                {
                    "webhook_id": str(item.get("webhook_id") or ""),
                    "name": str(item.get("name") or ""),
                    "health_status": str(item.get("health_status") or "green"),
                    "alerts": [
                        str(alert)
                        for alert in (item.get("alerts") if isinstance(item.get("alerts"), list) else [])
                        if isinstance(alert, str) and alert.strip()
                    ],
                    "failed_deliveries": int(item.get("failed_deliveries") or 0),
                    "exhausted_deliveries": int(item.get("exhausted_deliveries") or 0),
                    "failure_ratio": float(item.get("failure_ratio") or 0.0),
                }
                for item in dashboard_items
                if isinstance(item.get("alerts"), list) and len(item.get("alerts")) > 0
            ],
            key=lambda item: (
                self._health_rank(str(item.get("health_status") or "green")),
                len(item.get("alerts") if isinstance(item.get("alerts"), list) else []),
                int(item.get("failed_deliveries") or 0),
                int(item.get("exhausted_deliveries") or 0),
                float(item.get("failure_ratio") or 0.0),
            ),
            reverse=True,
        )[: max(5, normalized_top_limit * 3)]

        return {
            "ok": True,
            "total_webhooks": total_webhooks,
            "active_webhooks": active_webhooks,
            "inactive_webhooks": inactive_webhooks,
            "webhooks_green": webhooks_green,
            "webhooks_yellow": webhooks_yellow,
            "webhooks_red": webhooks_red,
            "total_deliveries": total_deliveries,
            "sent_deliveries": sent_deliveries,
            "failed_deliveries": failed_deliveries,
            "pending_deliveries": pending_deliveries,
            "top_webhooks_by_volume": top_webhooks_by_volume,
            "top_webhooks_by_failures": top_webhooks_by_failures,
            "top_webhooks_by_retries": top_webhooks_by_retries,
            "active_alerts": active_alerts,
            "recent_delivery_errors": recent_delivery_errors,
        }

    def get_webhook_health(
        self,
        webhook_id: str,
        recent_limit: int = 30,
        signals_limit: int = 10,
    ) -> Dict[str, Any]:
        normalized_webhook_id = webhook_id.strip()
        if not normalized_webhook_id:
            raise ValueError("webhook_id is required")

        webhook = self.runs_repository.get_webhook(normalized_webhook_id)
        if webhook is None:
            raise SequenceWebhookNotFoundError(f"Webhook not found: {webhook_id}")

        normalized_recent_limit = max(5, min(int(recent_limit), 200))
        normalized_signals_limit = max(1, min(int(signals_limit), 50))

        stats_by_webhook = self._index_webhook_stats_by_id(
            self.runs_repository.list_webhook_delivery_stats_by_webhook()
        )
        stats = stats_by_webhook.get(normalized_webhook_id)

        recent_deliveries = self.runs_repository.list_webhook_deliveries(
            limit=normalized_recent_limit,
            webhook_id=normalized_webhook_id,
        )

        recent_failed_deliveries = sum(
            1
            for item in recent_deliveries
            if str(item.get("delivery_status") or "").strip().lower() == "failed"
        )
        recent_error_count = sum(
            1
            for item in recent_deliveries
            if str(item.get("delivery_status") or "").strip().lower() == "failed"
            and self._safe_optional_text(item.get("error_message")) is not None
        )

        health_summary = self._build_webhook_health_summary(
            webhook=webhook,
            stats=stats,
            recent_error_count=recent_error_count,
        )

        last_success_at: Optional[str] = None
        last_failure_at: Optional[str] = None
        for delivery in recent_deliveries:
            status = str(delivery.get("delivery_status") or "").strip().lower()
            if status == "sent" and last_success_at is None:
                last_success_at = self._safe_optional_text(delivery.get("delivered_at")) or self._safe_optional_text(
                    delivery.get("last_attempt_at")
                )
            if status == "failed" and last_failure_at is None:
                last_failure_at = self._safe_optional_text(delivery.get("last_attempt_at")) or self._safe_optional_text(
                    delivery.get("created_at")
                )
            if last_success_at is not None and last_failure_at is not None:
                break

        public_webhook = self._build_webhook_public_response(webhook)
        public_webhook["health_status"] = str(health_summary.get("health_status") or "green")
        public_webhook["alerts"] = [
            str(item)
            for item in (health_summary.get("alerts") if isinstance(health_summary.get("alerts"), list) else [])
            if isinstance(item, str) and item.strip()
        ]

        total_deliveries = int(health_summary.get("total_deliveries") or 0)
        sent_deliveries = int(health_summary.get("sent_deliveries") or 0)
        failed_deliveries = int(health_summary.get("failed_deliveries") or 0)
        pending_deliveries = int(health_summary.get("pending_deliveries") or 0)
        exhausted_deliveries = int(health_summary.get("exhausted_deliveries") or 0)
        total_retries = int(health_summary.get("total_retries") or 0)
        failure_ratio = float(health_summary.get("failure_ratio") or 0.0)
        last_delivery_at = self._safe_optional_text(health_summary.get("last_delivery_at"))

        recent_signals = self._build_webhook_recent_signals(
            health_signals=health_summary.get("signals") if isinstance(health_summary.get("signals"), list) else [],
            recent_deliveries=recent_deliveries,
            limit=normalized_signals_limit,
        )

        return {
            "ok": True,
            "webhook": public_webhook,
            "operational_summary": {
                "total_deliveries": total_deliveries,
                "sent_deliveries": sent_deliveries,
                "failed_deliveries": failed_deliveries,
                "pending_deliveries": pending_deliveries,
                "exhausted_deliveries": exhausted_deliveries,
                "total_retries": total_retries,
                "failure_ratio": failure_ratio,
                "recent_deliveries": len(recent_deliveries),
                "recent_failed_deliveries": recent_failed_deliveries,
                "last_delivery_at": last_delivery_at,
                "last_success_at": last_success_at,
                "last_failure_at": last_failure_at,
            },
            "health_status": str(health_summary.get("health_status") or "green"),
            "alerts": [
                str(item)
                for item in (health_summary.get("alerts") if isinstance(health_summary.get("alerts"), list) else [])
                if isinstance(item, str) and item.strip()
            ],
            "recent_signals": recent_signals,
        }

    def list_notification_channels(
        self,
        limit: int = 100,
        include_disabled: bool = True,
        channel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_limit = max(1, min(int(limit), 500))
        normalized_channel_type = self._normalize_notification_channel_type(channel_type)
        channels = self.runs_repository.list_notification_channels(
            limit=normalized_limit,
            include_disabled=include_disabled,
            channel_type=normalized_channel_type,
        )
        return {
            "ok": True,
            "channels": [self._build_notification_channel_public_response(item) for item in channels],
            "limit": normalized_limit,
            "count": len(channels),
        }

    def create_notification_channel(
        self,
        channel_type: str,
        name: str,
        is_enabled: bool = True,
        config: Optional[Dict[str, Any]] = None,
        min_severity: str = "info",
        enabled_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        normalized_channel_type = self._normalize_notification_channel_type(channel_type, strict=True)
        normalized_name = str(name or "").strip()
        if not normalized_name:
            raise ValueError("name must be a non-empty string")

        normalized_config = self._normalize_notification_channel_config(
            channel_type=normalized_channel_type,
            config=config,
            strict=True,
        )

        normalized_min_severity = self._normalize_notification_severity(min_severity)
        if normalized_min_severity not in NOTIFICATION_SEVERITY_VALUES:
            raise ValueError("min_severity must be one of info, warning, critical")

        normalized_enabled_types = (
            deepcopy(DEFAULT_NOTIFICATION_ENABLED_TYPES)
            if enabled_types is None
            else self._normalize_notification_enabled_types(enabled_types)
        )

        now = self._now_iso()
        payload = {
            "channel_id": str(uuid4()),
            "channel_type": normalized_channel_type,
            "name": normalized_name,
            "is_enabled": bool(is_enabled),
            "config": normalized_config,
            "min_severity": normalized_min_severity,
            "enabled_types": normalized_enabled_types,
            "created_at": now,
            "updated_at": now,
        }
        persisted = self.runs_repository.create_notification_channel(payload)
        return {
            "ok": True,
            "channel": self._build_notification_channel_public_response(persisted),
        }

    def update_notification_channel(
        self,
        channel_id: str,
        name: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        config: Optional[Dict[str, Any]] = None,
        min_severity: Optional[str] = None,
        enabled_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        normalized_channel_id = str(channel_id or "").strip()
        if not normalized_channel_id:
            raise ValueError("channel_id is required")

        if (
            name is None
            and is_enabled is None
            and config is None
            and min_severity is None
            and enabled_types is None
        ):
            raise ValueError(
                "At least one channel field is required: name, is_enabled, config, min_severity or enabled_types"
            )

        existing = self.runs_repository.get_notification_channel(normalized_channel_id)
        if existing is None:
            raise SequenceNotificationChannelNotFoundError(f"Notification channel not found: {channel_id}")

        updates: Dict[str, Any] = {
            "updated_at": self._now_iso(),
        }

        if name is not None:
            normalized_name = str(name or "").strip()
            if not normalized_name:
                raise ValueError("name must be a non-empty string")
            updates["name"] = normalized_name

        if is_enabled is not None:
            updates["is_enabled"] = bool(is_enabled)

        existing_channel_type = self._normalize_notification_channel_type(existing.get("channel_type"), strict=True)
        if config is not None:
            existing_config = existing.get("config") if isinstance(existing.get("config"), dict) else {}
            merged_config = {**existing_config, **config}
            updates["config"] = self._normalize_notification_channel_config(
                channel_type=existing_channel_type,
                config=merged_config,
                strict=True,
            )

        if min_severity is not None:
            normalized_min_severity = self._normalize_notification_severity(min_severity)
            if normalized_min_severity not in NOTIFICATION_SEVERITY_VALUES:
                raise ValueError("min_severity must be one of info, warning, critical")
            updates["min_severity"] = normalized_min_severity

        if enabled_types is not None:
            updates["enabled_types"] = self._normalize_notification_enabled_types(enabled_types)

        updated = self.runs_repository.update_notification_channel(normalized_channel_id, updates)
        if updated is None:
            raise SequenceNotificationChannelNotFoundError(f"Notification channel not found: {channel_id}")

        return {
            "ok": True,
            "channel": self._build_notification_channel_public_response(updated),
        }

    def send_test_notification_channel_event(self, channel_id: str) -> Dict[str, Any]:
        normalized_channel_id = str(channel_id or "").strip()
        if not normalized_channel_id:
            raise ValueError("channel_id is required")

        channel = self.runs_repository.get_notification_channel(normalized_channel_id)
        if channel is None:
            raise SequenceNotificationChannelNotFoundError(f"Notification channel not found: {channel_id}")

        now = self._now_iso()
        test_collection = self._ensure_webhook_test_collection()
        test_collection_id = str(test_collection.get("collection_id") or WEBHOOK_TEST_COLLECTION_ID)
        notification = self.runs_repository.create_notification(
            {
                "notification_id": str(uuid4()),
                "collection_id": test_collection_id,
                "type": "CHANNEL_TEST_EVENT",
                "severity": "info",
                "message": "This is a test notification channel event",
                "created_at": now,
                "is_read": True,
            }
        )

        payload = self._build_notification_channel_payload(
            notification=notification,
            collection_name=str(test_collection.get("name") or ""),
            health_status="green",
            event_type="test_event",
        )
        message_text = self._build_notification_channel_message_text(
            channel_type=self._normalize_notification_channel_type(channel.get("channel_type"), strict=True),
            payload=payload,
        )

        max_attempts = NOTIFICATION_CHANNEL_DELIVERY_DEFAULT_MAX_ATTEMPTS
        delivery = self.runs_repository.create_notification_channel_delivery(
            {
                "delivery_id": str(uuid4()),
                "channel_id": normalized_channel_id,
                "channel_type": self._normalize_notification_channel_type(channel.get("channel_type"), strict=True),
                "notification_id": str(notification.get("notification_id") or ""),
                "collection_id": test_collection_id,
                "payload": payload,
                "message_text": message_text,
                "delivery_status": "pending",
                "attempt_count": 0,
                "max_attempts": max_attempts,
                "last_attempt_at": None,
                "next_retry_at": None,
                "final_failure_at": None,
                "is_test": True,
                "response_status_code": None,
                "response_body": None,
                "error_message": None,
                "created_at": now,
                "delivered_at": None,
            }
        )
        delivery_id = str(delivery.get("delivery_id") or "").strip()
        if not delivery_id:
            raise SequenceNotificationChannelDeliveryNotFoundError("Notification channel delivery not found")

        attempted = self._attempt_notification_channel_delivery(
            delivery_id=delivery_id,
            channel=channel,
            payload=payload,
            message_text=message_text,
            prior_attempt_count=0,
            max_attempts=max_attempts,
        )

        return {
            "ok": True,
            "delivery": self._build_notification_channel_delivery_public_response(attempted),
        }

    def list_notification_channel_deliveries(
        self,
        limit: int = 100,
        channel_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        notification_id: Optional[str] = None,
        channel_type: Optional[str] = None,
        is_test: Optional[bool] = None,
    ) -> Dict[str, Any]:
        normalized_limit = max(1, min(int(limit), 500))
        normalized_channel_id = self._safe_optional_text(channel_id)
        normalized_collection_id = self._safe_optional_text(collection_id)
        normalized_notification_id = self._safe_optional_text(notification_id)
        normalized_channel_type = self._normalize_notification_channel_type(channel_type)
        normalized_is_test = is_test if isinstance(is_test, bool) else None

        deliveries = self.runs_repository.list_notification_channel_deliveries(
            limit=normalized_limit,
            channel_id=normalized_channel_id,
            collection_id=normalized_collection_id,
            notification_id=normalized_notification_id,
            channel_type=normalized_channel_type,
            is_test=normalized_is_test,
        )
        return {
            "ok": True,
            "deliveries": [self._build_notification_channel_delivery_public_response(item) for item in deliveries],
            "limit": normalized_limit,
            "count": len(deliveries),
        }

    def retry_notification_channel_delivery(self, delivery_id: str) -> Dict[str, Any]:
        normalized_delivery_id = str(delivery_id or "").strip()
        if not normalized_delivery_id:
            raise ValueError("delivery_id is required")

        delivery = self.runs_repository.get_notification_channel_delivery(normalized_delivery_id)
        if delivery is None:
            raise SequenceNotificationChannelDeliveryNotFoundError(
                f"Notification channel delivery not found: {delivery_id}"
            )

        delivery_status = str(delivery.get("delivery_status") or "pending").strip().lower()
        if delivery_status != "failed":
            raise ValueError("Only failed deliveries can be retried")

        channel_id = str(delivery.get("channel_id") or "").strip()
        channel = self.runs_repository.get_notification_channel(channel_id)
        if channel is None:
            raise SequenceNotificationChannelNotFoundError(f"Notification channel not found: {channel_id}")

        payload = delivery.get("payload") if isinstance(delivery.get("payload"), dict) else {}
        message_text = str(delivery.get("message_text") or "")
        prior_attempt_count = int(delivery.get("attempt_count") or 0)
        max_attempts = max(1, int(delivery.get("max_attempts") or NOTIFICATION_CHANNEL_DELIVERY_DEFAULT_MAX_ATTEMPTS))
        if prior_attempt_count >= max_attempts:
            raise ValueError("Delivery max attempts exhausted")

        retried = self._attempt_notification_channel_delivery(
            delivery_id=normalized_delivery_id,
            channel=channel,
            payload=payload,
            message_text=message_text,
            prior_attempt_count=prior_attempt_count,
            max_attempts=max_attempts,
        )

        return {
            "ok": True,
            "delivery": self._build_notification_channel_delivery_public_response(retried),
        }

    def process_notification_channel_delivery_retries(
        self,
        limit: int = 100,
        channel_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        channel_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_limit = max(1, min(int(limit), 500))
        normalized_channel_id = self._safe_optional_text(channel_id)
        normalized_collection_id = self._safe_optional_text(collection_id)
        normalized_channel_type = self._normalize_notification_channel_type(channel_type)
        due_before = self._now_iso()

        pending_deliveries = self.runs_repository.list_notification_channel_deliveries_pending_retry(
            due_before=due_before,
            limit=normalized_limit,
            channel_id=normalized_channel_id,
            collection_id=normalized_collection_id,
            channel_type=normalized_channel_type,
        )

        processed: List[Dict[str, Any]] = []
        sent_count = 0
        failed_count = 0
        exhausted_count = 0

        for delivery in pending_deliveries:
            delivery_id = str(delivery.get("delivery_id") or "").strip()
            if not delivery_id:
                continue

            delivery_channel_id = str(delivery.get("channel_id") or "").strip()
            channel = self.runs_repository.get_notification_channel(delivery_channel_id)
            if channel is None:
                failed_delivery = self._mark_notification_channel_delivery_failed_without_request(
                    delivery=delivery,
                    error_message=f"Notification channel not found: {delivery_channel_id}",
                )
                processed.append(failed_delivery)
                failed_count += 1
                if failed_delivery.get("final_failure_at") is not None:
                    exhausted_count += 1
                continue

            payload = delivery.get("payload") if isinstance(delivery.get("payload"), dict) else {}
            message_text = str(delivery.get("message_text") or "")
            prior_attempt_count = int(delivery.get("attempt_count") or 0)
            max_attempts = max(1, int(delivery.get("max_attempts") or NOTIFICATION_CHANNEL_DELIVERY_DEFAULT_MAX_ATTEMPTS))

            try:
                updated = self._attempt_notification_channel_delivery(
                    delivery_id=delivery_id,
                    channel=channel,
                    payload=payload,
                    message_text=message_text,
                    prior_attempt_count=prior_attempt_count,
                    max_attempts=max_attempts,
                )
            except Exception as error:
                updated = self._mark_notification_channel_delivery_failed_without_request(
                    delivery=delivery,
                    error_message=str(error),
                )
            processed.append(updated)

            if str(updated.get("delivery_status") or "").strip().lower() == "sent":
                sent_count += 1
            else:
                failed_count += 1
                if updated.get("final_failure_at") is not None:
                    exhausted_count += 1

        return {
            "ok": True,
            "processed_count": len(processed),
            "sent_count": sent_count,
            "failed_count": failed_count,
            "exhausted_count": exhausted_count,
            "deliveries": [self._build_notification_channel_delivery_public_response(item) for item in processed],
        }

    def list_alert_routing_rules(
        self,
        limit: int = 100,
        include_disabled: bool = True,
        target_channel_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_limit = max(1, min(int(limit), 500))
        normalized_target_channel_id = self._safe_optional_text(target_channel_id)
        rules = self.runs_repository.list_alert_routing_rules(
            limit=normalized_limit,
            include_disabled=include_disabled,
            target_channel_id=normalized_target_channel_id,
        )
        return {
            "ok": True,
            "rules": [self._build_alert_routing_rule_public_response(item) for item in rules],
            "limit": normalized_limit,
            "count": len(rules),
        }

    def create_alert_routing_rule(
        self,
        name: str,
        target_channel_id: str,
        match_types: Optional[List[str]] = None,
        min_severity: str = "info",
        is_enabled: bool = True,
        match_collection_id: Optional[str] = None,
        match_health_status: Optional[str] = None,
        target_channel_kind: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_name = str(name or "").strip()
        if not normalized_name:
            raise ValueError("name must be a non-empty string")

        normalized_target_channel_id = str(target_channel_id or "").strip()
        if not normalized_target_channel_id:
            raise ValueError("target_channel_id is required")

        resolved_target = self._resolve_alert_routing_target(
            target_channel_id=normalized_target_channel_id,
            target_channel_kind=target_channel_kind,
            strict=True,
        )
        normalized_target_kind = self._normalize_alert_routing_target_kind(
            resolved_target.get("target_channel_kind"),
            strict=True,
        )

        normalized_match_types = self._normalize_alert_routing_match_types(match_types)
        normalized_min_severity = self._normalize_notification_severity(min_severity)
        if normalized_min_severity not in NOTIFICATION_SEVERITY_VALUES:
            raise ValueError("min_severity must be one of info, warning, critical")

        normalized_match_collection_id = self._safe_optional_text(match_collection_id)
        normalized_match_health_status = self._normalize_collection_health_status(match_health_status, strict=True)

        now = self._now_iso()
        payload = {
            "rule_id": str(uuid4()),
            "name": normalized_name,
            "is_enabled": bool(is_enabled),
            "target_channel_id": normalized_target_channel_id,
            "target_channel_kind": normalized_target_kind,
            "match_types": normalized_match_types,
            "min_severity": normalized_min_severity,
            "match_collection_id": normalized_match_collection_id,
            "match_health_status": normalized_match_health_status,
            "created_at": now,
            "updated_at": now,
        }
        persisted = self.runs_repository.create_alert_routing_rule(payload)
        return {
            "ok": True,
            "rule": self._build_alert_routing_rule_public_response(persisted),
        }

    def update_alert_routing_rule(
        self,
        rule_id: str,
        name: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        target_channel_id: Optional[str] = None,
        match_types: Optional[List[str]] = None,
        min_severity: Optional[str] = None,
        match_collection_id: Optional[str] = None,
        match_health_status: Optional[str] = None,
        target_channel_kind: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_rule_id = str(rule_id or "").strip()
        if not normalized_rule_id:
            raise ValueError("rule_id is required")

        if (
            name is None
            and is_enabled is None
            and target_channel_id is None
            and match_types is None
            and min_severity is None
            and match_collection_id is None
            and match_health_status is None
            and target_channel_kind is None
        ):
            raise ValueError(
                "At least one routing rule field is required: name, is_enabled, target_channel_id, match_types, min_severity, match_collection_id, match_health_status or target_channel_kind"
            )

        existing = self.runs_repository.get_alert_routing_rule(normalized_rule_id)
        if existing is None:
            raise SequenceAlertRoutingRuleNotFoundError(f"Alert routing rule not found: {rule_id}")

        updates: Dict[str, Any] = {
            "updated_at": self._now_iso(),
        }

        if name is not None:
            normalized_name = str(name or "").strip()
            if not normalized_name:
                raise ValueError("name must be a non-empty string")
            updates["name"] = normalized_name

        if is_enabled is not None:
            updates["is_enabled"] = bool(is_enabled)

        next_target_channel_id = (
            str(target_channel_id or "").strip()
            if target_channel_id is not None
            else str(existing.get("target_channel_id") or "").strip()
        )
        if target_channel_id is not None and not next_target_channel_id:
            raise ValueError("target_channel_id must be a non-empty string")

        next_target_channel_kind = (
            target_channel_kind
            if target_channel_kind is not None
            else existing.get("target_channel_kind")
        )

        if target_channel_id is not None or target_channel_kind is not None:
            resolved_target = self._resolve_alert_routing_target(
                target_channel_id=next_target_channel_id,
                target_channel_kind=next_target_channel_kind,
                strict=True,
            )
            updates["target_channel_id"] = next_target_channel_id
            updates["target_channel_kind"] = self._normalize_alert_routing_target_kind(
                resolved_target.get("target_channel_kind"),
                strict=True,
            )

        if match_types is not None:
            updates["match_types"] = self._normalize_alert_routing_match_types(match_types)

        if min_severity is not None:
            normalized_min_severity = self._normalize_notification_severity(min_severity)
            if normalized_min_severity not in NOTIFICATION_SEVERITY_VALUES:
                raise ValueError("min_severity must be one of info, warning, critical")
            updates["min_severity"] = normalized_min_severity

        if match_collection_id is not None:
            updates["match_collection_id"] = self._safe_optional_text(match_collection_id)

        if match_health_status is not None:
            updates["match_health_status"] = self._normalize_collection_health_status(match_health_status, strict=True)

        updated = self.runs_repository.update_alert_routing_rule(normalized_rule_id, updates)
        if updated is None:
            raise SequenceAlertRoutingRuleNotFoundError(f"Alert routing rule not found: {rule_id}")

        return {
            "ok": True,
            "rule": self._build_alert_routing_rule_public_response(updated),
        }

    def delete_alert_routing_rule(self, rule_id: str) -> Dict[str, Any]:
        normalized_rule_id = str(rule_id or "").strip()
        if not normalized_rule_id:
            raise ValueError("rule_id is required")

        deleted = self.runs_repository.delete_alert_routing_rule(normalized_rule_id)
        if not deleted:
            raise SequenceAlertRoutingRuleNotFoundError(f"Alert routing rule not found: {rule_id}")

        return {
            "ok": True,
            "rule_id": normalized_rule_id,
            "deleted": True,
        }

    def create_webhook(
        self,
        name: str,
        url: str,
        is_enabled: bool = True,
        auth_mode: str = "none",
        secret_token: Optional[str] = None,
        min_severity: str = "info",
        enabled_types: Optional[List[str]] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        payload_template_mode: str = "default",
        payload_template: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("name must be a non-empty string")

        normalized_url = url.strip()
        if not normalized_url:
            raise ValueError("url must be a non-empty string")

        normalized_auth_mode = self._normalize_webhook_auth_mode(auth_mode, strict=True)
        normalized_secret_token = self._normalize_webhook_secret_token(secret_token)
        if normalized_auth_mode in {"bearer", "hmac_sha256"} and not normalized_secret_token:
            raise ValueError("secret_token is required when auth_mode is bearer or hmac_sha256")

        normalized_min_severity = str(min_severity or "").strip().lower()
        if normalized_min_severity not in NOTIFICATION_SEVERITY_VALUES:
            raise ValueError("min_severity must be one of info, warning, critical")

        normalized_enabled_types = (
            deepcopy(DEFAULT_NOTIFICATION_ENABLED_TYPES)
            if enabled_types is None
            else self._normalize_notification_enabled_types(enabled_types)
        )
        normalized_custom_headers = self._normalize_webhook_custom_headers(custom_headers)
        normalized_template_mode = self._normalize_webhook_payload_template_mode(payload_template_mode, strict=True)
        normalized_payload_template = self._normalize_webhook_payload_template(payload_template)
        if normalized_template_mode == "custom" and normalized_payload_template is None:
            raise ValueError("payload_template is required when payload_template_mode is custom")
        if normalized_template_mode != "custom":
            normalized_payload_template = None

        now = self._now_iso()
        payload = {
            "webhook_id": str(uuid4()),
            "name": normalized_name,
            "url": normalized_url,
            "is_enabled": bool(is_enabled),
            "auth_mode": normalized_auth_mode,
            "secret_token": normalized_secret_token,
            "min_severity": normalized_min_severity,
            "enabled_types": normalized_enabled_types,
            "custom_headers": normalized_custom_headers,
            "payload_template_mode": normalized_template_mode,
            "payload_template": normalized_payload_template,
            "created_at": now,
            "updated_at": now,
        }
        persisted = self.runs_repository.create_webhook(payload)
        return {
            "ok": True,
            "webhook": self._build_webhook_public_response(persisted),
        }

    def update_webhook(
        self,
        webhook_id: str,
        name: Optional[str] = None,
        url: Optional[str] = None,
        is_enabled: Optional[bool] = None,
        auth_mode: Optional[str] = None,
        secret_token: Optional[str] = None,
        min_severity: Optional[str] = None,
        enabled_types: Optional[List[str]] = None,
        custom_headers: Optional[Dict[str, str]] = None,
        payload_template_mode: Optional[str] = None,
        payload_template: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized_webhook_id = webhook_id.strip()
        if not normalized_webhook_id:
            raise ValueError("webhook_id is required")

        if (
            name is None
            and url is None
            and is_enabled is None
            and auth_mode is None
            and secret_token is None
            and min_severity is None
            and enabled_types is None
            and custom_headers is None
            and payload_template_mode is None
            and payload_template is None
        ):
            raise ValueError(
                "At least one webhook field is required: name, url, is_enabled, auth_mode, secret_token, min_severity, enabled_types, custom_headers, payload_template_mode or payload_template"
            )

        existing = self.runs_repository.get_webhook(normalized_webhook_id)
        if existing is None:
            raise SequenceWebhookNotFoundError(f"Webhook not found: {webhook_id}")

        updates: Dict[str, Any] = {
            "updated_at": self._now_iso(),
        }

        if name is not None:
            normalized_name = name.strip()
            if not normalized_name:
                raise ValueError("name must be a non-empty string")
            updates["name"] = normalized_name

        if url is not None:
            normalized_url = url.strip()
            if not normalized_url:
                raise ValueError("url must be a non-empty string")
            updates["url"] = normalized_url

        if is_enabled is not None:
            updates["is_enabled"] = bool(is_enabled)

        next_auth_mode = self._normalize_webhook_auth_mode(existing.get("auth_mode"))
        if auth_mode is not None:
            next_auth_mode = self._normalize_webhook_auth_mode(auth_mode, strict=True)
            updates["auth_mode"] = next_auth_mode

        next_secret_token = self._normalize_webhook_secret_token(existing.get("secret_token"))
        if secret_token is not None:
            next_secret_token = self._normalize_webhook_secret_token(secret_token)
            updates["secret_token"] = next_secret_token

        if next_auth_mode in {"bearer", "hmac_sha256"} and not next_secret_token:
            raise ValueError("secret_token is required when auth_mode is bearer or hmac_sha256")

        if min_severity is not None:
            normalized_min_severity = min_severity.strip().lower()
            if normalized_min_severity not in NOTIFICATION_SEVERITY_VALUES:
                raise ValueError("min_severity must be one of info, warning, critical")
            updates["min_severity"] = normalized_min_severity

        if enabled_types is not None:
            updates["enabled_types"] = self._normalize_notification_enabled_types(enabled_types)

        if custom_headers is not None:
            updates["custom_headers"] = self._normalize_webhook_custom_headers(custom_headers)

        next_template_mode = self._normalize_webhook_payload_template_mode(existing.get("payload_template_mode"))
        if payload_template_mode is not None:
            next_template_mode = self._normalize_webhook_payload_template_mode(payload_template_mode, strict=True)
            updates["payload_template_mode"] = next_template_mode

        next_payload_template = self._normalize_webhook_payload_template(existing.get("payload_template"))
        if payload_template is not None:
            next_payload_template = self._normalize_webhook_payload_template(payload_template)
            updates["payload_template"] = next_payload_template

        if next_template_mode == "custom" and next_payload_template is None:
            raise ValueError("payload_template is required when payload_template_mode is custom")

        if next_template_mode != "custom" and (
            "payload_template_mode" in updates or payload_template is not None
        ):
            updates["payload_template"] = None

        updated = self.runs_repository.update_webhook(normalized_webhook_id, updates)
        if updated is None:
            raise SequenceWebhookNotFoundError(f"Webhook not found: {webhook_id}")

        return {
            "ok": True,
            "webhook": self._build_webhook_public_response(updated),
        }

    def list_webhook_deliveries(
        self,
        limit: int = 100,
        webhook_id: Optional[str] = None,
        collection_id: Optional[str] = None,
        notification_id: Optional[str] = None,
        is_test: Optional[bool] = None,
    ) -> Dict[str, Any]:
        normalized_limit = max(1, min(int(limit), 500))
        normalized_webhook_id = self._safe_optional_text(webhook_id)
        normalized_collection_id = self._safe_optional_text(collection_id)
        normalized_notification_id = self._safe_optional_text(notification_id)
        normalized_is_test = is_test if isinstance(is_test, bool) else None

        deliveries = self.runs_repository.list_webhook_deliveries(
            limit=normalized_limit,
            webhook_id=normalized_webhook_id,
            collection_id=normalized_collection_id,
            notification_id=normalized_notification_id,
            is_test=normalized_is_test,
        )
        return {
            "ok": True,
            "deliveries": [self._build_webhook_delivery_public_response(item) for item in deliveries],
            "limit": normalized_limit,
            "count": len(deliveries),
        }

    def compare_webhook_deliveries(
        self,
        left_delivery_id: str,
        right_delivery_id: str,
    ) -> Dict[str, Any]:
        left_id = left_delivery_id.strip()
        right_id = right_delivery_id.strip()
        if not left_id or not right_id:
            raise ValueError("left_delivery_id and right_delivery_id are required")

        left_delivery = self.runs_repository.get_webhook_delivery(left_id)
        if left_delivery is None:
            raise SequenceWebhookDeliveryNotFoundError(f"Webhook delivery not found: {left_delivery_id}")

        right_delivery = self.runs_repository.get_webhook_delivery(right_id)
        if right_delivery is None:
            raise SequenceWebhookDeliveryNotFoundError(f"Webhook delivery not found: {right_delivery_id}")

        left_payload = left_delivery.get("payload") if isinstance(left_delivery.get("payload"), dict) else {}
        right_payload = right_delivery.get("payload") if isinstance(right_delivery.get("payload"), dict) else {}

        left_headers = self._normalize_webhook_custom_headers(left_delivery.get("request_headers"))
        right_headers = self._normalize_webhook_custom_headers(right_delivery.get("request_headers"))

        return {
            "ok": True,
            "left_delivery_id": left_id,
            "right_delivery_id": right_id,
            "auth_mode_left": self._normalize_webhook_auth_mode(left_delivery.get("auth_mode")),
            "auth_mode_right": self._normalize_webhook_auth_mode(right_delivery.get("auth_mode")),
            "payload_template_mode_left": self._normalize_webhook_payload_template_mode(left_delivery.get("template_mode")),
            "payload_template_mode_right": self._normalize_webhook_payload_template_mode(right_delivery.get("template_mode")),
            "payload_diff": self._build_structured_webhook_diff(left_payload, right_payload),
            "headers_diff": self._build_structured_webhook_diff(left_headers, right_headers),
        }

    def preview_webhook_payload(
        self,
        webhook_id: str,
        event_type: Optional[str] = None,
        sample_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized_webhook_id = webhook_id.strip()
        if not normalized_webhook_id:
            raise ValueError("webhook_id is required")

        webhook = self.runs_repository.get_webhook(normalized_webhook_id)
        if webhook is None:
            raise SequenceWebhookNotFoundError(f"Webhook not found: {webhook_id}")

        now = self._now_iso()
        base_payload = self._build_webhook_test_payload(
            webhook=webhook,
            created_at=now,
            event_type=event_type,
            sample_data=sample_data,
        )
        rendered_payload_data = self._apply_webhook_payload_template(
            webhook=webhook,
            default_payload=base_payload,
        )
        rendered_payload = (
            rendered_payload_data.get("payload")
            if isinstance(rendered_payload_data.get("payload"), dict)
            else {}
        )

        auth_mode = self._normalize_webhook_auth_mode(webhook.get("auth_mode"))
        secret_token = self._normalize_webhook_secret_token(webhook.get("secret_token"))
        custom_headers = self._normalize_webhook_custom_headers(webhook.get("custom_headers"))
        body_text = self._canonicalize_webhook_payload(rendered_payload)
        header_preview = self._build_webhook_request_headers(
            webhook_id=normalized_webhook_id,
            body_text=body_text,
            auth_mode=auth_mode,
            secret_token=secret_token,
            custom_headers=custom_headers,
        )

        request_headers = header_preview.get("request_headers")
        normalized_headers = request_headers if isinstance(request_headers, dict) else {}
        signature_preview = self._safe_optional_text(header_preview.get("signature_preview"))

        return {
            "ok": True,
            "webhook_id": normalized_webhook_id,
            "auth_mode": auth_mode,
            "payload_template_mode": self._normalize_webhook_payload_template_mode(
                rendered_payload_data.get("template_mode")
            ),
            "rendered_payload": rendered_payload,
            "rendered_headers": self._sanitize_webhook_headers(normalized_headers),
            "signature_preview": signature_preview,
        }

    def send_test_webhook_event(self, webhook_id: str) -> Dict[str, Any]:
        normalized_webhook_id = webhook_id.strip()
        if not normalized_webhook_id:
            raise ValueError("webhook_id is required")

        webhook = self.runs_repository.get_webhook(normalized_webhook_id)
        if webhook is None:
            raise SequenceWebhookNotFoundError(f"Webhook not found: {webhook_id}")

        webhook_url = str(webhook.get("url") or "").strip()
        if not webhook_url:
            raise ValueError("webhook url is required")

        now = self._now_iso()
        base_payload = self._build_webhook_test_payload(
            webhook=webhook,
            created_at=now,
            event_type="test_event",
            sample_data=None,
        )
        rendered_payload = self._apply_webhook_payload_template(
            webhook=webhook,
            default_payload=base_payload,
        )
        notification_payload = (
            rendered_payload.get("payload")
            if isinstance(rendered_payload.get("payload"), dict)
            else {}
        )
        template_mode = self._normalize_webhook_payload_template_mode(rendered_payload.get("template_mode"))

        test_collection = self._ensure_webhook_test_collection()
        test_collection_id = str(test_collection.get("collection_id") or WEBHOOK_TEST_COLLECTION_ID)
        notification = self.runs_repository.create_notification(
            {
                "notification_id": str(uuid4()),
                "collection_id": test_collection_id,
                "type": "WEBHOOK_TEST_EVENT",
                "severity": "info",
                "message": "This is a test webhook event",
                "created_at": now,
                "is_read": True,
            }
        )

        max_attempts = WEBHOOK_DELIVERY_DEFAULT_MAX_ATTEMPTS
        delivery = self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": str(uuid4()),
                "webhook_id": normalized_webhook_id,
                "notification_id": str(notification.get("notification_id") or ""),
                "collection_id": test_collection_id,
                "payload": notification_payload,
                "delivery_status": "pending",
                "attempt_count": 0,
                "max_attempts": max_attempts,
                "last_attempt_at": None,
                "next_retry_at": None,
                "final_failure_at": None,
                "is_test": True,
                "template_mode": template_mode,
                "auth_mode": self._normalize_webhook_auth_mode(webhook.get("auth_mode")),
                "request_headers": {},
                "signature_timestamp": None,
                "response_status_code": None,
                "response_body": None,
                "error_message": None,
                "created_at": now,
                "delivered_at": None,
            }
        )
        delivery_id = str(delivery.get("delivery_id") or "").strip()
        if not delivery_id:
            raise SequenceWebhookDeliveryNotFoundError("Webhook delivery not found")

        attempted = self._attempt_webhook_delivery(
            delivery_id=delivery_id,
            webhook_id=normalized_webhook_id,
            webhook_url=webhook_url,
            payload=notification_payload,
            prior_attempt_count=0,
            max_attempts=max_attempts,
            auth_mode=self._normalize_webhook_auth_mode(webhook.get("auth_mode")),
            secret_token=self._normalize_webhook_secret_token(webhook.get("secret_token")),
            custom_headers=self._normalize_webhook_custom_headers(webhook.get("custom_headers")),
        )

        return {
            "ok": True,
            "delivery": self._build_webhook_delivery_public_response(attempted),
        }

    def retry_webhook_delivery(self, delivery_id: str) -> Dict[str, Any]:
        normalized_delivery_id = delivery_id.strip()
        if not normalized_delivery_id:
            raise ValueError("delivery_id is required")

        delivery = self.runs_repository.get_webhook_delivery(normalized_delivery_id)
        if delivery is None:
            raise SequenceWebhookDeliveryNotFoundError(f"Webhook delivery not found: {delivery_id}")

        delivery_status = str(delivery.get("delivery_status") or "pending").strip().lower()
        if delivery_status != "failed":
            raise ValueError("Only failed deliveries can be retried")

        webhook_id = str(delivery.get("webhook_id") or "").strip()
        webhook = self.runs_repository.get_webhook(webhook_id)
        if webhook is None:
            raise SequenceWebhookNotFoundError(f"Webhook not found: {webhook_id}")

        payload = delivery.get("payload") if isinstance(delivery.get("payload"), dict) else {}
        prior_attempt_count = int(delivery.get("attempt_count") or 0)
        max_attempts = max(1, int(delivery.get("max_attempts") or WEBHOOK_DELIVERY_DEFAULT_MAX_ATTEMPTS))
        if prior_attempt_count >= max_attempts:
            raise ValueError("Delivery max attempts exhausted")

        retried = self._attempt_webhook_delivery(
            delivery_id=normalized_delivery_id,
            webhook_id=webhook_id,
            webhook_url=str(webhook.get("url") or ""),
            payload=payload,
            prior_attempt_count=prior_attempt_count,
            max_attempts=max_attempts,
            auth_mode=self._normalize_webhook_auth_mode(webhook.get("auth_mode")),
            secret_token=self._normalize_webhook_secret_token(webhook.get("secret_token")),
            custom_headers=self._normalize_webhook_custom_headers(webhook.get("custom_headers")),
        )

        return {
            "ok": True,
            "delivery": self._build_webhook_delivery_public_response(retried),
        }

    def process_webhook_delivery_retries(
        self,
        limit: int = 100,
        webhook_id: Optional[str] = None,
        collection_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_limit = max(1, min(int(limit), 500))
        normalized_webhook_id = self._safe_optional_text(webhook_id)
        normalized_collection_id = self._safe_optional_text(collection_id)
        due_before = self._now_iso()

        pending_deliveries = self.runs_repository.list_webhook_deliveries_pending_retry(
            due_before=due_before,
            limit=normalized_limit,
            webhook_id=normalized_webhook_id,
            collection_id=normalized_collection_id,
        )

        processed: List[Dict[str, Any]] = []
        sent_count = 0
        failed_count = 0
        exhausted_count = 0

        for delivery in pending_deliveries:
            delivery_id = str(delivery.get("delivery_id") or "").strip()
            if not delivery_id:
                continue

            webhook_for_delivery_id = str(delivery.get("webhook_id") or "").strip()
            webhook = self.runs_repository.get_webhook(webhook_for_delivery_id)
            if webhook is None:
                failed_delivery = self._mark_webhook_delivery_failed_without_request(
                    delivery=delivery,
                    error_message=f"Webhook not found: {webhook_for_delivery_id}",
                )
                processed.append(failed_delivery)
                failed_count += 1
                if failed_delivery.get("final_failure_at") is not None:
                    exhausted_count += 1
                continue

            payload = delivery.get("payload") if isinstance(delivery.get("payload"), dict) else {}
            prior_attempt_count = int(delivery.get("attempt_count") or 0)
            max_attempts = max(1, int(delivery.get("max_attempts") or WEBHOOK_DELIVERY_DEFAULT_MAX_ATTEMPTS))

            updated = self._attempt_webhook_delivery(
                delivery_id=delivery_id,
                webhook_id=webhook_for_delivery_id,
                webhook_url=str(webhook.get("url") or ""),
                payload=payload,
                prior_attempt_count=prior_attempt_count,
                max_attempts=max_attempts,
                auth_mode=self._normalize_webhook_auth_mode(webhook.get("auth_mode")),
                secret_token=self._normalize_webhook_secret_token(webhook.get("secret_token")),
                custom_headers=self._normalize_webhook_custom_headers(webhook.get("custom_headers")),
            )
            processed.append(updated)

            if str(updated.get("delivery_status") or "").strip().lower() == "sent":
                sent_count += 1
            else:
                failed_count += 1
                if updated.get("final_failure_at") is not None:
                    exhausted_count += 1

        return {
            "ok": True,
            "processed_count": len(processed),
            "sent_count": sent_count,
            "failed_count": failed_count,
            "exhausted_count": exhausted_count,
            "deliveries": [self._build_webhook_delivery_public_response(item) for item in processed],
        }

    def mark_notification_read(self, notification_id: str, is_read: bool = True) -> Dict[str, Any]:
        normalized_notification_id = notification_id.strip()
        if not normalized_notification_id:
            raise ValueError("notification_id is required")

        updated = self.runs_repository.update_notification_read(
            notification_id=normalized_notification_id,
            is_read=bool(is_read),
        )
        if updated is None:
            raise SequenceNotificationNotFoundError(f"Notification not found: {notification_id}")

        return {
            "ok": True,
            "notification": self._build_notification_public_response(updated),
        }

    def get_collection(self, collection_id: str) -> Optional[Dict[str, Any]]:
        collection = self.runs_repository.get_collection(collection_id)
        if collection is None:
            return None

        items = self.runs_repository.list_collection_items(collection_id)
        payload = self._build_collection_public_response(collection, items=items)
        return {
            "ok": True,
            "collection": self._attach_collection_health_summary(payload),
        }

    def update_collection(
        self,
        collection_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        color: Optional[str] = None,
        editorial_note: Optional[str] = None,
        is_archived: Optional[bool] = None,
        best_request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        existing = self.runs_repository.get_collection(collection_id)
        if existing is None:
            raise SequenceCollectionNotFoundError(f"Sequence collection not found: {collection_id}")

        updates: Dict[str, Any] = {"updated_at": self._now_iso()}

        if name is not None:
            normalized_name = name.strip()
            if not normalized_name:
                raise ValueError("name must be a non-empty string")
            updates["name"] = normalized_name

        if description is not None:
            updates["description"] = description.strip()

        if color is not None:
            updates["color"] = color.strip()

        if editorial_note is not None:
            updates["editorial_note"] = editorial_note.strip()

        if is_archived is not None:
            updates["is_archived"] = bool(is_archived)

        if best_request_id is not None:
            normalized_best_request_id = best_request_id.strip()
            updates["best_request_id"] = normalized_best_request_id or None

        updated = self.runs_repository.update_collection(collection_id, updates)
        if updated is None:
            raise SequenceCollectionNotFoundError(f"Sequence collection not found: {collection_id}")

        items = self.runs_repository.list_collection_items(collection_id)
        return {
            "ok": True,
            "collection": self._build_collection_public_response(updated, items=items),
        }

    def set_collection_best_request(self, collection_id: str, request_id: Optional[str]) -> Dict[str, Any]:
        collection = self.runs_repository.get_collection(collection_id)
        if collection is None:
            raise SequenceCollectionNotFoundError(f"Sequence collection not found: {collection_id}")

        normalized_request_id = request_id.strip() if isinstance(request_id, str) else ""

        if normalized_request_id:
            if self.runs_repository.get(normalized_request_id) is None:
                raise SequencePlanRunNotFoundError(
                    f"Sequence plan-and-render request not found: {normalized_request_id}"
                )

            items = self.runs_repository.list_collection_items(collection_id)
            is_linked = any(
                isinstance(item, dict) and str(item.get("request_id") or "") == normalized_request_id
                for item in items
            )
            if not is_linked:
                raise SequencePlanRunNotFoundError(
                    f"Sequence plan-and-render request not linked in collection: {normalized_request_id}"
                )

        updated = self.runs_repository.update_collection(
            collection_id,
            {
                "best_request_id": normalized_request_id or None,
                "updated_at": self._now_iso(),
            },
        )
        if updated is None:
            raise SequenceCollectionNotFoundError(f"Sequence collection not found: {collection_id}")

        items = self.runs_repository.list_collection_items(collection_id)
        return {
            "ok": True,
            "collection": self._build_collection_public_response(updated, items=items),
        }

    def delete_collection(self, collection_id: str) -> Dict[str, Any]:
        deleted = self.runs_repository.delete_collection(collection_id)
        if not deleted:
            raise SequenceCollectionNotFoundError(f"Sequence collection not found: {collection_id}")

        return {"ok": True, "collection_id": collection_id, "deleted": True}

    def add_collection_items(self, collection_id: str, request_ids: List[str]) -> Dict[str, Any]:
        collection = self.runs_repository.get_collection(collection_id)
        if collection is None:
            raise SequenceCollectionNotFoundError(f"Sequence collection not found: {collection_id}")

        normalized_request_ids = []
        seen = set()
        for request_id in request_ids:
            if not isinstance(request_id, str):
                continue
            trimmed = request_id.strip()
            if not trimmed:
                continue
            if trimmed in seen:
                continue
            seen.add(trimmed)
            normalized_request_ids.append(trimmed)

        if not normalized_request_ids:
            raise ValueError("request_ids must include at least one request_id")

        for request_id in normalized_request_ids:
            if self.runs_repository.get(request_id) is None:
                raise SequencePlanRunNotFoundError(f"Sequence plan-and-render request not found: {request_id}")

        now = self._now_iso()
        self.runs_repository.add_collection_items(
            collection_id=collection_id,
            request_ids=normalized_request_ids,
            added_at=now,
            updated_at=now,
        )

        refreshed_collection = self.runs_repository.get_collection(collection_id)
        items = self.runs_repository.list_collection_items(collection_id)

        return {
            "ok": True,
            "collection": self._build_collection_public_response(refreshed_collection or collection, items=items),
        }

    def remove_collection_item(self, collection_id: str, request_id: str) -> Dict[str, Any]:
        collection = self.runs_repository.get_collection(collection_id)
        if collection is None:
            raise SequenceCollectionNotFoundError(f"Sequence collection not found: {collection_id}")

        removed = self.runs_repository.remove_collection_item(
            collection_id=collection_id,
            request_id=request_id,
            updated_at=self._now_iso(),
        )
        if not removed:
            raise SequencePlanRunNotFoundError(
                f"Sequence plan-and-render request not linked in collection: {request_id}"
            )

        refreshed_collection = self.runs_repository.get_collection(collection_id)
        items = self.runs_repository.list_collection_items(collection_id)
        return {
            "ok": True,
            "collection": self._build_collection_public_response(refreshed_collection or collection, items=items),
        }

    def set_collection_item_highlight(
        self,
        collection_id: str,
        request_id: str,
        is_highlighted: bool,
    ) -> Dict[str, Any]:
        collection = self.runs_repository.get_collection(collection_id)
        if collection is None:
            raise SequenceCollectionNotFoundError(f"Sequence collection not found: {collection_id}")

        item = self.runs_repository.set_collection_item_highlight(
            collection_id=collection_id,
            request_id=request_id,
            is_highlighted=is_highlighted,
            updated_at=self._now_iso(),
        )
        if item is None:
            raise SequencePlanRunNotFoundError(
                f"Sequence plan-and-render request not linked in collection: {request_id}"
            )

        refreshed_collection = self.runs_repository.get_collection(collection_id)
        items = self.runs_repository.list_collection_items(collection_id)
        return {
            "ok": True,
            "collection": self._build_collection_public_response(refreshed_collection or collection, items=items),
            "item": item,
        }

    def get_collection_review(
        self,
        collection_id: str,
        ranking: Optional[str] = None,
        limit: int = 200,
    ) -> Dict[str, Any]:
        collection_payload = self.get_collection(collection_id)
        if collection_payload is None:
            raise SequenceCollectionNotFoundError(f"Sequence collection not found: {collection_id}")

        recent = self.list_recent_requests(
            limit=limit,
            collection_id=collection_id,
            ranking=ranking,
        )

        executions = recent.get("executions") if isinstance(recent.get("executions"), list) else []
        highlighted_count = sum(
            1 for item in executions if isinstance(item, dict) and bool(item.get("collection_candidate", False))
        )
        problematic_count = sum(
            1
            for item in executions
            if isinstance(item, dict)
            and (
                int(item.get("status_summary", {}).get("by_status", {}).get("failed", 0)) > 0
                or int(item.get("status_summary", {}).get("by_status", {}).get("timeout", 0)) > 0
            )
        )

        return {
            "ok": True,
            "collection": collection_payload["collection"],
            "executions": executions,
            "count": len(executions),
            "limit": int(recent.get("limit") or limit),
            "summary": {
                "highlighted_count": highlighted_count,
                "problematic_count": problematic_count,
                "has_best": 1 if collection_payload["collection"].get("best_request_id") else 0,
            },
        }

    def get_collection_audit(self, collection_id: str, emit_notifications: bool = True) -> Dict[str, Any]:
        collection = self.runs_repository.get_collection(collection_id)
        if collection is None:
            raise SequenceCollectionNotFoundError(f"Sequence collection not found: {collection_id}")

        items = self.runs_repository.list_collection_items(collection_id)
        linked_request_ids: List[str] = []
        seen_request_ids = set()
        for item in items:
            if not isinstance(item, dict):
                continue
            request_id = str(item.get("request_id") or "").strip()
            if not request_id or request_id in seen_request_ids:
                continue
            seen_request_ids.add(request_id)
            linked_request_ids.append(request_id)

        total_executions = 0
        approved_count = 0
        rejected_count = 0
        pending_review_count = 0
        favorite_count = 0
        executions_without_review = 0

        total_retries = 0
        total_jobs = 0
        timeout_count = 0
        failed_count = 0
        succeeded_jobs = 0

        stale_request_ids: List[str] = []

        for request_id in linked_request_ids:
            run_record = self.runs_repository.get(request_id)
            if run_record is None:
                stale_request_ids.append(request_id)
                continue

            total_executions += 1

            review_status = str(run_record.get("review_status") or "pending_review").strip().lower()
            if review_status == "approved":
                approved_count += 1
            elif review_status == "rejected":
                rejected_count += 1
            else:
                pending_review_count += 1

            if bool(run_record.get("is_favorite", False)):
                favorite_count += 1

            total_retries += self._compute_total_retries(run_record)

            latest_jobs = self._collect_latest_jobs(run_record)
            total_jobs += len(latest_jobs)
            status_summary = self._build_status_summary(latest_jobs)
            by_status = status_summary.get("by_status") if isinstance(status_summary.get("by_status"), dict) else {}
            failed_count += int(by_status.get("failed") or 0)
            timeout_count += int(by_status.get("timeout") or 0)
            succeeded_jobs += int(by_status.get("succeeded") or 0)

            review_history_summary = self.runs_repository.get_review_history_summary(request_id)
            if int(review_history_summary.get("history_count") or 0) <= 0:
                executions_without_review += 1

        success_ratio = round((succeeded_jobs / total_jobs), 6) if total_jobs > 0 else 0.0
        best_request_id = self._safe_optional_text(collection.get("best_request_id"))

        signals: List[Dict[str, Any]] = []
        failed_red_threshold = max(3, int(total_jobs * 0.25)) if total_jobs > 0 else 3
        timeout_red_threshold = max(2, int(total_jobs * 0.20)) if total_jobs > 0 else 2

        if stale_request_ids:
            signals.append(
                {
                    "code": "STALE_COLLECTION_ITEMS",
                    "severity": "warning",
                    "message": (
                        f"{len(stale_request_ids)} request_id(s) linked in collection no longer exist in sequence runs."
                    ),
                }
            )

        if best_request_id and best_request_id not in seen_request_ids:
            signals.append(
                {
                    "code": "BEST_REQUEST_NOT_IN_COLLECTION",
                    "severity": "critical",
                    "message": "best_request_id is configured but is not currently linked to this collection.",
                }
            )

        if total_executions > 0 and not best_request_id:
            signals.append(
                {
                    "code": "MISSING_BEST_REQUEST",
                    "severity": "warning",
                    "message": "Collection has executions but no best_request_id selected.",
                }
            )

        pending_yellow_threshold = max(2, (total_executions + 1) // 2)
        if pending_review_count >= pending_yellow_threshold and total_executions > 0:
            signals.append(
                {
                    "code": "PENDING_EDITORIAL_REVIEW_HIGH",
                    "severity": "warning",
                    "message": (
                        f"High pending editorial review: {pending_review_count}/{total_executions} executions pending."
                    ),
                }
            )
        elif pending_review_count > 0:
            signals.append(
                {
                    "code": "PENDING_EDITORIAL_REVIEW",
                    "severity": "warning",
                    "message": f"{pending_review_count} execution(s) are still pending editorial decision.",
                }
            )

        retry_yellow_threshold = max(3, total_executions)
        if total_retries >= retry_yellow_threshold and total_executions > 0:
            signals.append(
                {
                    "code": "HIGH_RETRY_VOLUME",
                    "severity": "warning",
                    "message": f"High retry volume: total_retries={total_retries}.",
                }
            )

        if executions_without_review > 0:
            signals.append(
                {
                    "code": "MISSING_REVIEW_HISTORY",
                    "severity": "warning",
                    "message": f"{executions_without_review} execution(s) have no editorial history entries.",
                }
            )

        if failed_count >= failed_red_threshold and total_jobs > 0:
            signals.append(
                {
                    "code": "FAILED_COUNT_CRITICAL",
                    "severity": "critical",
                    "message": (
                        f"Failed jobs exceed threshold: failed={failed_count}, threshold={failed_red_threshold}."
                    ),
                }
            )
        elif failed_count > 0:
            signals.append(
                {
                    "code": "FAILED_COUNT_WARNING",
                    "severity": "warning",
                    "message": f"Failed jobs detected: failed={failed_count}.",
                }
            )

        if timeout_count >= timeout_red_threshold and total_jobs > 0:
            signals.append(
                {
                    "code": "TIMEOUT_COUNT_CRITICAL",
                    "severity": "critical",
                    "message": (
                        f"Timeout jobs exceed threshold: timeout={timeout_count}, threshold={timeout_red_threshold}."
                    ),
                }
            )
        elif timeout_count > 0:
            signals.append(
                {
                    "code": "TIMEOUT_COUNT_WARNING",
                    "severity": "warning",
                    "message": f"Timeout jobs detected: timeout={timeout_count}.",
                }
            )

        if total_jobs > 0 and (failed_count + timeout_count) > 0 and success_ratio < 0.45:
            signals.append(
                {
                    "code": "LOW_SUCCESS_RATIO_CRITICAL",
                    "severity": "critical",
                    "message": f"Overall success ratio is critically low: {success_ratio:.3f}.",
                }
            )
        elif total_jobs > 0 and (failed_count + timeout_count) > 0 and success_ratio < 0.75:
            signals.append(
                {
                    "code": "LOW_SUCCESS_RATIO_WARNING",
                    "severity": "warning",
                    "message": f"Overall success ratio is below target: {success_ratio:.3f}.",
                }
            )

        success_ratio_summary = {
            "succeeded_jobs": succeeded_jobs,
            "total_jobs": total_jobs,
            "ratio": success_ratio,
        }

        critical_count = sum(
            1
            for signal in signals
            if isinstance(signal, dict) and str(signal.get("severity") or "").lower() == "critical"
        )
        warning_count = sum(
            1
            for signal in signals
            if isinstance(signal, dict) and str(signal.get("severity") or "").lower() == "warning"
        )

        if critical_count > 0:
            health_status = "red"
        elif warning_count > 0:
            health_status = "yellow"
        else:
            health_status = "green"

        alerts = [
            str(signal.get("message") or "")
            for signal in signals
            if isinstance(signal, dict)
            and str(signal.get("severity") or "").lower() in {"warning", "critical"}
            and str(signal.get("message") or "").strip()
        ]

        if emit_notifications:
            self._emit_collection_notifications(
                collection_id=collection_id,
                health_status=health_status,
                best_request_id=best_request_id,
                total_executions=total_executions,
                pending_review_count=pending_review_count,
                failed_count=failed_count,
                timeout_count=timeout_count,
                failed_red_threshold=failed_red_threshold,
                timeout_red_threshold=timeout_red_threshold,
            )

        return {
            "ok": True,
            "collection_id": collection_id,
            "total_executions": total_executions,
            "approved_count": approved_count,
            "rejected_count": rejected_count,
            "pending_review_count": pending_review_count,
            "favorite_count": favorite_count,
            "total_retries": total_retries,
            "total_jobs": total_jobs,
            "timeout_count": timeout_count,
            "failed_count": failed_count,
            "success_ratio_summary": success_ratio_summary,
            "best_request_id": best_request_id,
            "executions_without_review": executions_without_review,
            "health_status": health_status,
            "alerts": alerts,
            "editorial_summary": {
                "total_executions": total_executions,
                "approved_count": approved_count,
                "rejected_count": rejected_count,
                "pending_review_count": pending_review_count,
                "favorite_count": favorite_count,
                "executions_without_review": executions_without_review,
            },
            "operational_summary": {
                "total_jobs": total_jobs,
                "total_retries": total_retries,
                "failed_count": failed_count,
                "timeout_count": timeout_count,
                "success_ratio_summary": success_ratio_summary,
            },
            "signals": signals,
        }

    def get_plan_and_render_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        run_record = self.runs_repository.get(request_id)
        if not run_record:
            return None

        latest_jobs = self._collect_latest_jobs(run_record)
        updated_record = self.runs_repository.update(
            request_id,
            {
                "updated_at": self._now_iso(),
                "created_jobs": latest_jobs,
                "job_count": len(latest_jobs),
            },
        )

        if updated_record:
            run_record = updated_record
        else:
            run_record["created_jobs"] = latest_jobs
            run_record["job_count"] = len(latest_jobs)

        return self._build_public_response(run_record)

    def list_recent_requests(
        self,
        limit: int = 20,
        q: Optional[str] = None,
        project_id: Optional[str] = None,
        sequence_id: Optional[str] = None,
        status: Optional[str] = None,
        is_favorite: Optional[bool] = None,
        tag: Optional[str] = None,
        ranking: Optional[str] = None,
        collection_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        normalized_limit = max(1, min(int(limit), 200))
        normalized_q = self._safe_optional_text(q)
        normalized_project_id = self._safe_optional_text(project_id)
        normalized_sequence_id = self._safe_optional_text(sequence_id)
        normalized_status = self._normalize_recent_status_filter(status)
        normalized_tag = self._safe_optional_text(tag)
        normalized_ranking = self._normalize_recent_ranking_filter(ranking)
        normalized_collection_id = self._safe_optional_text(collection_id)

        collection_items_by_request_id: Dict[str, Dict[str, Any]] = {}
        collection_best_request_id: Optional[str] = None
        if normalized_collection_id is not None:
            collection = self.runs_repository.get_collection(normalized_collection_id)
            if collection is None:
                raise SequenceCollectionNotFoundError(f"Sequence collection not found: {normalized_collection_id}")

            collection_best_request_id = self._safe_optional_text(collection.get("best_request_id"))

            items = self.runs_repository.list_collection_items(normalized_collection_id)
            collection_items_by_request_id = {
                str(item.get("request_id") or ""): item
                for item in items
                if isinstance(item, dict) and isinstance(item.get("request_id"), str)
            }

        runs = self.runs_repository.list_recent(None)

        executions: List[Dict[str, Any]] = []
        for run_record in runs:
            request_id = str(run_record.get("request_id") or "")
            collection_item = collection_items_by_request_id.get(request_id)
            if normalized_collection_id is not None and collection_item is None:
                continue

            latest_jobs = self._collect_latest_jobs(run_record)
            status_summary = self._build_status_summary(latest_jobs)

            plan = run_record.get("plan") if isinstance(run_record.get("plan"), dict) else {}
            request_payload = run_record.get("request_payload") if isinstance(run_record.get("request_payload"), dict) else {}

            sequence_summary = self._safe_optional_text(plan.get("sequence_summary"))
            if sequence_summary is None:
                sequence_summary = self._build_fallback_sequence_summary(request_payload, run_record)

            execution_item = {
                "request_id": request_id,
                "created_at": str(run_record.get("created_at") or ""),
                "updated_at": str(run_record.get("updated_at") or ""),
                "sequence_summary": sequence_summary,
                "job_count": len(latest_jobs),
                "success_ratio": self._compute_success_ratio(status_summary),
                "total_retries": self._compute_total_retries(run_record),
                "status_summary": status_summary,
                "sequence_id": self._safe_optional_text(request_payload.get("sequence_id")),
                "project_id": self._safe_optional_text(request_payload.get("project_id")),
                "is_favorite": bool(run_record.get("is_favorite", False)),
                "tags": self._normalize_meta_tags(run_record.get("tags") if isinstance(run_record.get("tags"), list) else []),
                "note": str(run_record.get("note") or ""),
                "review_status": str(run_record.get("review_status") or "pending_review"),
                "review_note": str(run_record.get("review_note") or ""),
                "reviewed_at": str(run_record.get("reviewed_at")) if run_record.get("reviewed_at") else None,
                "collection_candidate": bool(collection_item.get("is_highlighted", False)) if collection_item else False,
                "collection_added_at": str(collection_item.get("added_at") or "") if collection_item else None,
                "collection_best": bool(collection_best_request_id and collection_best_request_id == request_id),
            }

            if not self._matches_recent_filters(
                execution_item,
                q=normalized_q,
                project_id=normalized_project_id,
                sequence_id=normalized_sequence_id,
                status=normalized_status,
                is_favorite=is_favorite,
                tag=normalized_tag,
            ):
                continue

            executions.append(execution_item)

        if normalized_ranking is not None:
            executions = self._apply_recent_ranking(executions, normalized_ranking)

        executions = executions[:normalized_limit]

        return {
            "ok": True,
            "executions": executions,
            "limit": normalized_limit,
            "count": len(executions),
        }

    def execute_job(self, job_id: str) -> None:
        self.render_jobs_service.execute_job(job_id)

    def _collect_latest_jobs(self, run_record: Dict[str, Any]) -> List[Dict[str, Any]]:
        stored_jobs = run_record.get("created_jobs") if isinstance(run_record.get("created_jobs"), list) else []
        stored_by_id = {
            str(item.get("job_id")): item
            for item in stored_jobs
            if isinstance(item, dict) and isinstance(item.get("job_id"), str)
        }

        latest_jobs: List[Dict[str, Any]] = []
        job_ids = run_record.get("job_ids") if isinstance(run_record.get("job_ids"), list) else []
        for job_id in job_ids:
            if not isinstance(job_id, str) or not job_id.strip():
                continue

            current_job = self.render_jobs_service.get_job(job_id)
            if isinstance(current_job, dict):
                latest_jobs.append(current_job)
                continue

            fallback = stored_by_id.get(job_id)
            if fallback is not None:
                latest_jobs.append(fallback)

        if latest_jobs:
            return latest_jobs

        return [item for item in stored_jobs if isinstance(item, dict)]

    def _shot_links_for_shot(self, run_record: Dict[str, Any], shot_id: str) -> List[Dict[str, Any]]:
        links = run_record.get("shot_job_links") if isinstance(run_record.get("shot_job_links"), list) else []
        return [
            item
            for item in links
            if isinstance(item, dict) and str(item.get("shot_id") or "") == shot_id
        ]

    def _resolve_job_by_id(self, run_record: Dict[str, Any], job_id: str) -> Optional[Dict[str, Any]]:
        current_job = self.render_jobs_service.get_job(job_id)
        if isinstance(current_job, dict):
            return current_job

        stored_jobs = run_record.get("created_jobs") if isinstance(run_record.get("created_jobs"), list) else []
        for item in stored_jobs:
            if isinstance(item, dict) and str(item.get("job_id") or "") == job_id:
                return deepcopy(item)

        return None

    def _resolve_render_context(
        self,
        run_record: Dict[str, Any],
        shot_id: str,
        parent_job: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        links = self._shot_links_for_shot(run_record, shot_id)
        for link in reversed(links):
            context = link.get("render_context") if isinstance(link.get("render_context"), dict) else None
            if context is not None:
                return deepcopy(context)

        parent_payload = parent_job.get("request_payload") if isinstance(parent_job.get("request_payload"), dict) else {}
        metadata = parent_payload.get("metadata") if isinstance(parent_payload.get("metadata"), dict) else {}
        payload_context = metadata.get("render_context") if isinstance(metadata.get("render_context"), dict) else None
        if payload_context is not None:
            return deepcopy(payload_context)

        plan = run_record.get("plan") if isinstance(run_record.get("plan"), dict) else {}
        render_inputs = plan.get("render_inputs") if isinstance(plan.get("render_inputs"), dict) else {}
        jobs = render_inputs.get("jobs") if isinstance(render_inputs.get("jobs"), list) else []
        for job_input in jobs:
            if not isinstance(job_input, dict):
                continue
            if str(job_input.get("shot_id") or "") != shot_id:
                continue

            context = job_input.get("render_context") if isinstance(job_input.get("render_context"), dict) else None
            if context is not None:
                return deepcopy(context)

        return None

    def _apply_prompt_override(self, request_payload: Dict[str, Any], text: str) -> None:
        prompt_graph = request_payload.get("prompt") if isinstance(request_payload.get("prompt"), dict) else None
        if prompt_graph is None:
            return

        target_node = prompt_graph.get("6") if isinstance(prompt_graph.get("6"), dict) else None
        if target_node and target_node.get("class_type") == "CLIPTextEncode":
            inputs = target_node.get("inputs") if isinstance(target_node.get("inputs"), dict) else {}
            inputs["text"] = text
            target_node["inputs"] = inputs
            return

        clip_nodes = self._clip_text_nodes(prompt_graph)
        if clip_nodes:
            clip_nodes[0]["inputs"]["text"] = text

    def _apply_negative_prompt_override(self, request_payload: Dict[str, Any], text: str) -> None:
        prompt_graph = request_payload.get("prompt") if isinstance(request_payload.get("prompt"), dict) else None
        if prompt_graph is None:
            return

        target_node = prompt_graph.get("7") if isinstance(prompt_graph.get("7"), dict) else None
        if target_node and target_node.get("class_type") == "CLIPTextEncode":
            inputs = target_node.get("inputs") if isinstance(target_node.get("inputs"), dict) else {}
            inputs["text"] = text
            target_node["inputs"] = inputs
            return

        clip_nodes = self._clip_text_nodes(prompt_graph)
        if len(clip_nodes) >= 2:
            clip_nodes[1]["inputs"]["text"] = text
        elif clip_nodes:
            clip_nodes[0]["inputs"]["text"] = text

    def _clip_text_nodes(self, prompt_graph: Dict[str, Any]) -> List[Dict[str, Any]]:
        nodes: List[tuple[int, Dict[str, Any]]] = []
        for node_id, node in prompt_graph.items():
            if not isinstance(node, dict):
                continue
            if node.get("class_type") != "CLIPTextEncode":
                continue

            inputs = node.get("inputs") if isinstance(node.get("inputs"), dict) else {}
            node["inputs"] = inputs
            try:
                order = int(str(node_id))
            except ValueError:
                order = len(nodes) + 1000
            nodes.append((order, node))

        nodes.sort(key=lambda item: item[0])
        return [item[1] for item in nodes]

    def _inject_retry_trace_metadata(
        self,
        request_payload: Dict[str, Any],
        request_id: str,
        shot_id: str,
        parent_job_id: str,
        retry_index: int,
        reason: Optional[str],
    ) -> None:
        metadata = request_payload.get("metadata") if isinstance(request_payload.get("metadata"), dict) else {}
        metadata["sequence_retry"] = {
            "request_id": request_id,
            "shot_id": shot_id,
            "parent_job_id": parent_job_id,
            "retry_index": retry_index,
            "reason": reason,
        }
        request_payload["metadata"] = metadata

    def _build_public_response(self, run_record: Dict[str, Any]) -> Dict[str, Any]:
        created_jobs = run_record.get("created_jobs") if isinstance(run_record.get("created_jobs"), list) else []
        job_ids = run_record.get("job_ids") if isinstance(run_record.get("job_ids"), list) else []
        shot_job_links = run_record.get("shot_job_links") if isinstance(run_record.get("shot_job_links"), list) else []
        prompt_comparisons = run_record.get("prompt_comparisons") if isinstance(run_record.get("prompt_comparisons"), list) else []
        prompt_comparison_metrics = run_record.get("prompt_comparison_metrics") if isinstance(run_record.get("prompt_comparison_metrics"), dict) else {}
        plan = run_record.get("plan") if isinstance(run_record.get("plan"), dict) else {}
        request_payload = run_record.get("request_payload") if isinstance(run_record.get("request_payload"), dict) else {}
        request_id = str(run_record.get("request_id") or "")

        status_summary = self._build_status_summary(created_jobs)
        collections = self.runs_repository.list_collections_for_request(request_id) if request_id else []
        review_history_summary = self.runs_repository.get_review_history_summary(request_id) if request_id else {
            "history_count": 0,
            "latest_created_at": None,
        }

        return {
            "ok": True,
            "request_id": request_id,
            "request_payload": request_payload,
            "plan": plan,
            "prompt_comparisons": [item for item in prompt_comparisons if isinstance(item, dict)],
            "prompt_comparison_metrics": self._normalize_prompt_comparison_metrics(prompt_comparison_metrics),
            "created_jobs": created_jobs,
            "job_count": len(created_jobs),
            "job_ids": [str(item) for item in job_ids if isinstance(item, str)],
            "shot_job_links": [item for item in shot_job_links if isinstance(item, dict)],
            "status_summary": status_summary,
            "is_favorite": bool(run_record.get("is_favorite", False)),
            "tags": self._normalize_meta_tags(run_record.get("tags") if isinstance(run_record.get("tags"), list) else []),
            "note": str(run_record.get("note") or ""),
            "review_status": str(run_record.get("review_status") or "pending_review"),
            "review_note": str(run_record.get("review_note") or ""),
            "reviewed_at": str(run_record.get("reviewed_at")) if run_record.get("reviewed_at") else None,
            "review_history_summary": {
                "history_count": int(review_history_summary.get("history_count") or 0),
                "latest_created_at": (
                    str(review_history_summary.get("latest_created_at"))
                    if review_history_summary.get("latest_created_at")
                    else None
                ),
            },
            "collections": [
                {
                    "collection_id": str(item.get("collection_id") or ""),
                    "name": str(item.get("name") or ""),
                    "is_highlighted": bool(item.get("is_highlighted", False)),
                    "is_best": bool(item.get("is_best", False)),
                    "added_at": str(item.get("added_at") or ""),
                }
                for item in collections
                if isinstance(item, dict)
            ],
        }

    def _build_prompt_comparison_entry(
        self,
        *,
        request_id: str,
        shot_id: str,
        job_id: str,
        retry_index: int,
        job_input: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        prompt_base = str(job_input.get("prompt_base") or "").strip()
        prompt_enriched = str(job_input.get("prompt_enriched") or prompt_base).strip()
        semantic_summary_used = job_input.get("semantic_summary_used")
        semantic_enrichment_applied = bool(job_input.get("semantic_enrichment_applied", False))

        if not shot_id.strip() or not job_id.strip():
            return None

        return {
            "request_id": request_id,
            "shot_id": shot_id,
            "job_id": job_id,
            "retry_index": retry_index,
            "prompt_base": prompt_base,
            "prompt_enriched": prompt_enriched,
            "semantic_summary_used": str(semantic_summary_used).strip() if isinstance(semantic_summary_used, str) and semantic_summary_used.strip() else None,
            "semantic_enrichment_applied": semantic_enrichment_applied,
            "source": "initial",
        }

    def _build_prompt_comparison_metrics(self, prompt_comparisons: List[Dict[str, Any]]) -> Dict[str, Any]:
        total = 0
        enriched = 0
        retries = 0
        sources: Dict[str, int] = {}
        unique_shots: set[str] = set()
        shots_with_retries: set[str] = set()
        shots_with_enrichment: set[str] = set()

        for item in prompt_comparisons:
            if not isinstance(item, dict):
                continue

            total += 1
            shot_id = str(item.get("shot_id") or "").strip()
            if shot_id:
                unique_shots.add(shot_id)

            if bool(item.get("semantic_enrichment_applied", False)):
                enriched += 1
                if shot_id:
                    shots_with_enrichment.add(shot_id)

            retry_index = item.get("retry_index")
            if isinstance(retry_index, int) and retry_index > 0:
                retries += 1
                if shot_id:
                    shots_with_retries.add(shot_id)

            source = str(item.get("source") or "live").strip() or "live"
            sources[source] = sources.get(source, 0) + 1

        return {
            "total": total,
            "enriched": enriched,
            "not_enriched": max(total - enriched, 0),
            "retries": retries,
            "enrichment_ratio": float(enriched / total) if total > 0 else 0.0,
            "unique_shots": len(unique_shots),
            "shots_with_retries": len(shots_with_retries),
            "shots_with_enrichment": len(shots_with_enrichment),
            "sources": sources,
        }

    def _normalize_prompt_comparison_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        raw_sources = metrics.get("sources") if isinstance(metrics.get("sources"), dict) else {}
        normalized_sources = {
            str(key): int(value or 0)
            for key, value in raw_sources.items()
            if str(key).strip()
        }

        total = int(metrics.get("total") or 0)
        enriched = int(metrics.get("enriched") or 0)
        retries = int(metrics.get("retries") or 0)
        enrichment_ratio = float(metrics.get("enrichment_ratio") or 0.0)
        unique_shots = int(metrics.get("unique_shots") or 0)
        shots_with_retries = int(metrics.get("shots_with_retries") or 0)
        shots_with_enrichment = int(metrics.get("shots_with_enrichment") or 0)

        return {
            "total": total,
            "enriched": enriched,
            "not_enriched": int(metrics.get("not_enriched") or max(total - enriched, 0)),
            "retries": retries,
            "enrichment_ratio": enrichment_ratio,
            "unique_shots": unique_shots,
            "shots_with_retries": shots_with_retries,
            "shots_with_enrichment": shots_with_enrichment,
            "sources": normalized_sources,
        }

    def _resolve_retry_prompt_base(
        self,
        run_record: Dict[str, Any],
        shot_id: str,
        request_payload: Dict[str, Any],
    ) -> str:
        prompt_comparisons = run_record.get("prompt_comparisons") if isinstance(run_record.get("prompt_comparisons"), list) else []
        for item in reversed(prompt_comparisons):
            if not isinstance(item, dict):
                continue
            if str(item.get("shot_id") or "").strip() != shot_id:
                continue
            prompt_base = str(item.get("prompt_base") or "").strip()
            if prompt_base:
                return prompt_base

        return self._extract_positive_prompt_text(request_payload)

    def _extract_positive_prompt_text(self, request_payload: Dict[str, Any]) -> str:
        prompt_graph = request_payload.get("prompt") if isinstance(request_payload.get("prompt"), dict) else {}
        for node_id, node in prompt_graph.items():
            if not isinstance(node, dict):
                continue
            if str(node.get("class_type") or "") != "CLIPTextEncode":
                continue
            inputs = node.get("inputs") if isinstance(node.get("inputs"), dict) else {}
            text_value = inputs.get("text")
            if isinstance(text_value, str) and text_value.strip():
                if str(node_id) == "6":
                    return text_value.strip()

        for node in prompt_graph.values():
            if not isinstance(node, dict):
                continue
            if str(node.get("class_type") or "") != "CLIPTextEncode":
                continue
            inputs = node.get("inputs") if isinstance(node.get("inputs"), dict) else {}
            text_value = inputs.get("text")
            if isinstance(text_value, str) and text_value.strip():
                return text_value.strip()

        return ""

    def _build_status_summary(self, created_jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        by_status: Dict[str, int] = {}

        for job in created_jobs:
            status_value = "unknown"
            if isinstance(job, dict):
                raw_status = job.get("status")
                if isinstance(raw_status, str) and raw_status.strip():
                    status_value = raw_status.strip().lower()

            by_status[status_value] = by_status.get(status_value, 0) + 1

        terminal_jobs = 0
        for status in ("succeeded", "failed", "timeout"):
            terminal_jobs += by_status.get(status, 0)

        return {
            "total_jobs": len(created_jobs),
            "by_status": by_status,
            "terminal_jobs": terminal_jobs,
        }

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _safe_optional_text(self, value: Any) -> Optional[str]:
        if not isinstance(value, str):
            return None

        normalized = value.strip()
        return normalized or None

    def _build_fallback_sequence_summary(self, request_payload: Dict[str, Any], run_record: Dict[str, Any]) -> str:
        sequence_id = self._safe_optional_text(request_payload.get("sequence_id")) or "sequence"
        project_id = self._safe_optional_text(request_payload.get("project_id")) or "project"
        request_id = str(run_record.get("request_id") or "")
        short_request_id = request_id[:8] if request_id else "unknown"
        return f"{sequence_id} ({project_id}) [{short_request_id}]"

    def _normalize_recent_status_filter(self, value: Optional[str]) -> Optional[str]:
        normalized = self._safe_optional_text(value)
        if normalized is None:
            return None

        lowered = normalized.lower()
        if lowered not in RECENT_STATUS_FILTER_VALUES:
            raise ValueError("status must be one of queued, running, succeeded, failed, timeout")
        return lowered

    def _normalize_recent_ranking_filter(self, value: Optional[str]) -> Optional[str]:
        normalized = self._safe_optional_text(value)
        if normalized is None:
            return None

        lowered = normalized.lower()
        if lowered not in RECENT_RANKING_FILTER_VALUES:
            raise ValueError("ranking must be one of most_stable, most_problematic, most_retries, highest_success_ratio")
        return lowered

    def _matches_recent_filters(
        self,
        execution_item: Dict[str, Any],
        q: Optional[str],
        project_id: Optional[str],
        sequence_id: Optional[str],
        status: Optional[str],
        is_favorite: Optional[bool],
        tag: Optional[str],
    ) -> bool:
        item_project_id = self._safe_optional_text(execution_item.get("project_id"))
        item_sequence_id = self._safe_optional_text(execution_item.get("sequence_id"))
        item_is_favorite = bool(execution_item.get("is_favorite", False))
        item_tags = self._normalize_meta_tags(execution_item.get("tags") if isinstance(execution_item.get("tags"), list) else [])

        if project_id is not None:
            if item_project_id is None or item_project_id.lower() != project_id.lower():
                return False

        if sequence_id is not None:
            if item_sequence_id is None or item_sequence_id.lower() != sequence_id.lower():
                return False

        if status is not None:
            status_summary = execution_item.get("status_summary") if isinstance(execution_item.get("status_summary"), dict) else {}
            by_status = status_summary.get("by_status") if isinstance(status_summary.get("by_status"), dict) else {}
            count_value = by_status.get(status)
            if not isinstance(count_value, int) or count_value <= 0:
                return False

        if is_favorite is not None and item_is_favorite != is_favorite:
            return False

        if tag is not None:
            lowered_tag = tag.lower()
            if not any(lowered_tag == item_tag.lower() for item_tag in item_tags):
                return False

        if q is not None:
            query = q.lower()
            candidate_values = [
                str(execution_item.get("request_id") or ""),
                str(execution_item.get("sequence_summary") or ""),
                item_project_id or "",
                item_sequence_id or "",
            ]
            if not any(query in candidate.lower() for candidate in candidate_values):
                return False

        return True

    def _compute_success_ratio(self, status_summary: Dict[str, Any]) -> float:
        total_jobs = int(status_summary.get("total_jobs") or 0)
        if total_jobs <= 0:
            return 0.0

        by_status = status_summary.get("by_status") if isinstance(status_summary.get("by_status"), dict) else {}
        success_count = int(by_status.get("succeeded") or 0)
        return round(success_count / total_jobs, 6)

    def _compute_total_retries(self, run_record: Dict[str, Any]) -> int:
        links = run_record.get("shot_job_links") if isinstance(run_record.get("shot_job_links"), list) else []

        retries = 0
        for link in links:
            if not isinstance(link, dict):
                continue

            retry_index = link.get("retry_index")
            if isinstance(retry_index, int):
                if retry_index > 0:
                    retries += 1
                continue

            parent_job_id = link.get("parent_job_id")
            if isinstance(parent_job_id, str) and parent_job_id.strip():
                retries += 1

        return retries

    def _apply_recent_ranking(self, executions: List[Dict[str, Any]], ranking: str) -> List[Dict[str, Any]]:
        if ranking == "most_stable":
            for item in executions:
                stats = item.get("status_summary") if isinstance(item.get("status_summary"), dict) else {}
                by_status = stats.get("by_status") if isinstance(stats.get("by_status"), dict) else {}
                failed_count = int(by_status.get("failed") or 0)
                timeout_count = int(by_status.get("timeout") or 0)
                queued_count = int(by_status.get("queued") or 0)
                running_count = int(by_status.get("running") or 0)
                retries = int(item.get("total_retries") or 0)
                success_ratio = float(item.get("success_ratio") or 0.0)

                score = round(
                    (success_ratio * 100.0)
                    - (failed_count * 20.0)
                    - (timeout_count * 30.0)
                    - (retries * 4.0)
                    - ((queued_count + running_count) * 5.0),
                    6,
                )
                item["ranking_score"] = score
                item["ranking_reason"] = (
                    f"success_ratio={success_ratio:.3f}, failed={failed_count}, "
                    f"timeout={timeout_count}, retries={retries}"
                )

            return sorted(
                executions,
                key=lambda item: (
                    float(item.get("ranking_score") or 0.0),
                    str(item.get("updated_at") or ""),
                    str(item.get("request_id") or ""),
                ),
                reverse=True,
            )

        if ranking == "most_problematic":
            for item in executions:
                stats = item.get("status_summary") if isinstance(item.get("status_summary"), dict) else {}
                by_status = stats.get("by_status") if isinstance(stats.get("by_status"), dict) else {}
                failed_count = int(by_status.get("failed") or 0)
                timeout_count = int(by_status.get("timeout") or 0)
                queued_count = int(by_status.get("queued") or 0)
                running_count = int(by_status.get("running") or 0)
                retries = int(item.get("total_retries") or 0)
                success_ratio = float(item.get("success_ratio") or 0.0)

                score = round(
                    (failed_count * 25.0)
                    + (timeout_count * 35.0)
                    + (retries * 8.0)
                    + ((1.0 - success_ratio) * 100.0)
                    + ((queued_count + running_count) * 5.0),
                    6,
                )
                item["ranking_score"] = score
                item["ranking_reason"] = (
                    f"failed={failed_count}, timeout={timeout_count}, retries={retries}, "
                    f"success_ratio={success_ratio:.3f}"
                )

            return sorted(
                executions,
                key=lambda item: (
                    float(item.get("ranking_score") or 0.0),
                    str(item.get("updated_at") or ""),
                    str(item.get("request_id") or ""),
                ),
                reverse=True,
            )

        if ranking == "most_retries":
            for item in executions:
                retries = int(item.get("total_retries") or 0)
                item["ranking_score"] = float(retries)
                item["ranking_reason"] = f"total_retries={retries}"

            return sorted(
                executions,
                key=lambda item: (
                    int(item.get("total_retries") or 0),
                    str(item.get("updated_at") or ""),
                    str(item.get("request_id") or ""),
                ),
                reverse=True,
            )

        if ranking == "highest_success_ratio":
            for item in executions:
                success_ratio = float(item.get("success_ratio") or 0.0)
                retries = int(item.get("total_retries") or 0)
                item["ranking_score"] = round(success_ratio, 6)
                item["ranking_reason"] = f"success_ratio={success_ratio:.3f}, total_retries={retries}"

            return sorted(
                executions,
                key=lambda item: (
                    float(item.get("success_ratio") or 0.0),
                    -int(item.get("total_retries") or 0),
                    str(item.get("updated_at") or ""),
                    str(item.get("request_id") or ""),
                ),
                reverse=True,
            )

        return executions

    def _build_collection_public_response(
        self,
        collection: Dict[str, Any],
        items: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        payload = {
            "collection_id": str(collection.get("collection_id") or ""),
            "name": str(collection.get("name") or ""),
            "description": str(collection.get("description") or ""),
            "editorial_note": str(collection.get("editorial_note") or ""),
            "color": str(collection.get("color") or ""),
            "is_archived": bool(collection.get("is_archived", False)),
            "best_request_id": self._safe_optional_text(collection.get("best_request_id")),
            "created_at": str(collection.get("created_at") or ""),
            "updated_at": str(collection.get("updated_at") or ""),
            "item_count": int(collection.get("item_count") or 0),
            "highlighted_count": int(collection.get("highlighted_count") or 0),
            "health_status": str(collection.get("health_status") or "green"),
            "alerts": [
                str(item)
                for item in (collection.get("alerts") if isinstance(collection.get("alerts"), list) else [])
                if isinstance(item, str) and item.strip()
            ],
        }

        if items is not None:
            payload["items"] = [
                {
                    "collection_id": str(item.get("collection_id") or ""),
                    "request_id": str(item.get("request_id") or ""),
                    "is_highlighted": bool(item.get("is_highlighted", False)),
                    "added_at": str(item.get("added_at") or ""),
                }
                for item in items
                if isinstance(item, dict)
            ]

        return payload

    def _attach_collection_health_summary(self, collection_payload: Dict[str, Any]) -> Dict[str, Any]:
        collection_id = str(collection_payload.get("collection_id") or "")
        if not collection_id:
            collection_payload["health_status"] = "green"
            collection_payload["alerts"] = []
            return collection_payload

        audit = self.get_collection_audit(collection_id, emit_notifications=False)
        collection_payload["health_status"] = str(audit.get("health_status") or "green")
        collection_payload["alerts"] = [
            str(item)
            for item in (audit.get("alerts") if isinstance(audit.get("alerts"), list) else [])
            if isinstance(item, str) and item.strip()
        ]
        return collection_payload

    def _build_collection_dashboard_item(
        self,
        collection_payload: Dict[str, Any],
        audit: Dict[str, Any],
    ) -> Dict[str, Any]:
        success_ratio_summary = (
            audit.get("success_ratio_summary") if isinstance(audit.get("success_ratio_summary"), dict) else {}
        )
        return {
            "collection_id": str(collection_payload.get("collection_id") or ""),
            "name": str(collection_payload.get("name") or ""),
            "health_status": str(audit.get("health_status") or "green"),
            "alerts": [
                str(item)
                for item in (audit.get("alerts") if isinstance(audit.get("alerts"), list) else [])
                if isinstance(item, str) and item.strip()
            ],
            "item_count": int(collection_payload.get("item_count") or 0),
            "total_executions": int(audit.get("total_executions") or 0),
            "total_retries": int(audit.get("total_retries") or 0),
            "pending_review_count": int(audit.get("pending_review_count") or 0),
            "best_request_id": self._safe_optional_text(audit.get("best_request_id")),
            "success_ratio": float(success_ratio_summary.get("ratio") or 0.0),
            "updated_at": str(collection_payload.get("updated_at") or ""),
        }

    def _index_webhook_stats_by_id(self, stats: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        indexed: Dict[str, Dict[str, Any]] = {}
        for item in stats:
            if not isinstance(item, dict):
                continue
            webhook_id = str(item.get("webhook_id") or "").strip()
            if not webhook_id:
                continue
            indexed[webhook_id] = deepcopy(item)
        return indexed

    def _count_recent_errors_by_webhook(self, recent_errors: List[Dict[str, Any]]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for item in recent_errors:
            if not isinstance(item, dict):
                continue
            webhook_id = str(item.get("webhook_id") or "").strip()
            if not webhook_id:
                continue
            counts[webhook_id] = int(counts.get(webhook_id) or 0) + 1
        return counts

    def _is_webhook_delivery_exhausted(self, delivery: Dict[str, Any]) -> bool:
        if not isinstance(delivery, dict):
            return False
        if self._safe_optional_text(delivery.get("final_failure_at")) is not None:
            return True

        status = str(delivery.get("delivery_status") or "").strip().lower()
        if status != "failed":
            return False

        attempt_count = int(delivery.get("attempt_count") or 0)
        max_attempts = max(1, int(delivery.get("max_attempts") or WEBHOOK_DELIVERY_DEFAULT_MAX_ATTEMPTS))
        return attempt_count >= max_attempts

    def _build_webhook_health_summary(
        self,
        webhook: Dict[str, Any],
        stats: Optional[Dict[str, Any]] = None,
        recent_error_count: int = 0,
    ) -> Dict[str, Any]:
        stats_payload = stats if isinstance(stats, dict) else {}

        total_deliveries = int(stats_payload.get("total_deliveries") or 0)
        sent_deliveries = int(stats_payload.get("sent_deliveries") or 0)
        failed_deliveries = int(stats_payload.get("failed_deliveries") or 0)
        pending_deliveries = int(stats_payload.get("pending_deliveries") or 0)
        exhausted_deliveries = int(stats_payload.get("exhausted_deliveries") or 0)
        total_retries = int(stats_payload.get("total_retries") or 0)
        last_delivery_at = self._safe_optional_text(stats_payload.get("last_delivery_at"))

        is_enabled = bool(webhook.get("is_enabled", True))
        failure_ratio = (failed_deliveries / total_deliveries) if total_deliveries > 0 else 0.0

        signals: List[Dict[str, Any]] = []
        if failed_deliveries >= WEBHOOK_HEALTH_RED_FAILED_THRESHOLD:
            signals.append(
                {
                    "code": "FAILED_DELIVERIES_HIGH",
                    "severity": "critical",
                    "message": (
                        "Failed deliveries are above threshold: "
                        f"failed={failed_deliveries}, threshold={WEBHOOK_HEALTH_RED_FAILED_THRESHOLD}."
                    ),
                }
            )

        if exhausted_deliveries >= WEBHOOK_HEALTH_RED_EXHAUSTED_THRESHOLD:
            signals.append(
                {
                    "code": "EXHAUSTED_DELIVERIES_HIGH",
                    "severity": "critical",
                    "message": (
                        "Deliveries with retries exhausted are above threshold: "
                        f"exhausted={exhausted_deliveries}, threshold={WEBHOOK_HEALTH_RED_EXHAUSTED_THRESHOLD}."
                    ),
                }
            )

        if (
            total_deliveries >= WEBHOOK_HEALTH_MIN_DELIVERIES_FOR_RATIO
            and failure_ratio >= WEBHOOK_HEALTH_RED_FAILURE_RATIO_THRESHOLD
        ):
            signals.append(
                {
                    "code": "FAILURE_RATIO_CRITICAL",
                    "severity": "critical",
                    "message": f"Failure ratio is critical: ratio={failure_ratio:.2%}.",
                }
            )
        elif (
            total_deliveries >= WEBHOOK_HEALTH_MIN_DELIVERIES_FOR_RATIO
            and failure_ratio >= WEBHOOK_HEALTH_YELLOW_FAILURE_RATIO_THRESHOLD
        ):
            signals.append(
                {
                    "code": "FAILURE_RATIO_WARNING",
                    "severity": "warning",
                    "message": f"Failure ratio is elevated: ratio={failure_ratio:.2%}.",
                }
            )

        if int(recent_error_count) >= WEBHOOK_HEALTH_YELLOW_RECENT_ERRORS_THRESHOLD:
            signals.append(
                {
                    "code": "RECENT_ERRORS_REPEATED",
                    "severity": "warning",
                    "message": (
                        "Repeated recent errors detected: "
                        f"recent_errors={int(recent_error_count)}, "
                        f"threshold={WEBHOOK_HEALTH_YELLOW_RECENT_ERRORS_THRESHOLD}."
                    ),
                }
            )

        if total_retries >= WEBHOOK_HEALTH_YELLOW_RETRY_THRESHOLD:
            signals.append(
                {
                    "code": "RETRY_VOLUME_HIGH",
                    "severity": "warning",
                    "message": (
                        "Retry volume is high: "
                        f"total_retries={total_retries}, threshold={WEBHOOK_HEALTH_YELLOW_RETRY_THRESHOLD}."
                    ),
                }
            )

        if not is_enabled and (pending_deliveries > 0 or failed_deliveries > 0):
            signals.append(
                {
                    "code": "WEBHOOK_DISABLED_WITH_BACKLOG",
                    "severity": "warning",
                    "message": (
                        "Webhook is disabled while there are pending/failed deliveries: "
                        f"pending={pending_deliveries}, failed={failed_deliveries}."
                    ),
                }
            )

        critical_count = sum(
            1
            for signal in signals
            if isinstance(signal, dict) and str(signal.get("severity") or "").strip().lower() == "critical"
        )
        warning_count = sum(
            1
            for signal in signals
            if isinstance(signal, dict) and str(signal.get("severity") or "").strip().lower() == "warning"
        )

        if critical_count > 0:
            health_status = "red"
        elif warning_count > 0:
            health_status = "yellow"
        else:
            health_status = "green"

        alerts = [
            str(signal.get("message") or "")
            for signal in signals
            if isinstance(signal, dict)
            and str(signal.get("severity") or "").strip().lower() in {"warning", "critical"}
            and str(signal.get("message") or "").strip()
        ]

        return {
            "health_status": health_status,
            "alerts": alerts,
            "signals": signals,
            "total_deliveries": total_deliveries,
            "sent_deliveries": sent_deliveries,
            "failed_deliveries": failed_deliveries,
            "pending_deliveries": pending_deliveries,
            "exhausted_deliveries": exhausted_deliveries,
            "total_retries": total_retries,
            "failure_ratio": round(failure_ratio, 6),
            "last_delivery_at": last_delivery_at,
        }

    def _build_webhook_dashboard_item(
        self,
        stats: Dict[str, Any],
        recent_error_count: int = 0,
    ) -> Dict[str, Any]:
        webhook_stub = {
            "is_enabled": bool(stats.get("is_enabled", True)),
        }
        health_summary = self._build_webhook_health_summary(
            webhook=webhook_stub,
            stats=stats,
            recent_error_count=recent_error_count,
        )

        return {
            "webhook_id": str(stats.get("webhook_id") or ""),
            "name": str(stats.get("name") or ""),
            "is_enabled": bool(stats.get("is_enabled", True)),
            "health_status": str(health_summary.get("health_status") or "green"),
            "alerts": [
                str(item)
                for item in (health_summary.get("alerts") if isinstance(health_summary.get("alerts"), list) else [])
                if isinstance(item, str) and item.strip()
            ],
            "total_deliveries": int(health_summary.get("total_deliveries") or 0),
            "sent_deliveries": int(health_summary.get("sent_deliveries") or 0),
            "failed_deliveries": int(health_summary.get("failed_deliveries") or 0),
            "pending_deliveries": int(health_summary.get("pending_deliveries") or 0),
            "exhausted_deliveries": int(health_summary.get("exhausted_deliveries") or 0),
            "total_retries": int(health_summary.get("total_retries") or 0),
            "failure_ratio": float(health_summary.get("failure_ratio") or 0.0),
            "last_delivery_at": self._safe_optional_text(health_summary.get("last_delivery_at")),
        }

    def _build_webhook_dashboard_error_item(self, error_item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "delivery_id": str(error_item.get("delivery_id") or ""),
            "webhook_id": str(error_item.get("webhook_id") or ""),
            "webhook_name": str(error_item.get("webhook_name") or ""),
            "notification_id": str(error_item.get("notification_id") or ""),
            "collection_id": str(error_item.get("collection_id") or ""),
            "error_message": str(error_item.get("error_message") or ""),
            "attempt_count": int(error_item.get("attempt_count") or 0),
            "max_attempts": max(1, int(error_item.get("max_attempts") or WEBHOOK_DELIVERY_DEFAULT_MAX_ATTEMPTS)),
            "is_test": bool(error_item.get("is_test", False)),
            "auth_mode": self._normalize_webhook_auth_mode(error_item.get("auth_mode")),
            "payload_template_mode": self._normalize_webhook_payload_template_mode(error_item.get("template_mode")),
            "created_at": str(error_item.get("created_at") or ""),
            "last_attempt_at": self._safe_optional_text(error_item.get("last_attempt_at")),
        }

    def _build_webhook_recent_signals(
        self,
        health_signals: List[Dict[str, Any]],
        recent_deliveries: List[Dict[str, Any]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        normalized_limit = max(1, min(int(limit), 50))
        signals: List[Dict[str, Any]] = []

        for signal in health_signals:
            if not isinstance(signal, dict):
                continue
            message = str(signal.get("message") or "").strip()
            if not message:
                continue
            signals.append(
                {
                    "code": str(signal.get("code") or "WEBHOOK_HEALTH_SIGNAL"),
                    "severity": str(signal.get("severity") or "warning"),
                    "message": message,
                    "observed_at": None,
                }
            )

        for delivery in recent_deliveries:
            if not isinstance(delivery, dict):
                continue
            status = str(delivery.get("delivery_status") or "").strip().lower()
            if status != "failed":
                continue

            delivery_id = str(delivery.get("delivery_id") or "")
            attempt_count = int(delivery.get("attempt_count") or 0)
            max_attempts = max(1, int(delivery.get("max_attempts") or WEBHOOK_DELIVERY_DEFAULT_MAX_ATTEMPTS))
            error_text = self._safe_optional_text(delivery.get("error_message")) or "No error message"
            observed_at = self._safe_optional_text(delivery.get("last_attempt_at")) or self._safe_optional_text(
                delivery.get("created_at")
            )
            exhausted = self._is_webhook_delivery_exhausted(delivery)
            severity = "critical" if exhausted else "warning"

            signals.append(
                {
                    "code": "RECENT_DELIVERY_FAILURE",
                    "severity": severity,
                    "message": (
                        f"Delivery {delivery_id} failed "
                        f"(attempt {attempt_count}/{max_attempts}): {error_text}"
                    ),
                    "observed_at": observed_at,
                }
            )

        signals.sort(
            key=lambda item: (
                self._health_rank("red" if str(item.get("severity") or "").lower() == "critical" else "yellow"),
                self._parse_iso_datetime(item.get("observed_at")) or datetime.fromtimestamp(0, tz=timezone.utc),
            ),
            reverse=True,
        )
        return signals[:normalized_limit]

    def _sort_collection_dashboard_items(
        self,
        items: List[Dict[str, Any]],
        key: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        sorted_items = sorted(
            [deepcopy(item) for item in items],
            key=lambda item: (
                float(item.get(key) or 0.0),
                self._health_rank(str(item.get("health_status") or "green")),
                str(item.get("updated_at") or ""),
                str(item.get("collection_id") or ""),
            ),
            reverse=True,
        )
        normalized_limit = max(1, min(int(limit), 20))
        return sorted_items[:normalized_limit]

    def _health_rank(self, health_status: str) -> int:
        normalized = (health_status or "").strip().lower()
        if normalized == "red":
            return 3
        if normalized == "yellow":
            return 2
        return 1

    def _build_notification_public_response(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "notification_id": str(notification.get("notification_id") or ""),
            "collection_id": str(notification.get("collection_id") or ""),
            "type": str(notification.get("type") or ""),
            "severity": str(notification.get("severity") or "info"),
            "message": str(notification.get("message") or ""),
            "created_at": str(notification.get("created_at") or ""),
            "is_read": bool(notification.get("is_read", False)),
        }

    def _build_notification_preferences_public_response(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        normalized_enabled_types = self._normalize_notification_enabled_types(preferences.get("enabled_types"))
        return {
            "notifications_enabled": bool(preferences.get("notifications_enabled", True)),
            "min_severity": self._normalize_notification_severity(preferences.get("min_severity")),
            "enabled_types": normalized_enabled_types,
            "show_only_unread_by_default": bool(preferences.get("show_only_unread_by_default", False)),
            "updated_at": str(preferences.get("updated_at") or ""),
        }

    def _ensure_webhook_test_collection(self) -> Dict[str, Any]:
        existing = self.runs_repository.get_collection(WEBHOOK_TEST_COLLECTION_ID)
        if existing is not None:
            return existing

        now = self._now_iso()
        return self.runs_repository.create_collection(
            {
                "collection_id": WEBHOOK_TEST_COLLECTION_ID,
                "name": "[SYSTEM] Webhook Test Events",
                "description": "System collection used for webhook manual test events.",
                "editorial_note": "",
                "color": "#64748b",
                "is_archived": True,
                "best_request_id": None,
                "created_at": now,
                "updated_at": now,
            }
        )

    def _build_webhook_public_response(self, webhook: Dict[str, Any]) -> Dict[str, Any]:
        custom_headers = self._normalize_webhook_custom_headers(webhook.get("custom_headers"))
        auth_mode = self._normalize_webhook_auth_mode(webhook.get("auth_mode"))
        secret_token = self._normalize_webhook_secret_token(webhook.get("secret_token"))
        template_mode = self._normalize_webhook_payload_template_mode(webhook.get("payload_template_mode"))
        payload_template = self._normalize_webhook_payload_template(webhook.get("payload_template"))
        normalized_health_status = str(webhook.get("health_status") or "green").strip().lower()
        if normalized_health_status not in {"green", "yellow", "red"}:
            normalized_health_status = "green"
        return {
            "webhook_id": str(webhook.get("webhook_id") or ""),
            "name": str(webhook.get("name") or ""),
            "url": str(webhook.get("url") or ""),
            "is_enabled": bool(webhook.get("is_enabled", True)),
            "auth_mode": auth_mode,
            "has_secret_token": bool(secret_token),
            "min_severity": self._normalize_notification_severity(webhook.get("min_severity")),
            "enabled_types": self._normalize_notification_enabled_types(webhook.get("enabled_types")),
            "custom_headers": custom_headers,
            "payload_template_mode": template_mode,
            "payload_template": payload_template,
            "health_status": normalized_health_status,
            "alerts": [
                str(item)
                for item in (webhook.get("alerts") if isinstance(webhook.get("alerts"), list) else [])
                if isinstance(item, str) and item.strip()
            ],
            "created_at": str(webhook.get("created_at") or ""),
            "updated_at": str(webhook.get("updated_at") or ""),
        }

    def _build_webhook_delivery_public_response(self, delivery: Dict[str, Any]) -> Dict[str, Any]:
        payload = delivery.get("payload") if isinstance(delivery.get("payload"), dict) else {}
        request_headers = self._normalize_webhook_custom_headers(delivery.get("request_headers"))
        return {
            "delivery_id": str(delivery.get("delivery_id") or ""),
            "webhook_id": str(delivery.get("webhook_id") or ""),
            "notification_id": str(delivery.get("notification_id") or ""),
            "collection_id": str(delivery.get("collection_id") or ""),
            "routing_rule_id": str(delivery.get("routing_rule_id")) if delivery.get("routing_rule_id") is not None else None,
            "routing_rule_name": str(delivery.get("routing_rule_name"))
            if delivery.get("routing_rule_name") is not None
            else None,
            "payload": payload,
            "delivery_status": str(delivery.get("delivery_status") or "pending"),
            "attempt_count": max(0, int(delivery.get("attempt_count") or 0)),
            "max_attempts": max(1, int(delivery.get("max_attempts") or WEBHOOK_DELIVERY_DEFAULT_MAX_ATTEMPTS)),
            "last_attempt_at": str(delivery.get("last_attempt_at")) if delivery.get("last_attempt_at") is not None else None,
            "next_retry_at": str(delivery.get("next_retry_at")) if delivery.get("next_retry_at") is not None else None,
            "final_failure_at": str(delivery.get("final_failure_at"))
            if delivery.get("final_failure_at") is not None
            else None,
            "is_test": bool(delivery.get("is_test", False)),
            "template_mode": self._normalize_webhook_payload_template_mode(delivery.get("template_mode")),
            "auth_mode": self._normalize_webhook_auth_mode(delivery.get("auth_mode")),
            "request_headers": request_headers,
            "signature_timestamp": str(delivery.get("signature_timestamp"))
            if delivery.get("signature_timestamp") is not None
            else None,
            "response_status_code": int(delivery.get("response_status_code"))
            if delivery.get("response_status_code") is not None
            else None,
            "response_body": str(delivery.get("response_body")) if delivery.get("response_body") is not None else None,
            "error_message": str(delivery.get("error_message")) if delivery.get("error_message") is not None else None,
            "created_at": str(delivery.get("created_at") or ""),
            "delivered_at": str(delivery.get("delivered_at")) if delivery.get("delivered_at") is not None else None,
        }

    def _normalize_notification_channel_type(self, value: Any, strict: bool = False) -> Optional[str]:
        if value is None:
            if strict:
                raise ValueError("channel_type is required")
            return None

        normalized = str(value or "").strip().lower()
        if normalized in NOTIFICATION_CHANNEL_TYPE_VALUES:
            return normalized
        if strict:
            raise ValueError("channel_type must be one of webhook, slack, telegram")
        return None

    def _normalize_notification_channel_config(
        self,
        channel_type: str,
        config: Any,
        strict: bool = False,
    ) -> Dict[str, Any]:
        normalized_channel_type = self._normalize_notification_channel_type(channel_type, strict=True) or "webhook"
        raw_config = config if isinstance(config, dict) else {}

        if normalized_channel_type == "webhook":
            url_value = str(raw_config.get("url") or "").strip()
            if url_value:
                parsed = urlparse(url_value)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    raise ValueError("config.url must be a valid http/https URL")
            elif strict:
                raise ValueError("config.url is required for webhook channels")
            return {"url": url_value}

        if normalized_channel_type == "slack":
            webhook_url = str(raw_config.get("webhook_url") or "").strip()
            if webhook_url:
                parsed = urlparse(webhook_url)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                    raise ValueError("config.webhook_url must be a valid http/https URL")
            elif strict:
                raise ValueError("notification channel destination url is required")
            return {"webhook_url": webhook_url}

        bot_token = str(raw_config.get("bot_token") or "").strip()
        chat_id = str(raw_config.get("chat_id") or "").strip()
        if strict and not bot_token:
            raise ValueError("config.bot_token is required for telegram channels")
        if strict and not chat_id:
            raise ValueError("config.chat_id is required for telegram channels")
        return {
            "bot_token": bot_token,
            "chat_id": chat_id,
        }

    def _sanitize_notification_channel_config_for_public(self, channel_type: str, config: Dict[str, Any]) -> Dict[str, Any]:
        normalized_channel_type = self._normalize_notification_channel_type(channel_type, strict=True) or "webhook"
        normalized_config = config if isinstance(config, dict) else {}

        if normalized_channel_type == "webhook":
            return {
                "url": str(normalized_config.get("url") or "").strip(),
            }

        if normalized_channel_type == "slack":
            webhook_url = str(normalized_config.get("webhook_url") or "").strip()
            parsed = urlparse(webhook_url) if webhook_url else None
            return {
                "has_webhook_url": bool(webhook_url),
                "webhook_url_host": parsed.netloc if parsed is not None else None,
            }

        return {
            "chat_id": str(normalized_config.get("chat_id") or "").strip(),
            "has_bot_token": bool(str(normalized_config.get("bot_token") or "").strip()),
        }

    def _build_notification_channel_public_response(self, channel: Dict[str, Any]) -> Dict[str, Any]:
        normalized_channel_type = self._normalize_notification_channel_type(channel.get("channel_type"), strict=True) or "webhook"
        config = self._normalize_notification_channel_config(
            channel_type=normalized_channel_type,
            config=channel.get("config"),
            strict=False,
        )
        return {
            "channel_id": str(channel.get("channel_id") or ""),
            "channel_type": normalized_channel_type,
            "name": str(channel.get("name") or ""),
            "is_enabled": bool(channel.get("is_enabled", True)),
            "config": self._sanitize_notification_channel_config_for_public(normalized_channel_type, config),
            "min_severity": self._normalize_notification_severity(channel.get("min_severity")),
            "enabled_types": self._normalize_notification_enabled_types(channel.get("enabled_types")),
            "created_at": str(channel.get("created_at") or ""),
            "updated_at": str(channel.get("updated_at") or ""),
        }

    def _build_notification_channel_delivery_public_response(self, delivery: Dict[str, Any]) -> Dict[str, Any]:
        payload = delivery.get("payload") if isinstance(delivery.get("payload"), dict) else {}
        return {
            "delivery_id": str(delivery.get("delivery_id") or ""),
            "channel_id": str(delivery.get("channel_id") or ""),
            "channel_type": self._normalize_notification_channel_type(delivery.get("channel_type"), strict=True) or "webhook",
            "notification_id": str(delivery.get("notification_id") or ""),
            "collection_id": str(delivery.get("collection_id") or ""),
            "routing_rule_id": str(delivery.get("routing_rule_id")) if delivery.get("routing_rule_id") is not None else None,
            "routing_rule_name": str(delivery.get("routing_rule_name"))
            if delivery.get("routing_rule_name") is not None
            else None,
            "payload": payload,
            "message_text": str(delivery.get("message_text") or ""),
            "delivery_status": str(delivery.get("delivery_status") or "pending"),
            "attempt_count": max(0, int(delivery.get("attempt_count") or 0)),
            "max_attempts": max(1, int(delivery.get("max_attempts") or NOTIFICATION_CHANNEL_DELIVERY_DEFAULT_MAX_ATTEMPTS)),
            "last_attempt_at": str(delivery.get("last_attempt_at")) if delivery.get("last_attempt_at") is not None else None,
            "next_retry_at": str(delivery.get("next_retry_at")) if delivery.get("next_retry_at") is not None else None,
            "final_failure_at": str(delivery.get("final_failure_at")) if delivery.get("final_failure_at") is not None else None,
            "is_test": bool(delivery.get("is_test", False)),
            "response_status_code": int(delivery.get("response_status_code"))
            if delivery.get("response_status_code") is not None
            else None,
            "response_body": str(delivery.get("response_body")) if delivery.get("response_body") is not None else None,
            "error_message": str(delivery.get("error_message")) if delivery.get("error_message") is not None else None,
            "created_at": str(delivery.get("created_at") or ""),
            "delivered_at": str(delivery.get("delivered_at")) if delivery.get("delivered_at") is not None else None,
        }

    def _normalize_alert_routing_target_kind(self, value: Any, strict: bool = False) -> str:
        normalized = str(value or "notification_channel").strip().lower()
        if normalized in ALERT_ROUTING_TARGET_KIND_VALUES:
            return normalized
        if strict:
            raise ValueError("target_channel_kind must be one of notification_channel, webhook")
        return "notification_channel"

    def _normalize_alert_routing_match_types(self, value: Any) -> List[str]:
        if value is None:
            return []
        if not isinstance(value, list):
            raise ValueError("match_types must be an array of strings")

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed or trimmed in seen:
                continue
            seen.add(trimmed)
            normalized.append(trimmed)

        return normalized

    def _normalize_collection_health_status(self, value: Any, strict: bool = False) -> Optional[str]:
        if value is None:
            return None

        normalized = str(value or "").strip().lower()
        if not normalized:
            return None
        if normalized in COLLECTION_HEALTH_STATUS_VALUES:
            return normalized
        if strict:
            raise ValueError("match_health_status must be one of green, yellow, red")
        return None

    def _resolve_alert_routing_target(
        self,
        target_channel_id: str,
        target_channel_kind: Optional[str] = None,
        strict: bool = False,
    ) -> Optional[Dict[str, Any]]:
        normalized_target_channel_id = str(target_channel_id or "").strip()
        if not normalized_target_channel_id:
            if strict:
                raise ValueError("target_channel_id is required")
            return None

        if target_channel_kind is None:
            channel = self.runs_repository.get_notification_channel(normalized_target_channel_id)
            if isinstance(channel, dict):
                return {
                    "target_channel_id": normalized_target_channel_id,
                    "target_channel_kind": "notification_channel",
                    "target_name": str(channel.get("name") or ""),
                    "target_channel_type": self._normalize_notification_channel_type(channel.get("channel_type")),
                    "target_enabled": bool(channel.get("is_enabled", True)),
                    "target": channel,
                }

            webhook = self.runs_repository.get_webhook(normalized_target_channel_id)
            if isinstance(webhook, dict):
                return {
                    "target_channel_id": normalized_target_channel_id,
                    "target_channel_kind": "webhook",
                    "target_name": str(webhook.get("name") or ""),
                    "target_channel_type": "webhook",
                    "target_enabled": bool(webhook.get("is_enabled", True)),
                    "target": webhook,
                }

            if strict:
                raise ValueError(f"target_channel_id not found: {normalized_target_channel_id}")
            return {
                "target_channel_id": normalized_target_channel_id,
                "target_channel_kind": "notification_channel",
                "target_name": None,
                "target_channel_type": None,
                "target_enabled": False,
                "target": None,
            }

        normalized_target_kind = self._normalize_alert_routing_target_kind(target_channel_kind, strict=strict)
        if normalized_target_kind == "webhook":
            webhook = self.runs_repository.get_webhook(normalized_target_channel_id)
            if webhook is None:
                if strict:
                    raise ValueError(f"webhook target not found: {normalized_target_channel_id}")
                return {
                    "target_channel_id": normalized_target_channel_id,
                    "target_channel_kind": normalized_target_kind,
                    "target_name": None,
                    "target_channel_type": "webhook",
                    "target_enabled": False,
                    "target": None,
                }

            return {
                "target_channel_id": normalized_target_channel_id,
                "target_channel_kind": normalized_target_kind,
                "target_name": str(webhook.get("name") or ""),
                "target_channel_type": "webhook",
                "target_enabled": bool(webhook.get("is_enabled", True)),
                "target": webhook,
            }

        channel = self.runs_repository.get_notification_channel(normalized_target_channel_id)
        if channel is None:
            if strict:
                raise ValueError(f"notification channel target not found: {normalized_target_channel_id}")
            return {
                "target_channel_id": normalized_target_channel_id,
                "target_channel_kind": normalized_target_kind,
                "target_name": None,
                "target_channel_type": None,
                "target_enabled": False,
                "target": None,
            }

        return {
            "target_channel_id": normalized_target_channel_id,
            "target_channel_kind": normalized_target_kind,
            "target_name": str(channel.get("name") or ""),
            "target_channel_type": self._normalize_notification_channel_type(channel.get("channel_type")),
            "target_enabled": bool(channel.get("is_enabled", True)),
            "target": channel,
        }

    def _build_alert_routing_rule_public_response(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        normalized_target_channel_id = str(rule.get("target_channel_id") or "").strip()
        resolved_target = self._resolve_alert_routing_target(
            target_channel_id=normalized_target_channel_id,
            target_channel_kind=rule.get("target_channel_kind"),
            strict=False,
        )

        target_channel_kind = self._normalize_alert_routing_target_kind(
            resolved_target.get("target_channel_kind") if isinstance(resolved_target, dict) else rule.get("target_channel_kind")
        )
        target_name = self._safe_optional_text(
            resolved_target.get("target_name") if isinstance(resolved_target, dict) else None
        )
        target_channel_type = self._safe_optional_text(
            resolved_target.get("target_channel_type") if isinstance(resolved_target, dict) else None
        )
        target_exists = bool(isinstance(resolved_target, dict) and isinstance(resolved_target.get("target"), dict))

        return {
            "rule_id": str(rule.get("rule_id") or ""),
            "name": str(rule.get("name") or ""),
            "is_enabled": bool(rule.get("is_enabled", True)),
            "target_channel_id": normalized_target_channel_id,
            "target_channel_kind": target_channel_kind,
            "target_name": target_name,
            "target_channel_type": target_channel_type,
            "target_exists": target_exists,
            "match_types": self._normalize_alert_routing_match_types(rule.get("match_types")),
            "min_severity": self._normalize_notification_severity(rule.get("min_severity")),
            "match_collection_id": self._safe_optional_text(rule.get("match_collection_id")),
            "match_health_status": self._normalize_collection_health_status(rule.get("match_health_status")),
            "created_at": str(rule.get("created_at") or ""),
            "updated_at": str(rule.get("updated_at") or ""),
        }

    def _resolve_alert_routing_destinations_for_notification(
        self,
        notification: Dict[str, Any],
        health_status: Optional[str],
        routing_rules: List[Dict[str, Any]],
        webhooks: List[Dict[str, Any]],
        channels: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        notification_type = str(notification.get("type") or "").strip()
        notification_severity = self._normalize_notification_severity(notification.get("severity"))
        collection_id = str(notification.get("collection_id") or "").strip()
        normalized_health_status = self._normalize_collection_health_status(health_status)

        webhooks_by_id: Dict[str, Dict[str, Any]] = {}
        for webhook in webhooks:
            if not isinstance(webhook, dict):
                continue
            webhook_id = str(webhook.get("webhook_id") or "").strip()
            if not webhook_id:
                continue
            webhooks_by_id[webhook_id] = webhook

        channels_by_id: Dict[str, Dict[str, Any]] = {}
        for channel in channels:
            if not isinstance(channel, dict):
                continue
            channel_id = str(channel.get("channel_id") or "").strip()
            if not channel_id:
                continue
            channels_by_id[channel_id] = channel

        resolved_routes: List[Dict[str, Any]] = []
        seen_destinations = set()

        for rule in routing_rules:
            if not isinstance(rule, dict):
                continue
            if not bool(rule.get("is_enabled", True)):
                continue

            rule_match_types = self._normalize_alert_routing_match_types(rule.get("match_types"))
            if rule_match_types and notification_type not in set(rule_match_types):
                continue

            rule_min_severity = self._normalize_notification_severity(rule.get("min_severity"))
            if self._notification_severity_rank(notification_severity) < self._notification_severity_rank(rule_min_severity):
                continue

            rule_collection_id = self._safe_optional_text(rule.get("match_collection_id"))
            if rule_collection_id and rule_collection_id != collection_id:
                continue

            rule_health_status = self._normalize_collection_health_status(rule.get("match_health_status"))
            if rule_health_status and rule_health_status != normalized_health_status:
                continue

            target_channel_id = str(rule.get("target_channel_id") or "").strip()
            if not target_channel_id:
                continue
            target_kind = self._normalize_alert_routing_target_kind(rule.get("target_channel_kind"))

            if target_kind == "webhook":
                target = webhooks_by_id.get(target_channel_id)
            else:
                target = channels_by_id.get(target_channel_id)
            if not isinstance(target, dict):
                continue
            if not bool(target.get("is_enabled", True)):
                continue

            destination_min_severity = self._normalize_notification_severity(target.get("min_severity"))
            if self._notification_severity_rank(notification_severity) < self._notification_severity_rank(destination_min_severity):
                continue

            destination_enabled_types = set(self._normalize_notification_enabled_types(target.get("enabled_types")))
            if destination_enabled_types and notification_type not in destination_enabled_types:
                continue

            dedupe_key = f"{target_kind}:{target_channel_id}"
            if dedupe_key in seen_destinations:
                continue
            seen_destinations.add(dedupe_key)

            resolved_routes.append(
                {
                    "target_kind": target_kind,
                    "target_channel_id": target_channel_id,
                    "target": target,
                    "rule_id": str(rule.get("rule_id") or ""),
                    "rule_name": str(rule.get("name") or ""),
                }
            )

        return resolved_routes

    def _build_notification_channel_payload(
        self,
        notification: Dict[str, Any],
        collection_name: Optional[str],
        health_status: Optional[str],
        event_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        notification_type = str(notification.get("type") or "NOTIFICATION")
        severity = self._normalize_notification_severity(notification.get("severity"))
        message = str(notification.get("message") or "")
        created_at = str(notification.get("created_at") or "")
        normalized_collection_id = str(notification.get("collection_id") or "")

        payload: Dict[str, Any] = {
            "title": f"[{severity.upper()}] {notification_type}",
            "summary": message or notification_type,
            "type": notification_type,
            "severity": severity,
            "message": message,
            "collection_id": normalized_collection_id,
            "created_at": created_at,
        }

        normalized_health_status = self._safe_optional_text(health_status)
        if normalized_health_status:
            payload["health_status"] = normalized_health_status

        normalized_collection_name = self._safe_optional_text(collection_name)
        if normalized_collection_name:
            payload["collection_name"] = normalized_collection_name

        normalized_event_type = self._safe_optional_text(event_type)
        if normalized_event_type:
            payload["event_type"] = normalized_event_type

        return payload

    def _build_notification_channel_message_text(self, channel_type: str, payload: Dict[str, Any]) -> str:
        normalized_channel_type = self._normalize_notification_channel_type(channel_type, strict=True) or "webhook"
        title = str(payload.get("title") or payload.get("summary") or "Notification")
        lines = [title]

        severity = self._safe_optional_text(payload.get("severity"))
        if severity:
            lines.append(f"Severity: {severity}")

        message = self._safe_optional_text(payload.get("message"))
        if message:
            lines.append(f"Message: {message}")

        collection_id = self._safe_optional_text(payload.get("collection_id"))
        if collection_id:
            lines.append(f"Collection: {collection_id}")

        health_status = self._safe_optional_text(payload.get("health_status"))
        if health_status:
            lines.append(f"Health: {health_status}")

        created_at = self._safe_optional_text(payload.get("created_at"))
        if created_at:
            lines.append(f"Created at: {created_at}")

        if normalized_channel_type == "slack":
            return "\n".join(lines)
        if normalized_channel_type == "telegram":
            return "\n".join(lines)
        return "\n".join(lines)

    def _mark_notification_channel_delivery_failed_without_request(
        self,
        delivery: Dict[str, Any],
        error_message: str,
    ) -> Dict[str, Any]:
        delivery_id = str(delivery.get("delivery_id") or "").strip()
        if not delivery_id:
            raise SequenceNotificationChannelDeliveryNotFoundError("Notification channel delivery not found")

        prior_attempt_count = int(delivery.get("attempt_count") or 0)
        max_attempts = max(
            1,
            int(delivery.get("max_attempts") or NOTIFICATION_CHANNEL_DELIVERY_DEFAULT_MAX_ATTEMPTS),
        )
        attempt_count = prior_attempt_count + 1
        attempt_at = self._now_iso()
        retry_timestamps = self._calculate_webhook_retry_timestamps(
            attempt_count=attempt_count,
            max_attempts=max_attempts,
            attempt_at=attempt_at,
        )

        updated = self.runs_repository.update_notification_channel_delivery(
            delivery_id,
            {
                "delivery_status": "failed",
                "attempt_count": attempt_count,
                "max_attempts": max_attempts,
                "last_attempt_at": attempt_at,
                "next_retry_at": retry_timestamps.get("next_retry_at"),
                "final_failure_at": retry_timestamps.get("final_failure_at"),
                "response_status_code": None,
                "response_body": None,
                "error_message": self._trim_delivery_text(error_message),
                "delivered_at": None,
            },
        )
        if updated is None:
            raise SequenceNotificationChannelDeliveryNotFoundError(
                f"Notification channel delivery not found: {delivery_id}"
            )
        return updated

    def _send_notification_channel_notification(
        self,
        channel: Dict[str, Any],
        notification: Dict[str, Any],
        collection_name: Optional[str],
        health_status: Optional[str],
        routing_rule_id: Optional[str] = None,
        routing_rule_name: Optional[str] = None,
    ) -> None:
        channel_id = str(channel.get("channel_id") or "").strip()
        if not channel_id:
            return

        try:
            normalized_channel_type = self._normalize_notification_channel_type(channel.get("channel_type"), strict=True)
            normalized_config = self._normalize_notification_channel_config(
                channel_type=normalized_channel_type or "webhook",
                config=channel.get("config"),
                strict=True,
            )
        except Exception:
            return

        payload = self._build_notification_channel_payload(
            notification=notification,
            collection_name=collection_name,
            health_status=health_status,
        )
        message_text = self._build_notification_channel_message_text(
            channel_type=normalized_channel_type or "webhook",
            payload=payload,
        )

        now = self._now_iso()
        max_attempts = NOTIFICATION_CHANNEL_DELIVERY_DEFAULT_MAX_ATTEMPTS
        delivery = self.runs_repository.create_notification_channel_delivery(
            {
                "delivery_id": str(uuid4()),
                "channel_id": channel_id,
                "channel_type": normalized_channel_type,
                "notification_id": str(notification.get("notification_id") or ""),
                "collection_id": str(notification.get("collection_id") or ""),
                "routing_rule_id": self._safe_optional_text(routing_rule_id),
                "routing_rule_name": self._safe_optional_text(routing_rule_name),
                "payload": payload,
                "message_text": message_text,
                "delivery_status": "pending",
                "attempt_count": 0,
                "max_attempts": max_attempts,
                "last_attempt_at": None,
                "next_retry_at": None,
                "final_failure_at": None,
                "is_test": False,
                "response_status_code": None,
                "response_body": None,
                "error_message": None,
                "created_at": now,
                "delivered_at": None,
            }
        )
        delivery_id = str(delivery.get("delivery_id") or "").strip()
        if not delivery_id:
            return

        normalized_channel = {
            **deepcopy(channel),
            "channel_type": normalized_channel_type,
            "config": normalized_config,
        }
        try:
            self._attempt_notification_channel_delivery(
                delivery_id=delivery_id,
                channel=normalized_channel,
                payload=payload,
                message_text=message_text,
                prior_attempt_count=0,
                max_attempts=max_attempts,
            )
        except Exception:
            return

    def _attempt_notification_channel_delivery(
        self,
        delivery_id: str,
        channel: Dict[str, Any],
        payload: Dict[str, Any],
        message_text: str,
        prior_attempt_count: int,
        max_attempts: int,
    ) -> Dict[str, Any]:
        channel_id = str(channel.get("channel_id") or "").strip()
        if not channel_id:
            raise ValueError("channel_id is required")

        normalized_channel_type = self._normalize_notification_channel_type(channel.get("channel_type"), strict=True) or "webhook"
        normalized_config = self._normalize_notification_channel_config(
            channel_type=normalized_channel_type,
            config=channel.get("config"),
            strict=True,
        )

        if normalized_channel_type == "webhook":
            target_url = str(normalized_config.get("url") or "").strip()
            request_body_payload = payload if isinstance(payload, dict) else {}
        elif normalized_channel_type == "slack":
            target_url = str(normalized_config.get("webhook_url") or "").strip()
            request_body_payload = {
                "text": str(message_text or "").strip(),
            }
        else:
            bot_token = str(normalized_config.get("bot_token") or "").strip()
            chat_id = str(normalized_config.get("chat_id") or "").strip()
            target_url = f"{TELEGRAM_API_BASE_URL}/bot{bot_token}/sendMessage"
            request_body_payload = {
                "chat_id": chat_id,
                "text": str(message_text or "").strip(),
            }

        normalized_target_url = target_url.strip()
        if not normalized_target_url:
            raise ValueError("notification channel destination url is required")

        body_text = self._canonicalize_webhook_payload(request_body_payload)
        request_payload = body_text.encode("utf-8")

        request_headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": "cine-ai-notification-channel/1.0",
        }
        request = Request(
            normalized_target_url,
            data=request_payload,
            method="POST",
            headers=request_headers,
        )

        attempt_count = max(0, int(prior_attempt_count)) + 1
        normalized_max_attempts = max(1, int(max_attempts))
        attempt_at = self._now_iso()

        delivery_status = "failed"
        response_status_code: Optional[int] = None
        response_body: Optional[str] = None
        error_message: Optional[str] = None

        try:
            with urlopen(request, timeout=WEBHOOK_REQUEST_TIMEOUT_SECONDS) as response:
                status = response.getcode()
                response_status_code = int(status) if status is not None else None
                body_bytes = response.read()
                if isinstance(body_bytes, bytes):
                    response_body = body_bytes.decode("utf-8", errors="replace")

            if response_status_code is not None and 200 <= response_status_code < 300:
                delivery_status = "sent"
            else:
                delivery_status = "failed"
                error_message = (
                    f"Unexpected response status: {response_status_code}"
                    if response_status_code is not None
                    else "Notification channel response had no status code"
                )
        except HTTPError as error:
            delivery_status = "failed"
            response_status_code = int(error.code) if error.code is not None else None
            response_body = self._extract_http_error_body(error)
            error_message = str(error.reason) if getattr(error, "reason", None) else str(error)
        except URLError as error:
            delivery_status = "failed"
            error_message = str(error.reason) if getattr(error, "reason", None) else str(error)
        except Exception as error:
            delivery_status = "failed"
            error_message = str(error)

        if delivery_status == "sent":
            delivered_at = attempt_at
            next_retry_at = None
            final_failure_at = None
        else:
            delivered_at = None
            retry_timestamps = self._calculate_webhook_retry_timestamps(
                attempt_count=attempt_count,
                max_attempts=normalized_max_attempts,
                attempt_at=attempt_at,
            )
            next_retry_at = retry_timestamps.get("next_retry_at")
            final_failure_at = retry_timestamps.get("final_failure_at")

        updated = self.runs_repository.update_notification_channel_delivery(
            delivery_id,
            {
                "delivery_status": delivery_status,
                "attempt_count": attempt_count,
                "max_attempts": normalized_max_attempts,
                "last_attempt_at": attempt_at,
                "next_retry_at": next_retry_at,
                "final_failure_at": final_failure_at,
                "response_status_code": response_status_code,
                "response_body": self._trim_delivery_text(response_body),
                "error_message": self._trim_delivery_text(error_message),
                "delivered_at": delivered_at,
            },
        )
        if updated is None:
            raise SequenceNotificationChannelDeliveryNotFoundError(
                f"Notification channel delivery not found: {delivery_id}"
            )

        return updated

    def _trim_delivery_text(self, value: Optional[str], max_chars: int = WEBHOOK_RESPONSE_BODY_MAX_CHARS) -> Optional[str]:
        if value is None:
            return None
        if len(value) <= max_chars:
            return value
        return value[:max_chars]

    def _extract_http_error_body(self, error: HTTPError) -> Optional[str]:
        try:
            body = error.read()
        except Exception:
            return None
        if not isinstance(body, bytes):
            return None
        return body.decode("utf-8", errors="replace")

    def _normalize_webhook_auth_mode(self, value: Any, strict: bool = False) -> str:
        normalized = str(value or "none").strip().lower()
        if normalized in WEBHOOK_AUTH_MODE_VALUES:
            return normalized
        if strict:
            raise ValueError("auth_mode must be one of none, bearer, hmac_sha256")
        return "none"

    def _normalize_webhook_secret_token(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        normalized = str(value).strip()
        return normalized or None

    def _normalize_webhook_custom_headers(self, value: Any) -> Dict[str, str]:
        if not isinstance(value, dict):
            return {}

        normalized: Dict[str, str] = {}
        for raw_key, raw_value in value.items():
            if not isinstance(raw_key, str):
                continue
            key = raw_key.strip()
            if not key:
                continue
            if isinstance(raw_value, str):
                val = raw_value.strip()
            else:
                val = str(raw_value).strip()
            if not val:
                continue
            normalized[key] = val

        return normalized

    def _normalize_webhook_payload_template_mode(self, value: Any, strict: bool = False) -> str:
        normalized = str(value or "default").strip().lower()
        if normalized in WEBHOOK_PAYLOAD_TEMPLATE_MODE_VALUES:
            return normalized
        if strict:
            raise ValueError("payload_template_mode must be one of default, compact, custom")
        return "default"

    def _normalize_webhook_payload_template(self, value: Any) -> Optional[Dict[str, Any]]:
        if not isinstance(value, dict):
            return None

        normalized: Dict[str, Any] = {}
        for raw_key, raw_value in value.items():
            if not isinstance(raw_key, str):
                continue
            key = raw_key.strip()
            if not key:
                continue
            normalized[key] = deepcopy(raw_value)

        return normalized or None

    def _build_webhook_default_payload(
        self,
        notification: Dict[str, Any],
        collection_name: Optional[str],
        health_status: Optional[str],
    ) -> Dict[str, Any]:
        payload = {
            "notification_id": str(notification.get("notification_id") or ""),
            "collection_id": str(notification.get("collection_id") or ""),
            "type": str(notification.get("type") or ""),
            "severity": self._normalize_notification_severity(notification.get("severity")),
            "message": str(notification.get("message") or ""),
            "created_at": str(notification.get("created_at") or ""),
        }

        normalized_collection_name = self._safe_optional_text(collection_name)
        if normalized_collection_name:
            payload["collection_name"] = normalized_collection_name

        normalized_health_status = self._safe_optional_text(health_status)
        if normalized_health_status:
            payload["health_status"] = normalized_health_status

        return payload

    def _build_webhook_test_payload(
        self,
        webhook: Dict[str, Any],
        created_at: str,
        event_type: Optional[str] = None,
        sample_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        normalized_event_type = self._safe_optional_text(event_type) or "test_event"
        payload: Dict[str, Any] = {
            "event_type": normalized_event_type,
            "webhook_id": str(webhook.get("webhook_id") or ""),
            "webhook_name": str(webhook.get("name") or ""),
            "created_at": str(created_at or ""),
            "message": "This is a test webhook event",
        }

        if isinstance(sample_data, dict):
            for raw_key, raw_value in sample_data.items():
                if not isinstance(raw_key, str):
                    continue
                key = raw_key.strip()
                if not key:
                    continue
                payload[key] = deepcopy(raw_value)

        payload["event_type"] = normalized_event_type
        payload["webhook_id"] = str(webhook.get("webhook_id") or "")
        payload["webhook_name"] = str(webhook.get("name") or "")
        payload["created_at"] = str(created_at or "")
        if self._safe_optional_text(payload.get("message")) is None:
            payload["message"] = "This is a test webhook event"

        return payload

    def _build_webhook_compact_payload(self, default_payload: Dict[str, Any]) -> Dict[str, Any]:
        compact: Dict[str, Any] = {}
        preferred_keys = [
            "event_type",
            "webhook_id",
            "webhook_name",
            "notification_id",
            "collection_id",
            "type",
            "severity",
            "message",
            "created_at",
            "health_status",
        ]
        for key in preferred_keys:
            if key not in default_payload:
                continue
            compact[key] = deepcopy(default_payload.get(key))

        if not compact:
            for key, value in default_payload.items():
                if key not in compact:
                    compact[key] = deepcopy(value)
        return compact

    def _build_webhook_template_context(
        self,
        default_payload: Dict[str, Any],
        webhook: Dict[str, Any],
    ) -> Dict[str, Any]:
        context: Dict[str, Any] = {}
        for key, value in default_payload.items():
            if not isinstance(key, str):
                continue
            normalized_key = key.strip()
            if not normalized_key:
                continue
            context[normalized_key] = deepcopy(value)

        context["webhook_id"] = str(webhook.get("webhook_id") or "")
        context["webhook_name"] = str(webhook.get("name") or "")
        context["webhook_url"] = str(webhook.get("url") or "")

        return context

    def _render_webhook_custom_template_value(self, template_value: Any, context: Dict[str, Any]) -> Any:
        if isinstance(template_value, dict):
            rendered: Dict[str, Any] = {}
            for raw_key, raw_value in template_value.items():
                if not isinstance(raw_key, str):
                    continue
                key = raw_key.strip()
                if not key:
                    continue
                rendered[key] = self._render_webhook_custom_template_value(raw_value, context)
            return rendered

        if isinstance(template_value, list):
            return [self._render_webhook_custom_template_value(item, context) for item in template_value]

        if isinstance(template_value, str):
            stripped = template_value.strip()
            exact_match = WEBHOOK_TEMPLATE_TOKEN_PATTERN.fullmatch(stripped)
            if exact_match:
                replacement = context.get(exact_match.group(1))
                return deepcopy(replacement if replacement is not None else "")

            def replace_token(match: re.Match[str]) -> str:
                replacement = context.get(match.group(1))
                if replacement is None:
                    return ""
                return str(replacement)

            return WEBHOOK_TEMPLATE_TOKEN_PATTERN.sub(replace_token, template_value)

        return deepcopy(template_value)

    def _apply_webhook_payload_template(
        self,
        webhook: Dict[str, Any],
        default_payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        template_mode = self._normalize_webhook_payload_template_mode(webhook.get("payload_template_mode"))
        payload_template = self._normalize_webhook_payload_template(webhook.get("payload_template"))

        if template_mode == "compact":
            return {
                "template_mode": "compact",
                "payload": self._build_webhook_compact_payload(default_payload),
            }

        if template_mode == "custom" and payload_template is not None:
            context = self._build_webhook_template_context(default_payload=default_payload, webhook=webhook)
            rendered_payload = self._render_webhook_custom_template_value(payload_template, context)
            if isinstance(rendered_payload, dict):
                return {
                    "template_mode": "custom",
                    "payload": rendered_payload,
                }

        return {
            "template_mode": "default",
            "payload": default_payload,
        }

    def _build_structured_webhook_diff(
        self,
        left: Dict[str, Any],
        right: Dict[str, Any],
    ) -> Dict[str, Any]:
        left_dict = left if isinstance(left, dict) else {}
        right_dict = right if isinstance(right, dict) else {}

        left_keys = {str(key) for key in left_dict.keys() if isinstance(key, str)}
        right_keys = {str(key) for key in right_dict.keys() if isinstance(key, str)}

        added: Dict[str, Any] = {}
        removed: Dict[str, Any] = {}
        changed: Dict[str, Dict[str, Any]] = {}
        unchanged_count = 0

        for key in sorted(right_keys - left_keys):
            added[key] = deepcopy(right_dict.get(key))

        for key in sorted(left_keys - right_keys):
            removed[key] = deepcopy(left_dict.get(key))

        for key in sorted(left_keys & right_keys):
            left_value = left_dict.get(key)
            right_value = right_dict.get(key)
            if left_value == right_value:
                unchanged_count += 1
                continue
            changed[key] = {
                "left": deepcopy(left_value),
                "right": deepcopy(right_value),
            }

        return {
            "added": added,
            "removed": removed,
            "changed": changed,
            "unchanged_count": unchanged_count,
        }

    def _build_webhook_payload_for_delivery(
        self,
        webhook: Dict[str, Any],
        notification: Dict[str, Any],
        collection_name: Optional[str],
        health_status: Optional[str],
    ) -> Dict[str, Any]:
        default_payload = self._build_webhook_default_payload(
            notification=notification,
            collection_name=collection_name,
            health_status=health_status,
        )
        return self._apply_webhook_payload_template(webhook=webhook, default_payload=default_payload)

    def _canonicalize_webhook_payload(self, payload: Dict[str, Any]) -> str:
        normalized_payload = payload if isinstance(payload, dict) else {}
        return json.dumps(
            normalized_payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )

    def _compute_hmac_sha256_signature(self, body_text: str, timestamp: str, secret_token: str) -> str:
        raw = f"{timestamp}.{body_text}".encode("utf-8")
        secret = secret_token.encode("utf-8")
        digest = hmac.new(secret, raw, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def _build_webhook_request_headers(
        self,
        webhook_id: str,
        body_text: str,
        auth_mode: str,
        secret_token: Optional[str],
        custom_headers: Optional[Dict[str, str]],
    ) -> Dict[str, Any]:
        normalized_auth_mode = self._normalize_webhook_auth_mode(auth_mode)
        normalized_secret_token = self._normalize_webhook_secret_token(secret_token)
        normalized_custom_headers = self._normalize_webhook_custom_headers(custom_headers)
        if normalized_auth_mode in {"bearer", "hmac_sha256"} and not normalized_secret_token:
            raise ValueError("secret_token is required when auth_mode is bearer or hmac_sha256")

        request_headers: Dict[str, str] = {
            "Content-Type": "application/json",
            "User-Agent": "cine-ai-sequence-webhook/1.0",
        }
        for key, value in normalized_custom_headers.items():
            request_headers[key] = value

        signature_timestamp: Optional[str] = None
        signature_preview: Optional[str] = None
        if normalized_auth_mode == "bearer":
            request_headers["Authorization"] = f"Bearer {normalized_secret_token}"
        elif normalized_auth_mode == "hmac_sha256":
            signature_timestamp = str(int(time.time()))
            signature_preview = self._compute_hmac_sha256_signature(
                body_text=body_text,
                timestamp=signature_timestamp,
                secret_token=normalized_secret_token or "",
            )
            request_headers["X-Webhook-Timestamp"] = signature_timestamp
            request_headers["X-Webhook-Signature"] = signature_preview
            if webhook_id:
                request_headers["X-Webhook-Id"] = webhook_id

        return {
            "request_headers": request_headers,
            "signature_timestamp": signature_timestamp,
            "signature_preview": signature_preview,
        }

    def _sanitize_webhook_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        sanitized: Dict[str, str] = {}
        for key, value in headers.items():
            normalized_key = str(key or "").strip()
            if not normalized_key:
                continue
            normalized_value = str(value or "").strip()
            if not normalized_value:
                continue

            lowered_key = normalized_key.lower()
            if lowered_key == "authorization":
                sanitized[normalized_key] = "Bearer ***"
                continue
            if any(token in lowered_key for token in ["secret", "token", "password", "api-key", "apikey"]):
                sanitized[normalized_key] = "***"
                continue

            sanitized[normalized_key] = normalized_value

        return sanitized

    def _parse_iso_datetime(self, value: Any) -> Optional[datetime]:
        if not isinstance(value, str) or not value.strip():
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return None

        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)

    def _iso_datetime_add_seconds(self, base_iso: str, seconds: int) -> str:
        parsed = self._parse_iso_datetime(base_iso)
        base = parsed if parsed is not None else datetime.now(timezone.utc)
        return (base + timedelta(seconds=max(0, int(seconds)))).isoformat()

    def _next_retry_seconds_for_attempt(self, attempt_count: int) -> int:
        index = max(0, int(attempt_count) - 1)
        if index < len(WEBHOOK_RETRY_BACKOFF_SECONDS):
            return WEBHOOK_RETRY_BACKOFF_SECONDS[index]
        return WEBHOOK_RETRY_BACKOFF_SECONDS[-1]

    def _calculate_webhook_retry_timestamps(
        self,
        attempt_count: int,
        max_attempts: int,
        attempt_at: str,
    ) -> Dict[str, Optional[str]]:
        normalized_attempt_count = max(0, int(attempt_count))
        normalized_max_attempts = max(1, int(max_attempts))

        if normalized_attempt_count >= normalized_max_attempts:
            return {
                "next_retry_at": None,
                "final_failure_at": attempt_at,
            }

        delay_seconds = self._next_retry_seconds_for_attempt(normalized_attempt_count)
        return {
            "next_retry_at": self._iso_datetime_add_seconds(attempt_at, delay_seconds),
            "final_failure_at": None,
        }

    def _mark_webhook_delivery_failed_without_request(
        self,
        delivery: Dict[str, Any],
        error_message: str,
    ) -> Dict[str, Any]:
        delivery_id = str(delivery.get("delivery_id") or "").strip()
        if not delivery_id:
            raise SequenceWebhookDeliveryNotFoundError("Webhook delivery not found")

        prior_attempt_count = int(delivery.get("attempt_count") or 0)
        max_attempts = max(1, int(delivery.get("max_attempts") or WEBHOOK_DELIVERY_DEFAULT_MAX_ATTEMPTS))
        attempt_count = prior_attempt_count + 1
        attempt_at = self._now_iso()
        retry_timestamps = self._calculate_webhook_retry_timestamps(
            attempt_count=attempt_count,
            max_attempts=max_attempts,
            attempt_at=attempt_at,
        )

        updated = self.runs_repository.update_webhook_delivery(
            delivery_id,
            {
                "delivery_status": "failed",
                "attempt_count": attempt_count,
                "max_attempts": max_attempts,
                "last_attempt_at": attempt_at,
                "next_retry_at": retry_timestamps.get("next_retry_at"),
                "final_failure_at": retry_timestamps.get("final_failure_at"),
                "response_status_code": None,
                "response_body": None,
                "error_message": self._trim_delivery_text(error_message),
                "delivered_at": None,
            },
        )
        if updated is None:
            raise SequenceWebhookDeliveryNotFoundError(f"Webhook delivery not found: {delivery_id}")

        return updated

    def _send_webhook_notification(
        self,
        webhook: Dict[str, Any],
        notification: Dict[str, Any],
        collection_name: Optional[str],
        health_status: Optional[str],
        routing_rule_id: Optional[str] = None,
        routing_rule_name: Optional[str] = None,
    ) -> None:
        webhook_id = str(webhook.get("webhook_id") or "").strip()
        if not webhook_id:
            return

        webhook_url = str(webhook.get("url") or "").strip()
        if not webhook_url:
            return
        auth_mode = self._normalize_webhook_auth_mode(webhook.get("auth_mode"))
        secret_token = self._normalize_webhook_secret_token(webhook.get("secret_token"))
        custom_headers = self._normalize_webhook_custom_headers(webhook.get("custom_headers"))

        rendered_payload = self._build_webhook_payload_for_delivery(
            webhook=webhook,
            notification=notification,
            collection_name=collection_name,
            health_status=health_status,
        )
        notification_payload = (
            rendered_payload.get("payload")
            if isinstance(rendered_payload.get("payload"), dict)
            else {}
        )
        template_mode = self._normalize_webhook_payload_template_mode(rendered_payload.get("template_mode"))

        now = self._now_iso()
        max_attempts = WEBHOOK_DELIVERY_DEFAULT_MAX_ATTEMPTS
        delivery = self.runs_repository.create_webhook_delivery(
            {
                "delivery_id": str(uuid4()),
                "webhook_id": webhook_id,
                "notification_id": str(notification.get("notification_id") or ""),
                "collection_id": str(notification.get("collection_id") or ""),
                "routing_rule_id": self._safe_optional_text(routing_rule_id),
                "routing_rule_name": self._safe_optional_text(routing_rule_name),
                "payload": notification_payload,
                "delivery_status": "pending",
                "attempt_count": 0,
                "max_attempts": max_attempts,
                "last_attempt_at": None,
                "next_retry_at": None,
                "final_failure_at": None,
                "is_test": False,
                "template_mode": template_mode,
                "auth_mode": auth_mode,
                "request_headers": {},
                "signature_timestamp": None,
                "response_status_code": None,
                "response_body": None,
                "error_message": None,
                "created_at": now,
                "delivered_at": None,
            }
        )
        delivery_id = str(delivery.get("delivery_id") or "").strip()
        if not delivery_id:
            return

        try:
            self._attempt_webhook_delivery(
                delivery_id=delivery_id,
                webhook_id=webhook_id,
                webhook_url=webhook_url,
                payload=notification_payload,
                prior_attempt_count=0,
                max_attempts=max_attempts,
                auth_mode=auth_mode,
                secret_token=secret_token,
                custom_headers=custom_headers,
            )
        except Exception:
            return

    def _attempt_webhook_delivery(
        self,
        delivery_id: str,
        webhook_id: str,
        webhook_url: str,
        payload: Dict[str, Any],
        prior_attempt_count: int,
        max_attempts: int,
        auth_mode: str = "none",
        secret_token: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        normalized_webhook_url = webhook_url.strip()
        if not normalized_webhook_url:
            raise ValueError("webhook url is required")

        normalized_auth_mode = self._normalize_webhook_auth_mode(auth_mode)

        normalized_payload = payload if isinstance(payload, dict) else {}
        attempt_count = max(0, int(prior_attempt_count)) + 1
        normalized_max_attempts = max(1, int(max_attempts))
        attempt_at = self._now_iso()

        body_text = self._canonicalize_webhook_payload(normalized_payload)
        request_payload = body_text.encode("utf-8")

        header_data = self._build_webhook_request_headers(
            webhook_id=webhook_id,
            body_text=body_text,
            auth_mode=normalized_auth_mode,
            secret_token=secret_token,
            custom_headers=custom_headers,
        )
        raw_headers = header_data.get("request_headers")
        request_headers = raw_headers if isinstance(raw_headers, dict) else {}
        signature_timestamp = self._safe_optional_text(header_data.get("signature_timestamp"))

        request = Request(
            normalized_webhook_url,
            data=request_payload,
            method="POST",
            headers=request_headers,
        )

        delivery_status = "failed"
        response_status_code: Optional[int] = None
        response_body: Optional[str] = None
        error_message: Optional[str] = None

        try:
            with urlopen(request, timeout=WEBHOOK_REQUEST_TIMEOUT_SECONDS) as response:
                status = response.getcode()
                response_status_code = int(status) if status is not None else None
                body_bytes = response.read()
                if isinstance(body_bytes, bytes):
                    response_body = body_bytes.decode("utf-8", errors="replace")

            if response_status_code is not None and 200 <= response_status_code < 300:
                delivery_status = "sent"
            else:
                delivery_status = "failed"
                error_message = (
                    f"Unexpected response status: {response_status_code}"
                    if response_status_code is not None
                    else "Webhook response had no status code"
                )
        except HTTPError as error:
            delivery_status = "failed"
            response_status_code = int(error.code) if error.code is not None else None
            response_body = self._extract_http_error_body(error)
            error_message = str(error.reason) if getattr(error, "reason", None) else str(error)
        except URLError as error:
            delivery_status = "failed"
            error_message = str(error.reason) if getattr(error, "reason", None) else str(error)
        except Exception as error:
            delivery_status = "failed"
            error_message = str(error)

        if delivery_status == "sent":
            delivered_at = attempt_at
            next_retry_at = None
            final_failure_at = None
        else:
            delivered_at = None
            retry_timestamps = self._calculate_webhook_retry_timestamps(
                attempt_count=attempt_count,
                max_attempts=normalized_max_attempts,
                attempt_at=attempt_at,
            )
            next_retry_at = retry_timestamps.get("next_retry_at")
            final_failure_at = retry_timestamps.get("final_failure_at")

        updated = self.runs_repository.update_webhook_delivery(
            delivery_id,
            {
                "delivery_status": delivery_status,
                "attempt_count": attempt_count,
                "max_attempts": normalized_max_attempts,
                "last_attempt_at": attempt_at,
                "next_retry_at": next_retry_at,
                "final_failure_at": final_failure_at,
                "auth_mode": normalized_auth_mode,
                "request_headers": self._sanitize_webhook_headers(request_headers),
                "signature_timestamp": signature_timestamp,
                "response_status_code": response_status_code,
                "response_body": self._trim_delivery_text(response_body),
                "error_message": self._trim_delivery_text(error_message),
                "delivered_at": delivered_at,
            },
        )
        if updated is None:
            raise SequenceWebhookDeliveryNotFoundError(f"Webhook delivery not found: {delivery_id}")

        return updated

    def _normalize_notification_enabled_types(self, value: Any) -> List[str]:
        if not isinstance(value, list):
            return deepcopy(DEFAULT_NOTIFICATION_ENABLED_TYPES)

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed:
                continue
            if trimmed in seen:
                continue
            seen.add(trimmed)
            normalized.append(trimmed)
        return normalized

    def _normalize_notification_severity(self, value: Any) -> str:
        normalized = str(value or "info").strip().lower()
        if normalized in NOTIFICATION_SEVERITY_VALUES:
            return normalized
        return "info"

    def _notification_severity_rank(self, severity: str) -> int:
        normalized = self._normalize_notification_severity(severity)
        if normalized == "critical":
            return 3
        if normalized == "warning":
            return 2
        return 1

    def _emit_collection_notifications(
        self,
        collection_id: str,
        health_status: str,
        best_request_id: Optional[str],
        total_executions: int,
        pending_review_count: int,
        failed_count: int,
        timeout_count: int,
        failed_red_threshold: int,
        timeout_red_threshold: int,
    ) -> None:
        state = self.runs_repository.get_collection_notification_state(collection_id) or {
            "last_health_status": "green",
            "missing_best_active": False,
            "pending_review_high_active": False,
            "operational_risk_active": False,
        }

        previous_health_status = str(state.get("last_health_status") or "green").strip().lower() or "green"
        previous_missing_best = bool(state.get("missing_best_active", False))
        previous_pending_high = bool(state.get("pending_review_high_active", False))
        previous_operational_risk = bool(state.get("operational_risk_active", False))

        normalized_health_status = (health_status or "").strip().lower() or "green"
        missing_best_active = total_executions > 0 and not self._safe_optional_text(best_request_id)
        pending_threshold = max(2, (total_executions + 1) // 2)
        pending_review_high_active = total_executions > 0 and pending_review_count >= pending_threshold
        operational_risk_active = (
            (failed_count >= failed_red_threshold and failed_count > 0)
            or (timeout_count >= timeout_red_threshold and timeout_count > 0)
        )

        now = self._now_iso()
        collection = self.runs_repository.get_collection(collection_id)
        collection_name = (
            self._safe_optional_text(collection.get("name"))
            if isinstance(collection, dict)
            else None
        )

        preferences = self._build_notification_preferences_public_response(
            self.runs_repository.get_notification_preferences()
        )
        notifications_enabled = bool(preferences.get("notifications_enabled", True))
        min_severity = self._normalize_notification_severity(preferences.get("min_severity"))
        enabled_types = set(self._normalize_notification_enabled_types(preferences.get("enabled_types")))
        webhooks = self.runs_repository.list_webhooks(limit=500, include_disabled=False)
        channels = self.runs_repository.list_notification_channels(limit=500, include_disabled=False)
        routing_rules = self.runs_repository.list_alert_routing_rules(limit=1000, include_disabled=False)

        def maybe_emit(notification_type: str, severity: str, message: str) -> None:
            if not notifications_enabled:
                return
            if notification_type not in enabled_types:
                return
            if self._notification_severity_rank(severity) < self._notification_severity_rank(min_severity):
                return

            notification = self.runs_repository.create_notification(
                {
                    "notification_id": str(uuid4()),
                    "collection_id": collection_id,
                    "type": notification_type,
                    "severity": severity,
                    "message": message,
                    "created_at": now,
                    "is_read": False,
                }
            )

            if routing_rules:
                resolved_routes = self._resolve_alert_routing_destinations_for_notification(
                    notification=notification,
                    health_status=normalized_health_status,
                    routing_rules=routing_rules,
                    webhooks=webhooks,
                    channels=channels,
                )
                for route in resolved_routes:
                    target_kind = str(route.get("target_kind") or "").strip().lower()
                    target = route.get("target") if isinstance(route.get("target"), dict) else None
                    if not isinstance(target, dict):
                        continue

                    if target_kind == "webhook":
                        self._send_webhook_notification(
                            webhook=target,
                            notification=notification,
                            collection_name=collection_name,
                            health_status=normalized_health_status,
                            routing_rule_id=self._safe_optional_text(route.get("rule_id")),
                            routing_rule_name=self._safe_optional_text(route.get("rule_name")),
                        )
                    else:
                        self._send_notification_channel_notification(
                            channel=target,
                            notification=notification,
                            collection_name=collection_name,
                            health_status=normalized_health_status,
                            routing_rule_id=self._safe_optional_text(route.get("rule_id")),
                            routing_rule_name=self._safe_optional_text(route.get("rule_name")),
                        )
                return

            for webhook in webhooks:
                if not isinstance(webhook, dict):
                    continue
                if not bool(webhook.get("is_enabled", True)):
                    continue

                webhook_min_severity = self._normalize_notification_severity(webhook.get("min_severity"))
                if self._notification_severity_rank(severity) < self._notification_severity_rank(webhook_min_severity):
                    continue

                webhook_enabled_types = set(self._normalize_notification_enabled_types(webhook.get("enabled_types")))
                if webhook_enabled_types and notification_type not in webhook_enabled_types:
                    continue

                self._send_webhook_notification(
                    webhook=webhook,
                    notification=notification,
                    collection_name=collection_name,
                    health_status=normalized_health_status,
                )

            for channel in channels:
                if not isinstance(channel, dict):
                    continue
                if not bool(channel.get("is_enabled", True)):
                    continue

                channel_min_severity = self._normalize_notification_severity(channel.get("min_severity"))
                if self._notification_severity_rank(severity) < self._notification_severity_rank(channel_min_severity):
                    continue

                channel_enabled_types = set(self._normalize_notification_enabled_types(channel.get("enabled_types")))
                if channel_enabled_types and notification_type not in channel_enabled_types:
                    continue

                self._send_notification_channel_notification(
                    channel=channel,
                    notification=notification,
                    collection_name=collection_name,
                    health_status=normalized_health_status,
                )

        if normalized_health_status in {"yellow", "red"} and normalized_health_status != previous_health_status:
            severity = "critical" if normalized_health_status == "red" else "warning"
            maybe_emit(
                "HEALTH_STATUS_CHANGED",
                severity,
                f"Collection health changed from {previous_health_status} to {normalized_health_status}.",
            )

        if normalized_health_status == "red" and previous_health_status != "red":
            maybe_emit("COLLECTION_ENTERED_RED", "critical", "Collection entered RED risk status.")

        if missing_best_active and not previous_missing_best:
            maybe_emit(
                "MISSING_BEST_EXECUTION",
                "warning",
                "Collection has executions but no best execution selected.",
            )

        if pending_review_high_active and not previous_pending_high:
            maybe_emit(
                "PENDING_REVIEW_HIGH",
                "warning",
                f"Pending editorial review is high ({pending_review_count}/{total_executions}).",
            )

        if operational_risk_active and not previous_operational_risk:
            maybe_emit(
                "OPERATIONAL_FAILURE_THRESHOLD",
                "critical",
                f"Operational failure threshold reached (failed={failed_count}, timeout={timeout_count}).",
            )

        self.runs_repository.upsert_collection_notification_state(
            collection_id=collection_id,
            state_data={
                "last_health_status": normalized_health_status,
                "missing_best_active": missing_best_active,
                "pending_review_high_active": pending_review_high_active,
                "operational_risk_active": operational_risk_active,
                "updated_at": now,
            },
        )

    def _normalize_meta_tags(self, value: Any) -> List[str]:
        if not isinstance(value, list):
            return []

        normalized: List[str] = []
        seen = set()
        for item in value:
            if not isinstance(item, str):
                continue
            trimmed = item.strip()
            if not trimmed:
                continue
            lowered = trimmed.lower()
            if lowered in seen:
                continue
            seen.add(lowered)
            normalized.append(trimmed)

        return normalized
