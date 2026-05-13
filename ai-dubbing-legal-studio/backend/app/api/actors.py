from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models import Actor, User
from app.schemas import ActorCreate, ActorOut

router = APIRouter(prefix="/api/actors", tags=["actors"])


@router.post("", response_model=ActorOut)
async def create_actor(data: ActorCreate, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    actor = Actor(
        name=data.name, email=data.email,
        voice_gender=data.voice_gender, voice_language=data.voice_language,
        notes=data.notes, organization_id=user.organization_id,
    )
    db.add(actor)
    await db.commit()
    await db.refresh(actor)
    return actor


@router.get("", response_model=list[ActorOut])
async def list_actors(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Actor).where(Actor.organization_id == user.organization_id))
    return result.scalars().all()


@router.get("/{actor_id}", response_model=ActorOut)
async def get_actor(actor_id: int, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    result = await db.execute(select(Actor).where(Actor.id == actor_id))
    actor = result.scalar_one_or_none()
    if not actor:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Actor no encontrado")
    return actor
