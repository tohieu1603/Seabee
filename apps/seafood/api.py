"""
API endpoints cho hệ thống bán hải sản
"""
from ninja import Router
from pydantic import BaseModel
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
            'weighed_at': order.weighed_at,
            'weighed_by': order.weighed_by.email if order.weighed_by else None,
            'weight_images': order.weight_images,
            'shipped_at': order.shipped_at,
            'shipped_by': order.shipped_by.email if order.shipped_by else None,
            'shipping_notes': order.shipping_notes or '',
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
        'weighed_at': order.weighed_at,
        'weighed_by': order.weighed_by.email if order.weighed_by else None,
        'weight_images': order.weight_images,
        'shipped_at': order.shipped_at,
        'shipped_by': order.shipped_by.email if order.shipped_by else None,
        'shipping_notes': order.shipping_notes or '',
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
# ORDER WORKFLOW ENDPOINTS
# ============================================

@router.post("/orders/{order_id}/update-item")
def update_order_item(
    request,
    order_id: UUID,
    item_id: UUID,
    weight: float = None,
    unit_price: int = None,
    weight_image_url: str = None
):
    """Cập nhật trọng lượng và giá của order item (sau khi cân)"""
    order = get_object_or_404(Order, id=order_id)
    item = get_object_or_404(OrderItem, id=item_id, order=order)

    # Lưu trọng lượng cũ để tính chênh lệch stock
    old_weight = item.weight

    # Cập nhật item
    if weight is not None:
        item.weight = Decimal(str(weight))
    if unit_price is not None:
        item.unit_price = Decimal(str(unit_price))
    if weight_image_url is not None:
        item.weight_image_url = weight_image_url

    # Tính lại subtotal
    item.subtotal = item.weight * item.unit_price
    item.save()

    # Cập nhật stock nếu thay đổi trọng lượng
    if weight is not None:
        weight_diff = item.weight - old_weight
        seafood = item.seafood
        seafood.stock_quantity = Decimal(str(seafood.stock_quantity)) - weight_diff
        seafood.save()

        # Cập nhật batch
        if item.import_batch:
            batch = item.import_batch
            batch.remaining_weight = Decimal(str(batch.remaining_weight)) - weight_diff
            batch.save()

    # Tính lại tổng tiền đơn hàng
    order.subtotal = sum(
        Decimal(str(i.subtotal)) for i in order.items.all()
    )
    order.total_amount = order.subtotal - order.discount_amount
    if order.payment_status == 'paid':
        order.paid_amount = order.total_amount
    order.save()

    return {
        "success": True,
        "item": item,
        "order": order
    }


class MarkWeighedSchema(BaseModel):
    weight_images: List[str] = []

class MarkShippedSchema(BaseModel):
    shipping_notes: str = ""

@router.post("/orders/{order_id}/mark-weighed")
def mark_order_weighed(request, order_id: UUID, payload: MarkWeighedSchema = None):
    """Đánh dấu đơn hàng đã cân xong"""
    order = get_object_or_404(Order, id=order_id)

    order.status = 'weighed'
    order.weighed_at = timezone.now()

    # Get current user (for now, use admin)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    order.weighed_by = User.objects.filter(is_superuser=True).first()

    if payload and payload.weight_images:
        order.weight_images = payload.weight_images

    order.save()

    return {
        "success": True,
        "order": get_order(request, order_id)
    }


@router.post("/orders/{order_id}/mark-shipped")
def mark_order_shipped(request, order_id: UUID, payload: MarkShippedSchema = None):
    """Đánh dấu đơn hàng đã gửi vận chuyển"""
    order = get_object_or_404(Order, id=order_id)

    order.status = 'shipped'
    order.shipped_at = timezone.now()

    # Get current user (for now, use admin)
    from django.contrib.auth import get_user_model
    User = get_user_model()
    order.shipped_by = User.objects.filter(is_superuser=True).first()

    if payload and payload.shipping_notes:
        order.shipping_notes = payload.shipping_notes

    order.save()

    return {
        "success": True,
        "order": get_order(request, order_id)
    }


@router.get("/orders/{order_id}/export-pdf")
def export_order_pdf(request, order_id: UUID):
    """Xuất PDF hóa đơn"""
    from django.http import HttpResponse
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from io import BytesIO

    order = get_object_or_404(
        Order.objects.prefetch_related('items', 'items__seafood'),
        id=order_id
    )

    # Tạo PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    elements.append(Paragraph("HÓA ĐƠN BÁN HÀNG", title_style))
    elements.append(Spacer(1, 20))

    # Thông tin đơn hàng
    info_data = [
        ['Mã đơn hàng:', order.order_code],
        ['Ngày tạo:', order.created_at.strftime('%d/%m/%Y %H:%M')],
        ['Khách hàng:', order.customer_name or 'N/A'],
        ['Số điện thoại:', order.customer_phone],
        ['Địa chỉ:', order.customer_address or 'N/A'],
        ['Trạng thái:', order.get_status_display()],
    ]

    info_table = Table(info_data, colWidths=[4*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 30))

    # Bảng sản phẩm
    items_data = [['STT', 'Sản phẩm', 'Số lượng (kg)', 'Đơn giá', 'Thành tiền']]

    for idx, item in enumerate(order.items.all(), 1):
        items_data.append([
            str(idx),
            item.seafood.name,
            f"{item.weight:,.2f}",
            f"{item.unit_price:,.0f}đ",
            f"{item.subtotal:,.0f}đ"
        ])

    items_table = Table(items_data, colWidths=[1.5*cm, 7*cm, 3*cm, 3.5*cm, 4*cm])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 30))

    # Tổng tiền
    total_data = [
        ['Tạm tính:', f"{order.subtotal:,.0f}đ"],
        ['Giảm giá:', f"-{order.discount_amount:,.0f}đ"],
        ['TỔNG CỘNG:', f"{order.total_amount:,.0f}đ"],
    ]

    total_table = Table(total_data, colWidths=[14*cm, 5*cm])
    total_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 14),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#1e40af')),
        ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor('#1e40af')),
        ('TOPPADDING', (0, -1), (-1, -1), 15),
    ]))
    elements.append(total_table)

    # Build PDF
    doc.build(elements)

    # Trả về response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="order_{order.order_code}.pdf"'

    return response


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
