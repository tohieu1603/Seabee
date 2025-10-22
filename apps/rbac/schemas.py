"""
RBAC Schemas - Pydantic models for request/response validation
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr


# ============================================
# Common Schemas
# ============================================

class MessageResponse(BaseModel):
    """Simple message response"""
    message: str


# ============================================
# Permission Schemas
# ============================================

class PermissionBase(BaseModel):
    name: str = Field(..., max_length=100)
    codename: str = Field(..., max_length=100)
    description: Optional[str] = None
    module: str = Field(..., max_length=50)
    action: str


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PermissionOut(PermissionBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ============================================
# Role Schemas
# ============================================

class RoleBase(BaseModel):
    name: str = Field(..., max_length=50)
    slug: str = Field(..., max_length=50)
    description: Optional[str] = None
    level: int = Field(default=0, ge=0, le=100)
    color: str = Field(default="#6366f1", max_length=7)


class RoleCreate(RoleBase):
    permission_ids: Optional[List[UUID]] = []


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    level: Optional[int] = Field(None, ge=0, le=100)
    color: Optional[str] = Field(None, max_length=7)
    is_active: Optional[bool] = None


class RoleOut(RoleBase):
    id: UUID
    is_system: bool
    created_at: datetime
    updated_at: datetime
    is_active: bool
    permission_count: Optional[int] = 0
    user_count: Optional[int] = 0

    class Config:
        from_attributes = True


class RoleWithPermissions(RoleOut):
    permissions: List[PermissionOut] = []


# ============================================
# Role Permission Assignment
# ============================================

class RolePermissionAssign(BaseModel):
    permission_ids: List[UUID] = Field(..., min_length=1)


class RolePermissionRemove(BaseModel):
    permission_ids: List[UUID] = Field(..., min_length=1)


# ============================================
# User Role Schemas
# ============================================

class UserRoleBase(BaseModel):
    user_id: UUID
    role_id: UUID
    expires_at: Optional[datetime] = None


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(BaseModel):
    expires_at: Optional[datetime] = None
    is_active: Optional[bool] = None


class UserRoleOut(BaseModel):
    id: UUID
    user_id: UUID
    role_id: UUID
    assigned_by_id: Optional[UUID] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool
    is_expired: bool = False

    class Config:
        from_attributes = True


class UserRoleWithDetails(UserRoleOut):
    user_email: Optional[str] = None
    role_name: Optional[str] = None
    role_color: Optional[str] = None
    assigned_by_email: Optional[str] = None


# ============================================
# Bulk Assignment Schemas
# ============================================

class BulkUserRoleAssign(BaseModel):
    """Assign one role to multiple users"""
    user_ids: List[UUID] = Field(..., min_length=1)
    role_id: UUID
    expires_at: Optional[datetime] = None


class BulkRoleAssign(BaseModel):
    """Assign multiple roles to one user"""
    user_id: UUID
    role_ids: List[UUID] = Field(..., min_length=1)
    expires_at: Optional[datetime] = None


class BulkUserRoleRemove(BaseModel):
    """Remove roles from users"""
    user_ids: List[UUID] = Field(..., min_length=1)
    role_ids: List[UUID] = Field(..., min_length=1)


# ============================================
# Department Schemas
# ============================================

class DepartmentBase(BaseModel):
    name: str = Field(..., max_length=100)
    code: str = Field(..., max_length=20)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    default_role_id: Optional[UUID] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    manager_id: Optional[UUID] = None
    default_role_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class DepartmentOut(DepartmentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class DepartmentWithDetails(DepartmentOut):
    parent_name: Optional[str] = None
    manager_email: Optional[str] = None
    default_role_name: Optional[str] = None
    member_count: Optional[int] = 0


# ============================================
# Statistics & Reports
# ============================================

class RoleStats(BaseModel):
    total_roles: int
    active_roles: int
    system_roles: int
    custom_roles: int


class PermissionStats(BaseModel):
    total_permissions: int
    active_permissions: int
    permissions_by_module: dict


class UserRoleStats(BaseModel):
    total_assignments: int
    active_assignments: int
    expired_assignments: int
    users_with_roles: int


class RBACDashboard(BaseModel):
    role_stats: RoleStats
    permission_stats: PermissionStats
    user_role_stats: UserRoleStats
