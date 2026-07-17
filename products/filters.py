"""
Search and filter logic for products.
"""
from django.db.models import Q


class ProductFilter:
    """Filter products by various criteria."""
    
    @staticmethod
    def filter_by_category(queryset, category_id):
        """Filter products by category."""
        if category_id:
            return queryset.filter(category_id=category_id)
        return queryset
    
    @staticmethod
    def filter_by_price_range(queryset, min_price=None, max_price=None):
        """Filter products by price range."""
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        return queryset
    
    @staticmethod
    def search_products(queryset, query):
        """Search products by name or description."""
        if query:
            return queryset.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        return queryset
    
    @staticmethod
    def apply_filters(queryset, category_id=None, min_price=None, max_price=None, query=None):
        """Apply all filters at once."""
        queryset = ProductFilter.filter_by_category(queryset, category_id)
        queryset = ProductFilter.filter_by_price_range(queryset, min_price, max_price)
        queryset = ProductFilter.search_products(queryset, query)
        return queryset
