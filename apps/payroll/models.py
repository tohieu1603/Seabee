"""
Payroll Models - Hệ thống tính lương
"""
import uuid
from django.db import models
from django.utils import timezone
from apps.users.models import User


class SalaryConfiguration(models.Model):
    """
    Cấu hình lương cơ bản theo vị trí/role
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.ForeignKey(
        'rbac.Role',
        on_delete=models.CASCADE,
        related_name='salary_configs',
        help_text="Vai trò"
    )
    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Lương cơ bản (VND)"
    )
    standard_working_days = models.IntegerField(
        default=26,
        help_text="Số ngày làm việc chuẩn trong tháng"
    )

    # Allowances (Phụ cấp)
    attendance_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Phụ cấp chuyên cần (đi đủ công)"
    )
    transportation_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Phụ cấp xăng xe"
    )
    meal_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Phụ cấp ăn trưa"
    )
    phone_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Phụ cấp điện thoại"
    )

    # Commission config (Hoa hồng)
    enable_commission = models.BooleanField(
        default=False,
        help_text="Áp dụng hoa hồng doanh số"
    )
    commission_rate_1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        help_text="Hoa hồng < 20 triệu (%)"
    )
    commission_threshold_2 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=20000000,
        help_text="Ngưỡng bậc 2"
    )
    commission_rate_2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.5,
        help_text="Hoa hồng 20-50 triệu (%)"
    )
    commission_threshold_3 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=50000000,
        help_text="Ngưỡng bậc 3"
    )
    commission_rate_3 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=2.0,
        help_text="Hoa hồng 50-100 triệu (%)"
    )
    commission_threshold_4 = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=100000000,
        help_text="Ngưỡng bậc 4"
    )
    commission_rate_4 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=2.5,
        help_text="Hoa hồng > 100 triệu (%)"
    )

    # KPI bonus
    kpi_bonus_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000000,
        help_text="Mức thưởng KPI tối đa"
    )

    # Insurance rates
    social_insurance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=8.0,
        help_text="BHXH (%)"
    )
    health_insurance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.5,
        help_text="BHYT (%)"
    )
    unemployment_insurance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        help_text="BHTN (%)"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'salary_configurations'
        verbose_name = 'Cấu hình lương'
        verbose_name_plural = 'Cấu hình lương'
        unique_together = [['role', 'is_active']]

    def __str__(self):
        return f"{self.role.name} - {self.base_salary:,.0f}đ"

    @property
    def total_insurance_rate(self):
        """Tổng tỷ lệ bảo hiểm"""
        return self.social_insurance_rate + self.health_insurance_rate + self.unemployment_insurance_rate


class Payroll(models.Model):
    """
    Bảng lương hàng tháng
    """
    STATUS_CHOICES = [
        ('draft', 'Nháp'),
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('paid', 'Đã thanh toán'),
        ('cancelled', 'Đã hủy'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='payrolls',
        help_text="Nhân viên"
    )

    # Period
    year = models.IntegerField(help_text="Năm")
    month = models.IntegerField(help_text="Tháng")

    # Salary components
    base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Lương cơ bản"
    )
    working_days = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        help_text="Số ngày công thực tế"
    )
    standard_working_days = models.IntegerField(
        default=26,
        help_text="Số ngày làm việc chuẩn"
    )
    actual_base_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Lương cơ bản thực tế (theo ngày công)"
    )

    # Allowances
    attendance_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Phụ cấp chuyên cần"
    )
    transportation_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Phụ cấp xăng xe"
    )
    meal_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Phụ cấp ăn trưa"
    )
    phone_allowance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Phụ cấp điện thoại"
    )
    total_allowances = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Tổng phụ cấp"
    )

    # Bonuses
    sales_commission = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Thưởng doanh số"
    )
    sales_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text="Doanh thu tháng"
    )
    kpi_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Điểm KPI (0-100)"
    )
    kpi_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Thưởng KPI"
    )
    other_bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Thưởng khác"
    )
    total_bonuses = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Tổng thưởng"
    )

    # Gross salary
    gross_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Tổng thu nhập (trước thuế, BH)"
    )

    # Deductions - Insurance
    social_insurance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="BHXH (8%)"
    )
    health_insurance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="BHYT (1.5%)"
    )
    unemployment_insurance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="BHTN (1%)"
    )
    total_insurance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Tổng bảo hiểm"
    )

    # Tax
    taxable_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Thu nhập chịu thuế"
    )
    personal_deduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=11000000,
        help_text="Giảm trừ bản thân"
    )
    dependent_deduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Giảm trừ người phụ thuộc"
    )
    personal_income_tax = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Thuế TNCN"
    )

    # Other deductions
    advance_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Tạm ứng"
    )
    penalty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Phạt"
    )
    other_deduction = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Khấu trừ khác"
    )
    total_deductions = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Tổng khấu trừ"
    )

    # Net salary
    net_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Lương thực lĩnh"
    )

    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Trạng thái"
    )

    # Notes
    notes = models.TextField(blank=True, null=True, help_text="Ghi chú")

    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_payrolls',
        help_text="Người tạo"
    )
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_payrolls',
        help_text="Người duyệt"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payrolls'
        verbose_name = 'Bảng lương'
        verbose_name_plural = 'Bảng lương'
        ordering = ['-year', '-month', 'user__first_name']
        unique_together = [['user', 'year', 'month']]
        indexes = [
            models.Index(fields=['user', 'year', 'month']),
            models.Index(fields=['status']),
            models.Index(fields=['year', 'month']),
        ]

    def __str__(self):
        return f"{self.user.full_name} - {self.month}/{self.year} - {self.net_salary:,.0f}đ"


class PayrollAdjustment(models.Model):
    """
    Điều chỉnh lương (thưởng/phạt đột xuất)
    """
    ADJUSTMENT_TYPE_CHOICES = [
        ('bonus', 'Thưởng'),
        ('deduction', 'Khấu trừ'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payroll = models.ForeignKey(
        Payroll,
        on_delete=models.CASCADE,
        related_name='adjustments',
        help_text="Bảng lương"
    )
    adjustment_type = models.CharField(
        max_length=20,
        choices=ADJUSTMENT_TYPE_CHOICES,
        help_text="Loại điều chỉnh"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Số tiền"
    )
    reason = models.TextField(help_text="Lý do")

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_adjustments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payroll_adjustments'
        verbose_name = 'Điều chỉnh lương'
        verbose_name_plural = 'Điều chỉnh lương'

    def __str__(self):
        return f"{self.get_adjustment_type_display()} - {self.amount:,.0f}đ"
