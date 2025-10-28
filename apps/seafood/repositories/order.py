"""
Order Repository
"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from django.db.models import QuerySet, Q, Sum, Count
from apps.seafood.models import Order, OrderItem
from .base import BaseRepository


class OrderRepository(BaseRepository[Order]):
    """Repository for Order model"""

    def __init__(self):
        super().__init__(Order)

    def get_by_order_code(self, order_code: str) -> Optional[Order]:
        """Get order by order code"""
        try:
            return self.model.objects.select_related(
                'customer', 'created_by', 'sale_user',
                'assigned_employee', 'weighed_by'
            ).prefetch_related('items__seafood').get(order_code=order_code)
        except self.model.DoesNotExist:
            return None

    def get_with_items(self, order_id: UUID) -> Optional[Order]:
        """Get order with all related items"""
        try:
            return self.model.objects.select_related(
                'customer', 'created_by', 'sale_user',
                'assigned_employee', 'weighed_by'
            ).prefetch_related(
                'items__seafood',
                'items__import_batch'
            ).get(id=order_id)
        except self.model.DoesNotExist:
            return None

    def get_by_status(self, status: str, limit: Optional[int] = None) -> QuerySet[Order]:
        """Get orders by status"""
        queryset = self.model.objects.filter(status=status).select_related('customer', 'created_by')
        if limit:
            queryset = queryset[:limit]
        return queryset

    def get_by_customer_phone(self, phone: str, limit: Optional[int] = None) -> QuerySet[Order]:
        """Get orders by customer phone"""
        queryset = self.model.objects.filter(customer_phone=phone).order_by('-created_at')
        if limit:
            queryset = queryset[:limit]
        return queryset

    def get_by_customer(self, customer_id: UUID, limit: Optional[int] = None) -> QuerySet[Order]:
        """Get orders by customer"""
        queryset = self.model.objects.filter(customer_id=customer_id).order_by('-created_at')
        if limit:
            queryset = queryset[:limit]
        return queryset

    def get_by_created_by(self, user_id: UUID, limit: Optional[int] = None) -> QuerySet[Order]:
        """Get orders created by a user"""
        queryset = self.model.objects.filter(created_by_id=user_id).order_by('-created_at')
        if limit:
            queryset = queryset[:limit]
        return queryset

    def get_by_sale_user(self, sale_user_id: UUID, status: Optional[str] = None) -> QuerySet[Order]:
        """Get orders assigned to a sale user"""
        queryset = self.model.objects.filter(sale_user_id=sale_user_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.select_related('customer').order_by('-created_at')

    def get_by_assigned_employee(self, employee_id: UUID, status: Optional[str] = None) -> QuerySet[Order]:
        """Get orders assigned to an employee"""
        queryset = self.model.objects.filter(assigned_employee_id=employee_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.select_related('customer', 'sale_user').prefetch_related('items__seafood').order_by('-created_at')

    def get_pending_orders(self, limit: Optional[int] = None) -> QuerySet[Order]:
        """Get all pending orders"""
        queryset = self.model.objects.filter(
            status__in=['pending', 'pending_sale_confirm', 'confirmed']
        ).order_by('created_at')
        if limit:
            queryset = queryset[:limit]
        return queryset

    def search_orders(self, search_term: str, limit: Optional[int] = None) -> QuerySet[Order]:
        """Search orders by code, customer name, or phone"""
        queryset = self.model.objects.filter(
            Q(order_code__icontains=search_term) |
            Q(customer_name__icontains=search_term) |
            Q(customer_phone__icontains=search_term)
        ).select_related('customer', 'created_by').order_by('-created_at')
        if limit:
            queryset = queryset[:limit]
        return queryset

    def get_total_revenue(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> float:
        """Calculate total revenue for a period"""
        queryset = self.model.objects.filter(payment_status='paid')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        result = queryset.aggregate(total=Sum('total_amount'))
        return float(result['total'] or 0)

    def get_order_count_by_status(self) -> dict:
        """Get count of orders by status"""
        result = self.model.objects.values('status').annotate(count=Count('id'))
        return {item['status']: item['count'] for item in result}


class OrderItemRepository(BaseRepository[OrderItem]):
    """Repository for OrderItem model"""

    def __init__(self):
        super().__init__(OrderItem)

    def get_by_order(self, order_id: UUID) -> QuerySet[OrderItem]:
        """Get all items for an order"""
        return self.model.objects.filter(order_id=order_id).select_related(
            'seafood', 'import_batch'
        )

    def update_weight(self, item_id: UUID, weight: float, weight_image_url: Optional[str] = None) -> OrderItem:
        """Update item weight and image"""
        item = self.get_by_id(item_id)
        if item:
            item.weight = weight
            if weight_image_url:
                item.weight_image_url = weight_image_url
            item.save()  # save() method will auto-calculate subtotal
        return item
