from __future__ import annotations

import hashlib
import logging
import re
import secrets
from datetime import datetime, timedelta

import bcrypt
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from models.core import User
from models.password_reset import PasswordResetToken
from services.account_service import get_user_by_email
from services.email_service import send_password_reset_email

logger = logging.getLogger("servicios_cine.password_reset")

_PASSWORD_PATTERN = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$")


async def request_password_reset(
    db: AsyncSession,
    email: str,
    request_ip: str | None = None,
    user_agent: str | None = None,
) -> None:
    normalized_email = email.strip().lower()
    user = await get_user_by_email(db, normalized_email)

    if user and user.is_active:
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        settings = get_settings()

        reset_token = PasswordResetToken(
            user_id=str(user.id),
            token_hash=token_hash,
            expires_at=datetime.utcnow() + timedelta(minutes=settings.password_reset_token_ttl_minutes),
            request_ip=request_ip,
            user_agent=user_agent,
        )
        db.add(reset_token)
        await db.commit()

        reset_link = f"{settings.frontend_base_url}/reset-password?token={token}"
        await send_password_reset_email(normalized_email, reset_link)

    # Always return silently — never reveal whether the email exists


async def validate_reset_token(db: AsyncSession, token: str) -> PasswordResetToken:
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token_hash == token_hash)
    )
    reset_token = result.scalar_one_or_none()

    if not reset_token:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")
    if reset_token.used_at is not None:
        raise HTTPException(status_code=400, detail="Reset token has already been used")
    if datetime.utcnow() > reset_token.expires_at:
        raise HTTPException(status_code=400, detail="Reset token has expired")

    return reset_token


async def reset_password(
    db: AsyncSession,
    token: str,
    new_password: str,
    confirm_password: str,
) -> None:
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    if not _PASSWORD_PATTERN.match(new_password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters with one uppercase, one lowercase, and one number",
        )

    reset_token = await validate_reset_token(db, token)

    user_result = await db.execute(select(User).where(User.id == reset_token.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    reset_token.used_at = datetime.utcnow()
    await db.commit()
