#!/usr/bin/env python3
"""
Script tạo nhanh user và data mẫu cho hệ thống
Chạy: python3 manage.py shell < create_sample_data.py
"""

from django.contrib.auth import get_user_model
from apps.seafood.models import Seafood, Category, Order, OrderItem
from decimal import Decimal
import random

User = get_user_model()

print("=" * 60)
print("BẮT ĐẦU TẠO DATA MẪU")
print("=" * 60)

# 1. TẠO USERS
print("\n1. Tạo Users...")

users_data = [
    {
        'email': 'admin@seafood.com',
        'password': 'admin123',
        'user_type': 'admin',
        'full_name': 'Quản Trị Viên',
        'phone': '0901234567'
    },
    {
        'email': 'customer1@example.com',
        'password': 'customer123',
        'user_type': 'customer',
        'full_name': 'Nguyễn Văn A',
        'phone': '0912345678'
    },
    {
        'email': 'customer2@example.com',
        'password': 'customer123',
        'user_type': 'customer',
        'full_name': 'Trần Thị B',
        'phone': '0923456789'
    },
    {
        'email': 'staff1@seafood.com',
        'password': 'staff123',
        'user_type': 'staff',
        'full_name': 'Lê Văn C',
        'phone': '0934567890'
    }
]

created_users = {}
for user_data in users_data:
    email = user_data['email']
    if User.objects.filter(email=email).exists():
        user = User.objects.get(email=email)
        print(f"   ✓ User đã tồn tại: {email}")
    else:
        user = User.objects.create_user(
            email=email,
            password=user_data['password'],
            user_type=user_data['user_type'],
            full_name=user_data['full_name'],
            phone=user_data.get('phone', '')
        )
        print(f"   ✓ Tạo mới: {email} - {user_data['full_name']}")
    
    created_users[user_data['user_type']] = user

# 2. TẠO CATEGORIES
print("\n2. Tạo Danh Mục Sản Phẩm...")

categories_data = [
    {'name': 'Tôm', 'description': 'Các loại tôm tươi sống'},
    {'name': 'Cá', 'description': 'Cá biển tươi sống'},
    {'name': 'Mực', 'description': 'Mực và bạch tuộc'},
    {'name': 'Cua Ghẹ', 'description': 'Cua ghẹ các loại'},
    {'name': 'Ốc', 'description': 'Ốc biển tươi sống'}
]

categories = {}
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categories[cat_data['name']] = category
    status = "Tạo mới" if created else "Đã tồn tại"
    print(f"   ✓ {status}: {cat_data['name']}")

# 3. TẠO SEAFOOD PRODUCTS
print("\n3. Tạo Sản Phẩm Hải Sản...")

products_data = [
    # Tôm
    {'name': 'Tôm Sú', 'price': 350000, 'unit': 'kg', 'category': 'Tôm', 'stock': 50},
    {'name': 'Tôm Hùm', 'price': 1200000, 'unit': 'kg', 'category': 'Tôm', 'stock': 20},
    {'name': 'Tôm Càng Xanh', 'price': 280000, 'unit': 'kg', 'category': 'Tôm', 'stock': 40},
    
    # Cá
    {'name': 'Cá Hồi', 'price': 450000, 'unit': 'kg', 'category': 'Cá', 'stock': 30},
    {'name': 'Cá Chẽm', 'price': 180000, 'unit': 'kg', 'category': 'Cá', 'stock': 25},
    {'name': 'Cá Basa', 'price': 120000, 'unit': 'kg', 'category': 'Cá', 'stock': 60},
    
    # Mực
    {'name': 'Mực Ống', 'price': 220000, 'unit': 'kg', 'category': 'Mực', 'stock': 35},
    {'name': 'Bạch Tuộc', 'price': 380000, 'unit': 'kg', 'category': 'Mực', 'stock': 15},
    
    # Cua Ghẹ
    {'name': 'Ghẹ Xanh', 'price': 300000, 'unit': 'kg', 'category': 'Cua Ghẹ', 'stock': 45},
    {'name': 'Cua Hoàng Đế', 'price': 2500000, 'unit': 'kg', 'category': 'Cua Ghẹ', 'stock': 5},
    
    # Ốc
    {'name': 'Ốc Hương', 'price': 150000, 'unit': 'kg', 'category': 'Ốc', 'stock': 40},
    {'name': 'Ốc Móng Tay', 'price': 90000, 'unit': 'kg', 'category': 'Ốc', 'stock': 50}
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
    status = "Tạo mới" if created else "Đã tồn tại"
    print(f"   ✓ {status}: {prod_data['name']} - {prod_data['price']:,}đ/{prod_data['unit']}")

# 4. TẠO ĐỢN HÀNG MẪU
print("\n4. Tạo Đơn Hàng Mẫu...")

customer = created_users.get('customer')
if customer:
    orders_data = [
        {
            'status': 'pending',
            'payment_status': 'pending_verification',
            'payment_method': 'bank_transfer',
            'customer_source': 'facebook',
            'items': [
                {'product': products[0], 'quantity': 2},  # Tôm Sú
                {'product': products[6], 'quantity': 1},  # Mực Ống
            ]
        },
        {
            'status': 'confirmed',
            'payment_status': 'paid',
            'payment_method': 'cash',
            'customer_source': 'zalo',
            'items': [
                {'product': products[3], 'quantity': 3},  # Cá Hồi
                {'product': products[8], 'quantity': 1},  # Ghẹ Xanh
            ]
        },
        {
            'status': 'completed',
            'payment_status': 'paid',
            'payment_method': 'cod',
            'customer_source': 'telephone',
            'items': [
                {'product': products[1], 'quantity': 1},  # Tôm Hùm
                {'product': products[7], 'quantity': 2},  # Bạch Tuộc
                {'product': products[10], 'quantity': 1}, # Ốc Hương
            ]
        }
    ]
    
    addresses = [
        "123 Nguyễn Văn Linh, Phường Bình Thuận, Quận 7, TP.HCM",
        "456 Lê Văn Việt, Phường Tân Phú, Quận 9, TP.HCM",
        "789 Võ Văn Ngân, Phường Linh Chiểu, TP Thủ Đức, TP.HCM"
    ]
    
    for i, order_data in enumerate(orders_data):
        order = Order.objects.create(
            customer=customer,
            customer_phone=customer.phone,
            customer_name=customer.full_name,
            customer_address=addresses[i],
            status=order_data['status'],
            payment_status=order_data['payment_status'],
            payment_method=order_data['payment_method'],
            customer_source=order_data['customer_source'],
            notes=f"Đơn hàng mẫu số {i+1}"
        )
        
        total_amount = Decimal('0')
        for item_data in order_data['items']:
            product = item_data['product']
            quantity = Decimal(str(item_data['quantity']))
            
            OrderItem.objects.create(
                order=order,
                seafood=product,
                quantity=quantity,
                unit_price=product.price,
                total_price=product.price * quantity
            )
            total_amount += product.price * quantity
        
        order.total_amount = total_amount
        if order_data['payment_status'] == 'paid':
            order.paid_amount = total_amount
        order.save()
        
        print(f"   ✓ Đơn hàng #{order.order_code} - {order.get_status_display()} - {total_amount:,}đ")

print("\n" + "=" * 60)
print("HOÀN THÀNH TẠO DATA MẪU!")
print("=" * 60)

print("\n📋 THÔNG TIN ĐĂNG NHẬP:")
print("-" * 60)
for user_data in users_data:
    print(f"  {user_data['user_type'].upper():10} | {user_data['email']:25} | {user_data['password']}")
print("-" * 60)

print("\n📊 THỐNG KÊ:")
print(f"  • Users: {User.objects.count()}")
print(f"  • Danh mục: {Category.objects.count()}")
print(f"  • Sản phẩm: {Seafood.objects.count()}")
print(f"  • Đơn hàng: {Order.objects.count()}")

print("\n✅ Sẵn sàng sử dụng!")
print("=" * 60)
