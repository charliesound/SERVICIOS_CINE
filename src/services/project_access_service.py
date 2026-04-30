"""
Project access control service.
Manages project member permissions and delegation.
"""

from typing import Optional, List
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from models.core import Project, User
from models.project_member import (
    ProjectMember,
    ROLE_DEFAULT_PERMISSIONS,
    PROJECT_PERMISSIONS,
    PROFESSIONAL_ROLES,
)


async def get_project_member(
    db: AsyncSession, project_id: str, user_id: str
) -> Optional[ProjectMember]:
    """Get a project member by project and user ID."""
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    )
    return result.scalars().first()


async def get_project_members(
    db: AsyncSession, project_id: str
) -> List[ProjectMember]:
    """Get all members of a project."""
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.status == "active",
        )
    )
    return list(result.scalars().all())


async def get_project_owner(
    db: AsyncSession, project_id: str
) -> Optional[ProjectMember]:
    """Get the owner of a project."""
    result = await db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.professional_role == "owner",
            ProjectMember.status == "active",
        )
    )
    return result.scalars().first()


async def add_project_member(
    db: AsyncSession,
    project_id: str,
    organization_id: str,
    user_id: str,
    professional_role: str = "viewer",
    can_manage_permissions: bool = False,
    can_manage_members: bool = False,
    invited_by_user_id: Optional[str] = None,
) -> ProjectMember:
    """Add a member to a project."""
    existing = await get_project_member(db, project_id, user_id)
    if existing:
        existing.professional_role = professional_role
        existing.can_manage_permissions = can_manage_permissions
        existing.can_manage_members = can_manage_members
        existing.status = "active"
        await db.commit()
        await db.refresh(existing)
        return existing

    member = ProjectMember(
        id=uuid4().hex,
        project_id=project_id,
        organization_id=organization_id,
        user_id=user_id,
        professional_role=professional_role,
        can_manage_permissions=can_manage_permissions,
        can_manage_members=can_manage_members,
        invited_by_user_id=invited_by_user_id,
        status="active",
    )
    db.add(member)
    await db.commit()
    await db.refresh(member)
    return member


async def remove_project_member(
    db: AsyncSession, project_id: str, user_id: str
) -> bool:
    """Remove (deactivate) a member from a project."""
    member = await get_project_member(db, project_id, user_id)
    if not member:
        return False

    member.status = "inactive"
    await db.commit()
    return True


async def update_member_role(
    db: AsyncSession,
    project_id: str,
    user_id: str,
    professional_role: str,
) -> Optional[ProjectMember]:
    """Update a member's professional role."""
    member = await get_project_member(db, project_id, user_id)
    if not member:
        return None

    member.professional_role = professional_role
    await db.commit()
    await db.refresh(member)
    return member


async def delegate_permissions(
    db: AsyncSession,
    project_id: str,
    target_user_id: str,
    can_manage_permissions: bool,
    delegate_user_id: str,
) -> dict:
    """
    Delegate permission management to a member.
    Only the owner or producer with can_manage_permissions can delegate.
    """
    delegator = await get_project_member(db, project_id, delegate_user_id)
    if not delegator:
        return {"success": False, "error": "delegator_not_found"}

    if delegator.professional_role not in ["owner", "producer"]:
        if not delegator.can_manage_permissions:
            return {"success": False, "error": "permission_denied"}

    target = await get_project_member(db, project_id, target_user_id)
    if not target:
        return {"success": False, "error": "target_not_found"}

    target.can_manage_permissions = can_manage_permissions
    await db.commit()
    await db.refresh(target)

    return {
        "success": True,
        "member_id": target.id,
        "can_manage_permissions": target.can_manage_permissions,
    }


async def get_effective_permissions(
    db: AsyncSession, project_id: str, user_id: str
) -> List[str]:
    """
    Get effective permissions for a user in a project.
    Combines role-based permissions with delegated permissions.
    """
    member = await get_project_member(db, project_id, user_id)
    if not member:
        return []

    role = member.professional_role
    role_perms = ROLE_DEFAULT_PERMISSIONS.get(role, [])

    custom_perms = member.permissions_json or []
    if isinstance(custom_perms, list):
        return list(set(role_perms + custom_perms))
    return role_perms


async def check_permission(
    db: AsyncSession, project_id: str, user_id: str, permission: str
) -> bool:
    """Check if a user has a specific permission in a project."""
    perms = await get_effective_permissions(db, project_id, user_id)
    return permission in perms


async def can_manage_project_members(
    db: AsyncSession, project_id: str, user_id: str
) -> bool:
    """Check if a user can manage project members."""
    member = await get_project_member(db, project_id, user_id)
    if not member:
        return False

    if member.professional_role in ["owner", "producer"]:
        return True

    return member.can_manage_members


async def can_delegate_permissions(
    db: AsyncSession, project_id: str, user_id: str
) -> bool:
    """Check if a user can delegate permissions."""
    member = await get_project_member(db, project_id, user_id)
    if not member:
        return False

    if member.professional_role in ["owner", "producer"]:
        return True

    return member.can_manage_permissions


async def is_project_member(
    db: AsyncSession, project_id: str, user_id: str
) -> bool:
    """Check if a user is an active member of a project."""
    member = await get_project_member(db, project_id, user_id)
    return member is not None and member.status == "active"


async def is_project_owner(
    db: AsyncSession, project_id: str, user_id: str
) -> bool:
    """Check if a user is the owner of a project."""
    member = await get_project_member(db, project_id, user_id)
    return member is not None and member.professional_role == "owner"