"""
API filtering configuration.
"""
import django_filters


class ProductFilter(django_filters.FilterSet):
    """Filter products by various criteria."""
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr='lte')
    
    class Meta:
        model = None  # Will be set in API when implemented
        fields = ['category', 'min_price', 'max_price']
