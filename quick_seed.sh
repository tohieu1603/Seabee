#!/bin/bash
echo "🌊 QUICK SEED - Tạo nhanh users và data"
echo "========================================"

python3 manage.py shell << 'PYEND'
from django.contrib.auth import get_user_model
User = get_user_model()

users = [
    ('admin@seafood.com', 'admin123', 'admin', 'Quản Trị', 'Viên', '0901234567'),
    ('manager@seafood.com', 'manager123', 'manager', 'Nguyễn', 'Quản Lý', '0901234568'),
    ('sale1@seafood.com', 'sale123', 'staff', 'Trần', 'Bán Hàng', '0902345678'),
    ('sale2@seafood.com', 'sale123', 'staff', 'Lê', 'Nhân Viên', '0902345679'),
    ('warehouse@seafood.com', 'warehouse123', 'staff', 'Phạm', 'Thủ Kho', '0903456789'),
    ('accountant@seafood.com', 'accountant123', 'staff', 'Hoàng', 'Kế Toán', '0904567890'),
    ('testcustomer@example.com', 'customer123', 'customer', 'Nguyễn', 'Văn Test', '0912345678'),
    ('customer1@example.com', 'customer123', 'customer', 'Trần', 'Thị B', '0923456789'),
    ('customer2@example.com', 'customer123', 'customer', 'Lê', 'Văn C', '0934567890'),
]

print("\n✅ TẠO USERS")
print("-" * 60)
for email, pwd, utype, fname, lname, phone in users:
    if User.objects.filter(email=email).exists():
        print(f"⏭️  {email:30} | Đã tồn tại")
    else:
        User.objects.create_user(email=email, password=pwd, user_type=utype, 
                                first_name=fname, last_name=lname, phone=phone)
        print(f"✅ {email:30} | Tạo mới")

print(f"\n📊 Tổng: {User.objects.count()} users")
print("\n📋 THÔNG TIN ĐĂNG NHẬP:")
print("-" * 60)
print("ADMIN:      admin@seafood.com / admin123")
print("MANAGER:    manager@seafood.com / manager123")
print("SALE 1:     sale1@seafood.com / sale123")
print("SALE 2:     sale2@seafood.com / sale123")
print("WAREHOUSE:  warehouse@seafood.com / warehouse123")
print("ACCOUNTANT: accountant@seafood.com / accountant123")
print("CUSTOMER:   testcustomer@example.com / customer123")
print("-" * 60)
PYEND
