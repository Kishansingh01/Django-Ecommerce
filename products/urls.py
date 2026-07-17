"""
Product URLs.
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # Products
    path('', views.ProductListView.as_view(), name='product_list'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    
    # Wishlist
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('wishlist/add/', views.AddToWishlistView.as_view(), name='add_to_wishlist'),
    path('<int:pk>/wishlist/remove/', views.RemoveFromWishlistView.as_view(), name='remove_from_wishlist'),
]
