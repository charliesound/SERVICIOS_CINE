from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse

from src.auth.dependencies import get_current_auth_context
from src.schemas.auth import AuthLoginRequest, AuthLoginResponse, AuthLogoutResponse, AuthMeResponse


def create_auth_router() -> APIRouter:
    router = APIRouter(prefix="/api/auth", tags=["auth"])

    @router.post("/login", response_model=AuthLoginResponse)
    def login(payload: AuthLoginRequest, request: Request):
        auth_service = request.app.state.auth_service
        try:
            result = auth_service.login(payload.email, payload.password)
            return {"ok": True, **result}
        except ValueError as error:
            return JSONResponse(
                status_code=401,
                content={
                    "ok": False,
                    "error": {
                        "code": "AUTH_INVALID_CREDENTIALS",
                        "message": str(error),
                    },
                },
            )

    @router.get("/me", response_model=AuthMeResponse)
    def me(request: Request, authorization: str = Header(default="")):
        context = get_current_auth_context(request=request, authorization=authorization)
        return {"ok": True, "user": context["user"]}

    @router.post("/logout", response_model=AuthLogoutResponse)
    def logout(request: Request, authorization: str = Header(default="")):
        auth_service = request.app.state.auth_service
        context = get_current_auth_context(request=request, authorization=authorization)
        auth_service.revoke_token(context["token"])
        return {"ok": True, "message": "logged_out"}

    return router
