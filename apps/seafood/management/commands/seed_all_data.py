"""
Management command để seed toàn bộ dữ liệu: categories, products, import batches, orders
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import models
from apps.seafood.models import (
    SeafoodCategory, Seafood, ImportSource, ImportBatch,
    Order, OrderItem, InventoryLog
)
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed toàn bộ dữ liệu cho hệ thống bán hải sản'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Bắt đầu seed toàn bộ dữ liệu...\n')

        # Get users for assignment
        try:
            admin_user = User.objects.filter(email='admin@seafood.com').first()
            sale_user = User.objects.filter(email='sale1@seafood.com').first()
            warehouse_user = User.objects.filter(email='warehouse@seafood.com').first()

            if not admin_user:
                admin_user = User.objects.first()
            if not sale_user:
                sale_user = admin_user
            if not warehouse_user:
                warehouse_user = admin_user

        except Exception:
            admin_user = User.objects.first()
            sale_user = admin_user
            warehouse_user = admin_user

        # ============================================
        # 1. CREATE CATEGORIES
        # ============================================
        self.stdout.write('📂 Tạo danh mục...')

        categories_data = [
            {'name': 'Tôm', 'slug': 'tom', 'description': 'Các loại tôm tươi sống, đông lạnh', 'sort_order': 1},
            {'name': 'Cua', 'slug': 'cua', 'description': 'Cua biển, cua hoàng đế', 'sort_order': 2},
            {'name': 'Cá', 'slug': 'ca', 'description': 'Cá biển tươi sống', 'sort_order': 3},
            {'name': 'Mực', 'slug': 'muc', 'description': 'Mực tươi, mực ống', 'sort_order': 4},
            {'name': 'Ốc', 'slug': 'oc', 'description': 'Ốc hương, ốc len', 'sort_order': 5},
            {'name': 'Ngao Sò', 'slug': 'ngao-so', 'description': 'Ngao, sò điệp, nghêu', 'sort_order': 6},
            {'name': 'Hàu', 'slug': 'hau', 'description': 'Hàu tươi sống', 'sort_order': 7},
            {'name': 'Ghẹ', 'slug': 'ghe', 'description': 'Ghẹ xanh, ghẹ hoa', 'sort_order': 8},
        ]

        categories = {}
        for cat_data in categories_data:
            cat, created = SeafoodCategory.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description'],
                    'sort_order': cat_data['sort_order']
                }
            )
            categories[cat.slug] = cat
            status = '🆕' if created else '✓'
            self.stdout.write(f'  {status} {cat.name}')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Đã tạo {len(categories)} danh mục\n'))

        # ============================================
        # 2. CREATE IMPORT SOURCES
        # ============================================
        self.stdout.write('📞 Tạo nguồn nhập hàng...')

        sources_data = [
            {
                'name': 'Chợ Bình Điền',
                'source_type': 'market',
                'contact_info': {'phone': '0909123456', 'address': 'Quận 8, TP.HCM'}
            },
            {
                'name': 'Nguyễn Văn A - Facebook',
                'source_type': 'facebook',
                'contact_info': {'facebook_url': 'facebook.com/nguyenvana', 'phone': '0901234567'}
            },
            {
                'name': 'Trần Thị B - Zalo',
                'source_type': 'zalo',
                'contact_info': {'zalo_id': '0907654321', 'phone': '0907654321'}
            },
            {
                'name': 'Công ty Hải Sản Phú Quốc',
                'source_type': 'company',
                'contact_info': {'phone': '0297123456', 'email': 'info@haisan-phuquoc.com'}
            },
            {
                'name': 'Chợ Hải Sản Vũng Tàu',
                'source_type': 'market',
                'contact_info': {'phone': '0254123456', 'address': 'Vũng Tàu'}
            },
        ]

        sources = {}
        for src_data in sources_data:
            src, created = ImportSource.objects.get_or_create(
                name=src_data['name'],
                defaults={
                    'source_type': src_data['source_type'],
                    'contact_info': src_data['contact_info']
                }
            )
            sources[src.name] = src
            status = '🆕' if created else '✓'
            self.stdout.write(f'  {status} {src.name}')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Đã tạo {len(sources)} nguồn nhập hàng\n'))

        # ============================================
        # 3. CREATE SEAFOOD PRODUCTS
        # ============================================
        self.stdout.write('🦐 Tạo sản phẩm hải sản...')

        products_data = [
            # TÔM
            {
                'code': 'TOM001',
                'name': 'Tôm Hùm Alaska',
                'category': 'tom',
                'current_price': 1500000,
                'stock_quantity': 25.5,
                'description': 'Tôm hùm Alaska tươi sống, size lớn',
                'origin': 'Alaska, Mỹ',
                'status': 'active',
                'tags': ['cao cấp', 'tươi sống', 'nhập khẩu']
            },
            {
                'code': 'TOM002',
                'name': 'Tôm Sú',
                'category': 'tom',
                'current_price': 450000,
                'stock_quantity': 45.2,
                'description': 'Tôm sú tươi sống, size 3-4 con/kg',
                'origin': 'Cà Mau',
                'status': 'active',
                'tags': ['tươi sống', 'trong nước']
            },
            {
                'code': 'TOM003',
                'name': 'Tôm Càng Xanh',
                'category': 'tom',
                'current_price': 380000,
                'stock_quantity': 32.8,
                'description': 'Tôm càng xanh tươi sống',
                'origin': 'Đồng Nai',
                'status': 'active',
                'tags': ['tươi sống', 'nuôi']
            },

            # CUA
            {
                'code': 'CUA001',
                'name': 'Cua Hoàng Đế',
                'category': 'cua',
                'current_price': 2800000,
                'stock_quantity': 15.3,
                'description': 'Cua hoàng đế Alaska, size khủng',
                'origin': 'Alaska, Mỹ',
                'status': 'active',
                'tags': ['cao cấp', 'tươi sống', 'nhập khẩu']
            },
            {
                'code': 'CUA002',
                'name': 'Cua Gạch',
                'category': 'cua',
                'current_price': 650000,
                'stock_quantity': 28.5,
                'description': 'Cua gạch biển, nhiều gạch',
                'origin': 'Cà Mau',
                'status': 'active',
                'tags': ['tươi sống', 'trong nước']
            },

            # CÁ
            {
                'code': 'CA001',
                'name': 'Cá Hồi Na Uy',
                'category': 'ca',
                'current_price': 520000,
                'stock_quantity': 55.7,
                'description': 'Cá hồi Na Uy tươi nguyên con',
                'origin': 'Na Uy',
                'status': 'active',
                'tags': ['cao cấp', 'tươi', 'nhập khẩu']
            },
            {
                'code': 'CA002',
                'name': 'Cá Mú',
                'category': 'ca',
                'current_price': 380000,
                'stock_quantity': 42.3,
                'description': 'Cá mú tươi sống',
                'origin': 'Phú Quốc',
                'status': 'active',
                'tags': ['tươi sống', 'trong nước']
            },
            {
                'code': 'CA003',
                'name': 'Cá Chẽm',
                'category': 'ca',
                'current_price': 280000,
                'stock_quantity': 38.9,
                'description': 'Cá chẽm biển tươi',
                'origin': 'Vũng Tàu',
                'status': 'active',
                'tags': ['tươi sống']
            },

            # MỰC
            {
                'code': 'MUC001',
                'name': 'Mực Ống Tươi',
                'category': 'muc',
                'current_price': 220000,
                'stock_quantity': 62.5,
                'description': 'Mực ống tươi sống, size to',
                'origin': 'Vũng Tàu',
                'status': 'active',
                'tags': ['tươi sống']
            },
            {
                'code': 'MUC002',
                'name': 'Mực Nang',
                'category': 'muc',
                'current_price': 180000,
                'stock_quantity': 48.2,
                'description': 'Mực nang tươi',
                'origin': 'Phan Thiết',
                'status': 'active',
                'tags': ['tươi sống']
            },

            # ỐC
            {
                'code': 'OC001',
                'name': 'Ốc Hương',
                'category': 'oc',
                'current_price': 350000,
                'stock_quantity': 75.8,
                'description': 'Ốc hương tươi sống, size đại',
                'origin': 'Nha Trang',
                'status': 'active',
                'tags': ['tươi sống', 'cao cấp']
            },
            {
                'code': 'OC002',
                'name': 'Ốc Len',
                'category': 'oc',
                'current_price': 120000,
                'stock_quantity': 95.3,
                'description': 'Ốc len tươi',
                'origin': 'Cà Mau',
                'status': 'active',
                'tags': ['tươi sống']
            },

            # NGAO SÒ
            {
                'code': 'NGAO001',
                'name': 'Sò Điệp',
                'category': 'ngao-so',
                'current_price': 280000,
                'stock_quantity': 68.4,
                'description': 'Sò điệp tươi sống',
                'origin': 'Nha Trang',
                'status': 'active',
                'tags': ['tươi sống', 'cao cấp']
            },
            {
                'code': 'NGAO002',
                'name': 'Nghêu',
                'category': 'ngao-so',
                'current_price': 85000,
                'stock_quantity': 125.7,
                'description': 'Nghêu tươi',
                'origin': 'Cà Mau',
                'status': 'active',
                'tags': ['tươi sống']
            },

            # HÀU
            {
                'code': 'HAU001',
                'name': 'Hàu Sữa Phú Quốc',
                'category': 'hau',
                'current_price': 320000,
                'stock_quantity': 82.5,
                'description': 'Hàu sữa tươi sống Phú Quốc',
                'origin': 'Phú Quốc',
                'status': 'active',
                'tags': ['tươi sống', 'cao cấp']
            },

            # GHẸ
            {
                'code': 'GHE001',
                'name': 'Ghẹ Xanh',
                'category': 'ghe',
                'current_price': 450000,
                'stock_quantity': 35.6,
                'description': 'Ghẹ xanh tươi sống, có gạch',
                'origin': 'Cà Mau',
                'status': 'active',
                'tags': ['tươi sống']
            },
            {
                'code': 'GHE002',
                'name': 'Ghẹ Hoa',
                'category': 'ghe',
                'current_price': 380000,
                'stock_quantity': 42.3,
                'description': 'Ghẹ hoa tươi sống',
                'origin': 'Vũng Tàu',
                'status': 'active',
                'tags': ['tươi sống']
            },
        ]

        products = {}
        for prod_data in products_data:
            prod, created = Seafood.objects.get_or_create(
                code=prod_data['code'],
                defaults={
                    'name': prod_data['name'],
                    'category': categories[prod_data['category']],
                    'current_price': prod_data['current_price'],
                    'stock_quantity': prod_data['stock_quantity'],
                    'description': prod_data['description'],
                    'origin': prod_data['origin'],
                    'status': prod_data['status'],
                    'tags': prod_data['tags']
                }
            )
            products[prod.code] = prod
            status = '🆕' if created else '✓'
            self.stdout.write(f'  {status} {prod.code} - {prod.name} - {prod.stock_quantity}kg')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Đã tạo {len(products)} sản phẩm\n'))

        # ============================================
        # 4. CREATE IMPORT BATCHES
        # ============================================
        self.stdout.write('📦 Tạo lô nhập hàng...')

        import_batches = []
        batch_counter = 1

        # Tạo 2-3 lô cho mỗi sản phẩm
        for prod_code, product in products.items():
            num_batches = random.randint(2, 3)

            for i in range(num_batches):
                days_ago = random.randint(1, 30)
                import_date = timezone.now().date() - timedelta(days=days_ago)

                # Tính giá nhập/bán
                import_price = int(product.current_price * Decimal('0.7'))  # 70% giá bán
                sell_price = product.current_price

                # Tính số lượng
                total_weight = Decimal(str(random.uniform(10, 50))).quantize(Decimal('0.01'))
                remaining_weight = Decimal(str(random.uniform(5, total_weight))).quantize(Decimal('0.01'))

                batch = ImportBatch.objects.create(
                    seafood=product,
                    batch_code=f'BATCH{batch_counter:05d}',
                    import_source=random.choice(list(sources.values())),
                    import_date=import_date,
                    import_price=import_price,
                    sell_price=sell_price,
                    total_weight=total_weight,
                    remaining_weight=remaining_weight,
                    status='selling' if remaining_weight > 0 else 'sold_out',
                    imported_by=warehouse_user,
                    notes=f'Lô nhập {import_date}'
                )

                import_batches.append(batch)
                batch_counter += 1

                self.stdout.write(f'  ✓ {batch.batch_code} - {product.name} - {total_weight}kg')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Đã tạo {len(import_batches)} lô nhập hàng\n'))

        # ============================================
        # 5. CREATE ORDERS
        # ============================================
        self.stdout.write('📋 Tạo đơn hàng...')

        customers_data = [
            {'name': 'Nguyễn Văn A', 'phone': '0901234567', 'address': '123 Lê Lợi, Q1, TP.HCM'},
            {'name': 'Trần Thị B', 'phone': '0902345678', 'address': '456 Nguyễn Huệ, Q1, TP.HCM'},
            {'name': 'Lê Văn C', 'phone': '0903456789', 'address': '789 Trần Hưng Đạo, Q5, TP.HCM'},
            {'name': 'Phạm Thị D', 'phone': '0904567890', 'address': '321 Võ Văn Tần, Q3, TP.HCM'},
            {'name': 'Hoàng Văn E', 'phone': '0905678901', 'address': '654 Cách Mạng Tháng 8, Q10, TP.HCM'},
            {'name': 'Vũ Thị F', 'phone': '0906789012', 'address': '987 Lý Thường Kiệt, Q11, TP.HCM'},
            {'name': 'Đặng Văn G', 'phone': '0907890123', 'address': '147 Hai Bà Trưng, Q3, TP.HCM'},
            {'name': 'Bùi Thị H', 'phone': '0908901234', 'address': '258 Điện Biên Phủ, Bình Thạnh, TP.HCM'},
        ]

        order_counter = 1
        orders = []

        # Tạo 20 đơn hàng
        for i in range(20):
            # Random customer
            customer = random.choice(customers_data)

            # Random date trong 30 ngày qua
            days_ago = random.randint(0, 30)
            order_date = timezone.now() - timedelta(days=days_ago)

            # Random payment method và status
            payment_method = random.choice(['cash', 'transfer', 'momo'])
            payment_status = random.choice(['paid', 'paid', 'paid', 'pending'])  # 75% paid
            status = random.choice(['completed', 'completed', 'completed', 'pending'])  # 75% completed

            # Create order
            order = Order.objects.create(
                order_code=f'ORD{order_counter:05d}',
                customer_name=customer['name'],
                customer_phone=customer['phone'],
                customer_address=customer['address'],
                subtotal=0,  # Will calculate later
                discount_amount=0,
                total_amount=0,  # Will calculate later
                payment_method=payment_method,
                payment_status=payment_status,
                paid_amount=0,  # Will calculate later
                status=status,
                notes=f'Đơn hàng tạo {order_date.strftime("%d/%m/%Y")}',
                created_by=sale_user
            )
            order.created_at = order_date
            order.save()

            # Create 1-4 order items
            num_items = random.randint(1, 4)
            selected_products = random.sample(list(products.values()), num_items)

            subtotal = Decimal('0')

            for product in selected_products:
                # Random weight
                weight = Decimal(str(random.uniform(0.5, 5.0))).quantize(Decimal('0.01'))

                # Get a batch for this product
                batch = random.choice([b for b in import_batches if b.seafood == product])

                # Create order item
                item = OrderItem.objects.create(
                    order=order,
                    seafood=product,
                    import_batch=batch,
                    weight=weight,
                    unit_price=product.current_price,
                    notes=''
                )

                subtotal += item.subtotal

            # Update order totals
            discount = Decimal(str(random.choice([0, 0, 0, 10000, 20000, 50000])))  # 50% no discount
            order.subtotal = subtotal
            order.discount_amount = discount
            order.total_amount = subtotal - discount
            order.paid_amount = order.total_amount if payment_status == 'paid' else 0
            order.save()

            orders.append(order)
            order_counter += 1

            self.stdout.write(f'  ✓ {order.order_code} - {order.customer_name} - {order.items.count()} items - {order.total_amount:,.0f}đ')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Đã tạo {len(orders)} đơn hàng\n'))

        # ============================================
        # 6. SUMMARY
        # ============================================
        self.stdout.write(self.style.SUCCESS('='*60))
        self.stdout.write(self.style.SUCCESS('🎉 HOÀN THÀNH SEED DỮ LIỆU!'))
        self.stdout.write(self.style.SUCCESS('='*60))

        self.stdout.write('\n📊 THỐNG KÊ:')
        self.stdout.write(f'  • Danh mục: {SeafoodCategory.objects.count()}')
        self.stdout.write(f'  • Nguồn nhập hàng: {ImportSource.objects.count()}')
        self.stdout.write(f'  • Sản phẩm: {Seafood.objects.count()}')
        self.stdout.write(f'  • Lô nhập hàng: {ImportBatch.objects.count()}')
        self.stdout.write(f'  • Đơn hàng: {Order.objects.count()}')
        self.stdout.write(f'  • Chi tiết đơn hàng: {OrderItem.objects.count()}')

        # Tính tổng doanh thu
        total_revenue = Order.objects.filter(status='completed').aggregate(
            total=models.Sum('total_amount')
        )['total'] or 0

        self.stdout.write(f'\n💰 DOANH THU:')
        self.stdout.write(f'  • Tổng doanh thu (đơn hoàn thành): {total_revenue:,.0f}đ')

        self.stdout.write('\n📦 KHO HÀNG:')
        total_stock_value = sum(
            p.stock_quantity * p.current_price
            for p in Seafood.objects.all()
        )
        self.stdout.write(f'  • Tổng giá trị tồn kho: {total_stock_value:,.0f}đ')

        self.stdout.write(self.style.SUCCESS('\n✅ Dữ liệu đã sẵn sàng để sử dụng!'))
