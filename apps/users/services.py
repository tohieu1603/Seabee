"""
User Services
Business logic for user management
"""
from typing import List, Optional
from uuid import UUID
from django.db import transaction
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import User
from .schemas import UserCreate, UserUpdate


class UserService:
    """Service for managing users"""

    @staticmethod
    @transaction.atomic
    def create_user(data: UserCreate) -> User:
        """Create a new user"""
        # Check if email already exists
        if User.objects.filter(email=data.email).exists():
            raise ValidationError("Email already exists")

        # Check if username already exists (if provided)
        if data.username and User.objects.filter(username=data.username).exists():
            raise ValidationError("Username already exists")

        # Check if employee_id already exists (if provided)
        if data.employee_id and User.objects.filter(employee_id=data.employee_id).exists():
            raise ValidationError("Employee ID already exists")

        # Extract password
        password = data.password
        user_data = data.model_dump(exclude={'password'})

        # Create user
        user = User.objects.create_user(
            password=password,
            **user_data
        )

        return user

    @staticmethod
    def update_user(user_id: UUID, data: UserUpdate) -> User:
        """Update existing user"""
        user = User.objects.get(id=user_id)
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        user.save()
        return user

    @staticmethod
    def get_user(user_id: UUID) -> User:
        """Get user by ID"""
        return User.objects.select_related('department').get(id=user_id)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email"""
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            return None

    @staticmethod
    def list_users(
        department_id: Optional[UUID] = None,
        is_active: bool = True,
        search: Optional[str] = None
    ) -> List[User]:
        """List users with filters"""
        queryset = User.objects.filter(is_active=is_active).select_related('department').prefetch_related('user_roles__role')

        if department_id:
            queryset = queryset.filter(department_id=department_id)

        if search:
            queryset = queryset.filter(
                email__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )

        return list(queryset)

    @staticmethod
    def delete_user(user_id: UUID, soft: bool = True) -> None:
        """Delete user (soft or hard)"""
        user = User.objects.get(id=user_id)

        if soft:
            user.is_active = False
            user.save()
        else:
            user.delete()

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = authenticate(username=email, password=password)
        return user
