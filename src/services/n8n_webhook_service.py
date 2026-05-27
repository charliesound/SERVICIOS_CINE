from __future__ import annotations

import uuid

import httpx

from core.config import get_settings
from schemas.integration_schema import (
    IntegrationEventPayload,
    N8NStatusResponse,
    N8NTestResponse,
)
from services.logging_service import logger


class N8NWebhookService:
    def _settings(self):
        return get_settings()

    def is_enabled(self) -> bool:
        return bool(self._settings().n8n_enabled)

    def _timeout_seconds(self) -> int:
        return max(1, int(self._settings().n8n_default_timeout_seconds))

    def _normalized_path(self, path: str | None) -> str:
        candidate = (path or "").strip() or "/webhook/cid-test"
        return candidate if candidate.startswith("/") else f"/{candidate}"

    def _safe_base_url(self) -> str | None:
        raw = (self._settings().n8n_base_url or "").strip()
        if not raw:
            return None
        try:
            parsed = httpx.URL(raw)
        except Exception:
            return None
        if parsed.scheme not in {"http", "https"} or not parsed.host:
            return None
        port = f":{parsed.port}" if parsed.port else ""
        return f"{parsed.scheme}://{parsed.host}{port}"

    def _build_webhook_url(self, path: str | None) -> str:
        base_url = self._safe_base_url()
        if not base_url:
            raise ValueError("N8N base URL is not configured")
        return f"{base_url.rstrip('/')}{self._normalized_path(path)}"

    def _build_headers(self, trace_id: str, event_type: str) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "X-CID-Trace-ID": trace_id,
            "X-CID-Event-Type": event_type,
        }
        secret = (self._settings().n8n_webhook_secret or "").strip()
        if secret:
            headers["X-CID-Webhook-Secret"] = secret
        return headers

    async def get_status(self, *, trace_id: str | None = None) -> N8NStatusResponse:
        resolved_trace_id = trace_id or uuid.uuid4().hex
        base_url = self._safe_base_url()
        response = N8NStatusResponse(
            enabled=self.is_enabled(),
            status="disabled" if not self.is_enabled() else "configured",
            base_url=base_url,
            reachable=False,
            test_webhook_path=self._normalized_path(self._settings().n8n_test_webhook_path),
            timeout_seconds=self._timeout_seconds(),
            trace_id=resolved_trace_id,
        )

        if not self.is_enabled():
            return response
        if not base_url:
            response.status = "failed"
            response.error = "N8N base URL is not configured"
            return response

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds(), follow_redirects=True) as client:
                health_response = await client.get(base_url)
            response.reachable = health_response.status_code < 500
            response.status = "reachable" if response.reachable else "unreachable"
            if not response.reachable:
                response.error = f"Unexpected status from n8n: {health_response.status_code}"
        except httpx.TimeoutException:
            response.status = "failed"
            response.error = "Timed out while checking n8n reachability"
        except httpx.HTTPError as exc:
            response.status = "failed"
            response.error = f"Failed to reach n8n: {exc}"

        return response

    async def send_test_event(self, event: IntegrationEventPayload) -> N8NTestResponse:
        endpoint_path = self._normalized_path(self._settings().n8n_test_webhook_path)

        if not self.is_enabled():
            return N8NTestResponse(
                sent=False,
                status="skipped",
                trace_id=event.trace_id,
                event_type=event.event_type,
                endpoint_path=endpoint_path,
                error="n8n integration is disabled",
            )

        try:
            webhook_url = self._build_webhook_url(endpoint_path)
        except ValueError as exc:
            logger.warning("n8n test event skipped due to invalid configuration | trace_id=%s | error=%s", event.trace_id, exc)
            return N8NTestResponse(
                sent=False,
                status="failed",
                trace_id=event.trace_id,
                event_type=event.event_type,
                endpoint_path=endpoint_path,
                error=str(exc),
            )

        try:
            async with httpx.AsyncClient(timeout=self._timeout_seconds(), follow_redirects=True) as client:
                response = await client.post(
                    webhook_url,
                    json=event.model_dump(mode="json"),
                    headers=self._build_headers(event.trace_id, event.event_type),
                )
            if response.status_code >= 400:
                logger.warning(
                    "n8n webhook returned error | trace_id=%s | status_code=%s | path=%s",
                    event.trace_id,
                    response.status_code,
                    endpoint_path,
                )
                return N8NTestResponse(
                    sent=False,
                    status="failed",
                    trace_id=event.trace_id,
                    event_type=event.event_type,
                    endpoint_path=endpoint_path,
                    response_status_code=response.status_code,
                    error=f"n8n webhook returned status {response.status_code}",
                )
        except httpx.TimeoutException:
            logger.warning("n8n webhook timeout | trace_id=%s | path=%s", event.trace_id, endpoint_path)
            return N8NTestResponse(
                sent=False,
                status="failed",
                trace_id=event.trace_id,
                event_type=event.event_type,
                endpoint_path=endpoint_path,
                error="Timed out while calling n8n webhook",
            )
        except httpx.HTTPError as exc:
            logger.warning("n8n webhook call failed | trace_id=%s | path=%s | error=%s", event.trace_id, endpoint_path, exc)
            return N8NTestResponse(
                sent=False,
                status="failed",
                trace_id=event.trace_id,
                event_type=event.event_type,
                endpoint_path=endpoint_path,
                error=f"Failed to call n8n webhook: {exc}",
            )

        logger.info("n8n webhook sent | trace_id=%s | event_type=%s | path=%s", event.trace_id, event.event_type, endpoint_path)
        return N8NTestResponse(
            sent=True,
            status="sent",
            trace_id=event.trace_id,
            event_type=event.event_type,
            endpoint_path=endpoint_path,
            response_status_code=response.status_code,
        )


n8n_webhook_service = N8NWebhookService()
