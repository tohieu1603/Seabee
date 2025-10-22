"""
Management command to seed seafood database with initial data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.seafood import seed_data
from apps.seafood.models import (
    SeafoodCategory, Seafood, ImportSource, ImportBatch, Order, OrderItem, InventoryLog
)
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed seafood database with initial data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting seafood data seeding...'))

        # Clear existing data
        self.stdout.write('Clearing existing data...')
        OrderItem.objects.all().delete()
        Order.objects.all().delete()
        InventoryLog.objects.all().delete()
        ImportBatch.objects.all().delete()
        ImportSource.objects.all().delete()
        Seafood.objects.all().delete()
        SeafoodCategory.objects.all().delete()

        # Get existing admin user for orders
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@seafood.com',
                    password='admin123'
                )
                self.stdout.write(self.style.SUCCESS('Created admin user'))
            else:
                self.stdout.write(f'Using existing admin user: {admin_user.username}')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error getting admin user: {e}'))
            return

        # 1. Create Categories
        self.stdout.write('Creating categories...')
        categories = {}
        for cat_data in seed_data.CATEGORIES:
            category = SeafoodCategory.objects.create(**cat_data)
            categories[category.name] = category
            self.stdout.write(f'  - Created category: {category.name}')

        # 2. Create Seafood Products
        self.stdout.write('Creating seafood products...')
        seafood_products = {}
        for product_data in seed_data.SEAFOOD_PRODUCTS:
            category_name = product_data.pop('category')
            product_data['category'] = categories[category_name]
            seafood = Seafood.objects.create(**product_data)
            seafood_products[seafood.code] = seafood
            self.stdout.write(f'  - Created product: {seafood.name} - {seafood.current_price:,.0f}đ/kg')

        # 3. Create Import Sources
        self.stdout.write('Creating import sources...')
        import_sources = {}
        for source_data in seed_data.IMPORT_SOURCES:
            source = ImportSource.objects.create(**source_data)
            import_sources[source.name] = source
            self.stdout.write(f'  - Created source: {source.name}')

        # 4. Create Import Batches
        self.stdout.write('Creating import batches...')
        import_batches = {}
        for batch_data in seed_data.IMPORT_BATCHES:
            seafood_code = batch_data.pop('seafood_code')
            source_name = batch_data.pop('import_source')
            batch_data['seafood'] = seafood_products[seafood_code]
            batch_data['import_source'] = import_sources[source_name]
            batch_data['imported_by'] = admin_user
            batch = ImportBatch.objects.create(**batch_data)
            import_batches[batch.batch_code] = batch
            self.stdout.write(f'  - Created batch: {batch.batch_code} - {batch.seafood.name}')

        # 5. Create Sample Orders
        self.stdout.write('Creating sample orders...')
        for order_data in seed_data.SAMPLE_ORDERS:
            items = order_data.pop('items')
            order_data['created_by'] = admin_user

            # Calculate totals
            subtotal = Decimal('0')
            for item in items:
                item_total = Decimal(str(item['weight'])) * Decimal(str(item['unit_price']))
                subtotal += item_total

            order_data['subtotal'] = subtotal
            order_data['total_amount'] = subtotal - Decimal(str(order_data.get('discount_amount', 0)))
            order_data['paid_amount'] = order_data['total_amount'] if order_data.get('payment_status') == 'paid' else Decimal('0')

            order = Order.objects.create(**order_data)

            for item_data in items:
                seafood_code = item_data.pop('seafood_code')
                batch_code = item_data.pop('batch_code', None)

                item_data['order'] = order
                item_data['seafood'] = seafood_products[seafood_code]
                if batch_code:
                    item_data['import_batch'] = import_batches.get(batch_code)

                # Calculate item subtotal
                item_data['subtotal'] = Decimal(str(item_data['weight'])) * Decimal(str(item_data['unit_price']))

                order_item = OrderItem.objects.create(**item_data)

                # Update stock
                seafood = seafood_products[seafood_code]
                weight_decimal = Decimal(str(item_data['weight']))
                seafood.stock_quantity = Decimal(str(seafood.stock_quantity)) - weight_decimal
                seafood.save()

                # Update batch remaining weight
                if batch_code and batch_code in import_batches:
                    batch = import_batches[batch_code]
                    batch.remaining_weight = Decimal(str(batch.remaining_weight)) - weight_decimal
                    batch.save()

            self.stdout.write(f'  - Created order: {order.order_code} - {order.total_amount:,.0f}đ ({len(items)} items)')

        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Seeding Complete ==='))
        self.stdout.write(f'Categories: {SeafoodCategory.objects.count()}')
        self.stdout.write(f'Seafood Products: {Seafood.objects.count()}')
        self.stdout.write(f'Import Sources: {ImportSource.objects.count()}')
        self.stdout.write(f'Import Batches: {ImportBatch.objects.count()}')
        self.stdout.write(f'Orders: {Order.objects.count()}')
        self.stdout.write(f'Order Items: {OrderItem.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\nDatabase seeded successfully!'))
