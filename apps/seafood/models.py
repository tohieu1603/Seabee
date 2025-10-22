"""
Models cho hệ thống bán hải sản - Bán theo cân thực tế
Đơn giản: Sản phẩm -> Lô hàng -> Bán theo kg/lạng
"""
from django.db import models
from django.utils import timezone
from apps.base_models import BaseModel
from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()


# ============================================
# DANH MỤC SẢN PHẨM
# ============================================

class SeafoodCategory(BaseModel):
    """Danh mục hải sản: Tôm, Cua, Cá, Ốc,..."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'seafood_category'
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


# ============================================
# SẢN PHẨM HẢI SẢN
# ============================================

class Seafood(BaseModel):
    """
    Sản phẩm hải sản
    VD: Tôm hùm Alaska, Cua hoàng đế, Cá hồi...
    Bán theo kg/lạng, giá thay đổi theo lô nhập
    """
    STATUS_CHOICES = [
        ('active', 'Đang bán'),
        ('inactive', 'Ngừng bán'),
        ('out_of_stock', 'Hết hàng'),
    ]

    # Thông tin cơ bản
    code = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    category = models.ForeignKey(
        SeafoodCategory,
        on_delete=models.SET_NULL,
        null=True,
        related_name='seafoods'
    )

    # Giá hiện tại (cập nhật theo lô nhập mới nhất)
    current_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        help_text="Giá hiện tại/kg (VNĐ)"
    )

    # Tồn kho
    stock_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Số kg còn lại trong kho"
    )

    # Mô tả
    description = models.TextField(blank=True)
    origin = models.CharField(max_length=255, blank=True, help_text="Nguồn gốc: Cà Mau, Phú Quốc...")

    # Hình ảnh
    image_url = models.URLField(max_length=500, blank=True)

    # Trạng thái
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Tags
    tags = models.JSONField(default=list, blank=True, help_text="['tươi sống', 'đông lạnh', 'cao cấp']")

    class Meta:
        db_table = 'seafood'
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"


# ============================================
# NGUỒN NHẬP HÀNG
# ============================================

class ImportSource(BaseModel):
    """Nguồn nhập hàng: Facebook, Zalo, Messenger, Chợ,..."""
    SOURCE_TYPES = [
        ('facebook', 'Facebook'),
        ('zalo', 'Zalo'),
        ('messenger', 'Messenger'),
        ('phone', 'Điện thoại'),
        ('market', 'Chợ'),
        ('company', 'Công ty'),
        ('other', 'Khác'),
    ]

    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    contact_info = models.JSONField(
        default=dict,
        blank=True,
        help_text="Thông tin liên hệ: phone, facebook_url, zalo_id..."
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'import_source'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"


# ============================================
# LÔ NHẬP HÀNG
# ============================================

class ImportBatch(BaseModel):
    """
    Lô hàng nhập kho
    Mỗi lô có giá nhập riêng, theo dõi nguồn gốc
    """
    STATUS_CHOICES = [
        ('received', 'Đã nhận'),
        ('selling', 'Đang bán'),
        ('sold_out', 'Đã bán hết'),
    ]

    seafood = models.ForeignKey(Seafood, on_delete=models.CASCADE, related_name='import_batches')
    batch_code = models.CharField(max_length=50, unique=True, db_index=True)

    # Nguồn nhập
    import_source = models.ForeignKey(
        ImportSource,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Thông tin nhập hàng
    import_date = models.DateField(default=timezone.now)
    import_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        help_text="Giá nhập/kg (VNĐ)"
    )
    sell_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        help_text="Giá bán/kg (VNĐ)"
    )

    # Số lượng
    total_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Tổng kg nhập vào"
    )
    remaining_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Số kg còn lại"
    )

    # Chi tiết nhập hàng
    notes = models.TextField(blank=True)
    import_details = models.JSONField(
        default=dict,
        blank=True,
        help_text="Link chat, hình ảnh, thông tin giao dịch"
    )

    # Trạng thái
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')

    # Người nhập
    imported_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='seafood_imports'
    )

    class Meta:
        db_table = 'import_batch'
        ordering = ['-import_date', '-created_at']

    def __str__(self):
        return f"{self.batch_code} - {self.seafood.name}"


# ============================================
# ĐƠN HÀNG POS
# ============================================

class Order(BaseModel):
    """Đơn hàng bán tại quầy - không cần tài khoản khách"""
    PAYMENT_METHODS = [
        ('cash', 'Tiền mặt'),
        ('transfer', 'Chuyển khoản'),
        ('momo', 'MoMo'),
    ]

    PAYMENT_STATUS = [
        ('pending', 'Chờ thanh toán'),
        ('paid', 'Đã thanh toán'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),
        ('processing', 'Đang xử lý'),
        ('weighed', 'Đã cân'),
        ('ready', 'Sẵn sàng giao'),
        ('shipped', 'Đã gửi vận chuyển'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]

    # Mã đơn
    order_code = models.CharField(max_length=50, unique=True, db_index=True)

    # Khách hàng (không cần account)
    customer_name = models.CharField(max_length=255, blank=True)
    customer_phone = models.CharField(max_length=20, db_index=True)  # Required
    customer_address = models.TextField(blank=True)

    # Tổng tiền
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)

    # Thanh toán
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    # Trạng thái
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    # Workflow - Xử lý đơn hàng
    weighed_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian cân hàng")
    weighed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='weighed_orders',
        help_text="Nhân viên cân hàng"
    )
    weight_images = models.JSONField(
        default=list,
        blank=True,
        help_text="Danh sách URL ảnh cân hàng"
    )

    shipped_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian gửi vận chuyển")
    shipped_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='shipped_orders',
        help_text="Nhân viên gửi hàng"
    )
    shipping_notes = models.TextField(blank=True, help_text="Ghi chú vận chuyển")

    # Ghi chú
    notes = models.TextField(blank=True)

    # Nhân viên tạo đơn
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='pos_orders')

    class Meta:
        db_table = 'order'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_code} - {self.customer_phone}"


class OrderItem(BaseModel):
    """Chi tiết đơn hàng - bán theo cân thực tế"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    seafood = models.ForeignKey(Seafood, on_delete=models.PROTECT)
    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Lô hàng được bán"
    )

    # Cân nặng ban đầu (ước tính)
    estimated_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cân nặng ước tính ban đầu (kg)"
    )

    # Cân nặng thực tế (sau khi cân)
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Cân nặng thực tế (kg). VD: 0.5, 1.2, 3.5"
    )

    # Giá
    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        help_text="Giá/kg (VNĐ)"
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)

    # Ảnh cân cho từng sản phẩm
    weight_image_url = models.URLField(max_length=500, blank=True, help_text="Ảnh cân của sản phẩm này")

    # Ghi chú
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'order_item'

    def save(self, *args, **kwargs):
        # Tự động tính subtotal
        self.subtotal = self.weight * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.seafood.name} - {self.weight}kg"


# ============================================
# LỊCH SỬ TỒN KHO
# ============================================

class InventoryLog(BaseModel):
    """Lịch sử nhập/xuất kho"""
    TYPE_CHOICES = [
        ('import', 'Nhập hàng'),
        ('sale', 'Bán hàng'),
        ('adjust', 'Điều chỉnh'),
        ('loss', 'Hao hụt'),
    ]

    seafood = models.ForeignKey(Seafood, on_delete=models.CASCADE, related_name='inventory_logs')
    import_batch = models.ForeignKey(
        ImportBatch,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    weight_change = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Số kg thay đổi (+ nhập, - xuất)"
    )
    stock_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Tồn kho sau khi thay đổi"
    )

    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'inventory_log'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.seafood.name} - {self.get_type_display()} - {self.weight_change}kg"
