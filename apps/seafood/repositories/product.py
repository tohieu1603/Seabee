"""
Product Repository
"""
from typing import Optional
from uuid import UUID
from django.db.models import QuerySet, Q
from apps.seafood.models import Seafood
from .base import BaseRepository


class ProductRepository(BaseRepository[Seafood]):
    """Repository for Seafood (Product) model"""

    def __init__(self):
        super().__init__(Seafood)

    def get_by_code(self, code: str) -> Optional[Seafood]:
        """Get product by code"""
        try:
            return self.model.objects.get(code=code)
        except self.model.DoesNotExist:
            return None

    def get_active_products(self) -> QuerySet[Seafood]:
        """Get all active products"""
        return self.model.objects.filter(status='active')

    def get_by_category(self, category_id: UUID, status: Optional[str] = None) -> QuerySet[Seafood]:
        """Get products by category"""
        queryset = self.model.objects.filter(category_id=category_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def search_products(self, search_term: str, status: Optional[str] = None) -> QuerySet[Seafood]:
        """Search products by name or code"""
        queryset = self.model.objects.filter(
            Q(name__icontains=search_term) | Q(code__icontains=search_term)
        )
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    def get_low_stock_products(self, threshold: float = 5.0) -> QuerySet[Seafood]:
        """Get products with low stock"""
        return self.model.objects.filter(
            stock_quantity__lte=threshold,
            status='active'
        )

    def update_stock(self, product_id: UUID, quantity_change: float) -> Seafood:
        """Update product stock quantity"""
        product = self.get_by_id(product_id)
        if product:
            product.stock_quantity += quantity_change
            if product.stock_quantity <= 0:
                product.stock_quantity = 0
                product.status = 'out_of_stock'
            elif product.status == 'out_of_stock' and product.stock_quantity > 0:
                product.status = 'active'
            product.save()
        return product

    def update_price(self, product_id: UUID, new_price: float) -> Seafood:
        """Update product price"""
        product = self.get_by_id(product_id)
        if product:
            product.current_price = new_price
            product.save()
        return product
