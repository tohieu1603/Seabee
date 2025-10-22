"""
RBAC Services - Business logic layer
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from django.db import transaction
from django.db.models import Count, Q, Prefetch
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Permission, Role, RolePermission, UserRole, Department
from apps.users.models import User


# ============================================
# Permission Services
# ============================================

class PermissionService:
    """Service for Permission CRUD operations"""

    @staticmethod
    def list_permissions(
        module: Optional[str] = None,
        action: Optional[str] = None,
        is_active: bool = True
    ) -> List[Permission]:
        """List permissions with optional filters"""
        queryset = Permission.objects.all()

        if module:
            queryset = queryset.filter(module=module)
        if action:
            queryset = queryset.filter(action=action)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        return queryset.order_by('module', 'action')

    @staticmethod
    def get_permission(permission_id: UUID) -> Permission:
        """Get permission by ID"""
        return get_object_or_404(Permission, id=permission_id)

    @staticmethod
    def create_permission(
        name: str,
        codename: str,
        module: str,
        action: str,
        description: str = ""
    ) -> Permission:
        """Create new permission"""
        return Permission.objects.create(
            name=name,
            codename=codename,
            module=module,
            action=action,
            description=description
        )

    @staticmethod
    def update_permission(
        permission_id: UUID,
        **kwargs
    ) -> Permission:
        """Update permission"""
        permission = PermissionService.get_permission(permission_id)

        for key, value in kwargs.items():
            if value is not None and hasattr(permission, key):
                setattr(permission, key, value)

        permission.save()
        return permission

    @staticmethod
    def delete_permission(permission_id: UUID, hard_delete: bool = False):
        """Soft or hard delete permission"""
        permission = PermissionService.get_permission(permission_id)

        if hard_delete:
            permission.delete()
        else:
            permission.soft_delete()

    @staticmethod
    def get_modules() -> List[str]:
        """Get list of unique modules"""
        return list(
            Permission.objects.filter(is_active=True)
            .values_list('module', flat=True)
            .distinct()
            .order_by('module')
        )


# ============================================
# Role Services
# ============================================

class RoleService:
    """Service for Role CRUD operations"""

    @staticmethod
    def list_roles(
        is_active: bool = True,
        include_counts: bool = False
    ) -> List[Role]:
        """List roles with optional counts"""
        queryset = Role.objects.all()

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        if include_counts:
            queryset = queryset.annotate(
                permission_count=Count('permissions', filter=Q(permissions__is_active=True)),
                user_count=Count('role_users', filter=Q(role_users__is_active=True))
            )

        return queryset.order_by('-level', 'name')

    @staticmethod
    def get_role(role_id: UUID, with_permissions: bool = False) -> Role:
        """Get role by ID"""
        queryset = Role.objects.all()

        if with_permissions:
            queryset = queryset.prefetch_related(
                Prefetch(
                    'permissions',
                    queryset=Permission.objects.filter(is_active=True)
                )
            )

        return get_object_or_404(queryset, id=role_id)

    @staticmethod
    def get_role_by_slug(slug: str) -> Role:
        """Get role by slug"""
        return get_object_or_404(Role, slug=slug)

    @staticmethod
    @transaction.atomic
    def create_role(
        name: str,
        slug: str,
        description: str = "",
        level: int = 0,
        color: str = "#6366f1",
        permission_ids: List[UUID] = None
    ) -> Role:
        """Create new role with permissions"""
        role = Role.objects.create(
            name=name,
            slug=slug,
            description=description,
            level=level,
            color=color
        )

        if permission_ids:
            RoleService.assign_permissions(role.id, permission_ids)

        return role

    @staticmethod
    def update_role(role_id: UUID, **kwargs) -> Role:
        """Update role"""
        role = RoleService.get_role(role_id)

        # Prevent modification of system roles
        if role.is_system and 'is_active' in kwargs:
            raise ValueError("Cannot modify system role active status")

        for key, value in kwargs.items():
            if value is not None and hasattr(role, key):
                setattr(role, key, value)

        role.save()
        return role

    @staticmethod
    def delete_role(role_id: UUID, hard_delete: bool = False):
        """Soft or hard delete role"""
        role = RoleService.get_role(role_id)

        if role.is_system:
            raise ValueError("Cannot delete system role")

        if hard_delete:
            role.delete()
        else:
            role.soft_delete()

    @staticmethod
    @transaction.atomic
    def assign_permissions(
        role_id: UUID,
        permission_ids: List[UUID],
        granted_by_id: Optional[UUID] = None
    ):
        """Assign permissions to role"""
        role = RoleService.get_role(role_id)

        # Get valid permissions
        permissions = Permission.objects.filter(
            id__in=permission_ids,
            is_active=True
        )

        # Create role-permission relationships
        for permission in permissions:
            RolePermission.objects.get_or_create(
                role=role,
                permission=permission,
                defaults={'granted_by_id': granted_by_id}
            )

    @staticmethod
    @transaction.atomic
    def remove_permissions(role_id: UUID, permission_ids: List[UUID]):
        """Remove permissions from role"""
        role = RoleService.get_role(role_id)

        RolePermission.objects.filter(
            role=role,
            permission_id__in=permission_ids
        ).delete()

    @staticmethod
    def get_role_permissions(role_id: UUID) -> List[Permission]:
        """Get all permissions for a role"""
        role = RoleService.get_role(role_id, with_permissions=True)
        return list(role.permissions.filter(is_active=True))


# ============================================
# User Role Services
# ============================================

class UserRoleService:
    """Service for UserRole assignment operations"""

    @staticmethod
    def list_user_roles(
        user_id: Optional[UUID] = None,
        role_id: Optional[UUID] = None,
        is_active: bool = True,
        include_expired: bool = False
    ):
        """List user role assignments"""
        queryset = UserRole.objects.select_related('user', 'role', 'assigned_by')

        if user_id:
            queryset = queryset.filter(user_id=user_id)
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        if not include_expired:
            now = timezone.now()
            queryset = queryset.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=now)
            )

        return queryset.order_by('-created_at')

    @staticmethod
    def get_user_role(user_role_id: UUID) -> UserRole:
        """Get user role assignment by ID"""
        return get_object_or_404(UserRole, id=user_role_id)

    @staticmethod
    @transaction.atomic
    def assign_role(
        user_id: UUID,
        role_id: UUID,
        assigned_by_id: Optional[UUID] = None,
        expires_at: Optional[datetime] = None
    ) -> UserRole:
        """Assign role to user"""
        # Verify user and role exist
        user = get_object_or_404(User, id=user_id)
        role = get_object_or_404(Role, id=role_id, is_active=True)

        # Create or update assignment
        user_role, created = UserRole.objects.update_or_create(
            user=user,
            role=role,
            defaults={
                'assigned_by_id': assigned_by_id,
                'expires_at': expires_at,
                'is_active': True
            }
        )

        return user_role

    @staticmethod
    @transaction.atomic
    def bulk_assign_users(
        user_ids: List[UUID],
        role_id: UUID,
        assigned_by_id: Optional[UUID] = None,
        expires_at: Optional[datetime] = None
    ) -> List[UserRole]:
        """Assign one role to multiple users"""
        role = get_object_or_404(Role, id=role_id, is_active=True)
        users = User.objects.filter(id__in=user_ids, is_active=True)

        user_roles = []
        for user in users:
            user_role, _ = UserRole.objects.update_or_create(
                user=user,
                role=role,
                defaults={
                    'assigned_by_id': assigned_by_id,
                    'expires_at': expires_at,
                    'is_active': True
                }
            )
            user_roles.append(user_role)

        return user_roles

    @staticmethod
    @transaction.atomic
    def bulk_assign_roles(
        user_id: UUID,
        role_ids: List[UUID],
        assigned_by_id: Optional[UUID] = None,
        expires_at: Optional[datetime] = None
    ) -> List[UserRole]:
        """Assign multiple roles to one user"""
        user = get_object_or_404(User, id=user_id, is_active=True)
        roles = Role.objects.filter(id__in=role_ids, is_active=True)

        user_roles = []
        for role in roles:
            user_role, _ = UserRole.objects.update_or_create(
                user=user,
                role=role,
                defaults={
                    'assigned_by_id': assigned_by_id,
                    'expires_at': expires_at,
                    'is_active': True
                }
            )
            user_roles.append(user_role)

        return user_roles

    @staticmethod
    @transaction.atomic
    def remove_role(user_id: UUID, role_id: UUID, hard_delete: bool = False):
        """Remove role from user"""
        user_role = get_object_or_404(
            UserRole,
            user_id=user_id,
            role_id=role_id
        )

        if hard_delete:
            user_role.delete()
        else:
            user_role.soft_delete()

    @staticmethod
    @transaction.atomic
    def bulk_remove_roles(
        user_ids: List[UUID],
        role_ids: List[UUID],
        hard_delete: bool = False
    ):
        """Remove roles from multiple users"""
        user_roles = UserRole.objects.filter(
            user_id__in=user_ids,
            role_id__in=role_ids
        )

        if hard_delete:
            user_roles.delete()
        else:
            user_roles.update(is_active=False, updated_at=timezone.now())

    @staticmethod
    def update_user_role(
        user_role_id: UUID,
        **kwargs
    ) -> UserRole:
        """Update user role assignment"""
        user_role = UserRoleService.get_user_role(user_role_id)

        for key, value in kwargs.items():
            if hasattr(user_role, key):
                setattr(user_role, key, value)

        user_role.save()
        return user_role

    @staticmethod
    def get_user_permissions(user_id: UUID) -> List[Permission]:
        """Get all permissions for a user through their roles"""
        return Permission.objects.filter(
            roles__role_users__user_id=user_id,
            roles__role_users__is_active=True,
            roles__is_active=True,
            is_active=True
        ).distinct()


# ============================================
# Department Services
# ============================================

class DepartmentService:
    """Service for Department CRUD operations"""

    @staticmethod
    def list_departments(
        parent_id: Optional[UUID] = None,
        is_active: bool = True
    ) -> List[Department]:
        """List departments"""
        queryset = Department.objects.select_related(
            'parent', 'manager', 'default_role'
        )

        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)

        return queryset.order_by('code')

    @staticmethod
    def get_department(department_id: UUID) -> Department:
        """Get department by ID"""
        return get_object_or_404(
            Department.objects.select_related('parent', 'manager', 'default_role'),
            id=department_id
        )

    @staticmethod
    def create_department(
        name: str,
        code: str,
        description: str = "",
        parent_id: Optional[UUID] = None,
        manager_id: Optional[UUID] = None,
        default_role_id: Optional[UUID] = None
    ) -> Department:
        """Create new department"""
        return Department.objects.create(
            name=name,
            code=code,
            description=description,
            parent_id=parent_id,
            manager_id=manager_id,
            default_role_id=default_role_id
        )

    @staticmethod
    def update_department(department_id: UUID, **kwargs) -> Department:
        """Update department"""
        department = DepartmentService.get_department(department_id)

        for key, value in kwargs.items():
            if hasattr(department, key):
                setattr(department, key, value)

        department.save()
        return department

    @staticmethod
    def delete_department(department_id: UUID, hard_delete: bool = False):
        """Soft or hard delete department"""
        department = DepartmentService.get_department(department_id)

        if hard_delete:
            department.delete()
        else:
            department.soft_delete()
