"""
Pydantic schemas cho seafood API
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


# ============================================
# CATEGORY SCHEMAS
# ============================================

class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    sort_order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryRead(CategoryBase):
    id: UUID
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


# ============================================
# SEAFOOD SCHEMAS
# ============================================

class SeafoodBase(BaseModel):
    code: str
    name: str
    category_id: Optional[UUID] = None
    current_price: Decimal = Field(decimal_places=0)
    stock_quantity: Decimal = Field(default=Decimal('0'), decimal_places=2)
    description: Optional[str] = ""
    origin: Optional[str] = ""
    image_url: Optional[str] = ""
    tags: List[str] = []
    status: str = "active"


class SeafoodCreate(SeafoodBase):
    pass


class SeafoodUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[UUID] = None
    current_price: Optional[Decimal] = None
    stock_quantity: Optional[Decimal] = None
    description: Optional[str] = None
    origin: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class SeafoodRead(SeafoodBase):
    id: UUID
    created_at: datetime
    is_active: bool
    category: Optional[CategoryRead] = None

    class Config:
        from_attributes = True


# ============================================
# IMPORT SOURCE SCHEMAS
# ============================================

class ImportSourceBase(BaseModel):
    name: str
    source_type: str
    contact_info: dict = {}
    notes: Optional[str] = ""


class ImportSourceCreate(ImportSourceBase):
    pass


class ImportSourceUpdate(BaseModel):
    name: Optional[str] = None
    source_type: Optional[str] = None
    contact_info: Optional[dict] = None
    notes: Optional[str] = None


class ImportSourceRead(ImportSourceBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================
# IMPORT BATCH SCHEMAS
# ============================================

class ImportBatchBase(BaseModel):
    seafood_id: UUID
    batch_code: str
    import_source_id: Optional[UUID] = None
    import_date: date
    import_price: Decimal = Field(decimal_places=0)
    sell_price: Decimal = Field(decimal_places=0)
    total_weight: Decimal = Field(decimal_places=2)
    remaining_weight: Decimal = Field(decimal_places=2)
    notes: Optional[str] = ""
    import_details: dict = {}
    status: str = "received"


class ImportBatchCreate(ImportBatchBase):
    pass


class ImportBatchUpdate(BaseModel):
    seafood_id: Optional[UUID] = None
    import_source_id: Optional[UUID] = None
    import_date: Optional[date] = None
    import_price: Optional[Decimal] = None
    sell_price: Optional[Decimal] = None
    remaining_weight: Optional[Decimal] = None
    notes: Optional[str] = None
    import_details: Optional[dict] = None
    status: Optional[str] = None


class ImportBatchRead(ImportBatchBase):
    id: UUID
    created_at: datetime
    seafood: SeafoodRead
    import_source: Optional[ImportSourceRead] = None

    class Config:
        from_attributes = True


# ============================================
# ORDER ITEM SCHEMAS
# ============================================

class OrderItemBase(BaseModel):
    seafood_id: UUID
    import_batch_id: Optional[UUID] = None
    weight: Decimal = Field(decimal_places=2)
    unit_price: Decimal = Field(decimal_places=0)
    notes: Optional[str] = ""


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemRead(OrderItemBase):
    id: UUID
    subtotal: Decimal
    seafood: SeafoodRead

    class Config:
        from_attributes = True


# ============================================
# ORDER SCHEMAS
# ============================================

class OrderBase(BaseModel):
    customer_name: Optional[str] = ""
    customer_phone: str
    customer_address: Optional[str] = ""
    payment_method: Optional[str] = ""
    payment_status: str = "pending"
    status: str = "pending"
    notes: Optional[str] = ""
    discount_amount: Decimal = Field(default=Decimal('0'), decimal_places=0)


class OrderCreate(BaseModel):
    customer_name: Optional[str] = ""
    customer_phone: str
    customer_address: Optional[str] = ""
    payment_method: Optional[str] = ""
    payment_status: str = "pending"
    discount_amount: Decimal = Field(default=Decimal('0'), decimal_places=0)
    notes: Optional[str] = ""
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    payment_method: Optional[str] = None
    payment_status: Optional[str] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    discount_amount: Optional[Decimal] = None


class OrderRead(OrderBase):
    id: UUID
    order_code: str
    subtotal: Decimal
    total_amount: Decimal
    paid_amount: Decimal
    created_at: datetime
    items: List[OrderItemRead] = []

    class Config:
        from_attributes = True


# ============================================
# STATS SCHEMAS
# ============================================

class DashboardStats(BaseModel):
    total_products: int
    total_stock_value: Decimal
    today_orders: int
    today_revenue: Decimal
    low_stock_products: int


class ProductStats(BaseModel):
    code: str
    name: str
    stock_quantity: Decimal
    current_price: Decimal
    total_sold: Decimal
    revenue: Decimal
