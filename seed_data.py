#!/usr/bin/env python3
"""
Script seed data đầy đủ cho hệ thống BaseSystem
Dựa trên ACCOUNTS.md

CÁCH CHẠY:
    cd backend
    python3 manage.py shell < seed_data.py
"""

from django.contrib.auth import get_user_model
from apps.seafood.models import Seafood, SeafoodCategory, Order, OrderItem
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
    {'email': 'admin@seafood.com', 'password': 'admin123', 'user_type': 'admin', 
     'first_name': 'Quản Trị', 'last_name': 'Viên', 'phone': '0901234567', 'role': '👑 Super Admin'},
    
    {'email': 'manager@seafood.com', 'password': 'manager123', 'user_type': 'manager',
     'first_name': 'Nguyễn', 'last_name': 'Quản Lý', 'phone': '0901234568', 'role': '💼 Quản lý'},

    # SALE
    {'email': 'sale1@seafood.com', 'password': 'sale123', 'user_type': 'staff',
     'first_name': 'Trần', 'last_name': 'Bán Hàng', 'phone': '0902345678', 'role': '💼 Sale 1'},
    
    {'email': 'sale2@seafood.com', 'password': 'sale123', 'user_type': 'staff',
     'first_name': 'Lê', 'last_name': 'Nhân Viên', 'phone': '0902345679', 'role': '💼 Sale 2'},

    # WAREHOUSE
    {'email': 'warehouse@seafood.com', 'password': 'warehouse123', 'user_type': 'staff',
     'first_name': 'Phạm', 'last_name': 'Thủ Kho', 'phone': '0903456789', 'role': '📦 Thủ kho'},

    # ACCOUNTANT
    {'email': 'accountant@seafood.com', 'password': 'accountant123', 'user_type': 'staff',
     'first_name': 'Hoàng', 'last_name': 'Kế Toán', 'phone': '0904567890', 'role': '📊 Kế toán'},

    # CUSTOMERS
    {'email': 'testcustomer@example.com', 'password': 'customer123', 'user_type': 'customer',
     'first_name': 'Nguyễn', 'last_name': 'Văn Test', 'phone': '0912345678', 'role': '📱 Khách hàng'},
    
    {'email': 'customer1@example.com', 'password': 'customer123', 'user_type': 'customer',
     'first_name': 'Trần', 'last_name': 'Thị B', 'phone': '0923456789', 'role': '📱 Khách hàng'},
    
    {'email': 'customer2@example.com', 'password': 'customer123', 'user_type': 'customer',
     'first_name': 'Lê', 'last_name': 'Văn C', 'phone': '0934567890', 'role': '📱 Khách hàng'},
]

created_users = {}
for config in users_config:
    email = config['email']
    
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        print(f"   ⏭️  Đã tồn tại: {config['role']:25} | {email}")
    else:
        user = User.objects.create_user(
            email=email,
            password=config['password'],
            user_type=config['user_type'],
            first_name=config['first_name'],
            last_name=config['last_name'],
            phone=config['phone']
        )
        print(f"   ✅ Tạo mới: {config['role']:25} | {email}")
    
    created_users[email] = user
    
    # Group by type
    if config['user_type'] == 'customer':
        if 'customers' not in created_users:
            created_users['customers'] = []
        created_users['customers'].append(user)

print(f"\n   📊 Tổng số users: {User.objects.count()}")

# =============================================================================
# 2. TẠO DANH MỤC
# =============================================================================
print("\n📋 BƯỚC 2: TẠO DANH MỤC SẢN PHẨM")
print("-"*70)

categories_data = [
    {'name': 'Tôm', 'description': 'Các loại tôm tươi sống'},
    {'name': 'Cá', 'description': 'Cá biển tươi sống'},
    {'name': 'Mực', 'description': 'Mực ống, bạch tuộc'},
    {'name': 'Cua Ghẹ', 'description': 'Cua ghẹ các loại'},
    {'name': 'Ốc', 'description': 'Ốc biển tươi sống'},
    {'name': 'Sò Điệp', 'description': 'Sò điệp, nghêu, ngao'},
]

categories = {}
for cat_data in categories_data:
    category, created = SeafoodCategory.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categories[cat_data['name']] = category
    status = "✅" if created else "⏭️ "
    print(f"   {status} {cat_data['name']:15} | {cat_data['description']}")

print(f"\n   📊 Tổng số danh mục: {SeafoodCategory.objects.count()}")

# =============================================================================
# 3. TẠO SẢN PHẨM
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
    # Mực
    {'name': 'Mực Ống', 'price': 220000, 'unit': 'kg', 'category': 'Mực', 'stock': 35},
    {'name': 'Bạch Tuộc', 'price': 380000, 'unit': 'kg', 'category': 'Mực', 'stock': 15},
    # Cua Ghẹ
    {'name': 'Ghẹ Xanh', 'price': 300000, 'unit': 'kg', 'category': 'Cua Ghẹ', 'stock': 45},
    {'name': 'Cua Hoàng Đế', 'price': 2500000, 'unit': 'kg', 'category': 'Cua Ghẹ', 'stock': 5},
    # Ốc
    {'name': 'Ốc Hương', 'price': 150000, 'unit': 'kg', 'category': 'Ốc', 'stock': 40},
    {'name': 'Ốc Móng Tay', 'price': 90000, 'unit': 'kg', 'category': 'Ốc', 'stock': 50},
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
            'description': f"{prod_data['name']} tươi sống, chất lượng cao"
        }
    )
    products.append(product)
    status = "✅" if created else "⏭️ "
    print(f"   {status} {prod_data['name']:18} | {prod_data['price']:>9,}đ/{prod_data['unit']} | Stock: {prod_data['stock']:>3}")

print(f"\n   📊 Tổng số sản phẩm: {Seafood.objects.count()}")

# =============================================================================
# 4. TẠO ĐƠN HÀNG MẪU
# =============================================================================
print("\n📋 BƯỚC 4: TẠO ĐƠN HÀNG MẪU")
print("-"*70)

customers_list = created_users.get('customers', [])
if not customers_list:
    print("   ⚠️  Không có customer nào để tạo đơn hàng")
else:
    addresses = [
        "123 Nguyễn Văn Linh, Phường Bình Thuận, Quận 7, TP.HCM",
        "456 Lê Văn Việt, Phường Tân Phú, Quận 9, TP.HCM",
        "789 Võ Văn Ngân, Phường Linh Chiểu, TP Thủ Đức, TP.HCM",
    ]
    
    orders_config = [
        {
            'status': 'pending',
            'payment_status': 'pending_verification',
            'payment_method': 'bank_transfer',
            'customer_source': 'facebook',
            'items': [(0, 2), (8, 1)],  # Tôm Sú x2, Mực Ống x1
        },
        {
            'status': 'confirmed',
            'payment_status': 'paid',
            'payment_method': 'cash',
            'customer_source': 'zalo',
            'items': [(4, 3), (10, 1)],  # Cá Hồi x3, Ghẹ Xanh x1
        },
        {
            'status': 'completed',
            'payment_status': 'paid',
            'payment_method': 'cod',
            'customer_source': 'telephone',
            'items': [(1, 1), (9, 2), (12, 1)],  # Tôm Hùm, Bạch Tuộc, Ốc Hương
        },
    ]
    
    for i, order_config in enumerate(orders_config):
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
            notes=f"Đơn hàng mẫu #{i+1}"
        )
        
        total_amount = Decimal('0')
        items_desc = []
        
        for product_idx, quantity in order_config['items']:
            product = products[product_idx]
            qty = Decimal(str(quantity))
            
            OrderItem.objects.create(
                order=order,
                seafood=product,
                quantity=qty,
                unit_price=product.price,
                total_price=product.price * qty
            )
            total_amount += product.price * qty
            items_desc.append(f"{product.name} x{quantity}")
        
        order.total_amount = total_amount
        if order_config['payment_status'] == 'paid':
            order.paid_amount = total_amount
        order.save()
        
        status_icon = {'pending': '⏳', 'confirmed': '✅', 'completed': '✨'}.get(order.status, '📦')
        print(f"   {status_icon} #{order.order_code} | {order.get_status_display():12} | {total_amount:>10,}đ")
    
    print(f"\n   📊 Tổng số đơn hàng: {Order.objects.count()}")

# =============================================================================
# THỐNG KÊ CUỐI
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
print(f"  👥 Users:         {User.objects.count():>3}")
print(f"  📂 Danh mục:      {SeafoodCategory.objects.count():>3}")
print(f"  🐟 Sản phẩm:      {Seafood.objects.count():>3}")
print(f"  📦 Đơn hàng:      {Order.objects.count():>3}")

print("\n🚀 SỬ DỤNG:")
print("  • Login: http://localhost:3000/auth/login")
print("  • Dashboard: http://localhost:3000/dashboard")
print("  • Đặt hàng: http://localhost:3000/order")

print("\n" + "="*70 + "\n")
