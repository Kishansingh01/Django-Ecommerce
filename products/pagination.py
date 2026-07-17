"""
Pagination utilities for both template and API views.
"""
from rest_framework.pagination import PageNumberPagination


class StandardPagination(PageNumberPagination):
    """Standard pagination for API views."""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class TemplatePaginator:
    """Unified paginator for template-based views."""
    
    def __init__(self, queryset, page_num, page_size=12):
        self.queryset = queryset
        self.page_num = page_num
        self.page_size = page_size
        self.total_items = queryset.count()
        self.total_pages = (self.total_items + self.page_size - 1) // self.page_size
    
    def get_page(self):
        """Get items for the current page."""
        start = (self.page_num - 1) * self.page_size
        end = start + self.page_size
        return self.queryset[start:end]
    
    def get_context(self):
        """Get pagination context for templates."""
        return {
            'items': self.get_page(),
            'total_items': self.total_items,
            'total_pages': self.total_pages,
            'current_page': self.page_num,
            'has_previous': self.page_num > 1,
            'has_next': self.page_num < self.total_pages,
            'page_range': range(1, self.total_pages + 1),
        }
