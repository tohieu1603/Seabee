"""
Payroll Services - Business logic for salary calculation
"""
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from apps.users.models import User, Attendance
from apps.seafood.models import Order
from .models import SalaryConfiguration, Payroll, PayrollAdjustment


class PayrollCalculationService:
    """Service để tính lương"""

    def __init__(self, user: User, year: int, month: int):
        self.user = user
        self.year = year
        self.month = month
        self.salary_config = self._get_salary_config()

    def _get_salary_config(self) -> SalaryConfiguration:
        """Lấy cấu hình lương của user"""
        # Get user's primary role
        user_role = self.user.get_roles().first()
        if not user_role:
            raise ValueError(f"User {self.user.email} không có role")

        # Get salary configuration for this role
        config = SalaryConfiguration.objects.filter(
            role=user_role.role,
            is_active=True
        ).first()

        if not config:
            raise ValueError(f"Không tìm thấy cấu hình lương cho role {user_role.role.name}")

        return config

    def calculate_working_days(self) -> Decimal:
        """
        Tính số ngày công thực tế
        - Full day = 1 ngày
        - Half day = 0.5 ngày
        - Off = 0 ngày
        """
        # Get first and last day of month
        first_day = datetime(self.year, self.month, 1).date()
        if self.month == 12:
            last_day = datetime(self.year + 1, 1, 1).date()
        else:
            last_day = datetime(self.year, self.month + 1, 1).date()

        # Get attendances
        attendances = Attendance.objects.filter(
            user=self.user,
            date__gte=first_day,
            date__lt=last_day
        )

        full_days = attendances.filter(attendance_type='full').count()
        half_days = attendances.filter(attendance_type='half').count()

        total_days = Decimal(full_days) + (Decimal(half_days) * Decimal('0.5'))
        return total_days

    def calculate_actual_base_salary(self, working_days: Decimal) -> Decimal:
        """
        Tính lương cơ bản thực tế theo công thức:
        Lương CB thực = (Lương CB / Số ngày chuẩn) × Số ngày công thực tế
        """
        daily_rate = self.salary_config.base_salary / Decimal(self.salary_config.standard_working_days)
        actual_salary = daily_rate * working_days
        return actual_salary.quantize(Decimal('0.01'))

    def calculate_attendance_allowance(self, working_days: Decimal) -> Decimal:
        """
        Tính phụ cấp chuyên cần:
        - Đi đủ công (>= standard - 1): Full allowance
        - Nghỉ 1-2 ngày: 60% allowance
        - Nghỉ >2 ngày: 0
        """
        standard_days = Decimal(self.salary_config.standard_working_days)
        days_off = standard_days - working_days

        if days_off <= 1:
            return self.salary_config.attendance_allowance
        elif days_off <= 3:
            return self.salary_config.attendance_allowance * Decimal('0.6')
        else:
            return Decimal('0')

    def calculate_sales_commission(self) -> tuple[Decimal, Decimal]:
        """
        Tính hoa hồng doanh số theo bậc thang:
        - < 20M: 1%
        - 20-50M: 1.5%
        - 50-100M: 2%
        - > 100M: 2.5%

        Returns: (commission_amount, total_revenue)
        """
        if not self.salary_config.enable_commission:
            return Decimal('0'), Decimal('0')

        # Get first and last day of month
        first_day = datetime(self.year, self.month, 1)
        if self.month == 12:
            last_day = datetime(self.year + 1, 1, 1)
        else:
            last_day = datetime(self.year, self.month + 1, 1)

        # Get total revenue from completed orders
        orders = Order.objects.filter(
            created_by=self.user,
            created_at__gte=first_day,
            created_at__lt=last_day,
            status='completed'
        )

        total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

        # Calculate commission based on revenue tiers
        if total_revenue < self.salary_config.commission_threshold_2:
            commission_rate = self.salary_config.commission_rate_1
        elif total_revenue < self.salary_config.commission_threshold_3:
            commission_rate = self.salary_config.commission_rate_2
        elif total_revenue < self.salary_config.commission_threshold_4:
            commission_rate = self.salary_config.commission_rate_3
        else:
            commission_rate = self.salary_config.commission_rate_4

        commission = (total_revenue * commission_rate / Decimal('100')).quantize(Decimal('0.01'))
        return commission, total_revenue

    def calculate_kpi_score(self) -> Decimal:
        """
        Tính điểm KPI (0-100):
        - Doanh số đạt (30 điểm)
        - Số đơn hàng (20 điểm)
        - Tỷ lệ thu tiền (20 điểm)
        - Chất lượng dịch vụ (15 điểm)
        - Chấm công (15 điểm)
        """
        # Get first and last day of month
        first_day = datetime(self.year, self.month, 1)
        if self.month == 12:
            last_day = datetime(self.year + 1, 1, 1)
        else:
            last_day = datetime(self.year, self.month + 1, 1)

        # Get orders
        orders = Order.objects.filter(
            created_by=self.user,
            created_at__gte=first_day,
            created_at__lt=last_day
        )

        total_orders = orders.count()
        completed_orders = orders.filter(status='completed').count()
        total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        total_paid = orders.aggregate(total=Sum('paid_amount'))['total'] or Decimal('0')

        score = Decimal('0')

        # 1. Doanh số đạt (30 điểm) - Mục tiêu 50M
        revenue_target = Decimal('50000000')
        if total_revenue >= revenue_target:
            score += Decimal('30')
        else:
            score += (total_revenue / revenue_target) * Decimal('30')

        # 2. Số đơn hàng (20 điểm) - Mục tiêu 20 đơn
        orders_target = 20
        if total_orders >= orders_target:
            score += Decimal('20')
        else:
            score += (Decimal(total_orders) / Decimal(orders_target)) * Decimal('20')

        # 3. Tỷ lệ thu tiền (20 điểm)
        if total_revenue > 0:
            collection_rate = (total_paid / total_revenue) * Decimal('20')
            score += collection_rate
        else:
            score += Decimal('0')

        # 4. Chất lượng dịch vụ (15 điểm) - Tỷ lệ hoàn thành
        if total_orders > 0:
            completion_rate = (Decimal(completed_orders) / Decimal(total_orders)) * Decimal('15')
            score += completion_rate
        else:
            score += Decimal('0')

        # 5. Chấm công (15 điểm)
        working_days = self.calculate_working_days()
        standard_days = Decimal(self.salary_config.standard_working_days)
        attendance_rate = (working_days / standard_days) * Decimal('15')
        score += attendance_rate

        return score.quantize(Decimal('0.01'))

    def calculate_kpi_bonus(self, kpi_score: Decimal) -> Decimal:
        """
        Tính thưởng KPI dựa trên điểm KPI:
        Thưởng KPI = (Điểm KPI / 100) × Mức thưởng KPI
        """
        kpi_bonus = (kpi_score / Decimal('100')) * self.salary_config.kpi_bonus_amount
        return kpi_bonus.quantize(Decimal('0.01'))

    def calculate_insurance(self, base_salary: Decimal) -> dict:
        """
        Tính bảo hiểm:
        - BHXH: 8%
        - BHYT: 1.5%
        - BHTN: 1%
        """
        social_insurance = (base_salary * self.salary_config.social_insurance_rate / Decimal('100')).quantize(Decimal('0.01'))
        health_insurance = (base_salary * self.salary_config.health_insurance_rate / Decimal('100')).quantize(Decimal('0.01'))
        unemployment_insurance = (base_salary * self.salary_config.unemployment_insurance_rate / Decimal('100')).quantize(Decimal('0.01'))

        total_insurance = social_insurance + health_insurance + unemployment_insurance

        return {
            'social_insurance': social_insurance,
            'health_insurance': health_insurance,
            'unemployment_insurance': unemployment_insurance,
            'total_insurance': total_insurance
        }

    def calculate_personal_income_tax(self, gross_salary: Decimal, total_insurance: Decimal, dependents: int = 0) -> dict:
        """
        Tính thuế TNCN theo bậc thang lũy tiến:

        Thu nhập chịu thuế = Tổng thu nhập - BH - Giảm trừ bản thân - Giảm trừ người phụ thuộc

        Bậc thuế:
        - Đến 5M: 5%
        - Trên 5-10M: 10%
        - Trên 10-18M: 15%
        - Trên 18-32M: 20%
        - Trên 32-52M: 25%
        - Trên 52-80M: 30%
        - Trên 80M: 35%
        """
        personal_deduction = Decimal('11000000')  # 11M
        dependent_deduction = Decimal('4400000') * Decimal(dependents)  # 4.4M per dependent

        # Calculate taxable income
        taxable_income = gross_salary - total_insurance - personal_deduction - dependent_deduction

        if taxable_income <= 0:
            return {
                'taxable_income': Decimal('0'),
                'personal_deduction': personal_deduction,
                'dependent_deduction': dependent_deduction,
                'tax': Decimal('0')
            }

        # Tax brackets (in VND)
        brackets = [
            (5000000, 0.05),
            (10000000, 0.10),
            (18000000, 0.15),
            (32000000, 0.20),
            (52000000, 0.25),
            (80000000, 0.30),
            (float('inf'), 0.35)
        ]

        tax = Decimal('0')
        remaining = taxable_income
        prev_bracket = Decimal('0')

        for bracket_limit, rate in brackets:
            if remaining <= 0:
                break

            taxable_in_bracket = min(remaining, Decimal(bracket_limit) - prev_bracket)
            tax += taxable_in_bracket * Decimal(str(rate))
            remaining -= taxable_in_bracket
            prev_bracket = Decimal(bracket_limit)

        return {
            'taxable_income': taxable_income,
            'personal_deduction': personal_deduction,
            'dependent_deduction': dependent_deduction,
            'tax': tax.quantize(Decimal('0.01'))
        }

    def calculate_payroll(self, dependents: int = 0, advance_payment: Decimal = Decimal('0'),
                         penalty: Decimal = Decimal('0'), other_bonus: Decimal = Decimal('0'),
                         other_deduction: Decimal = Decimal('0'), notes: str = '') -> Payroll:
        """
        Tính toán và tạo bảng lương hoàn chỉnh
        """
        # 1. Calculate working days
        working_days = self.calculate_working_days()

        # 2. Calculate actual base salary
        actual_base_salary = self.calculate_actual_base_salary(working_days)

        # 3. Calculate allowances
        attendance_allowance = self.calculate_attendance_allowance(working_days)
        transportation_allowance = self.salary_config.transportation_allowance
        meal_allowance = self.salary_config.meal_allowance
        phone_allowance = self.salary_config.phone_allowance
        total_allowances = attendance_allowance + transportation_allowance + meal_allowance + phone_allowance

        # 4. Calculate bonuses
        sales_commission, sales_revenue = self.calculate_sales_commission()
        kpi_score = self.calculate_kpi_score()
        kpi_bonus = self.calculate_kpi_bonus(kpi_score)
        total_bonuses = sales_commission + kpi_bonus + other_bonus

        # 5. Calculate gross salary
        gross_salary = actual_base_salary + total_allowances + total_bonuses

        # 6. Calculate insurance (based on base salary)
        insurance = self.calculate_insurance(self.salary_config.base_salary)

        # 7. Calculate tax
        tax_data = self.calculate_personal_income_tax(
            gross_salary,
            insurance['total_insurance'],
            dependents
        )

        # 8. Calculate total deductions
        total_deductions = (
            insurance['total_insurance'] +
            tax_data['tax'] +
            advance_payment +
            penalty +
            other_deduction
        )

        # 9. Calculate net salary
        net_salary = gross_salary - total_deductions

        # 10. Create payroll record
        payroll = Payroll.objects.create(
            user=self.user,
            year=self.year,
            month=self.month,

            # Base salary
            base_salary=self.salary_config.base_salary,
            working_days=working_days,
            standard_working_days=self.salary_config.standard_working_days,
            actual_base_salary=actual_base_salary,

            # Allowances
            attendance_allowance=attendance_allowance,
            transportation_allowance=transportation_allowance,
            meal_allowance=meal_allowance,
            phone_allowance=phone_allowance,
            total_allowances=total_allowances,

            # Bonuses
            sales_commission=sales_commission,
            sales_revenue=sales_revenue,
            kpi_score=kpi_score,
            kpi_bonus=kpi_bonus,
            other_bonus=other_bonus,
            total_bonuses=total_bonuses,

            # Gross
            gross_salary=gross_salary,

            # Insurance
            social_insurance=insurance['social_insurance'],
            health_insurance=insurance['health_insurance'],
            unemployment_insurance=insurance['unemployment_insurance'],
            total_insurance=insurance['total_insurance'],

            # Tax
            taxable_income=tax_data['taxable_income'],
            personal_deduction=tax_data['personal_deduction'],
            dependent_deduction=tax_data['dependent_deduction'],
            personal_income_tax=tax_data['tax'],

            # Other deductions
            advance_payment=advance_payment,
            penalty=penalty,
            other_deduction=other_deduction,
            total_deductions=total_deductions,

            # Net
            net_salary=net_salary,

            # Status
            status='draft',
            notes=notes
        )

        return payroll
