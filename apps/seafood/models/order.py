"""
Order Models
"""
from django.db import models
from django.contrib.auth import get_user_model
from apps.base_models import BaseModel
from .product import Seafood
from .import_batch import ImportBatch

User = get_user_model()


class Order(BaseModel):
    """Đơn hàng bán tại quầy - không cần tài khoản khách"""
    PAYMENT_METHODS = [
        ('cash', 'Tiền mặt'),
        ('bank_transfer', 'Chuyển khoản (VietQR)'),
        ('cod', 'Tiền khi nhận hàng'),
        ('transfer', 'Chuyển khoản'),  # Legacy - keep for old data
        ('momo', 'MoMo'),  # Keep for future use
    ]

    PAYMENT_STATUS = [
        ('unpaid', 'Chưa thanh toán'),
        ('pending_verification', 'Chờ xác minh'),
        ('paid', 'Đã thanh toán'),
    ]

    CUSTOMER_SOURCE = [
        ('telephone', 'Điện thoại'),
        ('facebook', 'Facebook'),
        ('zalo', 'Zalo'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Chờ xử lý'),  # Sale vừa tạo đơn
        ('pending_sale_confirm', 'Chờ Sale xác nhận'),  # Customer tạo đơn, chờ Sale
        ('confirmed', 'Đã xác nhận'),  # Sale đã confirm
        ('assigned_to_warehouse', 'Đã giao cho kho'),  # Đã assign cho Employee
        ('weighing', 'Đang cân'),  # Employee đang xử lý
        ('weighed', 'Đã cân xong'),  # Employee đã cân xong
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
    ]

    # Mã đơn
    order_code = models.CharField(max_length=50, unique=True, db_index=True)

    # Khách hàng (có thể có hoặc không có account)
    customer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='customer_orders',
        help_text="Tài khoản khách hàng (nếu có)"
    )
    customer_name = models.CharField(max_length=255, blank=True)
    customer_phone = models.CharField(max_length=20, db_index=True)  # Required
    customer_address = models.TextField(blank=True)
    customer_source = models.CharField(max_length=20, choices=CUSTOMER_SOURCE, blank=True, help_text="Nguồn khách hàng")

    # Tổng tiền
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=0)

    # Thanh toán
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0)

    # Trạng thái
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='pending')

    # Workflow - Quy trình xử lý đơn hàng

    # Sale workflow
    sale_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sale_orders',
        help_text="Sale phụ trách đơn hàng"
    )
    confirmed_by_sale_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian Sale xác nhận")

    # Employee (Warehouse) workflow
    assigned_employee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_orders',
        help_text="Nhân viên kho được giao cân hàng"
    )
    assigned_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian giao cho nhân viên kho")

    weighed_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian cân hàng xong")
    weighed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='weighed_orders',
        help_text="Nhân viên đã cân hàng"
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

    delivered_at = models.DateTimeField(null=True, blank=True, help_text="Thời gian giao hàng thành công")
    delivered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivered_orders',
        help_text="Nhân viên xác nhận giao hàng"
    )

    # Ghi chú
    notes = models.TextField(blank=True)

    # Nhân viên tạo đơn (created_by có thể là Sale hoặc hệ thống khi Customer tự tạo)
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

    # Số lượng (cho sản phẩm tính theo con/thùng)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Số lượng (con/thùng). VD: 10 con ốc, 2 thùng tôm"
    )

    # Khoảng cân ước tính (Customer chọn khi đặt hàng)
    estimated_weight_range = models.CharField(
        max_length=50,
        blank=True,
        help_text="Khoảng cân ước tính customer chọn. VD: '2-3.5kg', '1-2kg'"
    )

    # Cân nặng ban đầu (ước tính) - DEPRECATED, dùng estimated_weight_range
    estimated_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cân nặng ước tính ban đầu (kg)"
    )

    # Cân nặng thực tế (sau khi cân) - Admin cập nhật
    weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cân nặng thực tế (kg). VD: 0.5, 1.2, 3.5. NULL = chưa cân"
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
        # Tự động tính subtotal - chỉ khi đã có weight thực tế
        if self.weight:
            self.subtotal = self.weight * self.unit_price
        else:
            # Chưa cân xong, tạm để subtotal = 0
            self.subtotal = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.seafood.name} - {self.weight}kg"
