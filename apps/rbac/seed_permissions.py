"""
Seed Data - Permissions cho hệ thống
Các module: products, users, orders, dashboard, system
"""

PERMISSIONS = [
    # ============================================
    # PRODUCTS MODULE
    # ============================================
    {
        "name": "Xem sản phẩm",
        "codename": "products.view",
        "module": "products",
        "action": "view",
        "description": "Xem danh sách và chi tiết sản phẩm"
    },
    {
        "name": "Tạo sản phẩm",
        "codename": "products.create",
        "module": "products",
        "action": "create",
        "description": "Thêm sản phẩm mới vào hệ thống"
    },
    {
        "name": "Cập nhật sản phẩm",
        "codename": "products.update",
        "module": "products",
        "action": "update",
        "description": "Chỉnh sửa thông tin sản phẩm"
    },
    {
        "name": "Xóa sản phẩm",
        "codename": "products.delete",
        "module": "products",
        "action": "delete",
        "description": "Xóa sản phẩm khỏi hệ thống"
    },
    {
        "name": "Quản lý sản phẩm",
        "codename": "products.manage",
        "module": "products",
        "action": "manage",
        "description": "Toàn quyền quản lý sản phẩm"
    },
    {
        "name": "Export sản phẩm",
        "codename": "products.export",
        "module": "products",
        "action": "export",
        "description": "Xuất danh sách sản phẩm ra file"
    },
    {
        "name": "Import sản phẩm",
        "codename": "products.import",
        "module": "products",
        "action": "import",
        "description": "Nhập sản phẩm từ file"
    },

    # ============================================
    # USERS MODULE
    # ============================================
    {
        "name": "Xem người dùng",
        "codename": "users.view",
        "module": "users",
        "action": "view",
        "description": "Xem danh sách và thông tin người dùng"
    },
    {
        "name": "Tạo người dùng",
        "codename": "users.create",
        "module": "users",
        "action": "create",
        "description": "Thêm người dùng mới"
    },
    {
        "name": "Cập nhật người dùng",
        "codename": "users.update",
        "module": "users",
        "action": "update",
        "description": "Chỉnh sửa thông tin người dùng"
    },
    {
        "name": "Xóa người dùng",
        "codename": "users.delete",
        "module": "users",
        "action": "delete",
        "description": "Xóa người dùng khỏi hệ thống"
    },
    {
        "name": "Quản lý người dùng",
        "codename": "users.manage",
        "module": "users",
        "action": "manage",
        "description": "Toàn quyền quản lý người dùng"
    },
    {
        "name": "Export người dùng",
        "codename": "users.export",
        "module": "users",
        "action": "export",
        "description": "Xuất danh sách người dùng"
    },
    {
        "name": "Import người dùng",
        "codename": "users.import",
        "module": "users",
        "action": "import",
        "description": "Nhập người dùng từ file"
    },

    # ============================================
    # ORDERS MODULE
    # ============================================
    {
        "name": "Xem đơn hàng",
        "codename": "orders.view",
        "module": "orders",
        "action": "view",
        "description": "Xem danh sách và chi tiết đơn hàng"
    },
    {
        "name": "Tạo đơn hàng",
        "codename": "orders.create",
        "module": "orders",
        "action": "create",
        "description": "Tạo đơn hàng mới"
    },
    {
        "name": "Cập nhật đơn hàng",
        "codename": "orders.update",
        "module": "orders",
        "action": "update",
        "description": "Chỉnh sửa thông tin đơn hàng"
    },
    {
        "name": "Xóa đơn hàng",
        "codename": "orders.delete",
        "module": "orders",
        "action": "delete",
        "description": "Xóa đơn hàng"
    },
    {
        "name": "Quản lý đơn hàng",
        "codename": "orders.manage",
        "module": "orders",
        "action": "manage",
        "description": "Toàn quyền quản lý đơn hàng"
    },
    {
        "name": "Duyệt đơn hàng",
        "codename": "orders.approve",
        "module": "orders",
        "action": "approve",
        "description": "Phê duyệt đơn hàng"
    },
    {
        "name": "Export đơn hàng",
        "codename": "orders.export",
        "module": "orders",
        "action": "export",
        "description": "Xuất danh sách đơn hàng"
    },

    # ============================================
    # DASHBOARD MODULE
    # ============================================
    {
        "name": "Xem dashboard",
        "codename": "dashboard.view",
        "module": "dashboard",
        "action": "view",
        "description": "Truy cập trang dashboard"
    },
    {
        "name": "Xem thống kê",
        "codename": "dashboard.stats",
        "module": "dashboard",
        "action": "view",
        "description": "Xem các thống kê tổng quan"
    },
    {
        "name": "Xem báo cáo",
        "codename": "dashboard.reports",
        "module": "dashboard",
        "action": "view",
        "description": "Xem các báo cáo chi tiết"
    },
    {
        "name": "Export báo cáo",
        "codename": "dashboard.export",
        "module": "dashboard",
        "action": "export",
        "description": "Xuất báo cáo dashboard"
    },

    # ============================================
    # SYSTEM MODULE
    # ============================================
    {
        "name": "Xem cài đặt hệ thống",
        "codename": "system.view",
        "module": "system",
        "action": "view",
        "description": "Xem cấu hình hệ thống"
    },
    {
        "name": "Cập nhật cài đặt",
        "codename": "system.update",
        "module": "system",
        "action": "update",
        "description": "Thay đổi cấu hình hệ thống"
    },
    {
        "name": "Quản lý vai trò",
        "codename": "system.roles",
        "module": "system",
        "action": "manage",
        "description": "Quản lý vai trò và phân quyền"
    },
    {
        "name": "Quản lý permissions",
        "codename": "system.permissions",
        "module": "system",
        "action": "manage",
        "description": "Quản lý quyền hạn trong hệ thống"
    },
    {
        "name": "Xem logs hệ thống",
        "codename": "system.logs",
        "module": "system",
        "action": "view",
        "description": "Xem nhật ký hoạt động hệ thống"
    },
    {
        "name": "Backup hệ thống",
        "codename": "system.backup",
        "module": "system",
        "action": "manage",
        "description": "Sao lưu và phục hồi dữ liệu"
    },
    {
        "name": "Quản lý toàn hệ thống",
        "codename": "system.manage",
        "module": "system",
        "action": "manage",
        "description": "Toàn quyền quản trị hệ thống"
    },
]


ROLES = [
    {
        "name": "Super Admin",
        "slug": "super-admin",
        "description": "Quản trị viên tối cao - toàn quyền trên hệ thống",
        "level": 100,
        "color": "#dc2626",
        "is_system": True,
        "permissions": [
            # Tất cả permissions
            "products.view", "products.create", "products.update", "products.delete",
            "products.manage", "products.export", "products.import",
            "users.view", "users.create", "users.update", "users.delete",
            "users.manage", "users.export", "users.import",
            "orders.view", "orders.create", "orders.update", "orders.delete",
            "orders.manage", "orders.approve", "orders.export",
            "dashboard.view", "dashboard.stats", "dashboard.reports", "dashboard.export",
            "system.view", "system.update", "system.roles", "system.permissions",
            "system.logs", "system.backup", "system.manage",
        ]
    },
    {
        "name": "Admin",
        "slug": "admin",
        "description": "Quản trị viên - quản lý hầu hết chức năng",
        "level": 80,
        "color": "#ea580c",
        "is_system": True,
        "permissions": [
            "products.view", "products.create", "products.update", "products.delete", "products.export",
            "users.view", "users.create", "users.update", "users.export",
            "orders.view", "orders.create", "orders.update", "orders.approve", "orders.export",
            "dashboard.view", "dashboard.stats", "dashboard.reports", "dashboard.export",
            "system.view", "system.roles",
        ]
    },
    {
        "name": "Manager",
        "slug": "manager",
        "description": "Quản lý - quản lý sản phẩm và đơn hàng",
        "level": 60,
        "color": "#f59e0b",
        "is_system": True,
        "permissions": [
            "products.view", "products.create", "products.update", "products.export",
            "users.view",
            "orders.view", "orders.create", "orders.update", "orders.approve", "orders.export",
            "dashboard.view", "dashboard.stats", "dashboard.reports",
        ]
    },
    {
        "name": "Sales",
        "slug": "sales",
        "description": "Nhân viên bán hàng - tạo và quản lý đơn hàng",
        "level": 40,
        "color": "#10b981",
        "is_system": False,
        "permissions": [
            "products.view",
            "users.view",
            "orders.view", "orders.create", "orders.update",
            "dashboard.view", "dashboard.stats",
        ]
    },
    {
        "name": "Product Manager",
        "slug": "product-manager",
        "description": "Quản lý sản phẩm - CRUD sản phẩm",
        "level": 50,
        "color": "#3b82f6",
        "is_system": False,
        "permissions": [
            "products.view", "products.create", "products.update", "products.delete",
            "products.export", "products.import",
            "dashboard.view", "dashboard.stats",
        ]
    },
    {
        "name": "Customer Service",
        "slug": "customer-service",
        "description": "Chăm sóc khách hàng - xem thông tin",
        "level": 30,
        "color": "#8b5cf6",
        "is_system": False,
        "permissions": [
            "products.view",
            "users.view",
            "orders.view",
            "dashboard.view",
        ]
    },
    {
        "name": "Viewer",
        "slug": "viewer",
        "description": "Người xem - chỉ xem thông tin",
        "level": 10,
        "color": "#6b7280",
        "is_system": False,
        "permissions": [
            "dashboard.view",
            "products.view",
            "orders.view",
        ]
    },
]
