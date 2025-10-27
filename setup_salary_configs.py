"""
Setup initial salary configurations for all roles
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.rbac.models import Role
from apps.payroll.models import SalaryConfiguration
from decimal import Decimal

# Define salary configurations for each role
configs = [
    {
        'role_slug': 'salesperson',
        'base_salary': Decimal('8000000'),  # 8 triệu
        'standard_working_days': 26,
        'attendance_allowance': Decimal('500000'),
        'transportation_allowance': Decimal('300000'),
        'meal_allowance': Decimal('750000'),  # 30k/day x 25 days
        'phone_allowance': Decimal('200000'),
        'enable_commission': True,
        'commission_rate_1': Decimal('1.0'),
        'commission_rate_2': Decimal('1.5'),
        'commission_rate_3': Decimal('2.0'),
        'commission_rate_4': Decimal('2.5'),
        'kpi_bonus_amount': Decimal('1000000'),  # 1 triệu max
    },
    {
        'role_slug': 'accountant',
        'base_salary': Decimal('10000000'),  # 10 triệu
        'standard_working_days': 26,
        'attendance_allowance': Decimal('500000'),
        'transportation_allowance': Decimal('300000'),
        'meal_allowance': Decimal('750000'),
        'phone_allowance': Decimal('200000'),
        'enable_commission': False,
        'kpi_bonus_amount': Decimal('1000000'),
    },
    {
        'role_slug': 'warehouse',
        'base_salary': Decimal('7000000'),  # 7 triệu
        'standard_working_days': 26,
        'attendance_allowance': Decimal('500000'),
        'transportation_allowance': Decimal('300000'),
        'meal_allowance': Decimal('750000'),
        'phone_allowance': Decimal('100000'),
        'enable_commission': False,
        'kpi_bonus_amount': Decimal('800000'),
    },
    {
        'role_slug': 'manager',
        'base_salary': Decimal('15000000'),  # 15 triệu
        'standard_working_days': 26,
        'attendance_allowance': Decimal('1000000'),
        'transportation_allowance': Decimal('500000'),
        'meal_allowance': Decimal('1000000'),
        'phone_allowance': Decimal('500000'),
        'enable_commission': True,
        'commission_rate_1': Decimal('0.5'),
        'commission_rate_2': Decimal('0.75'),
        'commission_rate_3': Decimal('1.0'),
        'commission_rate_4': Decimal('1.5'),
        'kpi_bonus_amount': Decimal('2000000'),  # 2 triệu max
    },
]

print("Setting up salary configurations...")

for config_data in configs:
    role_slug = config_data.pop('role_slug')
    try:
        role = Role.objects.get(slug=role_slug)

        # Check if config already exists
        existing = SalaryConfiguration.objects.filter(role=role, is_active=True).first()
        if existing:
            print(f"✓ Config for {role.name} already exists")
            continue

        # Create new config
        config = SalaryConfiguration.objects.create(
            role=role,
            **config_data
        )
        print(f"✓ Created salary config for {role.name} - Base: {config.base_salary:,}đ")

    except Role.DoesNotExist:
        print(f"✗ Role '{role_slug}' not found - skipping")

print("\n✅ Salary configuration setup complete!")
print(f"Total active configs: {SalaryConfiguration.objects.filter(is_active=True).count()}")
