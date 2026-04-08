import json
import socket
from time import monotonic, perf_counter, sleep
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


class ComfyUIClientError(Exception):
    def __init__(self, code: str, message: str, details: Optional[Dict[str, Any]] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or None
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "status_code": self.status_code,
        }


class ComfyUITimeoutError(ComfyUIClientError):
    pass


class ComfyUIClient:
    def __init__(self, base_url: str, timeout_seconds: float) -> None:
        self.base_url = (base_url or "").strip().rstrip("/")
        self.timeout_seconds = max(float(timeout_seconds), 0.1)

    def check_availability(self) -> dict:
        if not self.base_url:
            return {
                "configured": False,
                "reachable": False,
                "base_url": None,
                "timeout_seconds": self.timeout_seconds,
                "message": "ComfyUI base URL is not configured",
            }

        probe_url = urljoin(f"{self.base_url}/", "system_stats")
        started = perf_counter()

        try:
            with urlopen(probe_url, timeout=self.timeout_seconds) as response:
                elapsed_ms = int((perf_counter() - started) * 1000)
                return {
                    "configured": True,
                    "reachable": 200 <= response.status < 300,
                    "base_url": self.base_url,
                    "probe_url": probe_url,
                    "status_code": response.status,
                    "timeout_seconds": self.timeout_seconds,
                    "latency_ms": elapsed_ms,
                }
        except HTTPError as error:
            elapsed_ms = int((perf_counter() - started) * 1000)
            return {
                "configured": True,
                "reachable": False,
                "base_url": self.base_url,
                "probe_url": probe_url,
                "status_code": int(error.code),
                "timeout_seconds": self.timeout_seconds,
                "latency_ms": elapsed_ms,
                "error": f"HTTP {error.code}",
            }
        except URLError as error:
            elapsed_ms = int((perf_counter() - started) * 1000)
            return {
                "configured": True,
                "reachable": False,
                "base_url": self.base_url,
                "probe_url": probe_url,
                "timeout_seconds": self.timeout_seconds,
                "latency_ms": elapsed_ms,
                "error": str(getattr(error, "reason", error)),
            }
        except Exception as error:
            elapsed_ms = int((perf_counter() - started) * 1000)
            return {
                "configured": True,
                "reachable": False,
                "base_url": self.base_url,
                "probe_url": probe_url,
                "timeout_seconds": self.timeout_seconds,
                "latency_ms": elapsed_ms,
                "error": str(error),
            }

    def submit_prompt(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        response = self._request_json(method="POST", path="prompt", payload=payload)
        body = response["body"]
        return {
            "status_code": response["status_code"],
            "latency_ms": response["latency_ms"],
            "prompt_id": body.get("prompt_id") if isinstance(body, dict) else None,
            "provider_response": body,
        }

    def get_history(self, prompt_id: str) -> Dict[str, Any]:
        normalized_prompt_id = str(prompt_id or "").strip()
        if not normalized_prompt_id:
            raise ComfyUIClientError(
                code="INVALID_PROMPT_ID",
                message="prompt_id is required",
            )

        response = self._request_json(method="GET", path=f"history/{normalized_prompt_id}")
        body = response["body"]
        entry: Optional[Dict[str, Any]] = None

        if isinstance(body, dict):
            candidate = body.get(normalized_prompt_id)
            if isinstance(candidate, dict):
                entry = candidate
            elif "status" in body or "outputs" in body or "error" in body:
                entry = body

        return {
            "prompt_id": normalized_prompt_id,
            "status_code": response["status_code"],
            "latency_ms": response["latency_ms"],
            "provider_response": body,
            "history_entry": entry,
        }

    def get_prompt_state(self, prompt_id: str) -> Dict[str, Any]:
        history_response = self.get_history(prompt_id)
        entry = history_response.get("history_entry")

        if not isinstance(entry, dict):
            return {
                "prompt_id": history_response["prompt_id"],
                "state": "running",
                "has_outputs": False,
                "status_str": None,
                "error": None,
                "history_entry": None,
                "provider_response": history_response.get("provider_response"),
            }

        status_data = entry.get("status") if isinstance(entry.get("status"), dict) else {}
        status_str = str(status_data.get("status_str") or "").strip().lower() or None
        outputs = entry.get("outputs") if isinstance(entry.get("outputs"), dict) else {}
        has_outputs = len(outputs) > 0

        error_info = None
        if isinstance(entry.get("error"), dict):
            error_info = entry.get("error")
        elif entry.get("error") is not None:
            error_info = {"message": str(entry.get("error"))}

        message_errors = self._extract_status_message_errors(status_data)
        if error_info is None and message_errors:
            error_info = {
                "message": "ComfyUI history reported error message",
                "details": message_errors,
            }

        if error_info is not None or status_str in {"failed", "error"}:
            state = "failed"
        elif bool(status_data.get("completed")) or has_outputs or status_str in {"success", "succeeded", "completed"}:
            state = "succeeded"
        else:
            state = "running"

        return {
            "prompt_id": history_response["prompt_id"],
            "state": state,
            "has_outputs": has_outputs,
            "status_str": status_str,
            "error": error_info,
            "history_entry": entry,
            "provider_response": history_response.get("provider_response"),
        }

    def poll_prompt_until_terminal(
        self,
        prompt_id: str,
        max_wait_seconds: Optional[float] = None,
        poll_interval_seconds: float = 0.5,
    ) -> Dict[str, Any]:
        wait_seconds = max(float(max_wait_seconds or self.timeout_seconds), 0.1)
        interval_seconds = max(float(poll_interval_seconds), 0.1)

        started = monotonic()
        last_state: Optional[Dict[str, Any]] = None

        while True:
            elapsed = monotonic() - started
            if elapsed > wait_seconds:
                raise ComfyUITimeoutError(
                    code="COMFYUI_TIMEOUT",
                    message=f"ComfyUI did not report completion in time ({wait_seconds}s)",
                    details={
                        "prompt_id": str(prompt_id),
                        "last_state": last_state.get("state") if last_state else None,
                    },
                )

            state = self.get_prompt_state(prompt_id)
            last_state = state

            if state["state"] in {"succeeded", "failed"}:
                state["poll_elapsed_ms"] = int(elapsed * 1000)
                return state

            sleep(interval_seconds)

    def fetch_image(
        self,
        filename: str,
        subfolder: str = "",
        image_type: str = "output",
    ) -> tuple[bytes, str]:
        """Fetch an image from ComfyUI's /view endpoint.

        Returns (image_bytes, content_type).
        """
        if not self.base_url:
            raise ComfyUIClientError(
                code="COMFYUI_NOT_CONFIGURED",
                message="ComfyUI base URL is not configured",
            )

        from urllib.parse import urlencode

        params = urlencode({"filename": filename, "type": image_type, "subfolder": subfolder})
        path = f"view?{params}"

        response = self._request_binary(method="GET", path=path)
        content_type = response.get("content_type", "image/png")
        return response["body"], content_type

    def _request_binary(
        self,
        method: str,
        path: str,
    ) -> Dict[str, Any]:
        """Make a binary request and return raw bytes + content-type."""
        if not self.base_url:
            raise ComfyUIClientError(
                code="COMFYUI_NOT_CONFIGURED",
                message="ComfyUI base URL is not configured",
            )

        endpoint = urljoin(f"{self.base_url}/", path.lstrip("/"))
        request = Request(endpoint, method=method.upper())
        started = perf_counter()

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                body = response.read()
                content_type = response.getheader("Content-Type", "application/octet-stream")
                elapsed_ms = int((perf_counter() - started) * 1000)
                return {
                    "status_code": response.status,
                    "latency_ms": elapsed_ms,
                    "body": body,
                    "content_type": content_type,
                    "url": endpoint,
                }
        except HTTPError as error:
            raise ComfyUIClientError(
                code="COMFYUI_HTTP_ERROR",
                message=f"ComfyUI HTTP error: {error.code}",
                status_code=int(error.code),
            ) from error
        except (socket.timeout, TimeoutError) as error:
            raise ComfyUITimeoutError(
                code="COMFYUI_TIMEOUT",
                message=f"ComfyUI timeout after {self.timeout_seconds}s",
            ) from error
        except URLError as error:
            reason = getattr(error, "reason", None)
            raise ComfyUIClientError(
                code="COMFYUI_UNAVAILABLE",
                message=f"ComfyUI unavailable: {reason}",
            ) from error
        except Exception as error:
            raise ComfyUIClientError(
                code="COMFYUI_REQUEST_FAILED",
                message=f"ComfyUI request failed: {error}",
            ) from error

    def _request_json(
        self,
        method: str,
        path: str,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not self.base_url:
            raise ComfyUIClientError(
                code="COMFYUI_NOT_CONFIGURED",
                message="ComfyUI base URL is not configured",
            )

        endpoint = urljoin(f"{self.base_url}/", path.lstrip("/"))
        data = None
        headers: Dict[str, str] = {}

        if payload is not None:
            data = json.dumps(payload or {}, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(endpoint, data=data, method=method.upper(), headers=headers)
        started = perf_counter()

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                body = json.loads(raw) if raw else {}
                elapsed_ms = int((perf_counter() - started) * 1000)
                return {
                    "status_code": response.status,
                    "latency_ms": elapsed_ms,
                    "body": body,
                    "url": endpoint,
                }
        except HTTPError as error:
            details = self._extract_http_error_details(error)
            raise ComfyUIClientError(
                code="COMFYUI_HTTP_ERROR",
                message=f"ComfyUI HTTP error: {error.code}",
                details=details,
                status_code=int(error.code),
            ) from error
        except (socket.timeout, TimeoutError) as error:
            raise ComfyUITimeoutError(
                code="COMFYUI_TIMEOUT",
                message=f"ComfyUI timeout after {self.timeout_seconds}s",
            ) from error
        except URLError as error:
            reason = getattr(error, "reason", None)
            if isinstance(reason, (socket.timeout, TimeoutError)) or "timed out" in str(reason).lower():
                raise ComfyUITimeoutError(
                    code="COMFYUI_TIMEOUT",
                    message=f"ComfyUI timeout after {self.timeout_seconds}s",
                ) from error

            raise ComfyUIClientError(
                code="COMFYUI_UNAVAILABLE",
                message=f"ComfyUI unavailable: {reason}",
            ) from error
        except Exception as error:
            raise ComfyUIClientError(
                code="COMFYUI_REQUEST_FAILED",
                message=f"ComfyUI request failed: {error}",
            ) from error

    def _extract_http_error_details(self, error: HTTPError) -> Optional[Dict[str, Any]]:
        try:
            raw_error = error.read().decode("utf-8")
            if not raw_error:
                return None

            parsed = json.loads(raw_error)
            if isinstance(parsed, dict):
                return parsed

            return {"raw": parsed}
        except Exception:
            return None

    def _extract_status_message_errors(self, status_data: Dict[str, Any]) -> list[str]:
        messages = status_data.get("messages")
        if not isinstance(messages, list):
            return []

        errors: list[str] = []
        for item in messages:
            if not isinstance(item, list) or len(item) < 2:
                continue

            level = str(item[0]).lower()
            if level not in {"execution_error", "error"}:
                continue

            payload = item[1]
            if isinstance(payload, dict):
                message = payload.get("exception_message") or payload.get("message") or str(payload)
            else:
                message = str(payload)

            errors.append(message)

        return errors
