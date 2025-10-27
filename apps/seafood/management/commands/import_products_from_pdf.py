"""
Django management command to import seafood products from the PDF price list
Run: python3 manage.py import_products_from_pdf
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from apps.seafood.models import SeafoodCategory, Seafood
from decimal import Decimal


class Command(BaseCommand):
    help = 'Import all seafood products from PDF price list'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🐟 Bắt đầu import sản phẩm từ bảng giá PDF...'))

        # Step 1: Create categories
        self.create_categories()

        # Step 2: Import products
        self.import_products()

        self.stdout.write(self.style.SUCCESS('✅ Hoàn thành import!'))

    def create_categories(self):
        """Create all product categories from PDF"""
        self.stdout.write('📁 Tạo danh mục...')

        categories = [
            {
                'name': 'Hàng Tươi Sống',
                'description': 'Hải sản tươi sống cao cấp',
                'sort_order': 1,
            },
            {
                'name': 'Hàng Đông Lạnh',
                'description': 'Hải sản đông lạnh chất lượng',
                'sort_order': 2,
            },
            {
                'name': 'Hàng Ngộp',
                'description': 'Hải sản ngộp chất lượng',
                'sort_order': 3,
            },
            {
                'name': 'Công Cụ Dụng Cụ',
                'description': 'Công cụ và dụng cụ phục vụ',
                'sort_order': 4,
            },
        ]

        for cat_data in categories:
            category, created = SeafoodCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'slug': slugify(cat_data['name']),
                    'description': cat_data['description'],
                    'sort_order': cat_data['sort_order'],
                }
            )
            if created:
                self.stdout.write(f'  ✓ Tạo mới: {category.name}')
            else:
                self.stdout.write(f'  → Đã tồn tại: {category.name}')

    def import_products(self):
        """Import all products from PDF data"""
        self.stdout.write('📦 Import sản phẩm...')

        # Get category objects
        tuoi_song = SeafoodCategory.objects.get(name='Hàng Tươi Sống')
        dong_lanh = SeafoodCategory.objects.get(name='Hàng Đông Lạnh')
        hang_ngop = SeafoodCategory.objects.get(name='Hàng Ngộp')
        cong_cu = SeafoodCategory.objects.get(name='Công Cụ Dụng Cụ')

        # All products from PDF organized by category
        products_data = [
            # ===== HÀNG TƯƠI SỐNG =====
            {'code': 'TS.MN', 'name': 'Mực nhảy', 'category': tuoi_song, 'price': 760000, 'unit_type': 'kg'},
            {'code': 'TS.CHDN', 'name': 'Cua hoàng đế', 'category': tuoi_song, 'price': 1680000, 'unit_type': 'kg'},
            {'code': 'TS.MH', 'name': 'Mực hoa', 'category': tuoi_song, 'price': 800000, 'unit_type': 'kg'},
            {'code': 'TS.MNCC', 'name': 'Mực nang cực to', 'category': tuoi_song, 'price': 990000, 'unit_type': 'kg'},
            {'code': 'TS.MN', 'name': 'Mực nang', 'category': tuoi_song, 'price': 870000, 'unit_type': 'kg'},
            {'code': 'TS.MND', 'name': 'Mực nang đại', 'category': tuoi_song, 'price': 750000, 'unit_type': 'kg'},
            {'code': 'TS.MT', 'name': 'Mực trứng', 'category': tuoi_song, 'price': 850000, 'unit_type': 'kg'},
            {'code': 'TS.MTN', 'name': 'Mực trứng nhỏ', 'category': tuoi_song, 'price': 730000, 'unit_type': 'kg'},
            {'code': 'TS.ML', 'name': 'Mực lá', 'category': tuoi_song, 'price': 650000, 'unit_type': 'kg'},
            {'code': 'TS.ML1', 'name': 'Mực lá loại 1', 'category': tuoi_song, 'price': 510000, 'unit_type': 'kg'},
            {'code': 'TS.MLN', 'name': 'Mực lá nhỏ', 'category': tuoi_song, 'price': 290000, 'unit_type': 'kg'},
            {'code': 'TS.THL', 'name': 'Tôm hùm lông', 'category': tuoi_song, 'price': 1450000, 'unit_type': 'kg'},
            {'code': 'TS.TH', 'name': 'Tôm hùm', 'category': tuoi_song, 'price': 2200000, 'unit_type': 'kg'},
            {'code': 'TS.TĐN', 'name': 'Tôm đất nhảy', 'category': tuoi_song, 'price': 310000, 'unit_type': 'kg'},
            {'code': 'TS.TĐT', 'name': 'Tôm đất to', 'category': tuoi_song, 'price': 350000, 'unit_type': 'kg'},
            {'code': 'TS.TL', 'name': 'Tôm lớn', 'category': tuoi_song, 'price': 410000, 'unit_type': 'kg'},
            {'code': 'TS.TN', 'name': 'Tôm nhỏ', 'category': tuoi_song, 'price': 280000, 'unit_type': 'kg'},
            {'code': 'TS.TST', 'name': 'Tôm sú to', 'category': tuoi_song, 'price': 490000, 'unit_type': 'kg'},
            {'code': 'TS.TSV', 'name': 'Tôm sú vừa', 'category': tuoi_song, 'price': 390000, 'unit_type': 'kg'},
            {'code': 'TS.TSN', 'name': 'Tôm sú nhỏ', 'category': tuoi_song, 'price': 310000, 'unit_type': 'kg'},
            {'code': 'TS.GR', 'name': 'Ghẹ rang', 'category': tuoi_song, 'price': 550000, 'unit_type': 'kg'},
            {'code': 'TS.GTL', 'name': 'Ghẹ to lắm', 'category': tuoi_song, 'price': 680000, 'unit_type': 'kg'},
            {'code': 'TS.GT', 'name': 'Ghẹ to', 'category': tuoi_song, 'price': 610000, 'unit_type': 'kg'},
            {'code': 'TS.GV', 'name': 'Ghẹ vừa', 'category': tuoi_song, 'price': 510000, 'unit_type': 'kg'},
            {'code': 'TS.GN', 'name': 'Ghẹ nhỏ', 'category': tuoi_song, 'price': 410000, 'unit_type': 'kg'},
            {'code': 'TS.CH', 'name': 'Cua hoàng', 'category': tuoi_song, 'price': 280000, 'unit_type': 'kg'},
            {'code': 'TS.CB', 'name': 'Cua bể', 'category': tuoi_song, 'price': 180000, 'unit_type': 'kg'},
            {'code': 'TS.CG', 'name': 'Cua gạch', 'category': tuoi_song, 'price': 680000, 'unit_type': 'kg'},
            {'code': 'TS.HG', 'name': 'Hàu giống', 'category': tuoi_song, 'price': 90000, 'unit_type': 'kg'},
            {'code': 'TS.HVT', 'name': 'Hàu vỏ to', 'category': tuoi_song, 'price': 410000, 'unit_type': 'kg'},
            {'code': 'TS.HS', 'name': 'Hàu sữa', 'category': tuoi_song, 'price': 490000, 'unit_type': 'kg'},
            {'code': 'TS.HSL', 'name': 'Hàu sữa lớn', 'category': tuoi_song, 'price': 610000, 'unit_type': 'kg'},
            {'code': 'TS.SSH', 'name': 'Sò huyết', 'category': tuoi_song, 'price': 210000, 'unit_type': 'kg'},
            {'code': 'TS.SD', 'name': 'Sò dương', 'category': tuoi_song, 'price': 180000, 'unit_type': 'kg'},
            {'code': 'TS.SL', 'name': 'Sò lông', 'category': tuoi_song, 'price': 150000, 'unit_type': 'kg'},
            {'code': 'TS.SD1', 'name': 'Sò điệp', 'category': tuoi_song, 'price': 250000, 'unit_type': 'kg'},
            {'code': 'TS.OB', 'name': 'Ốc bươu', 'category': tuoi_song, 'price': 210000, 'unit_type': 'kg'},
            {'code': 'TS.OBN', 'name': 'Ốc bươu nhỏ', 'category': tuoi_song, 'price': 180000, 'unit_type': 'kg'},
            {'code': 'TS.OBCE', 'name': 'Ốc bươu cực to', 'category': tuoi_song, 'price': 250000, 'unit_type': 'kg'},
            {'code': 'TS.OH', 'name': 'Ốc hương', 'category': tuoi_song, 'price': 310000, 'unit_type': 'kg'},
            {'code': 'TS.OHN', 'name': 'Ốc hương nhỏ', 'category': tuoi_song, 'price': 210000, 'unit_type': 'kg'},
            {'code': 'TS.OM', 'name': 'Ốc móng tay', 'category': tuoi_song, 'price': 180000, 'unit_type': 'kg'},
            {'code': 'TS.OMTO', 'name': 'Ốc móng tay to', 'category': tuoi_song, 'price': 210000, 'unit_type': 'kg'},
            {'code': 'TS.ODL', 'name': 'Ốc đụn lớn', 'category': tuoi_song, 'price': 210000, 'unit_type': 'kg'},
            {'code': 'TS.ODV', 'name': 'Ốc đụn vừa', 'category': tuoi_song, 'price': 180000, 'unit_type': 'kg'},
            {'code': 'TS.OT', 'name': 'Ốc tai tượng', 'category': tuoi_song, 'price': 390000, 'unit_type': 'kg'},
            {'code': 'TS.ONN', 'name': 'Ốc nhảy nhót', 'category': tuoi_song, 'price': 290000, 'unit_type': 'kg'},
            {'code': 'TS.ON', 'name': 'Ốc nhảy', 'category': tuoi_song, 'price': 350000, 'unit_type': 'kg'},
            {'code': 'TS.TC', 'name': 'Tôm càng', 'category': tuoi_song, 'price': 180000, 'unit_type': 'kg'},
            {'code': 'TS.NH', 'name': 'Nghêu Hàn Quốc', 'category': tuoi_song, 'price': 110000, 'unit_type': 'kg'},
            {'code': 'TS.NB', 'name': 'Nghêu bể', 'category': tuoi_song, 'price': 90000, 'unit_type': 'kg'},
            {'code': 'TS.MK', 'name': 'Mực khoanh', 'category': tuoi_song, 'price': 410000, 'unit_type': 'kg'},

            # ===== HÀNG ĐÔNG LẠNH =====
            {'code': 'DL.MTDB', 'name': 'Mực trứng ĐB', 'category': dong_lanh, 'price': 1350000, 'unit_type': 'kg'},
            {'code': 'DL.MNDB', 'name': 'Mực nang ĐB', 'category': dong_lanh, 'price': 1400000, 'unit_type': 'kg'},
            {'code': 'DL.MTN', 'name': 'Mực trứng nhỏ', 'category': dong_lanh, 'price': 880000, 'unit_type': 'kg'},
            {'code': 'DL.MNĐA', 'name': 'Mực nang đại', 'category': dong_lanh, 'price': 1050000, 'unit_type': 'kg'},
            {'code': 'DL.M', 'name': 'Mực', 'category': dong_lanh, 'price': 680000, 'unit_type': 'kg'},
            {'code': 'DL.THL', 'name': 'Tôm hùm lông', 'category': dong_lanh, 'price': 1990000, 'unit_type': 'kg'},
            {'code': 'DL.TH', 'name': 'Tôm hùm', 'category': dong_lanh, 'price': 2990000, 'unit_type': 'kg'},
            {'code': 'DL.TN', 'name': 'Tôm nhỏ', 'category': dong_lanh, 'price': 410000, 'unit_type': 'kg'},
            {'code': 'DL.TL', 'name': 'Tôm lớn', 'category': dong_lanh, 'price': 550000, 'unit_type': 'kg'},
            {'code': 'DL.TĐN', 'name': 'Tôm đất nhảy', 'category': dong_lanh, 'price': 490000, 'unit_type': 'kg'},
            {'code': 'DL.TST', 'name': 'Tôm sú to', 'category': dong_lanh, 'price': 690000, 'unit_type': 'kg'},
            {'code': 'DL.TSV', 'name': 'Tôm sú vừa', 'category': dong_lanh, 'price': 550000, 'unit_type': 'kg'},
            {'code': 'DL.TSN', 'name': 'Tôm sú nhỏ', 'category': dong_lanh, 'price': 450000, 'unit_type': 'kg'},
            {'code': 'DL.GHĐ', 'name': 'Ghẹ Hoàng Đế', 'category': dong_lanh, 'price': 2300000, 'unit_type': 'kg'},
            {'code': 'DL.GT', 'name': 'Ghẹ to', 'category': dong_lanh, 'price': 880000, 'unit_type': 'kg'},
            {'code': 'DL.GV', 'name': 'Ghẹ vừa', 'category': dong_lanh, 'price': 650000, 'unit_type': 'kg'},
            {'code': 'DL.CH', 'name': 'Cua hoàng', 'category': dong_lanh, 'price': 410000, 'unit_type': 'kg'},
            {'code': 'DL.CB', 'name': 'Cua bể', 'category': dong_lanh, 'price': 280000, 'unit_type': 'kg'},
            {'code': 'DL.CG', 'name': 'Cua gạch', 'category': dong_lanh, 'price': 950000, 'unit_type': 'kg'},
            {'code': 'DL.HVT', 'name': 'Hàu vỏ to', 'category': dong_lanh, 'price': 550000, 'unit_type': 'kg'},
            {'code': 'DL.HS', 'name': 'Hàu sữa', 'category': dong_lanh, 'price': 650000, 'unit_type': 'kg'},
            {'code': 'DL.HSL', 'name': 'Hàu sữa lớn', 'category': dong_lanh, 'price': 850000, 'unit_type': 'kg'},
            {'code': 'DL.SSH', 'name': 'Sò huyết', 'category': dong_lanh, 'price': 310000, 'unit_type': 'kg'},
            {'code': 'DL.SD', 'name': 'Sò dương', 'category': dong_lanh, 'price': 280000, 'unit_type': 'kg'},
            {'code': 'DL.SL', 'name': 'Sò lông', 'category': dong_lanh, 'price': 210000, 'unit_type': 'kg'},
            {'code': 'DL.SD1', 'name': 'Sò điệp', 'category': dong_lanh, 'price': 350000, 'unit_type': 'kg'},
            {'code': 'DL.OH', 'name': 'Ốc hương', 'category': dong_lanh, 'price': 450000, 'unit_type': 'kg'},
            {'code': 'DL.OB', 'name': 'Ốc bươu', 'category': dong_lanh, 'price': 310000, 'unit_type': 'kg'},
            {'code': 'DL.OT', 'name': 'Ốc tai tượng', 'category': dong_lanh, 'price': 550000, 'unit_type': 'kg'},
            {'code': 'DL.OM', 'name': 'Ốc móng tay', 'category': dong_lanh, 'price': 250000, 'unit_type': 'kg'},
            {'code': 'DL.TC', 'name': 'Tôm càng', 'category': dong_lanh, 'price': 250000, 'unit_type': 'kg'},
            {'code': 'DL.NH', 'name': 'Nghêu Hàn Quốc', 'category': dong_lanh, 'price': 150000, 'unit_type': 'kg'},
            {'code': 'DL.ND', 'name': 'Nghêu Đài Loan', 'category': dong_lanh, 'price': 180000, 'unit_type': 'kg'},

            # ===== HÀNG NGỘP =====
            {'code': 'HN.MTĐ', 'name': 'Mực trứng đại', 'category': hang_ngop, 'price': 1150000, 'unit_type': 'kg'},
            {'code': 'HN.MT', 'name': 'Mực trứng', 'category': hang_ngop, 'price': 980000, 'unit_type': 'kg'},
            {'code': 'HN.MTN', 'name': 'Mực trứng nhỏ', 'category': hang_ngop, 'price': 710000, 'unit_type': 'kg'},
            {'code': 'HN.MH', 'name': 'Mực hoa', 'category': hang_ngop, 'price': 680000, 'unit_type': 'kg'},
            {'code': 'HN.MN', 'name': 'Mực nang', 'category': hang_ngop, 'price': 810000, 'unit_type': 'kg'},
            {'code': 'HN.MNĐ', 'name': 'Mực nang đại', 'category': hang_ngop, 'price': 680000, 'unit_type': 'kg'},
            {'code': 'HN.THL', 'name': 'Tôm hùm lông', 'category': hang_ngop, 'price': 1280000, 'unit_type': 'kg'},
            {'code': 'HN.TH', 'name': 'Tôm hùm', 'category': hang_ngop, 'price': 1990000, 'unit_type': 'kg'},
            {'code': 'HN.TĐN', 'name': 'Tôm đất nhảy', 'category': hang_ngop, 'price': 280000, 'unit_type': 'kg'},
            {'code': 'HN.TL', 'name': 'Tôm lớn', 'category': hang_ngop, 'price': 350000, 'unit_type': 'kg'},
            {'code': 'HN.TN', 'name': 'Tôm nhỏ', 'category': hang_ngop, 'price': 250000, 'unit_type': 'kg'},
            {'code': 'HN.TST', 'name': 'Tôm sú to', 'category': hang_ngop, 'price': 410000, 'unit_type': 'kg'},
            {'code': 'HN.TSV', 'name': 'Tôm sú vừa', 'category': hang_ngop, 'price': 350000, 'unit_type': 'kg'},
            {'code': 'HN.TSN', 'name': 'Tôm sú nhỏ', 'category': hang_ngop, 'price': 280000, 'unit_type': 'kg'},
            {'code': 'HN.GT', 'name': 'Ghẹ to', 'category': hang_ngop, 'price': 550000, 'unit_type': 'kg'},
            {'code': 'HN.GV', 'name': 'Ghẹ vừa', 'category': hang_ngop, 'price': 450000, 'unit_type': 'kg'},
            {'code': 'HN.GN', 'name': 'Ghẹ nhỏ', 'category': hang_ngop, 'price': 350000, 'unit_type': 'kg'},
            {'code': 'HN.CH', 'name': 'Cua hoàng', 'category': hang_ngop, 'price': 250000, 'unit_type': 'kg'},
            {'code': 'HN.CB', 'name': 'Cua bể', 'category': hang_ngop, 'price': 150000, 'unit_type': 'kg'},
            {'code': 'HN.CG', 'name': 'Cua gạch', 'category': hang_ngop, 'price': 580000, 'unit_type': 'kg'},
            {'code': 'HN.HVT', 'name': 'Hàu vỏ to', 'category': hang_ngop, 'price': 350000, 'unit_type': 'kg'},
            {'code': 'HN.HS', 'name': 'Hàu sữa', 'category': hang_ngop, 'price': 410000, 'unit_type': 'kg'},
            {'code': 'HN.HSL', 'name': 'Hàu sữa lớn', 'category': hang_ngop, 'price': 550000, 'unit_type': 'kg'},
            {'code': 'HN.SSH', 'name': 'Sò huyết', 'category': hang_ngop, 'price': 180000, 'unit_type': 'kg'},
            {'code': 'HN.SD', 'name': 'Sò dương', 'category': hang_ngop, 'price': 150000, 'unit_type': 'kg'},
            {'code': 'HN.SL', 'name': 'Sò lông', 'category': hang_ngop, 'price': 110000, 'unit_type': 'kg'},
            {'code': 'HN.SĐ', 'name': 'Sò điệp', 'category': hang_ngop, 'price': 210000, 'unit_type': 'kg'},
            {'code': 'HN.OB', 'name': 'Ốc bươu', 'category': hang_ngop, 'price': 180000, 'unit_type': 'kg'},
            {'code': 'HN.OH', 'name': 'Ốc hương', 'category': hang_ngop, 'price': 280000, 'unit_type': 'kg'},
            {'code': 'HN.OT', 'name': 'Ốc tai tượng', 'category': hang_ngop, 'price': 350000, 'unit_type': 'kg'},
            {'code': 'HN.OM', 'name': 'Ốc móng tay', 'category': hang_ngop, 'price': 150000, 'unit_type': 'kg'},
            {'code': 'HN.TC', 'name': 'Tôm càng', 'category': hang_ngop, 'price': 150000, 'unit_type': 'kg'},
            {'code': 'HN.NH', 'name': 'Nghêu Hàn Quốc', 'category': hang_ngop, 'price': 90000, 'unit_type': 'kg'},
            {'code': 'HN.RCX', 'name': 'Rau câu xanh', 'category': hang_ngop, 'price': 180000, 'unit_type': 'kg'},
            {'code': 'HN.RCĐ', 'name': 'Rau câu đỏ', 'category': hang_ngop, 'price': 180000, 'unit_type': 'kg'},

            # ===== CÔNG CỤ DỤNG CỤ =====
            {'code': 'CC.TN', 'name': 'Thùng nhựa', 'category': cong_cu, 'price': 110000, 'unit_type': 'piece'},
            {'code': 'CC.BD', 'name': 'Bao đá', 'category': cong_cu, 'price': 18000, 'unit_type': 'piece'},
            {'code': 'CC.TĐL', 'name': 'Thùng đá lớn', 'category': cong_cu, 'price': 680000, 'unit_type': 'piece'},
            {'code': 'CC.TĐN', 'name': 'Thùng đá nhỏ', 'category': cong_cu, 'price': 450000, 'unit_type': 'piece'},
            {'code': 'CC.ĐÁLL', 'name': 'Đá lạnh lớn', 'category': cong_cu, 'price': 50000, 'unit_type': 'piece'},
            {'code': 'CC.ĐLN', 'name': 'Đá lạnh nhỏ', 'category': cong_cu, 'price': 25000, 'unit_type': 'piece'},
        ]

        created_count = 0
        updated_count = 0

        for product_data in products_data:
            seafood, created = Seafood.objects.update_or_create(
                code=product_data['code'],
                defaults={
                    'name': product_data['name'],
                    'category': product_data['category'],
                    'current_price': Decimal(str(product_data['price'])),
                    'unit_type': product_data['unit_type'],
                    'stock_quantity': Decimal('0'),
                    'status': 'active',
                }
            )

            if created:
                created_count += 1
                self.stdout.write(f'  ✓ Tạo mới: {seafood.code} - {seafood.name}')
            else:
                updated_count += 1
                self.stdout.write(f'  → Cập nhật: {seafood.code} - {seafood.name}')

        self.stdout.write(self.style.SUCCESS(f'\n📊 Tổng kết:'))
        self.stdout.write(f'  • Tạo mới: {created_count} sản phẩm')
        self.stdout.write(f'  • Cập nhật: {updated_count} sản phẩm')
        self.stdout.write(f'  • Tổng cộng: {len(products_data)} sản phẩm')
