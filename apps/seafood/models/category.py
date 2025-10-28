"""
Seafood Category Model
"""
from django.db import models
from apps.base_models import BaseModel


class SeafoodCategory(BaseModel):
    """Danh mục hải sản: Tôm, Cua, Cá, Ốc,..."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image_url = models.URLField(max_length=500, blank=True)
    sort_order = models.IntegerField(default=0)

    class Meta:
        db_table = 'seafood_category'
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name
