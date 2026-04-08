from pydantic import BaseModel, EmailStr
from typing import Optional


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    plan: str = "free"


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    plan: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(BaseModel):
    user_id: str
    username: str
    email: str
    hashed_password: str
    plan: str
    role: str
    is_active: bool
