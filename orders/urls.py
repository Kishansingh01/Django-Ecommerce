from django.urls import path
from orders import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('confirmation/<int:pk>/', views.OrderConfirmationView.as_view(), name='order_confirmation'),
    path('history/', views.OrderListView.as_view(), name='order_list'),
    path('detail/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
]
