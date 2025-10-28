"""
Import Batch Models
"""
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.base_models import BaseModel
from .product import Seafood

User = get_user_model()


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
