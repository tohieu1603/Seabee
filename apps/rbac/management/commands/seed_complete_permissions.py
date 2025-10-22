"""
Seed comprehensive permissions for the entire system
Based on actual pages and features currently in use
"""
from django.core.management.base import BaseCommand
from apps.rbac.models import Permission, Role
from django.db import transaction


class Command(BaseCommand):
    help = 'Seed comprehensive permissions and default roles for complete system'

    def handle(self, *args, **kwargs):
        with transaction.atomic():
            self.stdout.write(self.style.WARNING('Starting permission seeding...'))

            # Define all permissions
            PERMISSIONS = [
                # ==========================================
                # DASHBOARD MODULE
                # ==========================================
                {
                    'module': 'dashboard',
                    'name': 'Xem Dashboard Tổng quan',
                    'codename': 'view_dashboard',
                    'action': 'read',
                    'description': 'Xem trang dashboard tổng quan với biểu đồ'
                },
                {
                    'module': 'dashboard',
                    'name': 'Xem Dashboard Hải sản',
                    'codename': 'view_seafood_dashboard',
                    'action': 'read',
                    'description': 'Xem dashboard hải sản chi tiết'
                },

                # ==========================================
                # SEAFOOD PRODUCTS MODULE
                # ==========================================
                {
                    'module': 'seafood',
                    'name': 'Xem danh sách sản phẩm',
                    'codename': 'view_products',
                    'action': 'list',
                    'description': 'Xem danh sách sản phẩm hải sản'
                },
                {
                    'module': 'seafood',
                    'name': 'Tạo sản phẩm mới',
                    'codename': 'create_product',
                    'action': 'create',
                    'description': 'Thêm sản phẩm hải sản mới'
                },
                {
                    'module': 'seafood',
                    'name': 'Sửa sản phẩm',
                    'codename': 'update_product',
                    'action': 'update',
                    'description': 'Chỉnh sửa thông tin sản phẩm'
                },
                {
                    'module': 'seafood',
                    'name': 'Xóa sản phẩm',
                    'codename': 'delete_product',
                    'action': 'delete',
                    'description': 'Xóa sản phẩm khỏi hệ thống'
                },
                {
                    'module': 'seafood',
                    'name': 'Xem chi tiết sản phẩm',
                    'codename': 'view_product_detail',
                    'action': 'read',
                    'description': 'Xem thông tin chi tiết sản phẩm'
                },

                # ==========================================
                # ORDERS MODULE
                # ==========================================
                {
                    'module': 'orders',
                    'name': 'Xem danh sách đơn hàng',
                    'codename': 'view_orders',
                    'action': 'list',
                    'description': 'Xem danh sách tất cả đơn hàng'
                },
                {
                    'module': 'orders',
                    'name': 'Tạo đơn hàng',
                    'codename': 'create_order',
                    'action': 'create',
                    'description': 'Tạo đơn hàng mới (POS)'
                },
                {
                    'module': 'orders',
                    'name': 'Xem chi tiết đơn hàng',
                    'codename': 'view_order_detail',
                    'action': 'read',
                    'description': 'Xem thông tin chi tiết đơn hàng'
                },
                {
                    'module': 'orders',
                    'name': 'Cập nhật đơn hàng',
                    'codename': 'update_order',
                    'action': 'update',
                    'description': 'Cập nhật trạng thái, thông tin đơn hàng'
                },
                {
                    'module': 'orders',
                    'name': 'Hủy đơn hàng',
                    'codename': 'cancel_order',
                    'action': 'delete',
                    'description': 'Hủy đơn hàng'
                },

                # ==========================================
                # POS MODULE
                # ==========================================
                {
                    'module': 'pos',
                    'name': 'Truy cập POS',
                    'codename': 'access_pos',
                    'action': 'manage',
                    'description': 'Truy cập trang POS bán hàng'
                },
                {
                    'module': 'pos',
                    'name': 'Tạo đơn POS',
                    'codename': 'create_pos_order',
                    'action': 'create',
                    'description': 'Tạo đơn hàng từ POS'
                },
                {
                    'module': 'pos',
                    'name': 'Áp dụng giảm giá',
                    'codename': 'apply_discount',
                    'action': 'update',
                    'description': 'Áp dụng giảm giá cho đơn hàng'
                },

                # ==========================================
                # CATEGORIES MODULE
                # ==========================================
                {
                    'module': 'categories',
                    'name': 'Xem danh mục',
                    'codename': 'view_categories',
                    'action': 'list',
                    'description': 'Xem danh sách danh mục sản phẩm'
                },
                {
                    'module': 'categories',
                    'name': 'Tạo danh mục',
                    'codename': 'create_category',
                    'action': 'create',
                    'description': 'Tạo danh mục mới'
                },
                {
                    'module': 'categories',
                    'name': 'Sửa danh mục',
                    'codename': 'update_category',
                    'action': 'update',
                    'description': 'Chỉnh sửa danh mục'
                },
                {
                    'module': 'categories',
                    'name': 'Xóa danh mục',
                    'codename': 'delete_category',
                    'action': 'delete',
                    'description': 'Xóa danh mục'
                },

                # ==========================================
                # IMPORT/INVENTORY MODULE
                # ==========================================
                {
                    'module': 'inventory',
                    'name': 'Xem lô nhập hàng',
                    'codename': 'view_import_batches',
                    'action': 'list',
                    'description': 'Xem danh sách lô nhập hàng'
                },
                {
                    'module': 'inventory',
                    'name': 'Tạo lô nhập hàng',
                    'codename': 'create_import_batch',
                    'action': 'create',
                    'description': 'Tạo phiếu nhập hàng mới'
                },
                {
                    'module': 'inventory',
                    'name': 'Cập nhật lô nhập',
                    'codename': 'update_import_batch',
                    'action': 'update',
                    'description': 'Cập nhật thông tin lô nhập'
                },
                {
                    'module': 'inventory',
                    'name': 'Xem nguồn nhập',
                    'codename': 'view_import_sources',
                    'action': 'list',
                    'description': 'Xem danh sách nguồn nhập hàng'
                },
                {
                    'module': 'inventory',
                    'name': 'Quản lý nguồn nhập',
                    'codename': 'manage_import_sources',
                    'action': 'manage',
                    'description': 'Thêm/Sửa/Xóa nguồn nhập hàng'
                },

                # ==========================================
                # USERS MODULE
                # ==========================================
                {
                    'module': 'users',
                    'name': 'Xem danh sách người dùng',
                    'codename': 'view_users',
                    'action': 'list',
                    'description': 'Xem danh sách người dùng hệ thống'
                },
                {
                    'module': 'users',
                    'name': 'Tạo người dùng',
                    'codename': 'create_user',
                    'action': 'create',
                    'description': 'Thêm người dùng mới'
                },
                {
                    'module': 'users',
                    'name': 'Sửa thông tin người dùng',
                    'codename': 'update_user',
                    'action': 'update',
                    'description': 'Chỉnh sửa thông tin người dùng'
                },
                {
                    'module': 'users',
                    'name': 'Xóa người dùng',
                    'codename': 'delete_user',
                    'action': 'delete',
                    'description': 'Xóa người dùng khỏi hệ thống'
                },
                {
                    'module': 'users',
                    'name': 'Gán vai trò cho user',
                    'codename': 'assign_user_roles',
                    'action': 'manage',
                    'description': 'Gán và xóa vai trò của người dùng'
                },

                # ==========================================
                # ROLES MODULE
                # ==========================================
                {
                    'module': 'roles',
                    'name': 'Xem danh sách vai trò',
                    'codename': 'view_roles',
                    'action': 'list',
                    'description': 'Xem danh sách vai trò'
                },
                {
                    'module': 'roles',
                    'name': 'Tạo vai trò',
                    'codename': 'create_role',
                    'action': 'create',
                    'description': 'Tạo vai trò mới'
                },
                {
                    'module': 'roles',
                    'name': 'Sửa vai trò',
                    'codename': 'update_role',
                    'action': 'update',
                    'description': 'Chỉnh sửa thông tin vai trò'
                },
                {
                    'module': 'roles',
                    'name': 'Xóa vai trò',
                    'codename': 'delete_role',
                    'action': 'delete',
                    'description': 'Xóa vai trò'
                },
                {
                    'module': 'roles',
                    'name': 'Gán quyền cho vai trò',
                    'codename': 'assign_role_permissions',
                    'action': 'manage',
                    'description': 'Gán và xóa quyền của vai trò'
                },

                # ==========================================
                # PERMISSIONS MODULE
                # ==========================================
                {
                    'module': 'permissions',
                    'name': 'Xem danh sách quyền',
                    'codename': 'view_permissions',
                    'action': 'list',
                    'description': 'Xem danh sách quyền hệ thống'
                },
                {
                    'module': 'permissions',
                    'name': 'Tạo quyền',
                    'codename': 'create_permission',
                    'action': 'create',
                    'description': 'Tạo quyền mới'
                },
                {
                    'module': 'permissions',
                    'name': 'Sửa quyền',
                    'codename': 'update_permission',
                    'action': 'update',
                    'description': 'Chỉnh sửa quyền'
                },
                {
                    'module': 'permissions',
                    'name': 'Xóa quyền',
                    'codename': 'delete_permission',
                    'action': 'delete',
                    'description': 'Xóa quyền'
                },

                # ==========================================
                # DEPARTMENTS MODULE
                # ==========================================
                {
                    'module': 'departments',
                    'name': 'Xem danh sách phòng ban',
                    'codename': 'view_departments',
                    'action': 'list',
                    'description': 'Xem danh sách phòng ban'
                },
                {
                    'module': 'departments',
                    'name': 'Tạo phòng ban',
                    'codename': 'create_department',
                    'action': 'create',
                    'description': 'Tạo phòng ban mới'
                },
                {
                    'module': 'departments',
                    'name': 'Sửa phòng ban',
                    'codename': 'update_department',
                    'action': 'update',
                    'description': 'Chỉnh sửa thông tin phòng ban'
                },
                {
                    'module': 'departments',
                    'name': 'Xóa phòng ban',
                    'codename': 'delete_department',
                    'action': 'delete',
                    'description': 'Xóa phòng ban'
                },

                # ==========================================
                # REPORTS MODULE
                # ==========================================
                {
                    'module': 'reports',
                    'name': 'Xem báo cáo doanh thu',
                    'codename': 'view_revenue_reports',
                    'action': 'read',
                    'description': 'Xem báo cáo doanh thu'
                },
                {
                    'module': 'reports',
                    'name': 'Xem báo cáo tồn kho',
                    'codename': 'view_inventory_reports',
                    'action': 'read',
                    'description': 'Xem báo cáo tồn kho'
                },
                {
                    'module': 'reports',
                    'name': 'Xuất báo cáo',
                    'codename': 'export_reports',
                    'action': 'manage',
                    'description': 'Xuất báo cáo ra file'
                },

                # ==========================================
                # SETTINGS MODULE
                # ==========================================
                {
                    'module': 'settings',
                    'name': 'Xem cài đặt hệ thống',
                    'codename': 'view_settings',
                    'action': 'read',
                    'description': 'Xem cài đặt hệ thống'
                },
                {
                    'module': 'settings',
                    'name': 'Cập nhật cài đặt',
                    'codename': 'update_settings',
                    'action': 'update',
                    'description': 'Thay đổi cài đặt hệ thống'
                },
            ]

            # Create permissions
            created_count = 0
            updated_count = 0
            skipped_count = 0

            for perm_data in PERMISSIONS:
                try:
                    permission, created = Permission.objects.update_or_create(
                        codename=perm_data['codename'],
                        defaults={
                            'module': perm_data['module'],
                            'name': perm_data['name'],
                            'action': perm_data['action'],
                            'description': perm_data['description'],
                            'is_active': True
                        }
                    )
                    if created:
                        created_count += 1
                        self.stdout.write(f'  ✓ Created: {perm_data["name"]}')
                    else:
                        updated_count += 1
                except Exception as e:
                    # If permission exists with same name but different codename, skip
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ Skipped: {perm_data["name"]} - {str(e)}')
                    )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Permissions: Created {created_count}, Updated {updated_count}'
                )
            )

            # Create default roles with permissions
            self.stdout.write(self.style.WARNING('\nCreating default roles...'))

            roles_config = [
                {
                    'slug': 'super-admin',
                    'name': 'Super Admin',
                    'description': 'Toàn quyền quản trị hệ thống',
                    'level': 100,
                    'color': '#ef4444',
                    'is_system': True,
                    'permissions': 'all'
                },
                {
                    'slug': 'admin',
                    'name': 'Admin',
                    'description': 'Quản trị viên hệ thống',
                    'level': 90,
                    'color': '#f59e0b',
                    'is_system': True,
                    'permissions': 'exclude:delete_user,update_settings'
                },
                {
                    'slug': 'manager',
                    'name': 'Quản lý',
                    'description': 'Quản lý kinh doanh, xem báo cáo',
                    'level': 70,
                    'color': '#8b5cf6',
                    'is_system': False,
                    'permissions': [
                        'view_dashboard', 'view_seafood_dashboard',
                        'view_products', 'create_product', 'update_product', 'view_product_detail',
                        'view_orders', 'view_order_detail', 'update_order', 'create_order',
                        'view_import_batches', 'create_import_batch',
                        'view_revenue_reports', 'view_inventory_reports',
                        'view_categories', 'create_category', 'update_category'
                    ]
                },
                {
                    'slug': 'salesperson',
                    'name': 'Nhân viên bán hàng',
                    'description': 'Bán hàng POS, quản lý đơn hàng',
                    'level': 50,
                    'color': '#10b981',
                    'is_system': False,
                    'permissions': [
                        'view_dashboard',
                        'access_pos', 'create_pos_order',
                        'view_products', 'view_product_detail',
                        'view_orders', 'create_order', 'view_order_detail',
                        'view_categories'
                    ]
                },
                {
                    'slug': 'warehouse',
                    'name': 'Nhân viên kho',
                    'description': 'Quản lý kho, nhập hàng',
                    'level': 50,
                    'color': '#3b82f6',
                    'is_system': False,
                    'permissions': [
                        'view_dashboard',
                        'view_products', 'update_product', 'view_product_detail',
                        'view_import_batches', 'create_import_batch', 'update_import_batch',
                        'view_import_sources', 'manage_import_sources',
                        'view_inventory_reports',
                        'view_categories'
                    ]
                },
                {
                    'slug': 'accountant',
                    'name': 'Kế toán',
                    'description': 'Xem báo cáo, đơn hàng, doanh thu',
                    'level': 60,
                    'color': '#06b6d4',
                    'is_system': False,
                    'permissions': [
                        'view_dashboard', 'view_seafood_dashboard',
                        'view_orders', 'view_order_detail',
                        'view_products', 'view_product_detail',
                        'view_revenue_reports', 'view_inventory_reports', 'export_reports',
                        'view_import_batches'
                    ]
                }
            ]

            for role_config in roles_config:
                perms_config = role_config.pop('permissions')

                role, created = Role.objects.update_or_create(
                    slug=role_config['slug'],
                    defaults=role_config
                )

                # Assign permissions
                if perms_config == 'all':
                    role.permissions.set(Permission.objects.all())
                    perm_count = Permission.objects.count()
                elif isinstance(perms_config, str) and perms_config.startswith('exclude:'):
                    exclude_list = perms_config.replace('exclude:', '').split(',')
                    perms = Permission.objects.exclude(codename__in=exclude_list)
                    role.permissions.set(perms)
                    perm_count = perms.count()
                elif isinstance(perms_config, list):
                    perms = Permission.objects.filter(codename__in=perms_config)
                    role.permissions.set(perms)
                    perm_count = perms.count()

                status = '✓ Created' if created else '✓ Updated'
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  {status}: {role.name} (Level {role.level}) - {perm_count} permissions'
                    )
                )

            # Print summary
            self.stdout.write('\n' + '='*70)
            self.stdout.write(self.style.SUCCESS('SUMMARY'))
            self.stdout.write('='*70)

            modules = Permission.objects.values_list('module', flat=True).distinct().order_by('module')
            self.stdout.write('\nPermissions by Module:')
            for module in modules:
                count = Permission.objects.filter(module=module).count()
                self.stdout.write(f'  • {module.upper()}: {count} permissions')

            self.stdout.write(f'\n✓ Total Permissions: {Permission.objects.count()}')
            self.stdout.write(f'✓ Total Roles: {Role.objects.count()}')
            self.stdout.write(
                self.style.SUCCESS('\n🎉 Permission seeding completed successfully!\n')
            )
