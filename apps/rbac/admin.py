"""
Django Admin configuration for RBAC models
"""
from django.contrib import admin
from .models import Permission, Role, RolePermission, UserRole, Department


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('codename', 'name', 'module', 'action', 'is_active', 'created_at')
    list_filter = ('module', 'action', 'is_active')
    search_fields = ('name', 'codename', 'module')
    ordering = ('module', 'action', 'name')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'level', 'is_system', 'is_active', 'created_at')
    list_filter = ('is_system', 'is_active', 'level')
    search_fields = ('name', 'slug', 'description')
    ordering = ('-level', 'name')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'permission', 'granted_by', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('role__name', 'permission__name')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'assigned_by', 'expires_at', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'expires_at', 'created_at')
    search_fields = ('user__email', 'role__name')
    readonly_fields = ('id', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'manager', 'default_role', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'code', 'description')
    ordering = ('code',)
    readonly_fields = ('id', 'created_at', 'updated_at')
