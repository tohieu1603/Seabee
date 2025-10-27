# 🌊 HƯỚNG DẪN SEED DATA

## 🚀 Cách sử dụng nhanh

### 1. Tạo users (Nhanh nhất - Khuyến nghị)

```bash
cd backend
bash quick_seed.sh
```

Sẽ tạo tất cả tài khoản từ ACCOUNTS.md:
- ✅ Admin + Manager
- ✅ Sale 1, Sale 2
- ✅ Warehouse (Thủ kho)
- ✅ Accountant (Kế toán)
- ✅ 3 Customers

### 2. Tạo đầy đủ (Users + Sản phẩm + Đơn hàng)

```bash
cd backend
python3 manage.py shell < seed_data.py
```

Sẽ tạo:
- ✅ 9 users
- ✅ 6 danh mục sản phẩm
- ✅ 16 sản phẩm hải sản
- ✅ 3 đơn hàng mẫu

## 📋 Danh sách tài khoản

| Role | Email | Password |
|------|-------|----------|
| 👑 **Admin** | `admin@seafood.com` | `admin123` |
| 💼 **Manager** | `manager@seafood.com` | `manager123` |
| 💼 **Sale 1** | `sale1@seafood.com` | `sale123` |
| 💼 **Sale 2** | `sale2@seafood.com` | `sale123` |
| 📦 **Warehouse** | `warehouse@seafood.com` | `warehouse123` |
| 📊 **Accountant** | `accountant@seafood.com` | `accountant123` |
| 📱 **Customer** | `testcustomer@example.com` | `customer123` |
| 📱 **Customer 1** | `customer1@example.com` | `customer123` |
| 📱 **Customer 2** | `customer2@example.com` | `customer123` |

## 🔧 Lệnh hữu ích

### Xóa tất cả users (CẢNH BÁO: Nguy hiểm!)

```bash
python3 manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.all().delete()
>>> exit()
```

### Xóa tất cả đơn hàng

```bash
python3 manage.py shell
>>> from apps.seafood.models import Order
>>> Order.objects.all().delete()
>>> exit()
```

### Kiểm tra số lượng data

```bash
python3 manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from apps.seafood.models import Seafood, SeafoodCategory, Order
>>> User = get_user_model()
>>> print(f"Users: {User.objects.count()}")
>>> print(f"Categories: {SeafoodCategory.objects.count()}")
>>> print(f"Products: {Seafood.objects.count()}")
>>> print(f"Orders: {Order.objects.count()}")
>>> exit()
```

## 💡 Ghi chú

- Tất cả script đều check trùng lặp trước khi tạo
- An toàn chạy nhiều lần
- Không xóa data cũ

## 📞 Support

Nếu gặp lỗi:
1. Check database đã migrate chưa: `python3 manage.py migrate`
2. Check backend server đang chạy: `python3 manage.py runserver`
3. Xem logs để debug

---

**Created by:** Claude Code  
**Last Updated:** 2025-10-27
