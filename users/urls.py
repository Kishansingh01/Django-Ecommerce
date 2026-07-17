"""
User authentication URLs.
"""
from django.urls import path
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetCompleteView

from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Profile
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    
    # Addresses
    path('addresses/', views.AddressListView.as_view(), name='address_list'),
    path('addresses/<int:pk>/', views.AddressDetailView.as_view(), name='address_detail'),
    path('addresses/create/', views.AddressCreateView.as_view(), name='address_create'),
    path('addresses/<int:pk>/edit/', views.AddressUpdateView.as_view(), name='address_update'),
    path('addresses/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    
    # Password Reset
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset/complete/', PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # Password Change (for logged-in users)
    path('password-change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
]
