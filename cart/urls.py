"""
Shopping cart URLs.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartView.as_view(), name='cart'),
    path('add/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('remove/<int:product_id>/', views.RemoveFromCartView.as_view(), name='remove_from_cart'),
    path('update/<int:item_id>/', views.UpdateCartView.as_view(), name='update_cart_item'),
    path('clear/', views.ClearCartView.as_view(), name='clear_cart'),
    path('count/', views.CartCountView.as_view(), name='cart_count'),
]
