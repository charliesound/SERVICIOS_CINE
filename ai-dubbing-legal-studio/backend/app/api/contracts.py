import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import VoiceContract, Actor, User, AuditLog
from app.schemas import ContractCreate, ContractUpdate, ContractOut, ContractValidationResult
from app.services.contract_validation_service import validate_contract
from app.services.audit_service import log_audit

router = APIRouter(prefix="/api/contracts", tags=["contracts"])


@router.post("", response_model=ContractOut)
async def create_contract(data: ContractCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    contract = VoiceContract(
        actor_id=data.actor_id,
        organization_id=user.organization_id,
        contract_ref=data.contract_ref,
        signed_date=data.signed_date,
        expiry_date=data.expiry_date,
        ia_consent=data.ia_consent,
        allowed_languages=json.dumps(data.allowed_languages),
        allowed_territories=json.dumps(data.allowed_territories),
        allowed_usage_types=json.dumps(data.allowed_usage_types),
        max_duration_seconds=data.max_duration_seconds,
        compensation_terms=data.compensation_terms,
        document_path=data.document_path,
        notes=data.notes,
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    await log_audit(db, user_id=user.id, organization_id=user.organization_id,
                    action="contract.created", entity_type="voice_contract", entity_id=contract.id)
    return contract


@router.get("", response_model=list[ContractOut])
async def list_contracts(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(
        select(VoiceContract).where(VoiceContract.organization_id == user.organization_id)
    )
    return result.scalars().all()


@router.get("/{contract_id}", response_model=ContractOut)
async def get_contract(contract_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(VoiceContract).where(VoiceContract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return contract


@router.patch("/{contract_id}", response_model=ContractOut)
async def update_contract(contract_id: int, data: ContractUpdate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(VoiceContract).where(VoiceContract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in ("allowed_languages", "allowed_territories", "allowed_usage_types") and value is not None:
            setattr(contract, key, json.dumps(value))
        else:
            setattr(contract, key, value)
    await db.commit()
    await db.refresh(contract)
    await log_audit(db, user_id=user.id, organization_id=user.organization_id,
                    action="contract.updated", entity_type="voice_contract", entity_id=contract.id)
    return contract


@router.post("/{contract_id}/validate", response_model=ContractValidationResult)
async def validate_contract_endpoint(
    contract_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    body = await request.json()
    result = await validate_contract(
        db,
        contract_id=contract_id,
        mode=body.get("mode", "voz_original_ia_autorizada"),
        language=body.get("language", ""),
        territory=body.get("territory"),
        usage_type=body.get("usage_type"),
    )

    await log_audit(
        db, user_id=user.id, organization_id=user.organization_id,
        action=f"contract.validate.{'blocked' if result['blocked'] else 'passed'}",
        entity_type="voice_contract", entity_id=contract_id,
        details=result,
    )
    return result
