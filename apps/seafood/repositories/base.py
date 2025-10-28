"""
Base Repository
Generic repository pattern for data access operations
"""
from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID
from django.db.models import Model, QuerySet


ModelType = TypeVar("ModelType", bound=Model)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations
    """
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get single record by ID"""
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None

    def get_all(self) -> QuerySet[ModelType]:
        """Get all records"""
        return self.model.objects.all()

    def filter(self, **filters) -> QuerySet[ModelType]:
        """Filter records"""
        return self.model.objects.filter(**filters)

    def create(self, **data) -> ModelType:
        """Create new record"""
        return self.model.objects.create(**data)

    def update(self, instance: ModelType, **data) -> ModelType:
        """Update existing record"""
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def delete(self, instance: ModelType) -> None:
        """Delete record"""
        instance.delete()

    def exists(self, **filters) -> bool:
        """Check if record exists"""
        return self.model.objects.filter(**filters).exists()

    def count(self, **filters) -> int:
        """Count records"""
        return self.model.objects.filter(**filters).count()
