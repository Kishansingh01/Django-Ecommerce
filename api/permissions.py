"""
API permission classes.
"""
from rest_framework.permissions import BasePermission, IsAuthenticated


class IsOwnerOrReadOnly(BasePermission):
    """Custom permission to only allow owners to edit their data."""
    
    def has_object_permission(self, request, view, obj):
        # Allow GET, HEAD, OPTIONS always
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions require ownership
        return obj.user == request.user
