"""
Seafood Product Model
"""
from django.db import models
from apps.base_models import BaseModel
from .category import SeafoodCategory


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

    UNIT_TYPE_CHOICES = [
        ('kg', 'Kilogram (kg)'),
        ('piece', 'Con/Cái'),
        ('box', 'Thùng/Hộp'),
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

    # Đơn vị tính
    unit_type = models.CharField(
        max_length=20,
        choices=UNIT_TYPE_CHOICES,
        default='kg',
        help_text="Đơn vị tính: kg, con, thùng"
    )

    # Trọng lượng mỗi đơn vị (cho đơn vị con/thùng)
    avg_unit_weight = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Trọng lượng trung bình mỗi con/thùng (kg). VD: mỗi con ốc 0.05kg"
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

    # Weight Range Options - Khoảng cân ước tính cho khách chọn
    weight_range_options = models.JSONField(
        default=list,
        blank=True,
        help_text="Các khoảng cân khách có thể chọn. VD: ['0.5-1kg', '1-2kg', '2-3.5kg']"
    )

    class Meta:
        db_table = 'seafood'
        verbose_name = 'Sản phẩm'
        verbose_name_plural = 'Sản phẩm'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"
