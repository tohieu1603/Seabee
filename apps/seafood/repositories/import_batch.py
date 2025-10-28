"""
Import Batch Repository
"""
from typing import Optional
from uuid import UUID
from django.db.models import QuerySet
from apps.seafood.models import ImportBatch, ImportSource
from .base import BaseRepository


class ImportSourceRepository(BaseRepository[ImportSource]):
    """Repository for ImportSource model"""

    def __init__(self):
        super().__init__(ImportSource)

    def get_by_type(self, source_type: str) -> QuerySet[ImportSource]:
        """Get import sources by type"""
        return self.model.objects.filter(source_type=source_type)


class ImportBatchRepository(BaseRepository[ImportBatch]):
    """Repository for ImportBatch model"""

    def __init__(self):
        super().__init__(ImportBatch)

    def get_by_batch_code(self, batch_code: str) -> Optional[ImportBatch]:
        """Get import batch by batch code"""
        try:
            return self.model.objects.get(batch_code=batch_code)
        except self.model.DoesNotExist:
            return None

    def get_by_seafood(self, seafood_id: UUID, status: Optional[str] = None) -> QuerySet[ImportBatch]:
        """Get import batches by seafood"""
        queryset = self.model.objects.filter(seafood_id=seafood_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.select_related('seafood', 'import_source', 'imported_by')

    def get_active_batches(self, seafood_id: Optional[UUID] = None) -> QuerySet[ImportBatch]:
        """Get active (selling) batches"""
        queryset = self.model.objects.filter(status='selling')
        if seafood_id:
            queryset = queryset.filter(seafood_id=seafood_id)
        return queryset.select_related('seafood', 'import_source')

    def update_remaining_weight(self, batch_id: UUID, weight_change: float) -> ImportBatch:
        """Update remaining weight of batch"""
        batch = self.get_by_id(batch_id)
        if batch:
            batch.remaining_weight += weight_change
            if batch.remaining_weight <= 0:
                batch.remaining_weight = 0
                batch.status = 'sold_out'
            batch.save()
        return batch

    def get_latest_batch_by_seafood(self, seafood_id: UUID) -> Optional[ImportBatch]:
        """Get the latest import batch for a seafood product"""
        return self.model.objects.filter(
            seafood_id=seafood_id,
            status='selling'
        ).order_by('-import_date', '-created_at').first()
