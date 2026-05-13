from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    user_id: str
    username: str
    email: str
    plan: str
    role: str
    is_active: bool
    program: Optional[str] = "demo"
    signup_type: Optional[str] = "cid_user"
    account_status: Optional[str] = "active"
    access_level: Optional[str] = "standard"
    cid_enabled: Optional[bool] = True
    onboarding_completed: Optional[bool] = False
    full_name: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None


class RegisterCIDPayload(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=6)
    program: Optional[str] = "demo"
    full_name: Optional[str] = None
    company: Optional[str] = None
    country: Optional[str] = None
    accept_terms: bool = True


class RegisterDemoPayload(BaseModel):
    full_name: str
    email: EmailStr
    company: str
    position: Optional[str] = None
    need: str
    project_size: Optional[str] = None
    message: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6)


class RegisterPartnerPayload(BaseModel):
    full_name: str
    email: EmailStr
    company: str
    collaboration_type: str
    message: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6)


class TenantContext(BaseModel):
    user_id: str
    organization_id: str
    plan: str = "free"
    role: str
    is_admin: bool = False
    is_global_admin: bool = False
    auth_method: str = "jwt"
