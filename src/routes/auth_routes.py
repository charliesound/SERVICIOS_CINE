from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from schemas.auth_schema import UserRegister, UserLogin, TokenResponse, UserResponse
from services.user_service import user_store
from config import config

router = APIRouter(prefix="/api/auth", tags=["auth"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=60)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode, config["auth"]["secret_key"], algorithm=config["auth"]["algorithm"]
    )


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            config["auth"]["secret_key"],
            algorithms=[config["auth"]["algorithm"]],
        )
        return payload
    except JWTError:
        return None


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    existing = user_store.get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = user_store.create_user(
        username=user_data.username,
        email=user_data.email,
        password=pwd_context.hash(user_data.password),
        plan="free",
    )

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        plan=user.plan,
        role=user.role,
        is_active=user.is_active,
    )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = user_store.get_user_by_email(credentials.email)
    if not user or not pwd_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")

    token = create_access_token({"sub": user.user_id, "email": user.email})

    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=config["auth"]["access_token_expire_minutes"] * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(authorization: Optional[str] = Depends(lambda: None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = user_store.get_user(str(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        email=user.email,
        plan=user.plan,
        role=user.role,
        is_active=user.is_active,
    )
