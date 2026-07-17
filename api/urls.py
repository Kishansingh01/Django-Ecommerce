from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as token_views
from api import views
from rag.views import ChatAPIView

# Create a router for ViewSets   
router = DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'addresses', views.AddressViewSet, basename='address')
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='order')

app_name = 'api'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    path('chat/', ChatAPIView.as_view(), name='chat'),
    
    # Authentication
    path('auth/token/', token_views.obtain_auth_token, name='api_token_auth'),
]