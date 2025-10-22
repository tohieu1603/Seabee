"""
Authentication Backend for JWT
"""
from ninja.security import HttpBearer
from django.contrib.auth import get_user_model
from .jwt_utils import decode_access_token

User = get_user_model()


class JWTAuth(HttpBearer):
    """
    JWT Authentication for Django Ninja
    """
    def authenticate(self, request, token: str):
        """
        Authenticate user from JWT token
        """
        payload = decode_access_token(token)

        if not payload:
            return None

        user_id = payload.get("user_id")
        if not user_id:
            return None

        try:
            user = User.objects.get(id=user_id, is_active=True)
            return user
        except User.DoesNotExist:
            return None
