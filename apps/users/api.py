"""
Users API Endpoints
RESTful API for user management
"""
from typing import List, Optional
from uuid import UUID
from ninja import Router

from .models import User, Attendance
from .schemas import (
    UserCreate, UserUpdate, UserRead, UserLogin, UserLoginResponse,
    AttendanceCreate, AttendanceUpdate, AttendanceRead, AttendanceCalendar
)
from .services import UserService
from .authentication import JWTAuth
from .jwt_utils import create_access_token
from apps.rbac.schemas import MessageResponse
from apps.rbac.permissions import require_permission


router = Router(tags=["Users"])
jwt_auth = JWTAuth()


@router.post("/register", response=UserRead, auth=None)
def register(request, payload: UserCreate):
    """User registration endpoint"""
    user = UserService.create_user(payload)
    return user


@router.post("/customer/register", response=UserLoginResponse, auth=None)
def customer_register(request, payload: UserCreate):
    """Customer registration endpoint - auto creates customer with default role"""
    from apps.rbac.models import Role, UserRole

    # Create user with customer type
    user_data = payload.model_dump()
    user_data['user_type'] = 'customer'  # Force customer type

    # Create payload with customer type
    customer_payload = UserCreate(**user_data)
    user = UserService.create_user(customer_payload)

    # Assign customer role
    try:
        customer_role = Role.objects.get(slug='customer')
        UserRole.objects.create(
            user=user,
            role=customer_role,
            is_active=True
        )
    except Role.DoesNotExist:
        # If customer role doesn't exist, log warning but continue
        import logging
        logger = logging.getLogger(__name__)
        logger.warning("Customer role not found in database")

    # Generate JWT token automatically
    token = create_access_token(data={"user_id": str(user.id), "email": user.email})

    return {
        "access_token": token,
        "token_type": "Bearer",
        "user": user
    }


@router.post("/login", response=UserLoginResponse, auth=None)
def login(request, payload: UserLogin):
    """User login endpoint with JWT"""
    user = UserService.authenticate_user(
        email=payload.email,
        password=payload.password
    )

    if not user:
        from api.exceptions import Unauthorized
        raise Unauthorized("Invalid credentials")

    # Generate JWT token
    token = create_access_token(data={"user_id": str(user.id), "email": user.email})

    return {
        "access_token": token,
        "token_type": "Bearer",
        "user": user
    }


@router.get("/me", response=UserRead, auth=jwt_auth)
def get_current_user(request):
    """Get current authenticated user"""
    return request.auth


@router.get("/customer/orders", auth=jwt_auth)
def get_customer_orders(request, status: Optional[str] = None):
    """Get orders for the logged-in customer"""
    from apps.seafood.models import Order
    from apps.seafood.schemas import OrderRead

    user = request.auth

    # Only allow customers to access their own orders
    if user.user_type != 'customer':
        from api.exceptions import PermissionDenied
        raise PermissionDenied("Chỉ khách hàng mới có thể truy cập endpoint này")

    # Get orders for this customer - match by customer FK or phone number
    from django.db.models import Q

    # Build query based on whether user has phone
    if user.phone:
        query = Q(customer=user) | Q(customer_phone=user.phone)
    else:
        query = Q(customer=user)

    orders = Order.objects.filter(query).select_related(
        'created_by', 'sale_user', 'assigned_employee', 'customer', 'weighed_by', 'shipped_by'
    ).prefetch_related('items__seafood').order_by('-created_at')

    if status:
        orders = orders.filter(status=status)

    # Manual conversion to avoid RelatedManager serialization issue
    result = []
    for order in orders:
        items_list = [
            {
                'id': item.id,
                'seafood_id': item.seafood_id,
                'seafood': {
                    'id': item.seafood.id,
                    'name': item.seafood.name,
                    'code': item.seafood.code,
                    'unit_type': item.seafood.unit_type,
                    'current_price': float(item.seafood.current_price),
                } if item.seafood else None,
                'quantity': float(item.quantity) if item.quantity else 0,
                'weight': float(item.weight),
                'unit_price': float(item.unit_price),
                'subtotal': float(item.subtotal) if hasattr(item, 'subtotal') else float(item.weight * item.unit_price),
                'notes': item.notes or '',
            }
            for item in order.items.all()
        ]
        order_dict = {
            'id': order.id,
            'order_code': order.order_code,
            'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'customer_address': order.customer_address,
            'customer_source': order.customer_source,
            'subtotal': float(order.subtotal),
            'discount_amount': float(order.discount_amount),
            'total_amount': float(order.total_amount),
            'paid_amount': float(order.paid_amount),
            'payment_method': order.payment_method or '',
            'payment_status': order.payment_status,
            'status': order.status,
            'notes': order.notes,
            'created_at': order.created_at,
            'customer_id': order.customer_id,
            'sale_user_id': order.sale_user_id,
            'confirmed_by_sale_at': order.confirmed_by_sale_at,
            'assigned_employee_id': order.assigned_employee_id,
            'assigned_at': order.assigned_at,
            'weighed_at': order.weighed_at,
            'weighed_by_id': order.weighed_by_id,
            'weight_images': order.weight_images,
            'shipped_at': order.shipped_at,
            'shipped_by_id': order.shipped_by_id,
            'shipping_notes': order.shipping_notes,
            'delivered_at': order.delivered_at,
            'delivered_by_id': order.delivered_by_id if hasattr(order, 'delivered_by_id') else None,
            'items': items_list
        }
        result.append(order_dict)

    return result


@router.get("/customer/orders/{order_id}", auth=jwt_auth)
def get_customer_order_detail(request, order_id: UUID):
    """Get single order detail for the logged-in customer"""
    from apps.seafood.models import Order
    from django.shortcuts import get_object_or_404
    from django.db.models import Q
    from api.exceptions import PermissionDenied

    user = request.auth

    # Only allow customers to access their own orders
    if user.user_type != 'customer':
        raise PermissionDenied("Chỉ khách hàng mới có thể truy cập endpoint này")

    # Get the order - check both customer FK and phone number
    # (Some old orders might not have customer FK but have matching phone number)
    try:
        # Build query - always check customer FK
        if user.phone:
            # If user has phone, also match by phone number
            query = Q(id=order_id) & (Q(customer=user) | Q(customer_phone=user.phone))
        else:
            # If no phone, only match by customer FK
            query = Q(id=order_id) & Q(customer=user)

        order = Order.objects.get(query)
    except Order.DoesNotExist:
        raise PermissionDenied("Bạn không có quyền xem đơn hàng này hoặc đơn hàng không tồn tại")

    # Get order items
    items_list = [
        {
            'id': item.id,
            'seafood_id': item.seafood_id,
            'seafood': {
                'id': item.seafood.id,
                'name': item.seafood.name,
                'code': item.seafood.code,
                'unit_type': item.seafood.unit_type,
                'current_price': float(item.seafood.current_price),
            } if item.seafood else None,
            'quantity': float(item.quantity) if item.quantity else 0,
            'weight': float(item.weight),
            'unit_price': float(item.unit_price),
            'subtotal': float(item.subtotal) if hasattr(item, 'subtotal') else float(item.weight * item.unit_price),
            'notes': item.notes or '',
            'weight_image_url': item.weight_image_url or '',
        }
        for item in order.items.all()
    ]

    return {
        'id': order.id,
        'order_code': order.order_code,
        'customer_name': order.customer_name or '',
        'customer_phone': order.customer_phone,
        'customer_address': order.customer_address or '',
        'customer_source': order.customer_source or '',
        'subtotal': float(order.subtotal),
        'discount_amount': float(order.discount_amount),
        'total_amount': float(order.total_amount),
        'paid_amount': float(order.paid_amount),
        'payment_method': order.payment_method or '',
        'payment_status': order.payment_status,
        'status': order.status,
        'notes': order.notes or '',
        'created_at': order.created_at,
        'customer_id': order.customer_id,
        'sale_user_id': order.sale_user_id,
        'confirmed_by_sale_at': order.confirmed_by_sale_at,
        'assigned_employee_id': order.assigned_employee_id,
        'assigned_at': order.assigned_at,
        'weighed_at': order.weighed_at,
        'weighed_by': order.weighed_by.full_name if order.weighed_by else '',
        'weighed_by_id': order.weighed_by_id,
        'weight_images': order.weight_images,
        'shipped_at': order.shipped_at,
        'shipped_by': order.shipped_by.full_name if order.shipped_by else '',
        'shipped_by_id': order.shipped_by_id,
        'shipping_notes': order.shipping_notes or '',
        'delivered_at': order.delivered_at if hasattr(order, 'delivered_at') else None,
        'delivered_by_id': order.delivered_by_id if hasattr(order, 'delivered_by_id') else None,
        'items': items_list
    }


@router.get("", response=List[UserRead], auth=jwt_auth)
def list_users(
    request,
    department_id: Optional[UUID] = None,
    is_active: bool = True,
    search: Optional[str] = None
):
    """List all users with optional filters - Admin/Manager only"""
    # Check if user is customer - customers cannot list users
    if request.auth.user_type == 'customer':
        from api.exceptions import PermissionDenied
        raise PermissionDenied("Khách hàng không có quyền truy cập chức năng này")

    users = UserService.list_users(
        department_id=department_id,
        is_active=is_active,
        search=search
    )
    return users


@router.get("/{user_id}", response=UserRead, auth=jwt_auth)
def get_user(request, user_id: UUID):
    """Get user by ID"""
    user = UserService.get_user(user_id)
    return user


@router.post("", response=UserRead, auth=jwt_auth)
def create_user(request, payload: UserCreate):
    """Create new user"""
    user = UserService.create_user(payload)
    return user


@router.put("/{user_id}", response=UserRead, auth=jwt_auth)
def update_user(request, user_id: UUID, payload: UserUpdate):
    """Update existing user"""
    user = UserService.update_user(user_id, payload)
    return user


@router.delete("/{user_id}", response=MessageResponse, auth=jwt_auth)
def delete_user(request, user_id: UUID, hard: bool = False):
    """Delete user (soft delete by default)"""
    UserService.delete_user(user_id, soft=not hard)
    return {"message": "User deleted successfully"}


# ============================================
# STAFF KPI ENDPOINTS
# ============================================

@router.get("/staff/kpi-stats", auth=None)
def get_staff_kpi_stats(request, user_id: UUID = None):
    """Get KPI statistics for staff (day/month/year)"""
    from django.db.models import Sum, Count
    from apps.seafood.models import Order
    from decimal import Decimal
    from django.utils import timezone
    from datetime import datetime, timedelta

    # TODO: Get user_id from auth instead of param
    # For now, calculate for all staff or specific user

    today = timezone.now().date()
    current_month_start = today.replace(day=1)
    current_year_start = today.replace(month=1, day=1)

    # Base query - filter by created_by if user_id provided
    base_query = Order.objects.filter(status='completed')
    if user_id:
        base_query = base_query.filter(created_by_id=user_id)

    # Today stats
    today_orders = base_query.filter(created_at__date=today)
    today_stats = today_orders.aggregate(
        orders=Count('id'),
        revenue=Sum('total_amount'),
        items_sold=Count('items')
    )

    # Month stats
    month_orders = base_query.filter(created_at__date__gte=current_month_start)
    month_stats = month_orders.aggregate(
        orders=Count('id'),
        revenue=Sum('total_amount'),
        items_sold=Count('items')
    )

    # Year stats
    year_orders = base_query.filter(created_at__date__gte=current_year_start)
    year_stats = year_orders.aggregate(
        orders=Count('id'),
        revenue=Sum('total_amount'),
        items_sold=Count('items')
    )

    # Calculate month target (example: 100M VND)
    target_revenue = Decimal('100000000')
    month_revenue = month_stats['revenue'] or Decimal('0')
    completion_rate = (month_revenue / target_revenue * 100) if target_revenue > 0 else 0

    return {
        "today": {
            "orders": today_stats['orders'] or 0,
            "revenue": float(today_stats['revenue'] or 0),
            "items_sold": today_stats['items_sold'] or 0,
        },
        "month": {
            "orders": month_stats['orders'] or 0,
            "revenue": float(month_stats['revenue'] or 0),
            "items_sold": month_stats['items_sold'] or 0,
            "target_revenue": float(target_revenue),
            "completion_rate": float(completion_rate),
        },
        "year": {
            "orders": year_stats['orders'] or 0,
            "revenue": float(year_stats['revenue'] or 0),
            "items_sold": year_stats['items_sold'] or 0,
        }
    }


@router.get("/staff/monthly-stats", auth=None)
def get_staff_monthly_stats(request, user_id: UUID = None, months: int = 12):
    """Get monthly performance stats grouped by month"""
    from django.db.models import Sum, Count
    from django.db.models.functions import TruncMonth
    from apps.seafood.models import Order
    from django.utils import timezone
    from datetime import datetime, timedelta

    # Get orders from last N months
    end_date = timezone.now()
    start_date = end_date - timedelta(days=months * 30)

    # Base query
    base_query = Order.objects.filter(
        status='completed',
        created_at__gte=start_date
    )
    if user_id:
        base_query = base_query.filter(created_by_id=user_id)

    # Group by month
    monthly_data = base_query.annotate(
        month_date=TruncMonth('created_at')
    ).values('month_date').annotate(
        orders=Count('id'),
        revenue=Sum('total_amount'),
        items_sold=Count('items')
    ).order_by('-month_date')

    # Format response
    result = []
    for item in monthly_data:
        month_date = item['month_date']
        result.append({
            "month": str(month_date.month).zfill(2),
            "year": month_date.year,
            "orders": item['orders'],
            "revenue": float(item['revenue'] or 0),
            "items_sold": item['items_sold'],
        })

    return result


@router.get("/staff/weekly-details", auth=None)
def get_staff_weekly_details(request, user_id: UUID = None, weeks: int = 4):
    """Get detailed weekly breakdown with daily orders"""
    from django.db.models import Sum, Count
    from django.db.models.functions import TruncDate
    from apps.seafood.models import Order
    from django.utils import timezone
    from datetime import datetime, timedelta

    # Get data for last N weeks
    end_date = timezone.now()
    start_date = end_date - timedelta(weeks=weeks)

    # Base query
    base_query = Order.objects.filter(created_at__gte=start_date)
    if user_id:
        base_query = base_query.filter(created_by_id=user_id)

    # Group orders by week and day
    result = []
    current_date = end_date.date()

    for week_num in range(weeks):
        # Calculate week boundaries (Monday to Sunday)
        week_start = current_date - timedelta(days=current_date.weekday() + (week_num * 7))
        week_end = week_start + timedelta(days=6)

        # Get all orders in this week
        week_orders = base_query.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=week_end
        )

        # Group by day
        days_data = []
        for day_offset in range(7):
            current_day = week_start + timedelta(days=day_offset)

            # Get orders for this day
            day_orders = week_orders.filter(created_at__date=current_day)

            # Get order details
            orders_list = []
            for order in day_orders:
                orders_list.append({
                    "id": str(order.id),
                    "order_code": order.order_code,
                    "customer_name": order.customer_name or "",
                    "customer_phone": order.customer_phone,
                    "total_amount": float(order.total_amount),
                    "paid_amount": float(order.paid_amount),
                    "payment_status": order.payment_status,
                    "created_at": order.created_at.isoformat(),
                })

            # Calculate day stats
            day_stats = day_orders.aggregate(
                total_revenue=Sum('total_amount'),
                total_paid=Sum('paid_amount')
            )

            days_data.append({
                "date": current_day.isoformat(),
                "total_orders": day_orders.count(),
                "total_revenue": float(day_stats['total_revenue'] or 0),
                "total_paid": float(day_stats['total_paid'] or 0),
                "total_unpaid": float((day_stats['total_revenue'] or 0) - (day_stats['total_paid'] or 0)),
                "orders": orders_list
            })

        # Calculate week totals
        week_stats = week_orders.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount')
        )

        result.append({
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "days": days_data,
            "total_orders": week_stats['total_orders'] or 0,
            "total_revenue": float(week_stats['total_revenue'] or 0)
        })

    return result


@router.get("/staff/kpi-summary", auth=None)
def get_staff_kpi_summary(request, user_id: UUID = None):
    """Get KPI summary for header"""
    from django.db.models import Sum, Count
    from apps.seafood.models import Order
    from django.utils import timezone
    from datetime import timedelta

    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    # Base query
    base_query = Order.objects.all()
    if user_id:
        base_query = base_query.filter(created_by_id=user_id)

    # Today stats
    today_stats = base_query.filter(created_at__date=today).aggregate(
        revenue=Sum('total_amount'),
        paid=Sum('paid_amount')
    )

    # Week stats
    week_stats = base_query.filter(created_at__date__gte=week_start).aggregate(
        revenue=Sum('total_amount')
    )

    # Month stats
    month_stats = base_query.filter(created_at__date__gte=month_start).aggregate(
        revenue=Sum('total_amount')
    )

    # Calculate service efficiency (example: % of completed orders)
    total_orders = base_query.filter(created_at__date__gte=month_start).count()
    completed_orders = base_query.filter(
        created_at__date__gte=month_start,
        status='completed'
    ).count()
    service_efficiency = (completed_orders / total_orders * 100) if total_orders > 0 else 0

    return {
        "today_revenue": float(today_stats['revenue'] or 0),
        "today_paid": float(today_stats['paid'] or 0),
        "week_revenue": float(week_stats['revenue'] or 0),
        "month_revenue": float(month_stats['revenue'] or 0),
        "service_efficiency": float(service_efficiency)
    }


@router.get("/staff/all-kpi-summary", auth=jwt_auth)
def get_all_staff_kpi_summary(request):
    """Get KPI summary for all staff members - For Admin/Manager/Accountant"""
    from django.db.models import Sum, Count
    from apps.seafood.models import Order
    from django.utils import timezone
    from datetime import timedelta

    # Get all users who have created orders (staff members)
    # Use Order.created_by to find users who created orders
    user_ids = Order.objects.values_list('created_by_id', flat=True).distinct()
    users = User.objects.filter(id__in=user_ids)

    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)

    result = []
    for user in users:
        base_query = Order.objects.filter(created_by=user)

        # Today stats
        today_stats = base_query.filter(created_at__date=today).aggregate(
            revenue=Sum('total_amount'),
            paid=Sum('paid_amount')
        )

        # Week stats
        week_stats = base_query.filter(created_at__date__gte=week_start).aggregate(
            revenue=Sum('total_amount')
        )

        # Month stats
        month_stats = base_query.filter(created_at__date__gte=month_start).aggregate(
            revenue=Sum('total_amount')
        )

        # Calculate service efficiency
        total_orders = base_query.filter(created_at__date__gte=month_start).count()
        completed_orders = base_query.filter(
            created_at__date__gte=month_start,
            status='completed'
        ).count()
        service_efficiency = (completed_orders / total_orders * 100) if total_orders > 0 else 0

        result.append({
            "user_id": str(user.id),
            "user_email": user.email,
            "user_name": f"{user.first_name} {user.last_name}".strip() or user.email,
            "today_revenue": float(today_stats['revenue'] or 0),
            "today_paid": float(today_stats['paid'] or 0),
            "week_revenue": float(week_stats['revenue'] or 0),
            "month_revenue": float(month_stats['revenue'] or 0),
            "service_efficiency": float(service_efficiency)
        })

    # Sort by month revenue descending
    result.sort(key=lambda x: x['month_revenue'], reverse=True)

    return result


# ============================================
# ATTENDANCE ENDPOINTS
# ============================================

@router.get("/attendance", response=List[AttendanceRead], auth=None)
def list_attendance(
    request,
    user_id: Optional[UUID] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """List attendance records with optional filters"""
    from datetime import datetime

    query = Attendance.objects.all()

    if user_id:
        query = query.filter(user_id=user_id)

    if start_date:
        start = datetime.fromisoformat(start_date).date()
        query = query.filter(date__gte=start)

    if end_date:
        end = datetime.fromisoformat(end_date).date()
        query = query.filter(date__lte=end)

    return list(query.select_related('user'))


@router.post("/attendance", response=AttendanceRead, auth=None)
def create_attendance(request, payload: AttendanceCreate):
    """Create attendance record"""
    from api.exceptions import BadRequest

    # Check if attendance already exists for this user and date
    existing = Attendance.objects.filter(
        user_id=payload.user_id,
        date=payload.date.date()
    ).first()

    if existing:
        raise BadRequest("Chấm công cho ngày này đã tồn tại")

    attendance = Attendance.objects.create(
        user_id=payload.user_id,
        date=payload.date.date(),
        attendance_type=payload.attendance_type,
        check_in_time=payload.check_in_time.time() if payload.check_in_time else None,
        check_out_time=payload.check_out_time.time() if payload.check_out_time else None,
        notes=payload.notes,
        created_by_id=request.auth.id if hasattr(request, 'auth') and request.auth else None
    )

    return attendance


@router.put("/attendance/{attendance_id}", response=AttendanceRead, auth=None)
def update_attendance(request, attendance_id: UUID, payload: AttendanceUpdate):
    """Update attendance record"""
    from api.exceptions import ResourceNotFound

    try:
        attendance = Attendance.objects.get(id=attendance_id)
    except Attendance.DoesNotExist:
        raise ResourceNotFound("Không tìm thấy bản ghi chấm công")

    if payload.attendance_type is not None:
        attendance.attendance_type = payload.attendance_type
    if payload.check_in_time is not None:
        attendance.check_in_time = payload.check_in_time.time() if payload.check_in_time else None
    if payload.check_out_time is not None:
        attendance.check_out_time = payload.check_out_time.time() if payload.check_out_time else None
    if payload.notes is not None:
        attendance.notes = payload.notes

    attendance.save()
    return attendance


@router.delete("/attendance/{attendance_id}", response=MessageResponse, auth=None)
def delete_attendance(request, attendance_id: UUID):
    """Delete attendance record"""
    from api.exceptions import ResourceNotFound

    try:
        attendance = Attendance.objects.get(id=attendance_id)
    except Attendance.DoesNotExist:
        raise ResourceNotFound("Không tìm thấy bản ghi chấm công")

    attendance.delete()
    return {"message": "Đã xóa bản ghi chấm công"}


@router.get("/attendance/calendar/{user_id}", response=List[AttendanceCalendar], auth=None)
def get_attendance_calendar(
    request,
    user_id: UUID,
    year: Optional[int] = None,
    month: Optional[int] = None
):
    """Get attendance calendar for a specific user and month"""
    from django.utils import timezone
    from datetime import datetime, timedelta
    from calendar import monthrange
    from apps.seafood.models import Order

    # Default to current month if not provided
    now = timezone.now()
    year = year or now.year
    month = month or now.month

    # Get user's account creation date
    try:
        user = User.objects.get(id=user_id)
        account_start_date = user.date_joined.date()
    except User.DoesNotExist:
        from api.exceptions import ResourceNotFound
        raise ResourceNotFound("Không tìm thấy người dùng")

    # Get first and last day of the month
    first_day = datetime(year, month, 1).date()
    last_day = datetime(year, month, monthrange(year, month)[1]).date()

    # Only show from account creation date
    if first_day < account_start_date:
        first_day = account_start_date

    # Get all attendance records for this month (skip if table doesn't exist)
    try:
        attendances = Attendance.objects.filter(
            user_id=user_id,
            date__gte=first_day,
            date__lte=last_day
        )
        # Create a dict for quick lookup
        attendance_dict = {att.date: att for att in attendances}
    except:
        # If attendance table doesn't exist, use empty dict
        attendance_dict = {}

    # Get orders for this month to show if user had orders
    orders_by_date = {}
    orders = Order.objects.filter(
        created_by_id=user_id,
        created_at__date__gte=first_day,
        created_at__date__lte=last_day
    )
    for order in orders:
        order_date = order.created_at.date()
        if order_date not in orders_by_date:
            orders_by_date[order_date] = 0
        orders_by_date[order_date] += 1

    # Build calendar data for each day
    result = []
    current_date = first_day
    while current_date <= last_day:
        attendance = attendance_dict.get(current_date)

        if attendance:
            result.append({
                "date": current_date.isoformat(),
                "attendance_type": attendance.attendance_type,
                "check_in_time": attendance.check_in_time.isoformat() if attendance.check_in_time else None,
                "check_out_time": attendance.check_out_time.isoformat() if attendance.check_out_time else None,
                "working_hours": attendance.working_hours,
                "has_orders": current_date in orders_by_date,
                "orders_count": orders_by_date.get(current_date, 0)
            })
        else:
            # Default to "off" if no attendance record
            result.append({
                "date": current_date.isoformat(),
                "attendance_type": "off",
                "check_in_time": None,
                "check_out_time": None,
                "working_hours": 0,
                "has_orders": current_date in orders_by_date,
                "orders_count": orders_by_date.get(current_date, 0)
            })

        current_date += timedelta(days=1)

    return result


@router.get("/staff/monthly-details/{user_id}", auth=None)
def get_staff_monthly_details(request, user_id: UUID, months: int = 12):
    """Get detailed monthly breakdown grouped by month from account creation to now"""
    from django.db.models import Sum, Count
    from django.db.models.functions import TruncDate
    from apps.seafood.models import Order
    from django.utils import timezone
    from datetime import datetime, timedelta
    from calendar import monthrange

    # Get user's account creation date
    try:
        user = User.objects.get(id=user_id)
        start_date = user.date_joined.date()
    except User.DoesNotExist:
        from api.exceptions import ResourceNotFound
        raise ResourceNotFound("Không tìm thấy người dùng")

    end_date = timezone.now().date()

    # Get all orders for this user from account creation to now
    base_query = Order.objects.filter(
        created_by_id=user_id,
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )

    # Group by month
    result = []
    current_month_start = end_date.replace(day=1)

    while current_month_start >= start_date.replace(day=1):
        # Calculate month boundaries
        year = current_month_start.year
        month = current_month_start.month
        month_end = datetime(year, month, monthrange(year, month)[1]).date()

        # Get orders for this month
        month_orders = base_query.filter(
            created_at__date__gte=current_month_start,
            created_at__date__lte=month_end
        )

        # Get attendance for this month (skip if table doesn't exist)
        try:
            attendances = Attendance.objects.filter(
                user_id=user_id,
                date__gte=current_month_start,
                date__lte=month_end
            )
            # Count working days
            full_days = attendances.filter(attendance_type='full').count()
            half_days = attendances.filter(attendance_type='half').count()
            off_days = attendances.filter(attendance_type='off').count()
        except:
            # If attendance table doesn't exist, use default values
            attendances = []
            full_days = 0
            half_days = 0
            off_days = 0

        # Calculate total working days (half day = 0.5)
        total_working_days = full_days + (half_days * 0.5)

        # Group orders by day
        days_data = []
        current_day = current_month_start
        while current_day <= month_end and current_day <= end_date:
            day_orders = month_orders.filter(created_at__date=current_day)

            # Get attendance for this day
            try:
                attendance = attendances.filter(date=current_day).first() if attendances else None
            except:
                attendance = None

            # Get order details
            orders_list = []
            for order in day_orders:
                orders_list.append({
                    "id": str(order.id),
                    "order_code": order.order_code,
                    "customer_name": order.customer_name or "",
                    "customer_phone": order.customer_phone,
                    "total_amount": float(order.total_amount),
                    "paid_amount": float(order.paid_amount),
                    "payment_status": order.payment_status,
                    "created_at": order.created_at.isoformat(),
                })

            # Calculate day stats
            day_stats = day_orders.aggregate(
                total_revenue=Sum('total_amount'),
                total_paid=Sum('paid_amount')
            )

            days_data.append({
                "date": current_day.isoformat(),
                "total_orders": day_orders.count(),
                "total_revenue": float(day_stats['total_revenue'] or 0),
                "total_paid": float(day_stats['total_paid'] or 0),
                "total_unpaid": float((day_stats['total_revenue'] or 0) - (day_stats['total_paid'] or 0)),
                "orders": orders_list,
                "attendance_type": attendance.attendance_type if attendance else "off",
                "check_in_time": attendance.check_in_time.isoformat() if attendance and attendance.check_in_time else None,
                "check_out_time": attendance.check_out_time.isoformat() if attendance and attendance.check_out_time else None,
                "working_hours": attendance.working_hours if attendance else 0
            })

            current_day += timedelta(days=1)

        # Calculate month totals
        month_stats = month_orders.aggregate(
            total_orders=Count('id'),
            total_revenue=Sum('total_amount'),
            total_paid=Sum('paid_amount')
        )

        result.append({
            "year": year,
            "month": month,
            "month_start": current_month_start.isoformat(),
            "month_end": month_end.isoformat(),
            "days": days_data,
            "total_orders": month_stats['total_orders'] or 0,
            "total_revenue": float(month_stats['total_revenue'] or 0),
            "total_paid": float(month_stats['total_paid'] or 0),
            "total_unpaid": float((month_stats['total_revenue'] or 0) - (month_stats['total_paid'] or 0)),
            "full_days": full_days,
            "half_days": half_days,
            "off_days": off_days,
            "total_working_days": total_working_days
        })

        # Move to previous month
        if current_month_start.month == 1:
            current_month_start = current_month_start.replace(year=current_month_start.year - 1, month=12)
        else:
            current_month_start = current_month_start.replace(month=current_month_start.month - 1)

        # Limit to requested number of months
        if len(result) >= months:
            break

    return result
