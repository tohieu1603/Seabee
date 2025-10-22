"""
RBAC Models: Role-Based Access Control
Complete implementation with UUID, soft delete, and relationships
"""
from django.db import models
from django.contrib.auth import get_user_model
from apps.base_models import BaseModel


User = get_user_model()


class Permission(BaseModel):
    """
    Permission model - Quyền hạn cụ thể trong hệ thống
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Permission name (e.g., 'View Users')"
    )
    codename = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique code (e.g., 'users.view')"
    )
    description = models.TextField(
        blank=True,
        help_text="Detailed description"
    )
    module = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Module (e.g., 'users', 'sales')"
    )
    action = models.CharField(
        max_length=20,
        choices=[
            ('view', 'View'),
            ('create', 'Create'),
            ('update', 'Update'),
            ('delete', 'Delete'),
            ('export', 'Export'),
            ('import', 'Import'),
            ('approve', 'Approve'),
            ('manage', 'Manage All'),
        ],
        help_text="Action type"
    )

    class Meta:
        db_table = 'rbac_permissions'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        ordering = ['module', 'action']
        indexes = [
            models.Index(fields=['module']),
            models.Index(fields=['codename']),
        ]

    def __str__(self):
        return f"{self.module}.{self.action}: {self.name}"


class Role(BaseModel):
    """
    Role model - Vai trò trong hệ thống
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Role name (e.g., 'Admin')"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        help_text="URL-friendly identifier"
    )
    description = models.TextField(
        blank=True,
        help_text="Role description"
    )
    permissions = models.ManyToManyField(
        Permission,
        through='RolePermission',
        related_name='roles',
        help_text="Assigned permissions"
    )
    is_system = models.BooleanField(
        default=False,
        help_text="System role cannot be deleted"
    )
    level = models.IntegerField(
        default=0,
        db_index=True,
        help_text="Hierarchy level (higher = more authority)"
    )
    color = models.CharField(
        max_length=7,
        default='#6366f1',
        help_text="Display color (hex)"
    )

    class Meta:
        db_table = 'rbac_roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['-level', 'name']

    def __str__(self):
        return self.name

    def has_permission(self, permission_codename: str) -> bool:
        """Check if role has specific permission"""
        return self.permissions.filter(
            codename=permission_codename,
            is_active=True
        ).exists()


class RolePermission(BaseModel):
    """
    Many-to-many relationship between Role and Permission
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='permission_roles'
    )
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="User who granted this permission"
    )

    class Meta:
        db_table = 'rbac_role_permissions'
        unique_together = [['role', 'permission']]
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'

    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class UserRole(BaseModel):
    """
    User's assigned roles
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_users'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles',
        help_text="User who assigned this role"
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Role expiration (null = never expires)"
    )

    class Meta:
        db_table = 'rbac_user_roles'
        unique_together = [['user', 'role']]
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        indexes = [
            models.Index(fields=['user', 'role']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"

    def is_expired(self) -> bool:
        """Check if role is expired"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at


class Department(BaseModel):
    """
    Department/Team model
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Department name"
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Department code"
    )
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        help_text="Parent department"
    )
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        help_text="Department manager"
    )
    default_role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Default role for members"
    )

    class Meta:
        db_table = 'departments'
        verbose_name = 'Department'
        verbose_name_plural = 'Departments'
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"
