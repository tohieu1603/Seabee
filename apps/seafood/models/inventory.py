"""
Inventory Log Model
"""
from django.db import models
from django.contrib.auth import get_user_model
from apps.base_models import BaseModel

User = get_user_model()


class InventoryLog(BaseModel):
    """Lịch sử nhập/xuất kho"""
    TYPE_CHOICES = [
        ('import', 'Nhập hàng'),
        ('sale', 'Bán hàng'),
        ('adjust', 'Điều chỉnh'),
        ('loss', 'Hao hụt'),
    ]

    seafood = models.ForeignKey('seafood.Seafood', on_delete=models.CASCADE, related_name='inventory_logs')
    import_batch = models.ForeignKey(
        'seafood.ImportBatch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    order_item = models.ForeignKey(
        'seafood.OrderItem',
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
