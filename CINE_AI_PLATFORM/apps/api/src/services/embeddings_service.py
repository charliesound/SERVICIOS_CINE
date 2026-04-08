import json
from typing import Any, Dict, Optional
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


class EmbeddingsServiceError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
    ) -> None:
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


class EmbeddingsService:
    def __init__(self, base_url: str, timeout_seconds: float, expected_dimensions: int = 384) -> None:
        self.base_url = str(base_url or "").strip().rstrip("/")
        self.timeout_seconds = max(float(timeout_seconds), 0.1)
        self.expected_dimensions = max(int(expected_dimensions), 1)

    def embed_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        normalized_text = str(text or "").strip()
        if not normalized_text:
            raise ValueError("text is required")

        response = self._request_json(
            method="POST",
            path="embed",
            payload={
                "text": normalized_text,
                "metadata": metadata or {},
            },
        )
        body = response["body"]
        if not isinstance(body, dict):
            raise EmbeddingsServiceError(
                code="EMBEDDINGS_INVALID_RESPONSE",
                message="Embeddings service returned an invalid body",
                details={"body": body},
            )

        vector = body.get("vector")
        if not isinstance(vector, list):
            raise EmbeddingsServiceError(
                code="EMBEDDINGS_VECTOR_MISSING",
                message="Embeddings service response is missing vector[]",
                details={"body": body},
            )

        dimensions = int(body.get("dimensions") or len(vector))
        if dimensions != self.expected_dimensions or len(vector) != self.expected_dimensions:
            raise EmbeddingsServiceError(
                code="EMBEDDINGS_INVALID_DIMENSIONS",
                message=f"Embeddings dimensions must be {self.expected_dimensions}",
                details={"dimensions": dimensions, "vector_length": len(vector)},
            )

        return {
            "ok": bool(body.get("ok", True)),
            "model": str(body.get("model") or "unknown"),
            "dimensions": dimensions,
            "vector": [float(value) for value in vector],
            "metadata": body.get("metadata") if isinstance(body.get("metadata"), dict) else None,
        }

    def _request_json(self, method: str, path: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.base_url:
            raise EmbeddingsServiceError(
                code="EMBEDDINGS_BASE_URL_NOT_CONFIGURED",
                message="Embeddings service base URL is not configured",
            )

        url = urljoin(f"{self.base_url}/", path.lstrip("/"))
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(url=url, data=data, headers=headers, method=method.upper())

        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:
                raw_body = response.read().decode("utf-8")
                parsed_body = json.loads(raw_body) if raw_body else {}
                return {"status_code": int(response.status), "body": parsed_body}
        except HTTPError as error:
            details: Dict[str, Any] = {}
            try:
                raw_body = error.read().decode("utf-8")
                details["body"] = json.loads(raw_body) if raw_body else None
            except Exception:
                details["body"] = None
            raise EmbeddingsServiceError(
                code="EMBEDDINGS_HTTP_ERROR",
                message=f"Embeddings service returned HTTP {error.code}",
                details=details or None,
                status_code=int(error.code),
            ) from error
        except URLError as error:
            raise EmbeddingsServiceError(
                code="EMBEDDINGS_UNREACHABLE",
                message="Embeddings service is unreachable",
                details={"reason": str(getattr(error, "reason", error))},
            ) from error
        except Exception as error:
            raise EmbeddingsServiceError(
                code="EMBEDDINGS_REQUEST_FAILED",
                message="Embeddings request failed",
                details={"reason": str(error)},
            ) from error
