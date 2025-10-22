"""
Users API Endpoints
RESTful API for user management
"""
from typing import List, Optional
from uuid import UUID
from ninja import Router

from .models import User
from .schemas import UserCreate, UserUpdate, UserRead, UserLogin, UserLoginResponse
from .services import UserService
from .authentication import JWTAuth
from .jwt_utils import create_access_token
from apps.rbac.schemas import MessageResponse
from apps.rbac.permissions import require_permission


router = Router(tags=["Users"])
jwt_auth = JWTAuth()


@router.post("/register", response=UserRead, auth=None)
def register(request, payload: UserCreate):
    """User registration endpoint"""
    user = UserService.create_user(payload)
    return user


@router.post("/login", response=UserLoginResponse, auth=None)
def login(request, payload: UserLogin):
    """User login endpoint with JWT"""
    user = UserService.authenticate_user(
        email=payload.email,
        password=payload.password
    )

    if not user:
        from api.exceptions import Unauthorized
        raise Unauthorized("Invalid credentials")

    # Generate JWT token
    token = create_access_token(data={"user_id": str(user.id), "email": user.email})

    return {
        "access_token": token,
        "token_type": "Bearer",
        "user": user
    }


@router.get("/me", response=UserRead, auth=jwt_auth)
def get_current_user(request):
    """Get current authenticated user"""
    return request.auth


@router.get("", response=List[UserRead], auth=jwt_auth)
def list_users(
    request,
    department_id: Optional[UUID] = None,
    is_active: bool = True,
    search: Optional[str] = None
):
    """List all users with optional filters"""
    users = UserService.list_users(
        department_id=department_id,
        is_active=is_active,
        search=search
    )
    return users


@router.get("/{user_id}", response=UserRead, auth=jwt_auth)
def get_user(request, user_id: UUID):
    """Get user by ID"""
    user = UserService.get_user(user_id)
    return user


@router.post("", response=UserRead, auth=jwt_auth)
def create_user(request, payload: UserCreate):
    """Create new user"""
    user = UserService.create_user(payload)
    return user


@router.put("/{user_id}", response=UserRead, auth=jwt_auth)
def update_user(request, user_id: UUID, payload: UserUpdate):
    """Update existing user"""
    user = UserService.update_user(user_id, payload)
    return user


@router.delete("/{user_id}", response=MessageResponse, auth=jwt_auth)
def delete_user(request, user_id: UUID, hard: bool = False):
    """Delete user (soft delete by default)"""
    UserService.delete_user(user_id, soft=not hard)
    return {"message": "User deleted successfully"}
