# Seafood Module - Architecture Documentation

## Tổng quan

Module seafood đã được tổ chức lại theo kiến trúc **Clean Architecture** với các lớp:
- **Models**: Domain models (Django ORM)
- **Schemas**: DTOs (Pydantic schemas) cho API request/response
- **Repositories**: Data access layer
- **Services**: Business logic layer (sẽ implement tiếp)
- **Mappers**: Chuyển đổi giữa Models và DTOs (sẽ implement tiếp)
- **API**: API endpoints (Django Ninja views)

## Cấu trúc thư mục

```
apps/seafood/
├── models/                    # Domain Models
│   ├── __init__.py           # Export all models
│   ├── category.py           # SeafoodCategory
│   ├── product.py            # Seafood
│   ├── import_batch.py       # ImportBatch, ImportSource
│   ├── order.py              # Order, OrderItem
│   └── inventory.py          # InventoryLog
│
├── schemas/                   # Pydantic Schemas (DTOs)
│   ├── __init__.py
│   └── all.py                # All schemas (will be split later)
│
├── repositories/              # Data Access Layer
│   ├── __init__.py
│   ├── base.py               # BaseRepository with common CRUD
│   ├── category.py           # CategoryRepository
│   ├── product.py            # ProductRepository
│   ├── import_batch.py       # ImportBatchRepository, ImportSourceRepository
│   ├── order.py              # OrderRepository, OrderItemRepository
│   └── inventory.py          # InventoryRepository
│
├── services/                  # Business Logic (TODO)
│   └── (to be implemented)
│
├── mappers/                   # DTO Mappers (TODO)
│   └── (to be implemented)
│
├── api/                       # API Endpoints (TODO)
│   └── (to be refactored from api.py)
│
├── utils/                     # Utilities (TODO)
│   └── (pdf, excel handlers)
│
├── models.py                  # Backward compatibility
├── schemas.py                 # Backward compatibility
├── api.py                     # Current API (to be refactored)
└── README.md                  # This file
```

## Các Models

### 1. SeafoodCategory
Danh mục sản phẩm hải sản (Tôm, Cua, Cá, Ốc,...)

**Location**: `models/category.py`

**Fields**:
- name, slug, description
- image_url, sort_order

### 2. Seafood (Product)
Sản phẩm hải sản, bán theo kg/lạng

**Location**: `models/product.py`

**Fields**:
- code, name, category
- unit_type, avg_unit_weight
- current_price, stock_quantity
- description, origin, image_url
- status, tags, weight_range_options

### 3. ImportSource
Nguồn nhập hàng (Facebook, Zalo, Chợ,...)

**Location**: `models/import_batch.py`

### 4. ImportBatch
Lô hàng nhập kho

**Location**: `models/import_batch.py`

**Fields**:
- seafood, batch_code, import_source
- import_date, import_price, sell_price
- total_weight, remaining_weight
- status, imported_by

### 5. Order
Đơn hàng POS

**Location**: `models/order.py`

**Fields**:
- order_code
- customer (optional), customer_name, customer_phone, customer_address
- subtotal, discount_amount, total_amount
- payment_method, payment_status, paid_amount
- status (workflow states)
- sale_user, assigned_employee, weighed_by, shipped_by, delivered_by

**Workflow States**:
- pending → Chờ xử lý
- pending_sale_confirm → Chờ Sale xác nhận
- confirmed → Đã xác nhận
- assigned_to_warehouse → Đã giao cho kho
- weighing → Đang cân
- weighed → Đã cân xong
- completed → Hoàn thành
- cancelled → Đã hủy

### 6. OrderItem
Chi tiết đơn hàng

**Location**: `models/order.py`

**Fields**:
- order, seafood, import_batch
- quantity, estimated_weight_range
- weight (actual), unit_price, subtotal
- weight_image_url, notes

### 7. InventoryLog
Lịch sử nhập/xuất kho

**Location**: `models/inventory.py`

**Fields**:
- seafood, import_batch, order_item
- type (import/sale/adjust/loss)
- weight_change, stock_after
- created_by, notes

## Repositories

Repositories cung cấp các methods để truy vấn và thao tác dữ liệu.

### BaseRepository

**Location**: `repositories/base.py`

**Common methods**:
- `get_by_id(id: UUID)` - Lấy 1 record theo ID
- `get_all()` - Lấy tất cả records
- `filter(**filters)` - Lọc records
- `create(**data)` - Tạo mới record
- `update(instance, **data)` - Cập nhật record
- `delete(instance)` - Xóa record
- `exists(**filters)` - Kiểm tra tồn tại
- `count(**filters)` - Đếm số lượng

### CategoryRepository

**Location**: `repositories/category.py`

**Specific methods**:
- `get_by_slug(slug: str)`
- `get_active_categories()`

### ProductRepository

**Location**: `repositories/product.py`

**Specific methods**:
- `get_by_code(code: str)`
- `get_active_products()`
- `get_by_category(category_id: UUID, status: Optional[str])`
- `search_products(search_term: str, status: Optional[str])`
- `get_low_stock_products(threshold: float)`
- `update_stock(product_id: UUID, quantity_change: float)`
- `update_price(product_id: UUID, new_price: float)`

### ImportBatchRepository

**Location**: `repositories/import_batch.py`

**Specific methods**:
- `get_by_batch_code(batch_code: str)`
- `get_by_seafood(seafood_id: UUID, status: Optional[str])`
- `get_active_batches(seafood_id: Optional[UUID])`
- `update_remaining_weight(batch_id: UUID, weight_change: float)`
- `get_latest_batch_by_seafood(seafood_id: UUID)`

### OrderRepository

**Location**: `repositories/order.py`

**Specific methods**:
- `get_by_order_code(order_code: str)`
- `get_with_items(order_id: UUID)`
- `get_by_status(status: str, limit: Optional[int])`
- `get_by_customer_phone(phone: str, limit: Optional[int])`
- `get_by_customer(customer_id: UUID, limit: Optional[int])`
- `get_by_created_by(user_id: UUID, limit: Optional[int])`
- `get_by_sale_user(sale_user_id: UUID, status: Optional[str])`
- `get_by_assigned_employee(employee_id: UUID, status: Optional[str])`
- `get_pending_orders(limit: Optional[int])`
- `search_orders(search_term: str, limit: Optional[int])`
- `get_total_revenue(start_date, end_date)`
- `get_order_count_by_status()`

### OrderItemRepository

**Location**: `repositories/order.py`

**Specific methods**:
- `get_by_order(order_id: UUID)`
- `update_weight(item_id: UUID, weight: float, weight_image_url: Optional[str])`

### InventoryRepository

**Location**: `repositories/inventory.py`

**Specific methods**:
- `get_by_seafood(seafood_id: UUID, limit: Optional[int])`
- `get_by_type(log_type: str, limit: Optional[int])`
- `create_log(seafood_id, log_type, weight_change, stock_after, ...)`

## Cách sử dụng Repositories

### Ví dụ 1: Lấy danh sách sản phẩm

```python
from apps.seafood.repositories import ProductRepository

product_repo = ProductRepository()

# Lấy tất cả sản phẩm active
products = product_repo.get_active_products()

# Lấy sản phẩm theo category
products = product_repo.get_by_category(category_id='xxx-xxx-xxx')

# Tìm kiếm sản phẩm
products = product_repo.search_products('tôm hùm')

# Lấy sản phẩm sắp hết hàng
low_stock = product_repo.get_low_stock_products(threshold=5.0)
```

### Ví dụ 2: Tạo đơn hàng mới

```python
from apps.seafood.repositories import OrderRepository
from apps.seafood.models import Order

order_repo = OrderRepository()

# Tạo đơn hàng
order = order_repo.create(
    order_code='ORD-20231028-001',
    customer_phone='0912345678',
    customer_name='Nguyễn Văn A',
    subtotal=500000,
    total_amount=500000,
    status='pending',
    created_by_id=user.id
)

# Lấy đơn hàng với items
order = order_repo.get_with_items(order.id)

# Tìm đơn hàng theo số điện thoại
orders = order_repo.get_by_customer_phone('0912345678')
```

### Ví dụ 3: Cập nhật tồn kho

```python
from apps.seafood.repositories import ProductRepository, InventoryRepository

product_repo = ProductRepository()
inventory_repo = InventoryRepository()

# Cập nhật stock khi bán hàng
product = product_repo.update_stock(
    product_id='xxx-xxx-xxx',
    quantity_change=-2.5  # Trừ 2.5kg
)

# Ghi log inventory
inventory_repo.create_log(
    seafood_id=product.id,
    log_type='sale',
    weight_change=-2.5,
    stock_after=product.stock_quantity,
    order_item_id=order_item.id,
    created_by_id=user.id
)
```

## Backward Compatibility

Các file cũ `models.py` và `schemas.py` vẫn tồn tại để đảm bảo backward compatibility:

```python
# Old imports still work
from apps.seafood.models import Seafood, Order, OrderItem
from apps.seafood.schemas import SeafoodCreate, OrderCreate

# New recommended imports
from apps.seafood.models import Seafood, Order, OrderItem
from apps.seafood.schemas import SeafoodCreate, OrderCreate
# (same, but organized better internally)
```

## Next Steps (TODO)

1. **Services Layer**: Tạo các service classes chứa business logic
   - ProductService: Quản lý sản phẩm, tồn kho
   - OrderService: Xử lý workflow đơn hàng
   - PaymentService: Xử lý thanh toán, webhook SePay
   - NotificationService: Gửi thông báo Telegram

2. **Mappers Layer**: Tạo các mapper để chuyển đổi Model ↔ DTO
   - ProductMapper
   - OrderMapper

3. **API Refactoring**: Tách file `api.py` thành nhiều file nhỏ
   - api/categories.py
   - api/products.py
   - api/import_batches.py
   - api/orders.py
   - api/dashboard.py
   - api/webhooks.py

4. **Utils**: Tách các utility functions
   - utils/pdf_generator.py
   - utils/excel_handler.py
   - utils/validators.py

5. **Tests**: Viết unit tests cho từng layer
   - tests/repositories/
   - tests/services/
   - tests/api/

## Migration Notes

- Không cần run migrations mới vì chỉ reorganize code, không thay đổi database schema
- Models vẫn sử dụng các `db_table` names cũ
- API endpoints không thay đổi
- Frontend không cần update

## Benefits của kiến trúc mới

1. **Separation of Concerns**: Mỗi layer có trách nhiệm rõ ràng
2. **Testability**: Dễ dàng viết unit tests cho từng layer
3. **Reusability**: Repositories và Services có thể tái sử dụng
4. **Maintainability**: Code dễ đọc, dễ maintain hơn
5. **Scalability**: Dễ dàng mở rộng thêm features mới
