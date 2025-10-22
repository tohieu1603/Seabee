"""
RBAC Permission Decorators
"""
from functools import wraps
from typing import List, Callable
from django.http import HttpRequest, JsonResponse
from apps.users.models import User


def get_user_from_request(request: HttpRequest) -> User:
    """Extract authenticated user from request"""
    if hasattr(request, 'auth') and request.auth:
        return request.auth
    return getattr(request, 'user', None)


def require_permission(permission_codename: str):
    """
    Decorator to check if user has specific permission

    Usage:
        @require_permission('users.view')
        def list_users(request):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            user = get_user_from_request(request)

            if not user or not user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )

            if not user.has_permission(permission_codename):
                return JsonResponse(
                    {
                        'error': 'Permission denied',
                        'required_permission': permission_codename
                    },
                    status=403
                )

            return func(request, *args, **kwargs)

        return wrapper
    return decorator


def require_any_permission(permission_codenames: List[str]):
    """
    Decorator to check if user has at least one of the specified permissions

    Usage:
        @require_any_permission(['users.view', 'users.manage'])
        def list_users(request):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            user = get_user_from_request(request)

            if not user or not user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )

            has_permission = any(
                user.has_permission(perm) for perm in permission_codenames
            )

            if not has_permission:
                return JsonResponse(
                    {
                        'error': 'Permission denied',
                        'required_permissions': permission_codenames,
                        'note': 'At least one permission required'
                    },
                    status=403
                )

            return func(request, *args, **kwargs)

        return wrapper
    return decorator


def require_all_permissions(permission_codenames: List[str]):
    """
    Decorator to check if user has all specified permissions

    Usage:
        @require_all_permissions(['users.view', 'users.update'])
        def update_user(request):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            user = get_user_from_request(request)

            if not user or not user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )

            missing_permissions = [
                perm for perm in permission_codenames
                if not user.has_permission(perm)
            ]

            if missing_permissions:
                return JsonResponse(
                    {
                        'error': 'Permission denied',
                        'missing_permissions': missing_permissions
                    },
                    status=403
                )

            return func(request, *args, **kwargs)

        return wrapper
    return decorator


def require_role(role_slug: str):
    """
    Decorator to check if user has specific role

    Usage:
        @require_role('admin')
        def admin_dashboard(request):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            user = get_user_from_request(request)

            if not user or not user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )

            if not user.has_role(role_slug):
                return JsonResponse(
                    {
                        'error': 'Role required',
                        'required_role': role_slug
                    },
                    status=403
                )

            return func(request, *args, **kwargs)

        return wrapper
    return decorator


def require_any_role(role_slugs: List[str]):
    """
    Decorator to check if user has at least one of the specified roles

    Usage:
        @require_any_role(['admin', 'manager'])
        def management_dashboard(request):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            user = get_user_from_request(request)

            if not user or not user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )

            has_role = any(user.has_role(role) for role in role_slugs)

            if not has_role:
                return JsonResponse(
                    {
                        'error': 'Role required',
                        'required_roles': role_slugs,
                        'note': 'At least one role required'
                    },
                    status=403
                )

            return func(request, *args, **kwargs)

        return wrapper
    return decorator


def require_level(min_level: int):
    """
    Decorator to check if user's highest role level meets minimum requirement

    Usage:
        @require_level(50)  # Manager level or higher
        def approve_request(request):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(request: HttpRequest, *args, **kwargs):
            user = get_user_from_request(request)

            if not user or not user.is_authenticated:
                return JsonResponse(
                    {'error': 'Authentication required'},
                    status=401
                )

            user_level = user.get_highest_role_level()

            if user_level < min_level:
                return JsonResponse(
                    {
                        'error': 'Insufficient role level',
                        'required_level': min_level,
                        'user_level': user_level
                    },
                    status=403
                )

            return func(request, *args, **kwargs)

        return wrapper
    return decorator


def check_permission(user: User, permission_codename: str) -> bool:
    """
    Helper function to check if user has permission
    Use this in views/services for conditional logic

    Usage:
        if check_permission(request.user, 'users.delete'):
            # Allow deletion
        else:
            # Show warning
    """
    if not user or not user.is_authenticated:
        return False

    return user.has_permission(permission_codename)


def check_role(user: User, role_slug: str) -> bool:
    """
    Helper function to check if user has role

    Usage:
        if check_role(request.user, 'admin'):
            # Show admin features
    """
    if not user or not user.is_authenticated:
        return False

    return user.has_role(role_slug)


def get_user_permissions(user: User) -> List[str]:
    """
    Get list of all permission codenames for user

    Usage:
        permissions = get_user_permissions(request.user)
        # ['users.view', 'users.create', ...]
    """
    if not user or not user.is_authenticated:
        return []

    from .models import Permission

    return list(
        Permission.objects.filter(
            roles__role_users__user=user,
            roles__role_users__is_active=True,
            roles__is_active=True,
            is_active=True
        ).values_list('codename', flat=True).distinct()
    )


def get_user_roles(user: User) -> List[str]:
    """
    Get list of all role slugs for user

    Usage:
        roles = get_user_roles(request.user)
        # ['admin', 'developer', ...]
    """
    if not user or not user.is_authenticated:
        return []

    from .models import Role

    return list(
        Role.objects.filter(
            role_users__user=user,
            role_users__is_active=True,
            is_active=True
        ).values_list('slug', flat=True).distinct()
    )
