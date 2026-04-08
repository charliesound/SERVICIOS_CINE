from typing import Literal

from pydantic import BaseModel, Field


AuthRole = Literal["admin", "editor", "reviewer", "viewer"]


class AuthUser(BaseModel):
    user_id: str
    email: str
    role: AuthRole
    is_active: bool = True
    created_at: str
    updated_at: str


class AuthLoginRequest(BaseModel):
    email: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AuthLoginResponse(BaseModel):
    ok: bool = True
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: AuthUser


class AuthMeResponse(BaseModel):
    ok: bool = True
    user: AuthUser


class AuthLogoutResponse(BaseModel):
    ok: bool = True
    message: str = "logged_out"
