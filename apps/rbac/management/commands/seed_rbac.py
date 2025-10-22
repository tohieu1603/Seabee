"""
Management command to seed RBAC data (Roles, Permissions, Departments)
Usage: python manage.py seed_rbac
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.rbac.models import Permission, Role, RolePermission, Department
from apps.rbac.seed_data import (
    PERMISSIONS_TEMPLATE,
    ROLES_TEMPLATE,
    DEPARTMENTS_TEMPLATE
)


class Command(BaseCommand):
    help = 'Seed RBAC system with roles, permissions, and departments'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-permissions',
            action='store_true',
            help='Skip creating permissions',
        )
        parser.add_argument(
            '--skip-roles',
            action='store_true',
            help='Skip creating roles',
        )
        parser.add_argument(
            '--skip-departments',
            action='store_true',
            help='Skip creating departments',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        skip_permissions = options.get('skip_permissions', False)
        skip_roles = options.get('skip_roles', False)
        skip_departments = options.get('skip_departments', False)
        reset = options.get('reset', False)

        if reset:
            self.stdout.write(self.style.WARNING('Resetting RBAC data...'))
            RolePermission.objects.all().delete()
            Role.objects.all().delete()
            Permission.objects.all().delete()
            Department.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Reset complete'))

        # ====================
        # Seed Permissions
        # ====================
        if not skip_permissions:
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.HTTP_INFO('Seeding Permissions...'))
            self.stdout.write('='*50)

            created_count = 0
            updated_count = 0

            for perm_data in PERMISSIONS_TEMPLATE:
                perm, created = Permission.objects.update_or_create(
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
                    created_count += 1
                    self.stdout.write(
                        f"  ✓ Created: {perm.codename} ({perm.module}.{perm.action})"
                    )
                else:
                    updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Permissions: {created_count} created, {updated_count} updated'
                )
            )

        # ====================
        # Seed Roles
        # ====================
        if not skip_roles:
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.HTTP_INFO('Seeding Roles...'))
            self.stdout.write('='*50)

            created_count = 0
            updated_count = 0

            for role_data in ROLES_TEMPLATE:
                # Extract permission patterns
                permission_patterns = role_data.pop('permissions', [])

                # Create or update role
                role, created = Role.objects.update_or_create(
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
                    created_count += 1
                    self.stdout.write(
                        f"  ✓ Created: {role.name} (level {role.level})"
                    )
                else:
                    updated_count += 1

                # Assign permissions
                if permission_patterns:
                    self._assign_permissions_to_role(role, permission_patterns)

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Roles: {created_count} created, {updated_count} updated'
                )
            )

        # ====================
        # Seed Departments
        # ====================
        if not skip_departments:
            self.stdout.write('\n' + '='*50)
            self.stdout.write(self.style.HTTP_INFO('Seeding Departments...'))
            self.stdout.write('='*50)

            created_count = 0
            updated_count = 0

            for dept_data in DEPARTMENTS_TEMPLATE:
                dept, created = Department.objects.update_or_create(
                    code=dept_data['code'],
                    defaults={
                        'name': dept_data['name'],
                        'description': dept_data.get('description', ''),
                        'is_active': True,
                    }
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        f"  ✓ Created: {dept.code} - {dept.name}"
                    )
                else:
                    updated_count += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Departments: {created_count} created, {updated_count} updated'
                )
            )

        # ====================
        # Summary
        # ====================
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('RBAC Seeding Complete!'))
        self.stdout.write('='*50)

        total_permissions = Permission.objects.filter(is_active=True).count()
        total_roles = Role.objects.filter(is_active=True).count()
        total_departments = Department.objects.filter(is_active=True).count()

        self.stdout.write(f"\nTotal Active Records:")
        self.stdout.write(f"  • Permissions: {total_permissions}")
        self.stdout.write(f"  • Roles: {total_roles}")
        self.stdout.write(f"  • Departments: {total_departments}")
        self.stdout.write("")

    def _assign_permissions_to_role(self, role, permission_patterns):
        """
        Assign permissions to role based on patterns
        Supports wildcards like 'users.*' or specific permissions like 'users.view'
        """
        permissions_to_assign = []

        for pattern in permission_patterns:
            if pattern == '*':
                # All permissions
                permissions_to_assign = list(Permission.objects.filter(is_active=True))
                break
            elif pattern.endswith('.*'):
                # Module wildcard (e.g., 'users.*')
                module = pattern[:-2]
                module_perms = Permission.objects.filter(
                    module=module,
                    is_active=True
                )
                permissions_to_assign.extend(module_perms)
            else:
                # Specific permission
                try:
                    perm = Permission.objects.get(codename=pattern, is_active=True)
                    permissions_to_assign.append(perm)
                except Permission.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(
                            f"  ⚠ Permission not found: {pattern}"
                        )
                    )

        # Assign permissions
        for permission in permissions_to_assign:
            RolePermission.objects.get_or_create(
                role=role,
                permission=permission
            )

        if permissions_to_assign:
            self.stdout.write(
                f"    → Assigned {len(permissions_to_assign)} permissions"
            )
