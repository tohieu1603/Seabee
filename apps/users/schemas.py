"""
User Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr

if TYPE_CHECKING:
    from apps.rbac.schemas import RoleRead, DepartmentRead


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    position: Optional[str] = Field(None, max_length=100)
    department_id: Optional[UUID] = None


class UserCreate(UserBase):
    """Schema for creating user"""
    password: str = Field(..., min_length=8)
    employee_id: Optional[str] = Field(None, max_length=50)
    username: Optional[str] = Field(None, max_length=150)


class UserUpdate(BaseModel):
    """Schema for updating user"""
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    position: Optional[str] = Field(None, max_length=100)
    department_id: Optional[UUID] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    is_active: Optional[bool] = None
    user_type: Optional[str] = None


class DepartmentSimple(BaseModel):
    """Simple department schema for user"""
    id: UUID
    name: str
    code: str

    class Config:
        from_attributes = True


class RoleSimple(BaseModel):
    """Simple role schema for user"""
    id: UUID
    name: str
    slug: str
    color: str
    level: int

    class Config:
        from_attributes = True


class UserRead(UserBase):
    """Schema for reading user"""
    id: UUID
    username: Optional[str] = None
    avatar: Optional[str] = None
    employee_id: Optional[str] = None
    is_active: bool
    is_staff: bool
    date_joined: datetime
    created_at: datetime
    updated_at: datetime
    department: Optional[DepartmentSimple] = None
    roles: List[RoleSimple] = []
    user_type: str = 'employee'

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    """Schema for login response"""
    access_token: str
    token_type: str = "Bearer"
    user: UserRead
