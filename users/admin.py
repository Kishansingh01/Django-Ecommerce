"""
Admin configuration for user app.
"""
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile, Address


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""
    model = UserProfile
    fields = ('bio', 'profile_picture', 'phone_number', 'date_of_birth')
    extra = 0


class AddressInline(admin.TabularInline):
    """Inline admin for Address."""
    model = Address
    fields = ('full_name', 'phone_number', 'city', 'country', 'address_type', 'is_default')
    extra = 0


class CustomUserAdmin(BaseUserAdmin):
    """Custom User admin with inline profiles and addresses."""
    inlines = [UserProfileInline, AddressInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    date_hierarchy = 'date_joined'


class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile."""
    list_display = ('user', 'phone_number', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'phone_number')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at')


class AddressAdmin(admin.ModelAdmin):
    """Admin for Address."""
    list_display = ('full_name', 'user', 'city', 'country', 'address_type', 'is_default', 'created_at')
    list_filter = ('address_type', 'is_default', 'created_at', 'country')
    search_fields = ('full_name', 'user__username', 'user__email', 'city', 'country')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('User Info', {
            'fields': ('user',)
        }),
        ('Address Details', {
            'fields': ('full_name', 'phone_number', 'address_type')
        }),
        ('Address', {
            'fields': (
                'street_address_1', 'street_address_2', 'city',
                'state_province', 'postal_code', 'country'
            )
        }),
        ('Settings', {
            'fields': ('is_default',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# Unregister the default User admin and register custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Address, AddressAdmin)
