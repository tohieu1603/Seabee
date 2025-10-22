"""
Custom User Model
Extended user model with additional fields
"""
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom user manager"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user"""
        if not email:
            raise ValueError('Email address is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model
    Uses email as username field
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    email = models.EmailField(
        unique=True,
        max_length=255,
        help_text="User email (used for login)"
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        null=True,
        blank=True,
        help_text="Optional username"
    )
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.URLField(blank=True, null=True, help_text="Avatar URL")

    # Department relationship
    department = models.ForeignKey(
        'rbac.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        help_text="User's department"
    )

    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Additional fields
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Employee ID"
    )
    position = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')

    # User type
    USER_TYPE_CHOICES = [
        ('customer', 'Khách hàng'),
        ('employee', 'Nhân viên'),
        ('manager', 'Quản lý'),
    ]
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='employee',
        db_index=True,
        help_text="Loại người dùng"
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['employee_id']),
        ]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.email

    @property
    def roles(self):
        """Return user's active roles"""
        return [ur.role for ur in self.user_roles.filter(is_active=True).select_related('role')]

    def get_roles(self):
        """Get user's active roles"""
        from apps.rbac.models import UserRole
        return UserRole.objects.filter(
            user=self,
            is_active=True
        ).select_related('role')

    def has_role(self, role_slug: str) -> bool:
        """Check if user has specific role"""
        return self.user_roles.filter(
            role__slug=role_slug,
            is_active=True
        ).exists()

    def has_permission(self, permission_codename: str) -> bool:
        """Check if user has specific permission through any role"""
        if self.is_superuser:
            return True

        from apps.rbac.models import Permission
        return Permission.objects.filter(
            roles__role_users__user=self,
            roles__role_users__is_active=True,
            codename=permission_codename,
            is_active=True
        ).exists()

    def get_all_permissions(self):
        """Get all permissions from all user's roles"""
        if self.is_superuser:
            from apps.rbac.models import Permission
            return Permission.objects.filter(is_active=True)

        from apps.rbac.models import Permission
        return Permission.objects.filter(
            roles__role_users__user=self,
            roles__role_users__is_active=True,
            is_active=True
        ).distinct()

    def get_highest_role_level(self) -> int:
        """Get the highest level from user's active roles"""
        if self.is_superuser:
            return 100

        from apps.rbac.models import Role
        highest = Role.objects.filter(
            role_users__user=self,
            role_users__is_active=True,
            is_active=True
        ).order_by('-level').first()

        return highest.level if highest else 0
