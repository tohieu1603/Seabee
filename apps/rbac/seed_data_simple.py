"""
RBAC Seed Data - Simplified with 3 roles only
Super Admin, Admin, Sales
"""

# ============================================
# PERMISSION DEFINITIONS - Simplified
# ============================================

PERMISSIONS_TEMPLATE = [
    # ===== USER MANAGEMENT =====
    {"name": "Xem người dùng", "codename": "users.view", "module": "users", "action": "view", "description": "Xem danh sách người dùng"},
    {"name": "Tạo người dùng", "codename": "users.create", "module": "users", "action": "create", "description": "Tạo người dùng mới"},
    {"name": "Sửa người dùng", "codename": "users.update", "module": "users", "action": "update", "description": "Cập nhật thông tin người dùng"},
    {"name": "Xóa người dùng", "codename": "users.delete", "module": "users", "action": "delete", "description": "Xóa người dùng"},
    {"name": "Quản lý tất cả người dùng", "codename": "users.manage", "module": "users", "action": "manage", "description": "Quản lý toàn bộ người dùng"},

    # ===== ROLE MANAGEMENT =====
    {"name": "Xem vai trò", "codename": "roles.view", "module": "roles", "action": "view", "description": "Xem danh sách vai trò"},
    {"name": "Tạo vai trò", "codename": "roles.create", "module": "roles", "action": "create", "description": "Tạo vai trò mới"},
    {"name": "Sửa vai trò", "codename": "roles.update", "module": "roles", "action": "update", "description": "Cập nhật vai trò"},
    {"name": "Xóa vai trò", "codename": "roles.delete", "module": "roles", "action": "delete", "description": "Xóa vai trò"},
    {"name": "Gán vai trò cho người dùng", "codename": "roles.assign", "module": "roles", "action": "manage", "description": "Gán vai trò"},
    {"name": "Quản lý quyền hạn vai trò", "codename": "roles.permissions", "module": "roles", "action": "manage", "description": "Quản lý permissions của role"},

    # ===== PERMISSION MANAGEMENT =====
    {"name": "Xem quyền hạn", "codename": "permissions.view", "module": "permissions", "action": "view", "description": "Xem danh sách quyền hạn"},
    {"name": "Tạo quyền hạn", "codename": "permissions.create", "module": "permissions", "action": "create", "description": "Tạo quyền hạn mới"},
    {"name": "Sửa quyền hạn", "codename": "permissions.update", "module": "permissions", "action": "update", "description": "Cập nhật quyền hạn"},
    {"name": "Xóa quyền hạn", "codename": "permissions.delete", "module": "permissions", "action": "delete", "description": "Xóa quyền hạn"},

    # ===== SALES MODULE =====
    {"name": "Xem bán hàng", "codename": "sales.view", "module": "sales", "action": "view", "description": "Xem dữ liệu bán hàng"},
    {"name": "Tạo đơn hàng", "codename": "sales.create", "module": "sales", "action": "create", "description": "Tạo đơn hàng mới"},
    {"name": "Sửa đơn hàng", "codename": "sales.update", "module": "sales", "action": "update", "description": "Cập nhật đơn hàng"},
    {"name": "Xóa đơn hàng", "codename": "sales.delete", "module": "sales", "action": "delete", "description": "Xóa đơn hàng"},
    {"name": "Quản lý khách hàng", "codename": "sales.customers", "module": "sales", "action": "manage", "description": "Quản lý khách hàng"},
    {"name": "Xem báo cáo bán hàng", "codename": "sales.reports", "module": "sales", "action": "view", "description": "Xem báo cáo"},

    # ===== DASHBOARD =====
    {"name": "Xem dashboard", "codename": "dashboard.view", "module": "dashboard", "action": "view", "description": "Xem dashboard tổng quan"},
    {"name": "Xem báo cáo", "codename": "reports.view", "module": "reports", "action": "view", "description": "Xem các báo cáo"},
]


# ============================================
# ROLE DEFINITIONS - 3 Roles Only
# ============================================

ROLES_TEMPLATE = [
    {
        "name": "Super Admin",
        "slug": "super-admin",
        "description": "Toàn quyền hệ thống - Quản lý mọi thứ",
        "level": 100,
        "color": "#dc2626",  # Red
        "is_system": True,
        "permissions": "all",  # All permissions
    },
    {
        "name": "Admin",
        "slug": "admin",
        "description": "Quản trị viên - Quản lý người dùng và hệ thống",
        "level": 80,
        "color": "#2563eb",  # Blue
        "is_system": True,
        "permissions": [
            # User management
            "users.view", "users.create", "users.update", "users.delete",
            # Role management
            "roles.view", "roles.assign",
            # Permissions
            "permissions.view",
            # Sales - view only
            "sales.view", "sales.customers", "sales.reports",
            # Dashboard
            "dashboard.view", "reports.view",
        ],
    },
    {
        "name": "Sales",
        "slug": "sales",
        "description": "Nhân viên bán hàng - Quản lý đơn hàng và khách hàng",
        "level": 50,
        "color": "#059669",  # Green
        "is_system": True,
        "permissions": [
            # Sales full access
            "sales.view", "sales.create", "sales.update", "sales.customers", "sales.reports",
            # Users - view only
            "users.view",
            # Dashboard
            "dashboard.view",
        ],
    },
]


# ============================================
# DEPARTMENT DEFINITIONS
# ============================================

DEPARTMENTS_TEMPLATE = [
    {
        "name": "Ban Giám Đốc",
        "code": "EXEC",
        "description": "Ban lãnh đạo công ty",
        "is_active": True,
    },
    {
        "name": "Phòng Kinh Doanh",
        "code": "SALES",
        "description": "Phòng bán hàng và chăm sóc khách hàng",
        "is_active": True,
    },
    {
        "name": "Phòng Hành Chính",
        "code": "ADMIN",
        "description": "Phòng hành chính nhân sự",
        "is_active": True,
    },
]
