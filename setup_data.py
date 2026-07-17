#!/usr/bin/env python
"""Setup script to create superuser and sample products."""
import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from django.contrib.auth.models import User
from products.models import Category, Product

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
    print("✓ Admin user created (username: admin, password: admin123)")
else:
    print("✓ Admin user already exists")

# Create categories
electronics, _ = Category.objects.get_or_create(
    name='Electronics',
    defaults={'slug': 'electronics', 'description': 'Electronic devices and gadgets'}
)

fashion, _ = Category.objects.get_or_create(
    name='Fashion',
    defaults={'slug': 'fashion', 'description': 'Clothing and accessories'}
)

home, _ = Category.objects.get_or_create(
    name='Home & Garden',
    defaults={'slug': 'home-garden', 'description': 'Home and garden products'}
)

print(f"✓ Created {Category.objects.count()} categories")

# Create sample products
products_data = [
    {'name': 'Wireless Headphones', 'category': electronics, 'price': 79.99},
    {'name': 'Smart Watch', 'category': electronics, 'price': 199.99},
    {'name': 'Laptop Stand', 'category': electronics, 'price': 49.99},
    {'name': 'T-Shirt', 'category': fashion, 'price': 19.99},
    {'name': 'Jeans', 'category': fashion, 'price': 59.99},
    {'name': 'Sneakers', 'category': fashion, 'price': 89.99},
    {'name': 'Desk Lamp', 'category': home, 'price': 39.99},
    {'name': 'Plant Pot', 'category': home, 'price': 24.99},
]

for product_data in products_data:
    slug = slugify(product_data['name'])
    Product.objects.get_or_create(
        slug=slug,
        defaults={
            'name': product_data['name'],
            'category': product_data['category'],
            'price': product_data['price'],
            'description': f'High-quality {product_data["name"]}',
            'is_active': True,
            'is_featured': True,
            'stock': 100,
        }
    )

print(f"✓ Created {Product.objects.count()} products")
print("\n✓ Database setup complete!")
print("\nYou can now:")
print("- Access the admin panel at: http://127.0.0.1:8000/admin/")
print("- Login with: admin / admin123")
print("- Browse products at: http://127.0.0.1:8000/products/")

