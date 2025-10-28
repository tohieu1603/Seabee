"""
Category Repository
"""
from typing import Optional
from django.db.models import QuerySet
from apps.seafood.models import SeafoodCategory
from .base import BaseRepository


class CategoryRepository(BaseRepository[SeafoodCategory]):
    """Repository for SeafoodCategory model"""

    def __init__(self):
        super().__init__(SeafoodCategory)

    def get_by_slug(self, slug: str) -> Optional[SeafoodCategory]:
        """Get category by slug"""
        try:
            return self.model.objects.get(slug=slug)
        except self.model.DoesNotExist:
            return None

    def get_active_categories(self) -> QuerySet[SeafoodCategory]:
        """Get all active categories ordered by sort_order"""
        return self.model.objects.all().order_by('sort_order', 'name')
