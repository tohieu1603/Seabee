"""
Base Models - Shared abstract models for the application
"""
import uuid
from django.db import models


class BaseModel(models.Model):
    """
    Abstract base model with UUID primary key, timestamps, and soft delete
    All app models should inherit from this
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Soft delete flag"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def soft_delete(self):
        """Soft delete the record"""
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])

    def restore(self):
        """Restore soft deleted record"""
        self.is_active = True
        self.save(update_fields=['is_active', 'updated_at'])
