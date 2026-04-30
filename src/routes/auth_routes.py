from datetime import datetime, timedelta
import hashlib
import secrets
from typing import Optional

import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from config import config
from database import get_db
from models.core import User as DBUser
from schemas.auth_schema import (
    RegisterCIDPayload,
    RegisterDemoPayload,
    RegisterPartnerPayload,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
    TenantContext,
)
from services.account_service import (
    build_user_response_from_db,
    create_user_account,
    get_user_by_email,
    get_user_by_id,
    resolve_effective_plan,
)
from services.logging_service import logger

router = APIRouter(prefix="/api/auth", tags=["auth"])


def raise_auth_database_unavailable(error: SQLAlchemyError) -> None:
    logger.exception("Auth database operation failed", exc_info=error)
    raise HTTPException(
        status_code=503,
        detail="Auth service database is unavailable",
    ) from error


def _audit_identity(value: str) -> str:
    normalized = (value or "").strip().lower().encode("utf-8")
    return hashlib.sha256(normalized).hexdigest()[:10]


def _is_cid_access_allowed(user: DBUser) -> bool:
    account_status = str(getattr(user, "account_status", "active") or "active").lower()
    cid_enabled = bool(getattr(user, "cid_enabled", True))
    return account_status == "active" and cid_enabled


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=config["auth"]["access_token_expire_minutes"])
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


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


security = HTTPBearer(auto_error=False)


@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    try:
        existing = await get_user_by_email(db, user_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = await create_user_account(
            db,
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            plan="free",
            full_name=user_data.username,
            organization_name=f"{user_data.username} Studio",
        )

        return await build_user_response_from_db(db, user)
    except SQLAlchemyError as error:
        raise_auth_database_unavailable(error)


@router.post("/register/cid", response_model=UserResponse)
async def register_cid(
    user_data: RegisterCIDPayload,
    db: AsyncSession = Depends(get_db),
):
    try:
        existing = await get_user_by_email(db, user_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user = await create_user_account(
            db,
            username=user_data.username,
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            plan="free",
            program=user_data.program or "demo",
            signup_type="cid_user",
            account_status="active",
            access_level="standard",
            cid_enabled=True,
            onboarding_completed=False,
            full_name=user_data.full_name or user_data.username,
            company=user_data.company,
            country=user_data.country,
            organization_name=user_data.company or f"{user_data.username} Studio",
        )

        return await build_user_response_from_db(db, user)
    except SQLAlchemyError as error:
        raise_auth_database_unavailable(error)


@router.post("/register/demo", response_model=UserResponse)
async def register_demo(
    user_data: RegisterDemoPayload,
    db: AsyncSession = Depends(get_db),
):
    try:
        existing = await get_user_by_email(db, user_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        pwd = user_data.password or secrets.token_urlsafe(18)
        username = user_data.email.split("@", 1)[0]
        user = await create_user_account(
            db,
            username=username,
            email=user_data.email,
            hashed_password=hash_password(pwd),
            plan="free",
            program="demo",
            signup_type="demo_request",
            account_status="pending",
            access_level="limited",
            cid_enabled=False,
            onboarding_completed=False,
            full_name=user_data.full_name,
            company=user_data.company,
            organization_name=user_data.company,
        )

        return await build_user_response_from_db(db, user)
    except SQLAlchemyError as error:
        raise_auth_database_unavailable(error)


@router.post("/register/partner", response_model=UserResponse)
async def register_partner(
    user_data: RegisterPartnerPayload,
    db: AsyncSession = Depends(get_db),
):
    try:
        existing = await get_user_by_email(db, user_data.email)
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        pwd = user_data.password or secrets.token_urlsafe(18)
        username = user_data.email.split("@", 1)[0]
        user = await create_user_account(
            db,
            username=username,
            email=user_data.email,
            hashed_password=hash_password(pwd),
            plan="free",
            program="demo",
            signup_type="partner_interest",
            account_status="pending",
            access_level="limited",
            cid_enabled=False,
            onboarding_completed=False,
            full_name=user_data.full_name,
            company=user_data.company,
            organization_name=user_data.company,
        )

        return await build_user_response_from_db(db, user)
    except SQLAlchemyError as error:
        raise_auth_database_unavailable(error)


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await get_user_by_email(db, credentials.email)
        if not user or not verify_password(credentials.password, user.hashed_password):
            logger.warning(
                "Login failed: invalid credentials ref=%s",
                _audit_identity(credentials.email),
            )
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_active:
            logger.warning(
                "Login failed: user disabled ref=%s",
                _audit_identity(credentials.email),
            )
            raise HTTPException(status_code=403, detail="User account is disabled")

        if not _is_cid_access_allowed(user):
            logger.warning(
                "Login blocked: account not approved for CID ref=%s",
                _audit_identity(credentials.email),
            )
            raise HTTPException(
                status_code=403,
                detail="Account is not approved for CID access",
            )

        token = create_access_token({"sub": str(user.id), "email": user.email})

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            expires_in=config["auth"]["access_token_expire_minutes"] * 60,
        )
    except SQLAlchemyError as error:
        raise_auth_database_unavailable(error)


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        logger.warning("Invalid token payload in /auth/me: no sub")
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = await get_user_by_id(db, str(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User account is disabled")

    if not _is_cid_access_allowed(user):
        raise HTTPException(status_code=403, detail="Account is not approved for CID access")

    return await build_user_response_from_db(db, user)


async def get_tenant_context(
    user_response: UserResponse = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TenantContext:
    """
    Central dependency to extract and verify organization identity.
    Enforces that every authorized request has a valid organization_id.
    """
    # Fetch DB user to get organization_id (not present in standard UserResponse sometimes or to verify)
    user = await get_user_by_id(db, user_response.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User account not found")

    if not user.organization_id:
        # This should technically not happen in a fully established multi-tenant system
        # unless it's a legacy or malformed account.
        logger.error(f"User {user.id} has no organization_id assigned")
        raise HTTPException(
            status_code=403, detail="Account is not associated with any organization"
        )

    return TenantContext(
        user_id=str(user.id),
        organization_id=str(user.organization_id),
        plan=await resolve_effective_plan(db, user),
        role=user.access_level or "standard",
        is_admin=(user.access_level == "admin"),
    )



async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[UserResponse]:
    if not credentials:
        return None

    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = await get_user_by_id(db, str(user_id))
    if not user or not user.is_active or not _is_cid_access_allowed(user):
        return None

    return await build_user_response_from_db(db, user)


async def check_project_ownership(
    project_id: str,
    user_id: str,
    db: AsyncSession,
) -> bool:
    from sqlalchemy import select

    from models.core import Project

    user = await get_user_by_id(db, user_id)
    if not user or not user.organization_id:
        return False

    project_result = await db.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()

    if not project:
        return False

    return project.organization_id == user.organization_id
