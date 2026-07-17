"""
Admin configuration for cart app.
"""
from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """Inline admin for CartItem."""
    model = CartItem
    fields = ('product', 'quantity', 'price_at_add', 'created_at')
    readonly_fields = ('price_at_add', 'created_at')
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for Cart."""
    list_display = ('user', 'total_items', 'total_price', 'updated_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user', 'created_at', 'updated_at')
    inlines = [CartItemInline]
    
    def total_items(self, obj):
        return obj.get_total_items()
    total_items.short_description = 'Total Items'
    
    def total_price(self, obj):
        return f"${obj.get_total_price():.2f}"
    total_price.short_description = 'Total Price'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin for CartItem."""
    list_display = ('product', 'cart', 'quantity', 'price_at_add', 'item_total', 'created_at')
    list_filter = ('created_at', 'cart__user')
    search_fields = ('product__name', 'cart__user__username')
    readonly_fields = ('price_at_add', 'created_at', 'updated_at')
    
    def item_total(self, obj):
        return f"${obj.get_item_total():.2f}"
    item_total.short_description = 'Item Total'
