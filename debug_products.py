#!/usr/bin/env python
"""Debug script to check products and slugs."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from products.models import Product

products = Product.objects.all()
print(f"Total products: {products.count()}")
for p in products:
    print(f"  {p.id}: {p.name} → slug: '{p.slug}'")

# Check for empty slugs
empty_slugs = products.filter(slug='') | products.filter(slug__isnull=True)
print(f"\nProducts with empty slugs: {empty_slugs.count()}")
