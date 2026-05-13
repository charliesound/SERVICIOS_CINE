import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.models import Base, User, UserRole, Organization, Project, DubbingJob, DubbingMode, JobStatus, VoiceContract, Actor
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token
from app.services.auth_service import register_user, authenticate_user
from app.services.contract_validation_service import validate_contract
from datetime import datetime, timezone, timedelta
import json


@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session_local = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_local() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_register_user(db_session):
    user = await register_user(db_session, "test@test.com", "password123", "Test User", "admin")
    assert user.email == "test@test.com"
    assert user.role == UserRole.admin


@pytest.mark.asyncio
async def test_authenticate_user(db_session):
    await register_user(db_session, "auth@test.com", "mypassword", "Auth User", "productor")
    result = await authenticate_user(db_session, "auth@test.com", "mypassword")
    assert "access_token" in result


@pytest.mark.asyncio
async def test_password_hashing():
    hashed = hash_password("test123")
    assert verify_password("test123", hashed)
    assert not verify_password("wrong", hashed)


@pytest.mark.asyncio
async def test_jwt_token():
    token = create_access_token({"sub": "1", "role": "admin"})
    payload = decode_access_token(token)
    assert payload["sub"] == "1"
    assert payload["role"] == "admin"


@pytest.mark.asyncio
async def test_validate_contract(db_session):
    org = Organization(name="Test Org")
    db_session.add(org)
    await db_session.commit()

    actor = Actor(name="Test Actor", organization_id=org.id)
    db_session.add(actor)
    await db_session.commit()

    contract = VoiceContract(
        actor_id=actor.id,
        organization_id=org.id,
        contract_ref="REF-001",
        signed_date=datetime.now(timezone.utc) - timedelta(days=30),
        expiry_date=datetime.now(timezone.utc) + timedelta(days=30),
        is_active=True,
        ia_consent=True,
        allowed_languages=json.dumps(["es", "en"]),
        allowed_territories=json.dumps(["ES", "MX"]),
        allowed_usage_types=json.dumps(["dubbing", "trailer"]),
    )
    db_session.add(contract)
    await db_session.commit()

    result = await validate_contract(
        db_session,
        contract_id=contract.id,
        mode="voz_original_ia_autorizada",
        language="es",
        territory="ES",
        usage_type="dubbing",
    )
    assert result["blocked"] is False

    result_blocked = await validate_contract(
        db_session,
        contract_id=contract.id,
        mode="voz_original_ia_autorizada",
        language="fr",
        territory="ES",
        usage_type="dubbing",
    )
    assert result_blocked["blocked"] is True
