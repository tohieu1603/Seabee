"""
Management command để seed users với roles và permissions
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.rbac.models import Role, Permission, UserRole, RolePermission

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed users với roles và permissions đầy đủ'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Bắt đầu seed users, roles, và permissions...\n')

        # ============================================
        # 1. CREATE PERMISSIONS
        # ============================================
        self.stdout.write('📋 Tạo permissions...')

        permissions_data = [
            # DASHBOARD
            {'module': 'dashboard', 'name': 'Xem Dashboard', 'codename': 'view_dashboard', 'action': 'read'},
            {'module': 'dashboard', 'name': 'Xem Dashboard Hải sản', 'codename': 'view_seafood_dashboard', 'action': 'read'},

            # SEAFOOD/PRODUCTS
            {'module': 'seafood', 'name': 'Xem sản phẩm', 'codename': 'view_products', 'action': 'list'},
            {'module': 'seafood', 'name': 'Tạo sản phẩm', 'codename': 'create_product', 'action': 'create'},
            {'module': 'seafood', 'name': 'Sửa sản phẩm', 'codename': 'update_product', 'action': 'update'},
            {'module': 'seafood', 'name': 'Xóa sản phẩm', 'codename': 'delete_product', 'action': 'delete'},

            # ORDERS
            {'module': 'orders', 'name': 'Xem đơn hàng', 'codename': 'view_orders', 'action': 'list'},
            {'module': 'orders', 'name': 'Tạo đơn hàng', 'codename': 'create_order', 'action': 'create'},
            {'module': 'orders', 'name': 'Sửa đơn hàng', 'codename': 'update_order', 'action': 'update'},
            {'module': 'orders', 'name': 'Xóa đơn hàng', 'codename': 'delete_order', 'action': 'delete'},
            {'module': 'orders', 'name': 'Xuất PDF đơn hàng', 'codename': 'export_order_pdf', 'action': 'export'},
            {'module': 'orders', 'name': 'Cân hàng và upload ảnh', 'codename': 'weigh_order', 'action': 'update'},
            {'module': 'orders', 'name': 'Đánh dấu đã gửi vận chuyển', 'codename': 'ship_order', 'action': 'update'},
            {'module': 'orders', 'name': 'Thay đổi giá và trọng lượng', 'codename': 'adjust_order_items', 'action': 'update'},

            # POS
            {'module': 'pos', 'name': 'Sử dụng POS', 'codename': 'use_pos', 'action': 'use'},
            {'module': 'pos', 'name': 'Tạo đơn POS', 'codename': 'create_pos_order', 'action': 'create'},
            {'module': 'pos', 'name': 'Hủy đơn POS', 'codename': 'cancel_pos_order', 'action': 'delete'},

            # CATEGORIES
            {'module': 'categories', 'name': 'Xem danh mục', 'codename': 'view_categories', 'action': 'list'},
            {'module': 'categories', 'name': 'Tạo danh mục', 'codename': 'create_category', 'action': 'create'},
            {'module': 'categories', 'name': 'Sửa danh mục', 'codename': 'update_category', 'action': 'update'},
            {'module': 'categories', 'name': 'Xóa danh mục', 'codename': 'delete_category', 'action': 'delete'},

            # INVENTORY
            {'module': 'inventory', 'name': 'Xem tồn kho', 'codename': 'view_inventory', 'action': 'list'},
            {'module': 'inventory', 'name': 'Nhập kho', 'codename': 'import_inventory', 'action': 'create'},
            {'module': 'inventory', 'name': 'Xuất kho', 'codename': 'export_inventory', 'action': 'create'},
            {'module': 'inventory', 'name': 'Kiểm kho', 'codename': 'check_inventory', 'action': 'update'},

            # USERS
            {'module': 'users', 'name': 'Xem người dùng', 'codename': 'view_users', 'action': 'list'},
            {'module': 'users', 'name': 'Tạo người dùng', 'codename': 'create_user', 'action': 'create'},
            {'module': 'users', 'name': 'Sửa người dùng', 'codename': 'update_user', 'action': 'update'},
            {'module': 'users', 'name': 'Xóa người dùng', 'codename': 'delete_user', 'action': 'delete'},
            {'module': 'users', 'name': 'Gán vai trò', 'codename': 'assign_role', 'action': 'update'},

            # ROLES
            {'module': 'roles', 'name': 'Xem vai trò', 'codename': 'view_roles', 'action': 'list'},
            {'module': 'roles', 'name': 'Tạo vai trò', 'codename': 'create_role', 'action': 'create'},
            {'module': 'roles', 'name': 'Sửa vai trò', 'codename': 'update_role', 'action': 'update'},
            {'module': 'roles', 'name': 'Xóa vai trò', 'codename': 'delete_role', 'action': 'delete'},

            # PERMISSIONS
            {'module': 'permissions', 'name': 'Xem quyền hạn', 'codename': 'view_permissions', 'action': 'list'},
            {'module': 'permissions', 'name': 'Gán quyền cho vai trò', 'codename': 'assign_permission', 'action': 'update'},

            # DEPARTMENTS
            {'module': 'departments', 'name': 'Xem phòng ban', 'codename': 'view_departments', 'action': 'list'},
            {'module': 'departments', 'name': 'Tạo phòng ban', 'codename': 'create_department', 'action': 'create'},
            {'module': 'departments', 'name': 'Sửa phòng ban', 'codename': 'update_department', 'action': 'update'},
            {'module': 'departments', 'name': 'Xóa phòng ban', 'codename': 'delete_department', 'action': 'delete'},

            # REPORTS
            {'module': 'reports', 'name': 'Xem báo cáo', 'codename': 'view_reports', 'action': 'read'},
            {'module': 'reports', 'name': 'Xuất báo cáo', 'codename': 'export_reports', 'action': 'export'},

            # SETTINGS
            {'module': 'settings', 'name': 'Xem cài đặt', 'codename': 'view_settings', 'action': 'read'},
            {'module': 'settings', 'name': 'Sửa cài đặt', 'codename': 'update_settings', 'action': 'update'},
        ]

        permissions = {}
        for perm_data in permissions_data:
            perm, created = Permission.objects.get_or_create(
                codename=perm_data['codename'],
                defaults={
                    'module': perm_data['module'],
                    'name': perm_data['name'],
                    'action': perm_data['action'],
                    'description': f"{perm_data['name']} - {perm_data['module']}"
                }
            )
            permissions[perm.codename] = perm
            if created:
                self.stdout.write(f'  ✓ {perm.name}')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Đã tạo {len(permissions)} permissions\n'))

        # ============================================
        # 2. CREATE ROLES
        # ============================================
        self.stdout.write('👥 Tạo roles...')

        roles_config = [
            {
                'slug': 'super-admin',
                'name': 'Super Admin',
                'level': 100,
                'color': '#ef4444',
                'permissions': 'all'
            },
            {
                'slug': 'manager',
                'name': 'Quản lý',
                'level': 70,
                'color': '#8b5cf6',
                'permissions': [
                    'view_dashboard', 'view_seafood_dashboard',
                    'view_products', 'create_product', 'update_product',
                    'view_orders', 'create_order', 'update_order', 'export_order_pdf',
                    'use_pos', 'create_pos_order',
                    'view_categories', 'create_category', 'update_category',
                    'view_inventory', 'import_inventory', 'export_inventory', 'check_inventory',
                    'view_users', 'view_roles', 'view_permissions', 'view_departments',
                    'view_reports', 'export_reports',
                    'view_settings'
                ]
            },
            {
                'slug': 'salesperson',
                'name': 'Nhân viên bán hàng',
                'level': 50,
                'color': '#10b981',
                'permissions': [
                    'view_dashboard',
                    'view_products',
                    'view_orders', 'update_order', 'export_order_pdf',
                    # Workflow permissions - chỉ xử lý đơn hàng đã tạo
                    'weigh_order',           # Cân hàng và upload ảnh
                    'ship_order',            # Đánh dấu đã gửi vận chuyển
                    'adjust_order_items',    # Thay đổi giá và trọng lượng
                    'view_categories',
                    'view_inventory'
                ]
            },
            {
                'slug': 'warehouse',
                'name': 'Thủ kho',
                'level': 50,
                'color': '#f59e0b',
                'permissions': [
                    'view_dashboard',
                    'view_products', 'update_product',
                    'view_orders',
                    'view_categories',
                    'view_inventory', 'import_inventory', 'export_inventory', 'check_inventory'
                ]
            },
            {
                'slug': 'accountant',
                'name': 'Kế toán',
                'level': 60,
                'color': '#06b6d4',
                'permissions': [
                    'view_dashboard',
                    'view_products',
                    'view_orders', 'export_order_pdf',
                    'view_categories',
                    'view_inventory',
                    'view_reports', 'export_reports'
                ]
            },
            {
                'slug': 'viewer',
                'name': 'Người xem',
                'level': 10,
                'color': '#64748b',
                'permissions': [
                    'view_dashboard',
                    'view_products',
                    'view_orders',
                    'view_categories'
                ]
            }
        ]

        roles = {}
        for role_config in roles_config:
            role, created = Role.objects.get_or_create(
                slug=role_config['slug'],
                defaults={
                    'name': role_config['name'],
                    'level': role_config['level'],
                    'color': role_config['color'],
                    'description': f'Vai trò {role_config["name"]}'
                }
            )
            roles[role.slug] = role

            # Assign permissions
            if role_config['permissions'] == 'all':
                # Super Admin gets all permissions
                for perm in permissions.values():
                    RolePermission.objects.get_or_create(role=role, permission=perm)
                self.stdout.write(f'  ✓ {role.name} - ALL permissions')
            else:
                # Other roles get specific permissions
                for perm_code in role_config['permissions']:
                    if perm_code in permissions:
                        RolePermission.objects.get_or_create(
                            role=role,
                            permission=permissions[perm_code]
                        )
                self.stdout.write(f'  ✓ {role.name} - {len(role_config["permissions"])} permissions')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Đã tạo {len(roles)} roles\n'))

        # ============================================
        # 3. CREATE USERS
        # ============================================
        self.stdout.write('👤 Tạo users...')

        users_data = [
            {
                'email': 'admin@seafood.com',
                'password': 'admin123',
                'first_name': 'Admin',
                'last_name': 'System',
                'user_type': 'manager',
                'role': 'super-admin'
            },
            {
                'email': 'manager@seafood.com',
                'password': 'manager123',
                'first_name': 'Nguyễn',
                'last_name': 'Quản Lý',
                'user_type': 'manager',
                'role': 'manager'
            },
            {
                'email': 'sale1@seafood.com',
                'password': 'sale123',
                'first_name': 'Trần',
                'last_name': 'Bán Hàng',
                'user_type': 'employee',
                'role': 'salesperson'
            },
            {
                'email': 'sale2@seafood.com',
                'password': 'sale123',
                'first_name': 'Lê',
                'last_name': 'Nhân Viên',
                'user_type': 'employee',
                'role': 'salesperson'
            },
            {
                'email': 'warehouse@seafood.com',
                'password': 'warehouse123',
                'first_name': 'Phạm',
                'last_name': 'Thủ Kho',
                'user_type': 'employee',
                'role': 'warehouse'
            },
            {
                'email': 'accountant@seafood.com',
                'password': 'accountant123',
                'first_name': 'Hoàng',
                'last_name': 'Kế Toán',
                'user_type': 'employee',
                'role': 'accountant'
            }
        ]

        created_users = []
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                email=user_data['email'],
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'user_type': user_data['user_type'],
                    'is_active': True
                }
            )

            if created:
                user.set_password(user_data['password'])
                user.save()

            # Assign role
            role = roles[user_data['role']]
            UserRole.objects.get_or_create(user=user, role=role)

            created_users.append({
                'email': user.email,
                'password': user_data['password'],
                'name': f'{user.first_name} {user.last_name}',
                'role': role.name
            })

            status = '🆕' if created else '✓'
            self.stdout.write(f'  {status} {user.email} → {role.name}')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Đã tạo {len(created_users)} users\n'))

        # ============================================
        # 4. SUMMARY
        # ============================================
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('🎉 HOÀN THÀNH SEED DỮ LIỆU!'))
        self.stdout.write(self.style.SUCCESS('='*60))

        self.stdout.write('\n📊 THỐNG KÊ:')
        self.stdout.write(f'  • Permissions: {len(permissions)}')
        self.stdout.write(f'  • Roles: {len(roles)}')
        self.stdout.write(f'  • Users: {len(created_users)}')

        self.stdout.write('\n👥 DANH SÁCH TÀI KHOẢN:\n')
        for user in created_users:
            self.stdout.write(f'  📧 {user["email"]}')
            self.stdout.write(f'     🔑 Password: {user["password"]}')
            self.stdout.write(f'     👤 Name: {user["name"]}')
            self.stdout.write(f'     🎭 Role: {user["role"]}\n')

        self.stdout.write(self.style.SUCCESS('✅ Bạn có thể đăng nhập với các tài khoản trên!'))
