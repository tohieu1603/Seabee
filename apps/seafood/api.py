"""
API endpoints cho hệ thống bán hải sản
"""
from ninja import Router
from typing import List
from django.shortcuts import get_object_or_404
from django.db.models import Sum, F, Q
from django.utils import timezone
from decimal import Decimal
from uuid import UUID
import uuid

from .models import (
    SeafoodCategory, Seafood, ImportSource, ImportBatch,
    Order, OrderItem, InventoryLog
)
from .schemas import (
    CategoryRead, CategoryCreate, CategoryUpdate,
    SeafoodRead, SeafoodCreate, SeafoodUpdate,
    ImportSourceRead, ImportSourceCreate, ImportSourceUpdate,
    ImportBatchRead, ImportBatchCreate, ImportBatchUpdate,
    OrderRead, OrderCreate, OrderUpdate, OrderItemRead,
    DashboardStats, ProductStats
)

router = Router(tags=["Seafood"], auth=None)  # No auth required for seafood APIs


# ============================================
# CATEGORY ENDPOINTS
# ============================================

@router.get("/categories", response=List[CategoryRead])
def list_categories(request):
    """Lấy danh sách danh mục"""
    return SeafoodCategory.objects.filter(is_active=True).all()


@router.post("/categories", response=CategoryRead)
def create_category(request, payload: CategoryCreate):
    """Tạo danh mục mới"""
    category = SeafoodCategory.objects.create(**payload.dict())
    return category


@router.put("/categories/{category_id}", response=CategoryRead)
def update_category(request, category_id: UUID, payload: CategoryUpdate):
    """Cập nhật danh mục"""
    category = get_object_or_404(SeafoodCategory, id=category_id)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(category, key, value)
    category.save()
    return category


@router.delete("/categories/{category_id}")
def delete_category(request, category_id: UUID):
    """Xóa danh mục (soft delete)"""
    category = get_object_or_404(SeafoodCategory, id=category_id)
    category.is_active = False
    category.save()
    return {"success": True}


# ============================================
# SEAFOOD PRODUCTS ENDPOINTS
# ============================================

@router.get("/products", response=List[SeafoodRead])
def list_products(request, category_id: UUID = None, status: str = None, search: str = None):
    """Lấy danh sách sản phẩm hải sản"""
    query = Seafood.objects.filter(is_active=True).select_related('category')

    if category_id:
        query = query.filter(category_id=category_id)
    if status:
        query = query.filter(status=status)
    if search:
        query = query.filter(Q(name__icontains=search) | Q(code__icontains=search))

    return query.all()


@router.get("/products/{product_id}", response=SeafoodRead)
def get_product(request, product_id: UUID):
    """Lấy chi tiết sản phẩm"""
    return get_object_or_404(Seafood.objects.select_related('category'), id=product_id)


@router.post("/products", response=SeafoodRead)
def create_product(request, payload: SeafoodCreate):
    """Tạo sản phẩm mới"""
    product = Seafood.objects.create(**payload.dict())
    return product


@router.put("/products/{product_id}", response=SeafoodRead)
def update_product(request, product_id: UUID, payload: SeafoodUpdate):
    """Cập nhật sản phẩm"""
    product = get_object_or_404(Seafood, id=product_id)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(product, key, value)
    product.save()
    return product


@router.delete("/products/{product_id}")
def delete_product(request, product_id: UUID):
    """Xóa sản phẩm (soft delete)"""
    product = get_object_or_404(Seafood, id=product_id)
    product.is_active = False
    product.save()
    return {"success": True}


# ============================================
# IMPORT SOURCE ENDPOINTS
# ============================================

@router.get("/import-sources", response=List[ImportSourceRead])
def list_import_sources(request):
    """Lấy danh sách nguồn nhập hàng"""
    return ImportSource.objects.filter(is_active=True).all()


@router.post("/import-sources", response=ImportSourceRead)
def create_import_source(request, payload: ImportSourceCreate):
    """Tạo nguồn nhập hàng mới"""
    source = ImportSource.objects.create(**payload.dict())
    return source


@router.put("/import-sources/{source_id}", response=ImportSourceRead)
def update_import_source(request, source_id: UUID, payload: ImportSourceUpdate):
    """Cập nhật nguồn nhập hàng"""
    source = get_object_or_404(ImportSource, id=source_id)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(source, key, value)
    source.save()
    return source


# ============================================
# IMPORT BATCH ENDPOINTS
# ============================================

@router.get("/import-batches", response=List[ImportBatchRead])
def list_import_batches(request, seafood_id: UUID = None):
    """Lấy danh sách lô nhập hàng"""
    query = ImportBatch.objects.filter(is_active=True).select_related(
        'seafood', 'seafood__category', 'import_source'
    )

    if seafood_id:
        query = query.filter(seafood_id=seafood_id)

    return query.all()


@router.get("/import-batches/{batch_id}", response=ImportBatchRead)
def get_import_batch(request, batch_id: UUID):
    """Lấy chi tiết lô nhập hàng"""
    return get_object_or_404(
        ImportBatch.objects.select_related('seafood', 'seafood__category', 'import_source'),
        id=batch_id
    )


@router.post("/import-batches", response=ImportBatchRead)
def create_import_batch(request, payload: ImportBatchCreate):
    """Tạo lô nhập hàng mới"""
    data = payload.dict()

    # Tạo batch_code tự động nếu không có
    if not data.get('batch_code'):
        today = timezone.now().strftime('%Y%m%d')
        count = ImportBatch.objects.filter(batch_code__startswith=f'IMP-{today}').count()
        data['batch_code'] = f'IMP-{today}-{count + 1:03d}'

    # Gán imported_by (optional, set to None if no auth)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    data['imported_by'] = User.objects.filter(is_superuser=True).first()

    batch = ImportBatch.objects.create(**data)

    # Cập nhật stock sản phẩm
    seafood = batch.seafood
    seafood.stock_quantity = Decimal(str(seafood.stock_quantity)) + batch.total_weight
    seafood.current_price = batch.sell_price
    seafood.save()

    # Tạo inventory log
    InventoryLog.objects.create(
        seafood=seafood,
        import_batch=batch,
        type='import',
        weight_change=batch.total_weight,
        stock_after=seafood.stock_quantity,
        notes=f'Nhập lô {batch.batch_code}',
        created_by=data['imported_by']
    )

    return batch


@router.put("/import-batches/{batch_id}", response=ImportBatchRead)
def update_import_batch(request, batch_id: UUID, payload: ImportBatchUpdate):
    """Cập nhật lô nhập hàng"""
    batch = get_object_or_404(ImportBatch, id=batch_id)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(batch, key, value)
    batch.save()
    return batch


# ============================================
# ORDER ENDPOINTS (POS)
# ============================================

@router.get("/orders", response=List[OrderRead])
def list_orders(request, status: str = None, customer_phone: str = None, limit: int = 50):
    """Lấy danh sách đơn hàng"""
    query = Order.objects.filter(is_active=True).prefetch_related(
        'items', 'items__seafood', 'items__seafood__category'
    )

    if status:
        query = query.filter(status=status)
    if customer_phone:
        query = query.filter(customer_phone__icontains=customer_phone)

    orders = query.order_by('-created_at')[:limit]

    # Convert to list of dicts to avoid RelatedManager serialization issue
    result = []
    for order in orders:
        items_list = list(order.items.all())
        order_dict = {
            'id': order.id,
            'order_code': order.order_code,
            'customer_name': order.customer_name or '',
            'customer_phone': order.customer_phone,
            'customer_address': order.customer_address or '',
            'payment_method': order.payment_method or '',
            'payment_status': order.payment_status,
            'status': order.status,
            'notes': order.notes or '',
            'discount_amount': order.discount_amount,
            'subtotal': order.subtotal,
            'total_amount': order.total_amount,
            'paid_amount': order.paid_amount,
            'created_at': order.created_at,
            'items': items_list
        }
        result.append(order_dict)

    return result


@router.get("/orders/{order_id}", response=OrderRead)
def get_order(request, order_id: UUID):
    """Lấy chi tiết đơn hàng"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items', 'items__seafood', 'items__seafood__category'),
        id=order_id
    )
    items_list = list(order.items.all())
    return {
        'id': order.id,
        'order_code': order.order_code,
        'customer_name': order.customer_name or '',
        'customer_phone': order.customer_phone,
        'customer_address': order.customer_address or '',
        'payment_method': order.payment_method or '',
        'payment_status': order.payment_status,
        'status': order.status,
        'notes': order.notes or '',
        'discount_amount': order.discount_amount,
        'subtotal': order.subtotal,
        'total_amount': order.total_amount,
        'paid_amount': order.paid_amount,
        'created_at': order.created_at,
        'items': items_list
    }


@router.post("/orders", response=OrderRead)
def create_order(request, payload: OrderCreate):
    """Tạo đơn hàng POS mới"""
    data = payload.dict()
    items_data = data.pop('items')

    # Tạo order_code tự động
    today = timezone.now().strftime('%Y%m%d')
    count = Order.objects.filter(order_code__startswith=f'POS-{today}').count()
    data['order_code'] = f'POS-{today}-{count + 1:03d}'

    # Tính tổng tiền
    subtotal = Decimal('0')
    for item in items_data:
        item_total = Decimal(str(item['weight'])) * Decimal(str(item['unit_price']))
        subtotal += item_total

    data['subtotal'] = subtotal
    data['total_amount'] = subtotal - Decimal(str(data.get('discount_amount', 0)))
    data['paid_amount'] = data['total_amount'] if data.get('payment_status') == 'paid' else Decimal('0')

    # Get default user (admin)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    data['created_by'] = User.objects.filter(is_superuser=True).first()

    # Tạo order
    order = Order.objects.create(**data)

    # Tạo order items và cập nhật stock
    for item_data in items_data:
        seafood = Seafood.objects.get(id=item_data['seafood_id'])
        weight = Decimal(str(item_data['weight']))

        # Tạo order item
        order_item = OrderItem.objects.create(
            order=order,
            seafood=seafood,
            import_batch_id=item_data.get('import_batch_id'),
            weight=weight,
            unit_price=item_data['unit_price'],
            subtotal=weight * Decimal(str(item_data['unit_price'])),
            notes=item_data.get('notes', '')
        )

        # Cập nhật stock sản phẩm
        seafood.stock_quantity = Decimal(str(seafood.stock_quantity)) - weight
        if seafood.stock_quantity <= 0:
            seafood.status = 'out_of_stock'
        seafood.save()

        # Cập nhật batch remaining weight
        if item_data.get('import_batch_id'):
            batch = ImportBatch.objects.get(id=item_data['import_batch_id'])
            batch.remaining_weight = Decimal(str(batch.remaining_weight)) - weight
            if batch.remaining_weight <= 0:
                batch.status = 'sold_out'
            batch.save()

        # Tạo inventory log
        InventoryLog.objects.create(
            seafood=seafood,
            import_batch_id=item_data.get('import_batch_id'),
            order_item=order_item,
            type='sale',
            weight_change=-weight,
            stock_after=seafood.stock_quantity,
            notes=f'Bán cho {order.customer_phone}',
            created_by=data['created_by']
        )

    return get_order(request, order.id)


@router.put("/orders/{order_id}", response=OrderRead)
def update_order(request, order_id: UUID, payload: OrderUpdate):
    """Cập nhật đơn hàng"""
    order = get_object_or_404(Order, id=order_id)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(order, key, value)

    # Cập nhật paid_amount nếu đổi payment_status
    if hasattr(payload, 'payment_status') and payload.payment_status == 'paid':
        order.paid_amount = order.total_amount

    order.save()
    return get_order(request, order_id)


@router.delete("/orders/{order_id}")
def cancel_order(request, order_id: UUID):
    """Hủy đơn hàng"""
    order = get_object_or_404(Order, id=order_id)
    order.status = 'cancelled'
    order.save()

    # Hoàn lại stock
    for item in order.items.all():
        seafood = item.seafood
        weight = Decimal(str(item.weight))
        seafood.stock_quantity = Decimal(str(seafood.stock_quantity)) + weight
        seafood.save()

        # Hoàn lại batch
        if item.import_batch:
            batch = item.import_batch
            batch.remaining_weight = Decimal(str(batch.remaining_weight)) + weight
            batch.save()

    return {"success": True}


# ============================================
# DASHBOARD / STATS ENDPOINTS
# ============================================

@router.get("/stats/dashboard", response=DashboardStats)
def get_dashboard_stats(request):
    """Lấy thống kê tổng quan"""
    today = timezone.now().date()

    # Tổng số sản phẩm
    total_products = Seafood.objects.filter(is_active=True, status='active').count()

    # Tổng giá trị tồn kho
    total_stock_value = Seafood.objects.filter(is_active=True).aggregate(
        total=Sum(F('stock_quantity') * F('current_price'))
    )['total'] or Decimal('0')

    # Đơn hàng hôm nay
    today_orders = Order.objects.filter(
        created_at__date=today,
        status__in=['pending', 'completed']
    ).count()

    # Doanh thu hôm nay
    today_revenue = Order.objects.filter(
        created_at__date=today,
        status='completed'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0')

    # Sản phẩm sắp hết hàng (< 10kg)
    low_stock_products = Seafood.objects.filter(
        is_active=True,
        stock_quantity__lt=10,
        status='active'
    ).count()

    return DashboardStats(
        total_products=total_products,
        total_stock_value=total_stock_value,
        today_orders=today_orders,
        today_revenue=today_revenue,
        low_stock_products=low_stock_products
    )


@router.get("/stats/products", response=List[ProductStats])
def get_product_stats(request, limit: int = 10):
    """Lấy thống kê sản phẩm bán chạy"""
    products = Seafood.objects.filter(is_active=True).annotate(
        total_sold=Sum('orderitem__weight'),
        revenue=Sum(F('orderitem__weight') * F('orderitem__unit_price'))
    ).order_by('-revenue')[:limit]

    return [
        ProductStats(
            code=p.code,
            name=p.name,
            stock_quantity=p.stock_quantity,
            current_price=p.current_price,
            total_sold=p.total_sold or Decimal('0'),
            revenue=p.revenue or Decimal('0')
        )
        for p in products
    ]
