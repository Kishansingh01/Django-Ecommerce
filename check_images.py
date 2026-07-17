#!/usr/bin/env python
"""Check if products have images."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from products.models import Product

products = Product.objects.all()
print(f"Total products: {products.count()}")
print("\nProduct images status:")
for p in products:
    if p.image:
        print(f"  ✓ {p.name}: {p.image.name}")
    else:
        print(f"  ✗ {p.name}: NO IMAGE")

# Check media directory
from django.conf import settings
media_root = settings.MEDIA_ROOT
print(f"\nMedia root: {media_root}")
print(f"Media root exists: {os.path.exists(media_root)}")
print(f"Media root is directory: {os.path.isdir(media_root)}")

if os.path.isdir(media_root):
    files = os.listdir(media_root)
    print(f"Files in media root: {files}")
    
    product_images_dir = os.path.join(media_root, 'product_images')
    if os.path.isdir(product_images_dir):
        images = os.listdir(product_images_dir)
        print(f"Product images: {images}")
