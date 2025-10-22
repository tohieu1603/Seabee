"""
Common dependencies for API endpoints
"""
from typing import Optional
from django.http import HttpRequest
from ninja import Query
from apps.users.models import User


def get_current_user(request: HttpRequest) -> Optional[User]:
    """
    Get currently authenticated user
    """
    if request.user.is_authenticated:
        return request.user
    return None


def require_authenticated_user(request: HttpRequest) -> User:
    """
    Require authenticated user or raise 401
    """
    user = get_current_user(request)
    if not user:
        from api.exceptions import Unauthorized
        raise Unauthorized("Authentication required")
    return user


class PaginationParams:
    """
    Pagination parameters
    """
    def __init__(
        self,
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100)
    ):
        self.page = page
        self.page_size = page_size
        self.offset = (page - 1) * page_size

    def paginate_queryset(self, queryset):
        """Apply pagination to queryset"""
        total = queryset.count()
        items = list(queryset[self.offset:self.offset + self.page_size])

        return {
            'total': total,
            'page': self.page,
            'page_size': self.page_size,
            'total_pages': (total + self.page_size - 1) // self.page_size,
            'items': items
        }
