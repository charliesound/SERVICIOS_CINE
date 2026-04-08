from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Callable
from datetime import datetime, timedelta
import time


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
        auth_header = request.headers.get("authorization", "")
        user_id = auth_header.split(".")[0] if auth_header else "anonymous"
        return f"{endpoint_type}:{client_ip}:{user_id}"

    def _cleanup_old_requests(self, key: str, window: int):
        if key in self._requests:
            cutoff = datetime.utcnow() - timedelta(seconds=window)
            self._requests[key] = [t for t in self._requests[key] if t > cutoff]

    def check_rate_limit(
        self, request: Request, endpoint_type: str = "default"
    ) -> bool:
        key = self._get_key(request, endpoint_type)
        limit_config = self._limits.get(endpoint_type, self._limits["default"])

        self._cleanup_old_requests(key, limit_config["window"])

        if key not in self._requests:
            self._requests[key] = []

        if len(self._requests[key]) >= limit_config["requests"]:
            return False

        self._requests[key].append(datetime.utcnow())
        return True

    def get_remaining(self, request: Request, endpoint_type: str = "default") -> int:
        key = self._get_key(request, endpoint_type)
        limit_config = self._limits.get(endpoint_type, self._limits["default"])

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
        return JSONResponse(
            status_code=429,
            content={
                "detail": "Rate limit exceeded",
                "retry_after": 60,
                "remaining": remaining,
            },
            headers={
                "X-RateLimit-Limit": "100",
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": "60",
            },
        )

    response = await call_next(request)
    remaining = rate_limiter.get_remaining(request, endpoint_type)
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = str(remaining)

    return response
