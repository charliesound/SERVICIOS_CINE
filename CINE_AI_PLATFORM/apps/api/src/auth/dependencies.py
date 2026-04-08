from typing import Any, Callable, Dict

from fastapi import Header, HTTPException, Request, status


def _get_auth_service(request: Request):
    auth_service = getattr(request.app.state, "auth_service", None)
    if auth_service is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "AUTH_SERVICE_NOT_CONFIGURED", "message": "Authentication service is not configured"},
        )
    return auth_service


def get_current_auth_context(request: Request, authorization: str = Header(default="")) -> Dict[str, Any]:
    auth_service = _get_auth_service(request)
    header_value = str(authorization or "").strip()
    if not header_value.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_REQUIRED", "message": "Authentication required"},
        )

    token = header_value.split(" ", 1)[1].strip()
    context = auth_service.get_authenticated_context(token)
    if context is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "AUTH_INVALID_TOKEN", "message": "Invalid or expired session"},
        )
    return context


def require_authenticated(request: Request, authorization: str = Header(default="")) -> Dict[str, Any]:
    return get_current_auth_context(request=request, authorization=authorization)


def require_roles(*allowed_roles: str) -> Callable[..., Dict[str, Any]]:
    normalized_allowed_roles = {str(role or "").strip().lower() for role in allowed_roles if str(role or "").strip()}

    def dependency(request: Request, authorization: str = Header(default="")) -> Dict[str, Any]:
        context = get_current_auth_context(request=request, authorization=authorization)
        role = str(context.get("user", {}).get("role") or "viewer").strip().lower()
        if role not in normalized_allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "INSUFFICIENT_ROLE",
                    "message": f"Role '{role}' is not allowed to perform this action",
                },
            )
        return context

    return dependency
