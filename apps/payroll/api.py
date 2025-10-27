"""
Payroll API Endpoints
"""
from typing import List, Optional
from uuid import UUID
from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count
from decimal import Decimal

from .models import SalaryConfiguration, Payroll, PayrollAdjustment
from .schemas import (
    PayrollRead, PayrollCalculateRequest, PayrollBulkCalculateRequest,
    PayrollApproveRequest, PayrollStatusUpdate, PayrollSummary,
    EmployeePayrollSummary
)
from .services import PayrollCalculationService
from apps.users.models import User

router = Router(tags=["Payroll"], auth=None)


@router.post("/calculate", response=PayrollRead)
def calculate_payroll(request, payload: PayrollCalculateRequest):
    """Tính lương cho một nhân viên"""
    user = get_object_or_404(User, id=payload.user_id)

    # Check if payroll already exists
    existing = Payroll.objects.filter(
        user=user,
        year=payload.year,
        month=payload.month
    ).first()

    if existing and existing.status != 'draft':
        from api.exceptions import BadRequest
        raise BadRequest(f"Bảng lương tháng {payload.month}/{payload.year} đã tồn tại với trạng thái {existing.status}")

    # Delete draft if exists
    if existing:
        existing.delete()

    # Calculate payroll
    service = PayrollCalculationService(user, payload.year, payload.month)
    payroll = service.calculate_payroll(
        dependents=payload.dependents,
        advance_payment=payload.advance_payment,
        penalty=payload.penalty,
        other_bonus=payload.other_bonus,
        other_deduction=payload.other_deduction,
        notes=payload.notes
    )

    # Add user info
    return _payroll_to_dict(payroll)


@router.post("/calculate-bulk")
def calculate_bulk_payroll(request, payload: PayrollBulkCalculateRequest):
    """Tính lương hàng loạt cho nhiều nhân viên"""
    # Get users to calculate
    if payload.user_ids:
        users = User.objects.filter(id__in=payload.user_ids, is_active=True)
    else:
        # Calculate for all active employees (exclude viewers)
        users = User.objects.filter(
            is_active=True,
            user_roles__role__slug__in=['salesperson', 'accountant', 'warehouse', 'manager']
        ).distinct()

    results = {
        'success': [],
        'failed': [],
        'total': users.count()
    }

    for user in users:
        try:
            # Check if already exists
            existing = Payroll.objects.filter(
                user=user,
                year=payload.year,
                month=payload.month
            ).first()

            if existing and existing.status != 'draft':
                results['failed'].append({
                    'user_id': str(user.id),
                    'user_name': user.full_name,
                    'reason': f'Đã tồn tại với trạng thái {existing.status}'
                })
                continue

            # Delete draft if exists
            if existing:
                existing.delete()

            # Calculate
            service = PayrollCalculationService(user, payload.year, payload.month)
            payroll = service.calculate_payroll()

            results['success'].append({
                'user_id': str(user.id),
                'user_name': user.full_name,
                'net_salary': float(payroll.net_salary)
            })

        except Exception as e:
            results['failed'].append({
                'user_id': str(user.id),
                'user_name': user.full_name,
                'reason': str(e)
            })

    return results


@router.get("/list", response=List[PayrollRead])
def list_payrolls(
    request,
    year: Optional[int] = None,
    month: Optional[int] = None,
    status: Optional[str] = None,
    user_id: Optional[UUID] = None
):
    """Lấy danh sách bảng lương"""
    query = Payroll.objects.select_related('user').all()

    if year:
        query = query.filter(year=year)
    if month:
        query = query.filter(month=month)
    if status:
        query = query.filter(status=status)
    if user_id:
        query = query.filter(user_id=user_id)

    payrolls = query.order_by('-year', '-month', 'user__first_name')

    return [_payroll_to_dict(p) for p in payrolls]


@router.get("/summary", response=PayrollSummary)
def get_payroll_summary(request, year: int, month: int):
    """Lấy tổng quan bảng lương tháng"""
    payrolls = Payroll.objects.filter(year=year, month=month)

    stats = payrolls.aggregate(
        total_gross=Sum('gross_salary'),
        total_net=Sum('net_salary'),
        total_insurance=Sum('total_insurance'),
        total_tax=Sum('personal_income_tax'),
        total_commission=Sum('sales_commission'),
        total_kpi=Sum('kpi_bonus')
    )

    status_counts = {
        'draft': payrolls.filter(status='draft').count(),
        'pending': payrolls.filter(status='pending').count(),
        'approved': payrolls.filter(status='approved').count(),
        'paid': payrolls.filter(status='paid').count(),
    }

    return {
        'total_employees': payrolls.count(),
        'total_gross_salary': stats['total_gross'] or Decimal('0'),
        'total_net_salary': stats['total_net'] or Decimal('0'),
        'total_insurance': stats['total_insurance'] or Decimal('0'),
        'total_tax': stats['total_tax'] or Decimal('0'),
        'total_commission': stats['total_commission'] or Decimal('0'),
        'total_kpi_bonus': stats['total_kpi'] or Decimal('0'),
        'draft_count': status_counts['draft'],
        'pending_count': status_counts['pending'],
        'approved_count': status_counts['approved'],
        'paid_count': status_counts['paid'],
    }


@router.get("/employees-summary", response=List[EmployeePayrollSummary])
def get_employees_payroll_summary(request, year: int, month: int):
    """Lấy tổng quan lương của tất cả nhân viên"""
    # Get all active employees
    users = User.objects.filter(
        is_active=True,
        user_roles__role__slug__in=['salesperson', 'accountant', 'warehouse', 'manager']
    ).distinct()

    result = []
    for user in users:
        # Get payroll if exists
        payroll = Payroll.objects.filter(
            user=user,
            year=year,
            month=month
        ).first()

        # Get role
        user_role = user.get_roles().first()
        role_name = user_role.role.name if user_role else 'N/A'

        # Get salary config
        config = None
        if user_role:
            config = SalaryConfiguration.objects.filter(
                role=user_role.role,
                is_active=True
            ).first()

        if payroll:
            result.append({
                'user_id': user.id,
                'user_name': user.full_name,
                'user_email': user.email,
                'role_name': role_name,
                'base_salary': payroll.base_salary,
                'working_days': payroll.working_days,
                'kpi_score': payroll.kpi_score,
                'sales_revenue': payroll.sales_revenue,
                'net_salary': payroll.net_salary,
                'status': payroll.status,
                'payroll_id': payroll.id
            })
        else:
            # Not calculated yet
            result.append({
                'user_id': user.id,
                'user_name': user.full_name,
                'user_email': user.email,
                'role_name': role_name,
                'base_salary': config.base_salary if config else Decimal('0'),
                'working_days': Decimal('0'),
                'kpi_score': Decimal('0'),
                'sales_revenue': Decimal('0'),
                'net_salary': Decimal('0'),
                'status': 'not_calculated',
                'payroll_id': None
            })

    return result


@router.get("/{payroll_id}", response=PayrollRead)
def get_payroll(request, payroll_id: UUID):
    """Lấy chi tiết bảng lương"""
    payroll = get_object_or_404(Payroll, id=payroll_id)
    return _payroll_to_dict(payroll)


@router.put("/{payroll_id}/status", response=PayrollRead)
def update_payroll_status(request, payroll_id: UUID, payload: PayrollStatusUpdate):
    """Cập nhật trạng thái bảng lương"""
    from django.utils import timezone

    payroll = get_object_or_404(Payroll, id=payroll_id)
    payroll.status = payload.status

    if payload.notes:
        payroll.notes = payload.notes

    # Update timestamps
    if payload.status == 'approved':
        payroll.approved_at = timezone.now()
    elif payload.status == 'paid':
        payroll.paid_at = timezone.now()

    payroll.save()
    return _payroll_to_dict(payroll)


@router.post("/approve", response=dict)
def approve_payrolls(request, payload: PayrollApproveRequest):
    """Duyệt nhiều bảng lương cùng lúc"""
    from django.utils import timezone

    payrolls = Payroll.objects.filter(id__in=payload.payroll_ids)

    updated_count = 0
    for payroll in payrolls:
        if payroll.status in ['draft', 'pending']:
            payroll.status = 'approved'
            payroll.approved_at = timezone.now()
            if payload.notes:
                payroll.notes = payload.notes
            payroll.save()
            updated_count += 1

    return {
        'success': True,
        'updated_count': updated_count,
        'total': len(payload.payroll_ids)
    }


@router.post("/mark-paid", response=dict)
def mark_payrolls_paid(request, payload: PayrollApproveRequest):
    """Đánh dấu đã chi trả lương"""
    from django.utils import timezone

    payrolls = Payroll.objects.filter(id__in=payload.payroll_ids, status='approved')

    updated_count = 0
    for payroll in payrolls:
        payroll.status = 'paid'
        payroll.paid_at = timezone.now()
        if payload.notes:
            payroll.notes = payload.notes
        payroll.save()
        updated_count += 1

    return {
        'success': True,
        'updated_count': updated_count,
        'total': len(payload.payroll_ids)
    }


@router.delete("/{payroll_id}")
def delete_payroll(request, payroll_id: UUID):
    """Xóa bảng lương (chỉ draft)"""
    payroll = get_object_or_404(Payroll, id=payroll_id)

    if payroll.status != 'draft':
        from api.exceptions import BadRequest
        raise BadRequest("Chỉ có thể xóa bảng lương ở trạng thái nháp")

    payroll.delete()
    return {'success': True, 'message': 'Đã xóa bảng lương'}


def _payroll_to_dict(payroll: Payroll) -> dict:
    """Convert payroll to dict with user info"""
    user_role = payroll.user.get_roles().first()

    return {
        'id': payroll.id,
        'user_id': payroll.user.id,
        'user_name': payroll.user.full_name,
        'user_email': payroll.user.email,
        'user_role': user_role.role.name if user_role else 'N/A',
        'year': payroll.year,
        'month': payroll.month,
        'base_salary': payroll.base_salary,
        'working_days': payroll.working_days,
        'standard_working_days': payroll.standard_working_days,
        'actual_base_salary': payroll.actual_base_salary,
        'total_allowances': payroll.total_allowances,
        'attendance_allowance': payroll.attendance_allowance,
        'transportation_allowance': payroll.transportation_allowance,
        'meal_allowance': payroll.meal_allowance,
        'phone_allowance': payroll.phone_allowance,
        'total_bonuses': payroll.total_bonuses,
        'sales_commission': payroll.sales_commission,
        'sales_revenue': payroll.sales_revenue,
        'kpi_score': payroll.kpi_score,
        'kpi_bonus': payroll.kpi_bonus,
        'other_bonus': payroll.other_bonus,
        'gross_salary': payroll.gross_salary,
        'total_insurance': payroll.total_insurance,
        'social_insurance': payroll.social_insurance,
        'health_insurance': payroll.health_insurance,
        'unemployment_insurance': payroll.unemployment_insurance,
        'taxable_income': payroll.taxable_income,
        'personal_income_tax': payroll.personal_income_tax,
        'personal_deduction': payroll.personal_deduction,
        'dependent_deduction': payroll.dependent_deduction,
        'total_deductions': payroll.total_deductions,
        'advance_payment': payroll.advance_payment,
        'penalty': payroll.penalty,
        'other_deduction': payroll.other_deduction,
        'net_salary': payroll.net_salary,
        'status': payroll.status,
        'notes': payroll.notes,
        'created_at': payroll.created_at,
        'approved_at': payroll.approved_at,
        'paid_at': payroll.paid_at,
    }
