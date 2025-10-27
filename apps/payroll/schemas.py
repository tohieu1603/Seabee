"""
Payroll Pydantic Schemas
"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field
from decimal import Decimal


class SalaryConfigRead(BaseModel):
    """Schema for reading salary configuration"""
    id: UUID
    role_name: str
    base_salary: Decimal
    standard_working_days: int
    attendance_allowance: Decimal
    transportation_allowance: Decimal
    meal_allowance: Decimal
    phone_allowance: Decimal
    enable_commission: bool
    commission_rate_1: Decimal
    commission_rate_2: Decimal
    commission_rate_3: Decimal
    commission_rate_4: Decimal
    kpi_bonus_amount: Decimal
    total_insurance_rate: Decimal
    is_active: bool

    class Config:
        from_attributes = True


class PayrollRead(BaseModel):
    """Schema for reading payroll"""
    id: UUID
    user_id: UUID
    user_name: str
    user_email: str
    user_role: str
    year: int
    month: int

    # Base
    base_salary: Decimal
    working_days: Decimal
    standard_working_days: int
    actual_base_salary: Decimal

    # Allowances
    total_allowances: Decimal
    attendance_allowance: Decimal
    transportation_allowance: Decimal
    meal_allowance: Decimal
    phone_allowance: Decimal

    # Bonuses
    total_bonuses: Decimal
    sales_commission: Decimal
    sales_revenue: Decimal
    kpi_score: Decimal
    kpi_bonus: Decimal
    other_bonus: Decimal

    # Gross
    gross_salary: Decimal

    # Insurance
    total_insurance: Decimal
    social_insurance: Decimal
    health_insurance: Decimal
    unemployment_insurance: Decimal

    # Tax
    taxable_income: Decimal
    personal_income_tax: Decimal
    personal_deduction: Decimal
    dependent_deduction: Decimal

    # Deductions
    total_deductions: Decimal
    advance_payment: Decimal
    penalty: Decimal
    other_deduction: Decimal

    # Net
    net_salary: Decimal

    # Status
    status: str
    notes: Optional[str] = None

    # Audit
    created_at: datetime
    approved_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PayrollCalculateRequest(BaseModel):
    """Schema for calculate payroll request"""
    user_id: UUID
    year: int
    month: int
    dependents: int = 0
    advance_payment: Decimal = Decimal('0')
    penalty: Decimal = Decimal('0')
    other_bonus: Decimal = Decimal('0')
    other_deduction: Decimal = Decimal('0')
    notes: Optional[str] = None


class PayrollBulkCalculateRequest(BaseModel):
    """Schema for bulk calculate payroll request"""
    year: int
    month: int
    user_ids: Optional[list[UUID]] = None  # If None, calculate for all eligible users


class PayrollApproveRequest(BaseModel):
    """Schema for approve payroll request"""
    payroll_ids: list[UUID]
    notes: Optional[str] = None


class PayrollStatusUpdate(BaseModel):
    """Schema for updating payroll status"""
    status: str = Field(..., pattern="^(draft|pending|approved|paid|cancelled)$")
    notes: Optional[str] = None


class PayrollSummary(BaseModel):
    """Schema for payroll summary statistics"""
    total_employees: int
    total_gross_salary: Decimal
    total_net_salary: Decimal
    total_insurance: Decimal
    total_tax: Decimal
    total_commission: Decimal
    total_kpi_bonus: Decimal

    draft_count: int
    pending_count: int
    approved_count: int
    paid_count: int


class EmployeePayrollSummary(BaseModel):
    """Schema for employee payroll summary"""
    user_id: UUID
    user_name: str
    user_email: str
    role_name: str
    base_salary: Decimal
    working_days: Decimal
    kpi_score: Decimal
    sales_revenue: Decimal
    net_salary: Decimal
    status: str
    payroll_id: Optional[UUID] = None

    class Config:
        from_attributes = True
