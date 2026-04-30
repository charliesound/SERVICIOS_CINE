"""
Project member routes.
API endpoints for managing project members and permissions.
"""

from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models.core import User as DBUser
from models.project_member import ProjectMember, PROFESSIONAL_ROLES
from routes.auth_routes import get_current_user_optional
from schemas.auth_schema import UserResponse
from services.project_access_service import (
    get_project_member,
    get_project_members,
    add_project_member,
    remove_project_member,
    update_member_role,
    delegate_permissions,
    get_effective_permissions,
    check_permission,
    can_manage_project_members,
    can_delegate_permissions,
    is_project_owner,
)


async def _get_user_org_id(user_id: str, db: AsyncSession) -> Optional[str]:
    from models.core import User
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user.organization_id if user else None


router = APIRouter(prefix="/api/projects/{project_id}/members", tags=["project-members"])


class AddMemberPayload(BaseModel):
    user_id: str
    professional_role: str = "viewer"
    can_manage_permissions: bool = False
    can_manage_members: bool = False


class UpdateMemberPayload(BaseModel):
    professional_role: Optional[str] = None
    can_manage_permissions: Optional[bool] = None
    can_manage_members: Optional[bool] = None


class DelegatePermissionsPayload(BaseModel):
    target_user_id: str
    can_manage_permissions: bool


class MemberResponse(BaseModel):
    id: str
    user_id: str
    professional_role: str
    can_manage_permissions: bool
    can_manage_members: bool
    status: str
    invited_by_user_id: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


def _member_to_response(member: ProjectMember) -> MemberResponse:
    return MemberResponse(
        id=member.id,
        user_id=member.user_id,
        professional_role=member.professional_role,
        can_manage_permissions=member.can_manage_permissions,
        can_manage_members=member.can_manage_members,
        status=member.status,
        invited_by_user_id=member.invited_by_user_id,
        created_at=member.created_at.isoformat() if member.created_at else "",
    )


@router.get("")
async def list_project_members(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """List all members of a project."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not await check_permission(db, project_id, current_user.user_id, "project.members.view"):
        raise HTTPException(status_code=403, detail="Permission denied")

    members = await get_project_members(db, project_id)

    result = []
    for member in members:
        user_result = await db.execute(
            select(DBUser).where(DBUser.user_id == member.user_id)
        )
        user = user_result.scalars().first()
        member_dict = _member_to_response(member).model_dump()
        member_dict["user"] = {
            "user_id": user.user_id if user else None,
            "email": user.email if user else None,
            "name": f"{user.first_name} {user.last_name}".strip() if user else None,
        }
        result.append(member_dict)

    return {"members": result}


@router.get("/me")
async def get_my_member_info(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Get current user's membership info for a project."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    member = await get_project_member(db, project_id, current_user.user_id)
    if not member:
        raise HTTPException(status_code=404, detail="Not a member of this project")

    permissions = await get_effective_permissions(db, project_id, current_user.user_id)

    return {
        "member": _member_to_response(member).model_dump(),
        "permissions": permissions,
        "can_manage_members": await can_manage_project_members(db, project_id, current_user.user_id),
        "can_delegate": await can_delegate_permissions(db, project_id, current_user.user_id),
        "is_owner": await is_project_owner(db, project_id, current_user.user_id),
    }


@router.get("/roles")
async def list_professional_roles():
    """List available professional roles."""
    return {"roles": PROFESSIONAL_ROLES}


@router.post("")
async def add_project_member_endpoint(
    project_id: str,
    payload: AddMemberPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Add a member to a project."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not await can_manage_project_members(db, project_id, current_user.user_id):
        raise HTTPException(status_code=403, detail="Cannot manage members")

    user_org_id = await _get_user_org_id(current_user.user_id, db)
    if not user_org_id:
        raise HTTPException(status_code=403, detail="User has no organization")

    member = await add_project_member(
        db=db,
        project_id=project_id,
        organization_id=user_org_id,
        user_id=payload.user_id,
        professional_role=payload.professional_role,
        can_manage_permissions=payload.can_manage_permissions,
        can_manage_members=payload.can_manage_members,
        invited_by_user_id=current_user.user_id,
    )

    return {"member": _member_to_response(member).model_dump()}


@router.delete("/{user_id}")
async def remove_project_member_endpoint(
    project_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Remove a member from a project."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not await can_manage_project_members(db, project_id, current_user.user_id):
        raise HTTPException(status_code=403, detail="Cannot manage members")

    if await is_project_owner(db, project_id, user_id):
        raise HTTPException(status_code=400, detail="Cannot remove project owner")

    success = await remove_project_member(db, project_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")

    return {"success": True}


@router.patch("/{user_id}")
async def update_project_member(
    project_id: str,
    user_id: str,
    payload: UpdateMemberPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Update a project member's role or permissions."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not await can_manage_project_members(db, project_id, current_user.user_id):
        raise HTTPException(status_code=403, detail="Cannot manage members")

    member = await get_project_member(db, project_id, user_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    if payload.professional_role:
        member.professional_role = payload.professional_role

    if payload.can_manage_permissions is not None:
        if not await can_delegate_permissions(db, project_id, current_user.user_id):
            raise HTTPException(status_code=403, detail="Cannot delegate permissions")
        member.can_manage_permissions = payload.can_manage_permissions

    if payload.can_manage_members is not None:
        if not await can_manage_project_members(db, project_id, current_user.user_id):
            raise HTTPException(status_code=403, detail="Cannot manage members")
        member.can_manage_members = payload.can_manage_members

    await db.commit()
    await db.refresh(member)

    return {"member": _member_to_response(member).model_dump()}


@router.post("/delegate")
async def delegate_member_permissions(
    project_id: str,
    payload: DelegatePermissionsPayload,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Delegate permission management to a member."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    result = await delegate_permissions(
        db=db,
        project_id=project_id,
        target_user_id=payload.target_user_id,
        can_manage_permissions=payload.can_manage_permissions,
        delegate_user_id=current_user.user_id,
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Delegate failed"))

    return result


@router.get("/{user_id}/permissions")
async def get_member_permissions(
    project_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[UserResponse] = Depends(get_current_user_optional),
):
    """Get effective permissions for a member."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Authentication required")

    if not await check_permission(db, project_id, current_user.user_id, "project.members.view"):
        raise HTTPException(status_code=403, detail="Permission denied")

    member = await get_project_member(db, project_id, user_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    permissions = await get_effective_permissions(db, project_id, user_id)

    return {"user_id": user_id, "permissions": permissions}