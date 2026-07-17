#!/usr/bin/env python
"""Fix script to update products with empty slugs."""
import os
import django
from django.utils.text import slugify

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from products.models import Product

# Find and fix products with empty slugs
empty_slug_products = Product.objects.filter(slug__isnull=True) | Product.objects.filter(slug='')
print(f"Found {empty_slug_products.count()} product(s) with empty slugs")

for product in empty_slug_products:
    original_name = product.name
    base_slug = slugify(product.name)
    
    # Handle duplicate slugs by appending product ID
    slug = base_slug
    counter = 1
    while Product.objects.filter(slug=slug).exclude(id=product.id).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    product.slug = slug
    try:
        product.save()
        print(f"✓ Fixed: {original_name} (ID: {product.id}) → slug: '{slug}'")
    except Exception as e:
        print(f"✗ Error fixing {original_name}: {e}")

print("\n✓ Slug fix complete!")

