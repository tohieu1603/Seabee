"""
Inventory Repository
"""
from typing import Optional
from uuid import UUID
from django.db.models import QuerySet
from apps.seafood.models import InventoryLog
from .base import BaseRepository


class InventoryRepository(BaseRepository[InventoryLog]):
    """Repository for InventoryLog model"""

    def __init__(self):
        super().__init__(InventoryLog)

    def get_by_seafood(self, seafood_id: UUID, limit: Optional[int] = None) -> QuerySet[InventoryLog]:
        """Get inventory logs for a seafood product"""
        queryset = self.model.objects.filter(seafood_id=seafood_id).select_related(
            'seafood', 'import_batch', 'order_item', 'created_by'
        ).order_by('-created_at')
        if limit:
            queryset = queryset[:limit]
        return queryset

    def get_by_type(self, log_type: str, limit: Optional[int] = None) -> QuerySet[InventoryLog]:
        """Get inventory logs by type"""
        queryset = self.model.objects.filter(type=log_type).select_related(
            'seafood', 'created_by'
        ).order_by('-created_at')
        if limit:
            queryset = queryset[:limit]
        return queryset

    def create_log(
        self,
        seafood_id: UUID,
        log_type: str,
        weight_change: float,
        stock_after: float,
        created_by_id: Optional[UUID] = None,
        import_batch_id: Optional[UUID] = None,
        order_item_id: Optional[UUID] = None,
        notes: str = ""
    ) -> InventoryLog:
        """Create a new inventory log entry"""
        return self.create(
            seafood_id=seafood_id,
            type=log_type,
            weight_change=weight_change,
            stock_after=stock_after,
            created_by_id=created_by_id,
            import_batch_id=import_batch_id,
            order_item_id=order_item_id,
            notes=notes
        )
