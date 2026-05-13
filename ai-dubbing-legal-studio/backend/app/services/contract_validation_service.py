import json
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import VoiceContract, AuditLog


async def validate_contract(db: AsyncSession, contract_id: int, mode: str, language: str, territory: str = None, usage_type: str = None) -> dict:
    result = await db.execute(select(VoiceContract).where(VoiceContract.id == contract_id))
    contract = result.scalar_one_or_none()

    checks = {}
    blocked = False
    reasons = []

    if not contract:
        return {"contract_id": contract_id, "blocked": True, "reason": "Contrato no encontrado", "checks": {}}

    checks["exists"] = True

    if not contract.is_active:
        blocked = True
        reasons.append("Contrato no está activo")
        checks["active"] = False
    else:
        checks["active"] = True

    if contract.expiry_date.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        blocked = True
        reasons.append("Contrato expirado")
        checks["expired"] = True
    else:
        checks["expired"] = False

    if mode == "voz_original_ia_autorizada":
        if not contract.ia_consent:
            blocked = True
            reasons.append("No existe consentimiento IA explícito")
            checks["ia_consent"] = False
        else:
            checks["ia_consent"] = True

        allowed_langs = json.loads(contract.allowed_languages) if isinstance(contract.allowed_languages, str) else contract.allowed_languages
        if allowed_langs and language not in allowed_langs:
            blocked = True
            reasons.append(f"Idioma '{language}' no autorizado en contrato")
            checks["language_allowed"] = False
        else:
            checks["language_allowed"] = True

        allowed_territories = json.loads(contract.allowed_territories) if isinstance(contract.allowed_territories, str) else contract.allowed_territories
        if territory and allowed_territories and territory not in allowed_territories:
            blocked = True
            reasons.append(f"Territorio '{territory}' no autorizado")
            checks["territory_allowed"] = False
        else:
            checks["territory_allowed"] = True

        allowed_usage = json.loads(contract.allowed_usage_types) if isinstance(contract.allowed_usage_types, str) else contract.allowed_usage_types
        if usage_type and allowed_usage and usage_type not in allowed_usage:
            blocked = True
            reasons.append(f"Tipo de uso '{usage_type}' no autorizado")
            checks["usage_allowed"] = False
        else:
            checks["usage_allowed"] = True

    result_data = {
        "contract_id": contract_id,
        "blocked": blocked,
        "reason": "; ".join(reasons) if reasons else None,
        "checks": checks,
    }

    return result_data
