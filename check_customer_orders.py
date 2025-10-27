"""
Debug script to check customer orders relationship
Run: python manage.py shell < check_customer_orders.py
"""

from django.contrib.auth import get_user_model
from apps.seafood.models import Order

User = get_user_model()

print("\n" + "="*60)
print("CHECKING CUSTOMER ORDERS DEBUG")
print("="*60 + "\n")

# Find test customer
try:
    customer = User.objects.get(email='testcustomer@example.com')
    print(f"✓ Found customer: {customer.email}")
    print(f"  - ID: {customer.id}")
    print(f"  - Full name: {customer.full_name}")
    print(f"  - Phone: {customer.phone or 'NO PHONE SET ❌'}")
    print(f"  - User type: {customer.user_type}")
except User.DoesNotExist:
    print("❌ Customer testcustomer@example.com not found!")
    print("\nAvailable customers:")
    for u in User.objects.filter(user_type='customer'):
        print(f"  - {u.email} (phone: {u.phone})")
    exit()

print("\n" + "-"*60)
print("ORDERS ANALYSIS")
print("-"*60 + "\n")

# Check all orders
all_orders = Order.objects.all()
print(f"Total orders in system: {all_orders.count()}")

# Check orders with customer FK
orders_with_fk = Order.objects.filter(customer=customer)
print(f"Orders linked to customer FK: {orders_with_fk.count()}")
for order in orders_with_fk[:5]:
    print(f"  - {order.order_code} (FK: ✓, Phone: {order.customer_phone})")

# Check orders with matching phone
if customer.phone:
    orders_with_phone = Order.objects.filter(customer_phone=customer.phone)
    print(f"\nOrders with matching phone ({customer.phone}): {orders_with_phone.count()}")
    for order in orders_with_phone[:5]:
        has_fk = "✓" if order.customer_id == customer.id else "✗"
        print(f"  - {order.order_code} (FK: {has_fk}, Phone: {order.customer_phone})")
else:
    print("\n❌ Customer has no phone number set!")
    print("   Cannot match orders by phone.")

# Check orders with no customer FK
orders_no_fk = Order.objects.filter(customer__isnull=True)
print(f"\nOrders without customer FK: {orders_no_fk.count()}")
if orders_no_fk.count() > 0:
    print("  Sample orders without FK:")
    for order in orders_no_fk[:3]:
        print(f"  - {order.order_code} (Phone: {order.customer_phone})")

print("\n" + "="*60)
print("RECOMMENDATIONS")
print("="*60 + "\n")

if not customer.phone:
    print("⚠️  Customer has no phone number!")
    print("   Solution: Update customer phone in admin or database")
    print(f"   Command: User.objects.filter(email='{customer.email}').update(phone='0123456789')")

if orders_with_fk.count() == 0 and (not customer.phone or orders_with_phone.count() == 0):
    print("\n⚠️  No orders found for this customer!")
    print("   Create a test order or link existing orders:")
    print(f"   Command: Order.objects.filter(customer_phone='PHONE').update(customer_id='{customer.id}')")

print("\n" + "="*60 + "\n")
