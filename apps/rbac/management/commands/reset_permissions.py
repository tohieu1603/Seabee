"""
Reset and re-seed all permissions and roles
This will delete ALL existing permissions, roles, and user-role assignments
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from apps.rbac.models import Permission, Role, UserRole
from django.db import transaction


class Command(BaseCommand):
    help = 'Reset all permissions and roles, then re-seed fresh data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--yes',
            action='store_true',
            help='Skip confirmation prompt',
        )

    def handle(self, *args, **options):
        # Ask for confirmation
        if not options['yes']:
            self.stdout.write(
                self.style.WARNING(
                    '\n⚠️  WARNING: This will DELETE ALL existing permissions, roles, and user-role assignments!\n'
                )
            )
            confirm = input('Are you sure you want to continue? Type "yes" to confirm: ')
            if confirm.lower() != 'yes':
                self.stdout.write(self.style.ERROR('Aborted.'))
                return

        with transaction.atomic():
            self.stdout.write(self.style.WARNING('\n🗑️  Deleting existing RBAC data...'))

            # Delete in correct order (respecting foreign keys)
            user_role_count = UserRole.objects.count()
            UserRole.objects.all().delete()
            self.stdout.write(f'  ✓ Deleted {user_role_count} user-role assignments')

            role_count = Role.objects.count()
            Role.objects.all().delete()
            self.stdout.write(f'  ✓ Deleted {role_count} roles')

            permission_count = Permission.objects.count()
            Permission.objects.all().delete()
            self.stdout.write(f'  ✓ Deleted {permission_count} permissions')

            self.stdout.write(self.style.SUCCESS('\n✓ All RBAC data cleared successfully!'))

        # Now run the seed command
        self.stdout.write(self.style.WARNING('\n🌱 Starting fresh seed...\n'))
        call_command('seed_complete_permissions')

        self.stdout.write(
            self.style.SUCCESS(
                '\n✅ Reset and re-seed completed successfully!\n'
            )
        )
