"""
Script đơn giản để seed RBAC data
Chạy: python manage.py shell < seed_rbac_simple.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.rbac.models import Role, Permission, RolePermission
from apps.rbac.seed_data import PERMISSIONS_TEMPLATE, ROLES_TEMPLATE

print("="*50)
print("SEED RBAC DATA")
print("="*50)

# 1. Xóa dữ liệu cũ
print("\n1. Xóa dữ liệu cũ...")
RolePermission.objects.all().delete()
Role.objects.all().delete()
Permission.objects.all().delete()
print("✓ Đã xóa")

# 2. Tạo permissions
print("\n2. Tạo Permissions...")
created_perms = 0
for perm_data in PERMISSIONS_TEMPLATE:
    permission, created = Permission.objects.get_or_create(
        codename=perm_data['codename'],
        defaults={
            'name': perm_data['name'],
            'module': perm_data['module'],
            'action': perm_data['action'],
            'description': perm_data.get('description', ''),
            'is_active': True,
        }
    )
    if created:
        created_perms += 1
        print(f"  ✓ {permission.codename}")

print(f"\n✓ Tạo {created_perms} permissions")

# 3. Tạo roles
print("\n3. Tạo Roles...")
created_roles = 0
for role_data in ROLES_TEMPLATE:
    permission_patterns = role_data.pop('permissions', [])

    role, created = Role.objects.get_or_create(
        slug=role_data['slug'],
        defaults={
            'name': role_data['name'],
            'description': role_data['description'],
            'level': role_data['level'],
            'color': role_data['color'],
            'is_system': role_data.get('is_system', False),
            'is_active': True,
        }
    )

    if created:
        created_roles += 1
        print(f"  ✓ {role.name}")

    # Gán permissions
    permissions_to_assign = []

    for pattern in permission_patterns:
        if pattern == '*':
            # All permissions
            permissions_to_assign = list(Permission.objects.filter(is_active=True))
            break
        elif pattern.endswith('.*'):
            # Module wildcard
            module = pattern[:-2]
            module_perms = Permission.objects.filter(module=module, is_active=True)
            permissions_to_assign.extend(module_perms)
        else:
            # Specific permission
            try:
                perm = Permission.objects.get(codename=pattern, is_active=True)
                permissions_to_assign.append(perm)
            except Permission.DoesNotExist:
                print(f"    ⚠ Permission not found: {pattern}")

    # Clear existing and add new
    RolePermission.objects.filter(role=role).delete()
    for permission in permissions_to_assign:
        RolePermission.objects.get_or_create(role=role, permission=permission)

    print(f"    → {len(permissions_to_assign)} permissions")

print(f"\n✓ Tạo {created_roles} roles")

# 4. Summary
print("\n" + "="*50)
print("KẾT QUẢ")
print("="*50)

roles = Role.objects.all()
permissions = Permission.objects.all()

print(f"\n📊 Thống kê:")
print(f"  • Roles: {roles.count()}")
print(f"  • Permissions: {permissions.count()}")

print(f"\n📋 Danh sách Roles:")
for role in roles.order_by('name'):
    perm_count = role.permissions.count()
    print(f"  • {role.name} ({role.slug}): {perm_count} permissions")

print(f"\n🔑 Permissions theo module:")
from django.db.models import Count
modules = Permission.objects.values('module').annotate(count=Count('id')).order_by('module')
for m in modules:
    print(f"  • {m['module']}: {m['count']} permissions")

print("\n" + "="*50)
print("✓ HOÀN THÀNH!")
print("="*50)
