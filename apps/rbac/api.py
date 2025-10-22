"""
RBAC API Endpoints - Complete CRUD operations
"""
from typing import List, Optional
from uuid import UUID
from ninja import Router
from django.db.models import Count, Q

from .models import Permission, Role, UserRole, Department
from .schemas import (
    PermissionCreate, PermissionUpdate, PermissionOut,
    RoleCreate, RoleUpdate, RoleOut, RoleWithPermissions,
    RolePermissionAssign, RolePermissionRemove,
    UserRoleCreate, UserRoleUpdate, UserRoleOut, UserRoleWithDetails,
    BulkUserRoleAssign, BulkRoleAssign, BulkUserRoleRemove,
    DepartmentCreate, DepartmentUpdate, DepartmentOut, DepartmentWithDetails,
    RoleStats, PermissionStats, UserRoleStats, RBACDashboard,
)
from .services import (
    PermissionService,
    RoleService,
    UserRoleService,
    DepartmentService,
)
from .permissions import require_permission, require_any_permission


router = Router(tags=["RBAC"])


# ============================================
# PERMISSION ENDPOINTS
# ============================================

@router.get("/permissions", response=List[PermissionOut])
def list_permissions(
    request,
    module: Optional[str] = None,
    action: Optional[str] = None,
    is_active: Optional[bool] = True,
):
    """List all permissions with optional filters"""
    permissions = PermissionService.list_permissions(
        module=module,
        action=action,
        is_active=is_active
    )
    return list(permissions)


@router.get("/permissions/modules", response=List[str])
def list_permission_modules(request):
    """Get list of unique modules"""
    return PermissionService.get_modules()


@router.get("/permissions/{permission_id}", response=PermissionOut)
def get_permission(request, permission_id: UUID):
    """Get permission by ID"""
    return PermissionService.get_permission(permission_id)


@router.post("/permissions", response=PermissionOut)
def create_permission(request, payload: PermissionCreate):
    """Create new permission"""
    return PermissionService.create_permission(
        name=payload.name,
        codename=payload.codename,
        module=payload.module,
        action=payload.action,
        description=payload.description or ""
    )


@router.put("/permissions/{permission_id}", response=PermissionOut)
def update_permission(request, permission_id: UUID, payload: PermissionUpdate):
    """Update permission"""
    update_data = payload.dict(exclude_unset=True)
    return PermissionService.update_permission(permission_id, **update_data)


@router.delete("/permissions/{permission_id}")
def delete_permission(request, permission_id: UUID, hard_delete: bool = False):
    """Delete permission (soft delete by default)"""
    PermissionService.delete_permission(permission_id, hard_delete=hard_delete)
    return {"message": "Permission deleted successfully"}


# ============================================
# ROLE ENDPOINTS
# ============================================

@router.get("/roles", response=List[RoleOut])
def list_roles(request, is_active: Optional[bool] = True):
    """List all roles with permission and user counts"""
    roles = RoleService.list_roles(is_active=is_active, include_counts=True)

    roles_data = []
    for role in roles:
        role_dict = {
            "id": role.id,
            "name": role.name,
            "slug": role.slug,
            "description": role.description,
            "level": role.level,
            "color": role.color,
            "is_system": role.is_system,
            "created_at": role.created_at,
            "updated_at": role.updated_at,
            "is_active": role.is_active,
            "permission_count": getattr(role, 'permission_count', 0),
            "user_count": getattr(role, 'user_count', 0),
        }
        roles_data.append(role_dict)

    return roles_data


@router.get("/roles/{role_id}", response=RoleWithPermissions)
def get_role(request, role_id: UUID):
    """Get role by ID with permissions"""
    role = RoleService.get_role(role_id, with_permissions=True)

    return {
        "id": role.id,
        "name": role.name,
        "slug": role.slug,
        "description": role.description,
        "level": role.level,
        "color": role.color,
        "is_system": role.is_system,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
        "is_active": role.is_active,
        "permission_count": role.permissions.count(),
        "user_count": role.role_users.filter(is_active=True).count(),
        "permissions": list(role.permissions.filter(is_active=True))
    }


@router.post("/roles", response=RoleOut)
def create_role(request, payload: RoleCreate):
    """Create new role with permissions"""
    role = RoleService.create_role(
        name=payload.name,
        slug=payload.slug,
        description=payload.description or "",
        level=payload.level,
        color=payload.color,
        permission_ids=payload.permission_ids or []
    )

    return {
        "id": role.id,
        "name": role.name,
        "slug": role.slug,
        "description": role.description,
        "level": role.level,
        "color": role.color,
        "is_system": role.is_system,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
        "is_active": role.is_active,
        "permission_count": 0,
        "user_count": 0,
    }


@router.put("/roles/{role_id}", response=RoleOut)
def update_role(request, role_id: UUID, payload: RoleUpdate):
    """Update role"""
    update_data = payload.dict(exclude_unset=True)
    role = RoleService.update_role(role_id, **update_data)

    return {
        "id": role.id,
        "name": role.name,
        "slug": role.slug,
        "description": role.description,
        "level": role.level,
        "color": role.color,
        "is_system": role.is_system,
        "created_at": role.created_at,
        "updated_at": role.updated_at,
        "is_active": role.is_active,
        "permission_count": role.permissions.filter(is_active=True).count(),
        "user_count": role.role_users.filter(is_active=True).count(),
    }


@router.delete("/roles/{role_id}")
def delete_role(request, role_id: UUID, hard_delete: bool = False):
    """Delete role (soft delete by default)"""
    RoleService.delete_role(role_id, hard_delete=hard_delete)
    return {"message": "Role deleted successfully"}


@router.put("/roles/{role_id}/permissions")
def assign_permissions_to_role(request, role_id: UUID, payload: RolePermissionAssign):
    """Assign permissions to role"""
    RoleService.assign_permissions(
        role_id=role_id,
        permission_ids=payload.permission_ids,
        granted_by_id=request.user.id if hasattr(request, 'user') else None
    )
    return {"message": f"Assigned {len(payload.permission_ids)} permissions to role"}


@router.delete("/roles/{role_id}/permissions")
def remove_permissions_from_role(request, role_id: UUID, payload: RolePermissionRemove):
    """Remove permissions from role"""
    RoleService.remove_permissions(role_id, payload.permission_ids)
    return {"message": f"Removed {len(payload.permission_ids)} permissions from role"}


@router.get("/roles/{role_id}/permissions", response=List[PermissionOut])
def get_role_permissions(request, role_id: UUID):
    """Get all permissions for a role"""
    permissions = RoleService.get_role_permissions(role_id)
    return list(permissions)


# ============================================
# USER ROLE ENDPOINTS
# ============================================

@router.get("/user-roles", response=List[UserRoleWithDetails])
def list_user_roles(
    request,
    user_id: Optional[UUID] = None,
    role_id: Optional[UUID] = None,
    is_active: Optional[bool] = True,
    include_expired: bool = False,
):
    """List user role assignments"""
    user_roles = UserRoleService.list_user_roles(
        user_id=user_id,
        role_id=role_id,
        is_active=is_active,
        include_expired=include_expired
    )

    user_roles_data = []
    for ur in user_roles:
        user_roles_data.append({
            "id": ur.id,
            "user_id": ur.user_id,
            "role_id": ur.role_id,
            "assigned_by_id": ur.assigned_by_id,
            "expires_at": ur.expires_at,
            "created_at": ur.created_at,
            "updated_at": ur.updated_at,
            "is_active": ur.is_active,
            "is_expired": ur.is_expired(),
            "user_email": ur.user.email if ur.user else None,
            "role_name": ur.role.name if ur.role else None,
            "role_color": ur.role.color if ur.role else None,
            "assigned_by_email": ur.assigned_by.email if ur.assigned_by else None,
        })

    return user_roles_data


@router.get("/user-roles/{user_role_id}", response=UserRoleWithDetails)
def get_user_role(request, user_role_id: UUID):
    """Get user role assignment by ID"""
    ur = UserRoleService.get_user_role(user_role_id)

    return {
        "id": ur.id,
        "user_id": ur.user_id,
        "role_id": ur.role_id,
        "assigned_by_id": ur.assigned_by_id,
        "expires_at": ur.expires_at,
        "created_at": ur.created_at,
        "updated_at": ur.updated_at,
        "is_active": ur.is_active,
        "is_expired": ur.is_expired(),
        "user_email": ur.user.email if ur.user else None,
        "role_name": ur.role.name if ur.role else None,
        "role_color": ur.role.color if ur.role else None,
        "assigned_by_email": ur.assigned_by.email if ur.assigned_by else None,
    }


@router.post("/user-roles", response=UserRoleOut)
def assign_role_to_user(request, payload: UserRoleCreate):
    """Assign role to user"""
    user_role = UserRoleService.assign_role(
        user_id=payload.user_id,
        role_id=payload.role_id,
        assigned_by_id=request.user.id if hasattr(request, 'user') else None,
        expires_at=payload.expires_at
    )

    return {
        "id": user_role.id,
        "user_id": user_role.user_id,
        "role_id": user_role.role_id,
        "assigned_by_id": user_role.assigned_by_id,
        "expires_at": user_role.expires_at,
        "created_at": user_role.created_at,
        "updated_at": user_role.updated_at,
        "is_active": user_role.is_active,
        "is_expired": user_role.is_expired(),
    }


@router.post("/user-roles/bulk-assign-users")
def bulk_assign_role_to_users(request, payload: BulkUserRoleAssign):
    """Assign one role to multiple users"""
    user_roles = UserRoleService.bulk_assign_users(
        user_ids=payload.user_ids,
        role_id=payload.role_id,
        assigned_by_id=request.user.id if hasattr(request, 'user') else None,
        expires_at=payload.expires_at
    )

    return {
        "message": f"Assigned role to {len(user_roles)} users",
        "count": len(user_roles)
    }


@router.post("/user-roles/bulk-assign-roles")
def bulk_assign_roles_to_user(request, payload: BulkRoleAssign):
    """Assign multiple roles to one user"""
    user_roles = UserRoleService.bulk_assign_roles(
        user_id=payload.user_id,
        role_ids=payload.role_ids,
        assigned_by_id=request.user.id if hasattr(request, 'user') else None,
        expires_at=payload.expires_at
    )

    return {
        "message": f"Assigned {len(user_roles)} roles to user",
        "count": len(user_roles)
    }


@router.delete("/user-roles/{user_role_id}")
def remove_user_role(request, user_role_id: UUID, hard_delete: bool = False):
    """Remove role from user"""
    user_role = UserRoleService.get_user_role(user_role_id)

    if hard_delete:
        user_role.delete()
    else:
        user_role.soft_delete()

    return {"message": "Role removed from user successfully"}


@router.post("/user-roles/bulk-remove")
def bulk_remove_user_roles(request, payload: BulkUserRoleRemove):
    """Remove roles from multiple users"""
    UserRoleService.bulk_remove_roles(
        user_ids=payload.user_ids,
        role_ids=payload.role_ids,
        hard_delete=False
    )

    return {
        "message": "Roles removed from users successfully",
        "user_count": len(payload.user_ids),
        "role_count": len(payload.role_ids)
    }


@router.put("/user-roles/{user_role_id}", response=UserRoleOut)
def update_user_role(request, user_role_id: UUID, payload: UserRoleUpdate):
    """Update user role assignment"""
    update_data = payload.dict(exclude_unset=True)
    user_role = UserRoleService.update_user_role(user_role_id, **update_data)

    return {
        "id": user_role.id,
        "user_id": user_role.user_id,
        "role_id": user_role.role_id,
        "assigned_by_id": user_role.assigned_by_id,
        "expires_at": user_role.expires_at,
        "created_at": user_role.created_at,
        "updated_at": user_role.updated_at,
        "is_active": user_role.is_active,
        "is_expired": user_role.is_expired(),
    }


# ============================================
# DEPARTMENT ENDPOINTS
# ============================================

@router.get("/departments", response=List[DepartmentOut])
def list_departments(
    request,
    parent_id: Optional[UUID] = None,
    is_active: Optional[bool] = True
):
    """List all departments"""
    departments = DepartmentService.list_departments(
        parent_id=parent_id,
        is_active=is_active
    )
    return list(departments)


@router.get("/departments/{department_id}", response=DepartmentWithDetails)
def get_department(request, department_id: UUID):
    """Get department by ID"""
    dept = DepartmentService.get_department(department_id)

    from apps.users.models import User
    member_count = User.objects.filter(
        department=dept,
        is_active=True
    ).count()

    return {
        "id": dept.id,
        "name": dept.name,
        "code": dept.code,
        "description": dept.description,
        "parent_id": dept.parent_id,
        "manager_id": dept.manager_id,
        "default_role_id": dept.default_role_id,
        "created_at": dept.created_at,
        "updated_at": dept.updated_at,
        "is_active": dept.is_active,
        "parent_name": dept.parent.name if dept.parent else None,
        "manager_email": dept.manager.email if dept.manager else None,
        "default_role_name": dept.default_role.name if dept.default_role else None,
        "member_count": member_count,
    }


@router.post("/departments", response=DepartmentOut)
def create_department(request, payload: DepartmentCreate):
    """Create new department"""
    return DepartmentService.create_department(
        name=payload.name,
        code=payload.code,
        description=payload.description or "",
        parent_id=payload.parent_id,
        manager_id=payload.manager_id,
        default_role_id=payload.default_role_id
    )


@router.put("/departments/{department_id}", response=DepartmentOut)
def update_department(request, department_id: UUID, payload: DepartmentUpdate):
    """Update department"""
    update_data = payload.dict(exclude_unset=True)
    return DepartmentService.update_department(department_id, **update_data)


@router.delete("/departments/{department_id}")
def delete_department(request, department_id: UUID, hard_delete: bool = False):
    """Delete department (soft delete by default)"""
    DepartmentService.delete_department(department_id, hard_delete=hard_delete)
    return {"message": "Department deleted successfully"}


# ============================================
# STATISTICS & DASHBOARD
# ============================================

@router.get("/stats/roles", response=RoleStats)
def get_role_stats(request):
    """Get role statistics"""
    total_roles = Role.objects.count()
    active_roles = Role.objects.filter(is_active=True).count()
    system_roles = Role.objects.filter(is_system=True, is_active=True).count()

    return {
        "total_roles": total_roles,
        "active_roles": active_roles,
        "system_roles": system_roles,
        "custom_roles": active_roles - system_roles,
    }


@router.get("/stats/permissions", response=PermissionStats)
def get_permission_stats(request):
    """Get permission statistics"""
    total = Permission.objects.count()
    active = Permission.objects.filter(is_active=True).count()

    by_module = {}
    modules = Permission.objects.filter(is_active=True).values('module').annotate(
        count=Count('id')
    )
    for m in modules:
        by_module[m['module']] = m['count']

    return {
        "total_permissions": total,
        "active_permissions": active,
        "permissions_by_module": by_module,
    }


@router.get("/stats/user-roles", response=UserRoleStats)
def get_user_role_stats(request):
    """Get user role assignment statistics"""
    from django.utils import timezone

    total = UserRole.objects.count()
    active = UserRole.objects.filter(is_active=True).count()

    now = timezone.now()
    expired = UserRole.objects.filter(
        expires_at__isnull=False,
        expires_at__lte=now
    ).count()

    users_with_roles = UserRole.objects.filter(
        is_active=True
    ).values('user_id').distinct().count()

    return {
        "total_assignments": total,
        "active_assignments": active,
        "expired_assignments": expired,
        "users_with_roles": users_with_roles,
    }


@router.get("/dashboard", response=RBACDashboard)
def get_rbac_dashboard(request):
    """Get complete RBAC dashboard statistics"""
    return {
        "role_stats": get_role_stats(request),
        "permission_stats": get_permission_stats(request),
        "user_role_stats": get_user_role_stats(request),
    }
