"""
Main URL configuration for ecommerce project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import HomeView

urlpatterns = [
    # Home
    path('', HomeView.as_view(), name='home'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Local app URLs
    path('accounts/', include('users.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    
    # API URLs
    path('api/', include('api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "E-commerce Admin"
admin.site.site_title = "E-commerce Administration"
