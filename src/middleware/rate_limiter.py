import hashlib

from fastapi import Request
from fastapi.responses import JSONResponse
from typing import Dict, Callable
from datetime import datetime, timedelta


class RateLimiter:
    def __init__(self):
        self._requests: Dict[str, list] = {}
        self._limits = {
            "default": {"requests": 100, "window": 60},
            "auth": {"requests": 10, "window": 60},
            "render": {"requests": 20, "window": 300},
            "admin": {"requests": 50, "window": 60},
        }

    def _get_key(self, request: Request, endpoint_type: str = "default") -> str:
        client_ip = request.client.host if request.client else "unknown"
        if endpoint_type == "auth":
            return f"{endpoint_type}:{client_ip}"
        auth_header = request.headers.get("authorization", "")
        auth_fingerprint = (
            hashlib.sha256(auth_header.encode("utf-8")).hexdigest()[:12]
            if auth_header
            else "anonymous"
        )
        return f"{endpoint_type}:{client_ip}:{auth_fingerprint}"

    def get_limit_config(self, endpoint_type: str = "default") -> Dict[str, int]:
        return self._limits.get(endpoint_type, self._limits["default"])

    def _cleanup_old_requests(self, key: str, window: int):
        if key in self._requests:
            cutoff = datetime.utcnow() - timedelta(seconds=window)
            self._requests[key] = [t for t in self._requests[key] if t > cutoff]

    def check_rate_limit(
        self, request: Request, endpoint_type: str = "default"
    ) -> bool:
        key = self._get_key(request, endpoint_type)
        limit_config = self.get_limit_config(endpoint_type)

        self._cleanup_old_requests(key, limit_config["window"])

        if key not in self._requests:
            self._requests[key] = []

        if len(self._requests[key]) >= limit_config["requests"]:
            return False

        self._requests[key].append(datetime.utcnow())
        return True

    def get_remaining(self, request: Request, endpoint_type: str = "default") -> int:
        key = self._get_key(request, endpoint_type)
        limit_config = self.get_limit_config(endpoint_type)

        self._cleanup_old_requests(key, limit_config["window"])

        return max(0, limit_config["requests"] - len(self._requests.get(key, [])))


rate_limiter = RateLimiter()


async def rate_limit_middleware(request: Request, call_next: Callable):
    endpoint_type = "default"
    if request.url.path.startswith("/api/auth"):
        endpoint_type = "auth"
    elif request.url.path.startswith("/api/render"):
        endpoint_type = "render"
    elif request.url.path.startswith("/api/admin"):
        endpoint_type = "admin"

    if not rate_limiter.check_rate_limit(request, endpoint_type):
        remaining = rate_limiter.get_remaining(request, endpoint_type)
        limit_config = rate_limiter.get_limit_config(endpoint_type)
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded",
                "retry_after": limit_config["window"],
                "remaining": remaining,
            },
            headers={
                "X-RateLimit-Limit": str(limit_config["requests"]),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": str(limit_config["window"]),
            },
        )

    response = await call_next(request)
    remaining = rate_limiter.get_remaining(request, endpoint_type)
    limit_config = rate_limiter.get_limit_config(endpoint_type)
    response.headers["X-RateLimit-Limit"] = str(limit_config["requests"])
    response.headers["X-RateLimit-Remaining"] = str(remaining)
    response.headers["X-RateLimit-Reset"] = str(limit_config["window"])

    return response
