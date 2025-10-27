#!/usr/bin/env python3
"""
Script seed data đầy đủ cho hệ thống BaseSystem
Dựa trên ACCOUNTS.md

CÁCH CHẠY:
    cd backend
    python3 manage.py shell < seed_data.py

HOẶC:
    python3 manage.py shell
    >>> exec(open('seed_data.py').read())
"""

from django.contrib.auth import get_user_model
from apps.seafood.models import Seafood, Category, Order, OrderItem
from decimal import Decimal
import random

User = get_user_model()

print("\n" + "="*70)
print("🌊 BASESYSTEM - SEED DATA SCRIPT")
print("="*70)

# =============================================================================
# 1. TẠO USERS THEO ACCOUNTS.MD
# =============================================================================
print("\n📋 BƯỚC 1: TẠO TÀI KHOẢN NGƯỜI DÙNG")
print("-"*70)

users_config = [
    # ADMIN / MANAGER
    {
        'email': 'admin@seafood.com',
        'password': 'admin123',
        'user_type': 'admin',
        'full_name': 'Quản Trị Viên',
        'phone': '0901234567',
        'role': '👑 Super Admin'
    },
    {
        'email': 'manager@seafood.com',
        'password': 'manager123',
        'user_type': 'manager',
        'full_name': 'Nguyễn Quản Lý',
        'phone': '0901234568',
        'role': '💼 Quản lý cửa hàng'
    },

    # SALE (Nhân viên bán hàng)
    {
        'email': 'sale1@seafood.com',
        'password': 'sale123',
        'user_type': 'staff',
        'full_name': 'Trần Bán Hàng',
        'phone': '0902345678',
        'role': '💼 Nhân viên bán hàng'
    },
    {
        'email': 'sale2@seafood.com',
        'password': 'sale123',
        'user_type': 'staff',
        'full_name': 'Lê Nhân Viên',
        'phone': '0902345679',
        'role': '💼 Nhân viên bán hàng'
    },

    # WAREHOUSE (Thủ kho)
    {
        'email': 'warehouse@seafood.com',
        'password': 'warehouse123',
        'user_type': 'staff',
        'full_name': 'Phạm Thủ Kho',
        'phone': '0903456789',
        'role': '📦 Thủ kho'
    },

    # ACCOUNTANT (Kế toán)
    {
        'email': 'accountant@seafood.com',
        'password': 'accountant123',
        'user_type': 'staff',
        'full_name': 'Hoàng Kế Toán',
        'phone': '0904567890',
        'role': '📊 Kế toán'
    },

    # CUSTOMER (Khách hàng)
    {
        'email': 'testcustomer@example.com',
        'password': 'customer123',
        'user_type': 'customer',
        'full_name': 'Nguyễn Văn Test',
        'phone': '0912345678',
        'role': '📱 Khách hàng'
    },
    {
        'email': 'customer1@example.com',
        'password': 'customer123',
        'user_type': 'customer',
        'full_name': 'Trần Thị B',
        'phone': '0923456789',
        'role': '📱 Khách hàng'
    },
    {
        'email': 'customer2@example.com',
        'password': 'customer123',
        'user_type': 'customer',
        'full_name': 'Lê Văn C',
        'phone': '0934567890',
        'role': '📱 Khách hàng'
    },
]

created_users = {}
for config in users_config:
    email = config['email']
    user_type_key = config['user_type']

    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        print(f"   ⏭️  Đã tồn tại: {config['role']:25} | {email}")
    else:
        user = User.objects.create_user(
            email=email,
            password=config['password'],
            user_type=user_type_key,
            full_name=config['full_name'],
            phone=config['phone']
        )
        print(f"   ✅ Tạo mới: {config['role']:25} | {email}")

    # Lưu user theo email key để dễ truy xuất
    created_users[email] = user

    # Lưu thêm theo type cho tiện
    if user_type_key == 'customer':
        if 'customers' not in created_users:
            created_users['customers'] = []
        created_users['customers'].append(user)
    elif user_type_key == 'staff':
        if email.startswith('sale'):
            if 'sales' not in created_users:
                created_users['sales'] = []
            created_users['sales'].append(user)

print(f"\n   📊 Tổng số users: {User.objects.count()}")

# =============================================================================
# 2. TẠO DANH MỤC SẢN PHẨM
# =============================================================================
print("\n📋 BƯỚC 2: TẠO DANH MỤC SẢN PHẨM")
print("-"*70)

categories_data = [
    {'name': 'Tôm', 'description': 'Các loại tôm tươi sống, tôm sú, tôm hùm, tôm càng xanh'},
    {'name': 'Cá', 'description': 'Cá biển tươi sống, cá hồi, cá chẽm, cá basa'},
    {'name': 'Mực', 'description': 'Mực ống, bạch tuộc các loại'},
    {'name': 'Cua Ghẹ', 'description': 'Cua ghẹ, ghẹ xanh, cua hoàng đế'},
    {'name': 'Ốc', 'description': 'Ốc biển tươi sống, ốc hương, ốc móng tay'},
    {'name': 'Sò Điệp', 'description': 'Sò điệp, nghêu, ngao các loại'},
]

categories = {}
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categories[cat_data['name']] = category
    status = "✅ Tạo mới" if created else "⏭️  Đã tồn tại"
    print(f"   {status}: {cat_data['name']:15} | {cat_data['description'][:40]}")

print(f"\n   📊 Tổng số danh mục: {Category.objects.count()}")

# =============================================================================
# 3. TẠO SẢN PHẨM HẢI SẢN
# =============================================================================
print("\n📋 BƯỚC 3: TẠO SẢN PHẨM HẢI SẢN")
print("-"*70)

products_data = [
    # Tôm
    {'name': 'Tôm Sú', 'price': 350000, 'unit': 'kg', 'category': 'Tôm', 'stock': 50},
    {'name': 'Tôm Hùm', 'price': 1200000, 'unit': 'kg', 'category': 'Tôm', 'stock': 20},
    {'name': 'Tôm Càng Xanh', 'price': 280000, 'unit': 'kg', 'category': 'Tôm', 'stock': 40},
    {'name': 'Tôm Thẻ', 'price': 180000, 'unit': 'kg', 'category': 'Tôm', 'stock': 60},

    # Cá
    {'name': 'Cá Hồi', 'price': 450000, 'unit': 'kg', 'category': 'Cá', 'stock': 30},
    {'name': 'Cá Chẽm', 'price': 180000, 'unit': 'kg', 'category': 'Cá', 'stock': 25},
    {'name': 'Cá Basa', 'price': 120000, 'unit': 'kg', 'category': 'Cá', 'stock': 60},
    {'name': 'Cá Ngừ', 'price': 320000, 'unit': 'kg', 'category': 'Cá', 'stock': 15},
    {'name': 'Cá Thu', 'price': 150000, 'unit': 'kg', 'category': 'Cá', 'stock': 35},

    # Mực
    {'name': 'Mực Ống', 'price': 220000, 'unit': 'kg', 'category': 'Mực', 'stock': 35},
    {'name': 'Bạch Tuộc', 'price': 380000, 'unit': 'kg', 'category': 'Mực', 'stock': 15},
    {'name': 'Mực Nang', 'price': 250000, 'unit': 'kg', 'category': 'Mực', 'stock': 25},

    # Cua Ghẹ
    {'name': 'Ghẹ Xanh', 'price': 300000, 'unit': 'kg', 'category': 'Cua Ghẹ', 'stock': 45},
    {'name': 'Cua Hoàng Đế', 'price': 2500000, 'unit': 'kg', 'category': 'Cua Ghẹ', 'stock': 5},
    {'name': 'Cua Gạch', 'price': 450000, 'unit': 'kg', 'category': 'Cua Ghẹ', 'stock': 20},

    # Ốc
    {'name': 'Ốc Hương', 'price': 150000, 'unit': 'kg', 'category': 'Ốc', 'stock': 40},
    {'name': 'Ốc Móng Tay', 'price': 90000, 'unit': 'kg', 'category': 'Ốc', 'stock': 50},
    {'name': 'Ốc Len', 'price': 120000, 'unit': 'kg', 'category': 'Ốc', 'stock': 30},

    # Sò Điệp
    {'name': 'Sò Điệp', 'price': 200000, 'unit': 'kg', 'category': 'Sò Điệp', 'stock': 40},
    {'name': 'Nghêu', 'price': 80000, 'unit': 'kg', 'category': 'Sò Điệp', 'stock': 70},
]

products = []
for prod_data in products_data:
    product, created = Seafood.objects.get_or_create(
        name=prod_data['name'],
        defaults={
            'price': Decimal(str(prod_data['price'])),
            'unit_type': prod_data['unit'],
            'category': categories[prod_data['category']],
            'stock_quantity': prod_data['stock'],
            'description': f"{prod_data['name']} tươi sống, chất lượng cao. Giá tốt nhất thị trường."
        }
    )
    products.append(product)
    status = "✅" if created else "⏭️ "
    print(f"   {status} {prod_data['name']:20} | {prod_data['price']:>10,}đ/{prod_data['unit']} | Stock: {prod_data['stock']:>3} kg")

print(f"\n   📊 Tổng số sản phẩm: {Seafood.objects.count()}")

# =============================================================================
# 4. TẠO ĐƠN HÀNG MẪU CHO CUSTOMER
# =============================================================================
print("\n📋 BƯỚC 4: TẠO ĐƠN HÀNG MẪU")
print("-"*70)

# Lấy customers
customers_list = created_users.get('customers', [])
if not customers_list:
    customers_list = [created_users['testcustomer@example.com']]

addresses = [
    "123 Nguyễn Văn Linh, Phường Bình Thuận, Quận 7, TP.HCM",
    "456 Lê Văn Việt, Phường Tân Phú, Quận 9, TP.HCM",
    "789 Võ Văn Ngân, Phường Linh Chiểu, TP Thủ Đức, TP.HCM",
    "101 Nguyễn Hữu Thọ, Phường Tân Hưng, Quận 7, TP.HCM",
    "202 Xa Lộ Hà Nội, Phường Thảo Điền, Quận 2, TP.HCM",
]

orders_config = [
    # Đơn chờ xử lý - Chuyển khoản
    {
        'status': 'pending',
        'payment_status': 'pending_verification',
        'payment_method': 'bank_transfer',
        'customer_source': 'facebook',
        'items': [
            {'product_idx': 0, 'quantity': 2},  # Tôm Sú
            {'product_idx': 9, 'quantity': 1},  # Mực Ống
        ]
    },
    # Đơn đã xác nhận - Tiền mặt
    {
        'status': 'confirmed',
        'payment_status': 'paid',
        'payment_method': 'cash',
        'customer_source': 'zalo',
        'items': [
            {'product_idx': 4, 'quantity': 3},  # Cá Hồi
            {'product_idx': 12, 'quantity': 1},  # Ghẹ Xanh
        ]
    },
    # Đơn hoàn thành - COD
    {
        'status': 'completed',
        'payment_status': 'paid',
        'payment_method': 'cod',
        'customer_source': 'telephone',
        'items': [
            {'product_idx': 1, 'quantity': 1},  # Tôm Hùm
            {'product_idx': 10, 'quantity': 2},  # Bạch Tuộc
            {'product_idx': 15, 'quantity': 1}, # Ốc Hương
        ]
    },
    # Đơn đang xử lý - Chuyển khoản
    {
        'status': 'processing',
        'payment_status': 'paid',
        'payment_method': 'bank_transfer',
        'customer_source': 'facebook',
        'items': [
            {'product_idx': 7, 'quantity': 2},  # Cá Ngừ
            {'product_idx': 11, 'quantity': 1},  # Mực Nang
        ]
    },
    # Đơn đã gửi - Cash
    {
        'status': 'shipped',
        'payment_status': 'paid',
        'payment_method': 'cash',
        'customer_source': 'zalo',
        'items': [
            {'product_idx': 14, 'quantity': 1},  # Cua Gạch
            {'product_idx': 18, 'quantity': 3},  # Sò Điệp
        ]
    },
]

for i, order_config in enumerate(orders_config):
    # Chọn customer ngẫu nhiên
    customer = random.choice(customers_list)
    address = random.choice(addresses)

    order = Order.objects.create(
        customer=customer,
        customer_phone=customer.phone,
        customer_name=customer.full_name,
        customer_address=address,
        status=order_config['status'],
        payment_status=order_config['payment_status'],
        payment_method=order_config['payment_method'],
        customer_source=order_config['customer_source'],
        notes=f"Đơn hàng mẫu #{i+1} - Test order"
    )

    total_amount = Decimal('0')
    items_desc = []

    for item_data in order_config['items']:
        product = products[item_data['product_idx']]
        quantity = Decimal(str(item_data['quantity']))

        OrderItem.objects.create(
            order=order,
            seafood=product,
            quantity=quantity,
            unit_price=product.price,
            total_price=product.price * quantity
        )
        total_amount += product.price * quantity
        items_desc.append(f"{product.name} x{quantity}")

    order.total_amount = total_amount
    if order_config['payment_status'] == 'paid':
        order.paid_amount = total_amount
    order.save()

    status_icon = {
        'pending': '⏳',
        'confirmed': '✅',
        'processing': '⚙️',
        'shipped': '🚚',
        'completed': '✨'
    }.get(order.status, '📦')

    print(f"   {status_icon} #{order.order_code} | {order.get_status_display():12} | {total_amount:>12,}đ | {', '.join(items_desc)}")

print(f"\n   📊 Tổng số đơn hàng: {Order.objects.count()}")

# =============================================================================
# 5. THỐNG KÊ CUỐI CÙNG
# =============================================================================
print("\n" + "="*70)
print("✅ HOÀN THÀNH SEED DATA!")
print("="*70)

print("\n📋 THÔNG TIN ĐĂNG NHẬP:")
print("-"*70)
print(f"{'ROLE':<25} | {'EMAIL':<30} | {'PASSWORD':<15}")
print("-"*70)
for config in users_config:
    print(f"{config['role']:<25} | {config['email']:<30} | {config['password']:<15}")
print("-"*70)

print("\n📊 THỐNG KÊ HỆ THỐNG:")
print("-"*70)
print(f"  👥 Users:            {User.objects.count():>3}")
print(f"  👑 Admin/Manager:    {User.objects.filter(user_type__in=['admin', 'manager']).count():>3}")
print(f"  💼 Staff:            {User.objects.filter(user_type='staff').count():>3}")
print(f"  📱 Customers:        {User.objects.filter(user_type='customer').count():>3}")
print(f"  📂 Danh mục:         {Category.objects.count():>3}")
print(f"  🐟 Sản phẩm:         {Seafood.objects.count():>3}")
print(f"  📦 Đơn hàng:         {Order.objects.count():>3}")
print(f"  📋 Order items:      {OrderItem.objects.count():>3}")
print("-"*70)

print("\n🚀 CÁCH SỬ DỤNG:")
print("  1. Đăng nhập: http://localhost:3000/auth/login")
print("  2. Admin dashboard: http://localhost:3000/dashboard")
print("  3. Customer dashboard: http://localhost:3000/customer/dashboard")
print("  4. Đặt hàng public: http://localhost:3000/order")

print("\n" + "="*70)
print("🎉 SẴN SÀNG SỬ DỤNG!")
print("="*70 + "\n")
