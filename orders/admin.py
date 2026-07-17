from django.contrib import admin
from django.utils.html import format_html
from orders.models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline admin for order items."""
    model = OrderItem
    readonly_fields = ('product', 'quantity', 'price', 'get_total')
    can_delete = False
    extra = 0
    
    def get_total(self, obj):
        return f"${obj.get_total():.2f}"
    get_total.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin for orders."""
    list_display = ('order_number', 'user', 'total_display', 'status_badge', 'payment_status_badge', 'created_at')
    list_filter = ('status', 'payment_status', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    readonly_fields = ('order_number', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Order Info', {'fields': ('order_number', 'user', 'created_at', 'updated_at')}),
        ('Pricing', {'fields': ('subtotal', 'tax', 'shipping', 'total')}),
        ('Addresses', {'fields': ('billing_address', 'shipping_address')}),
        ('Status', {'fields': ('status', 'payment_status', 'shipped_at', 'delivered_at')}),
    )
    
    def total_display(self, obj):
        return f"${obj.total:.2f}"
    total_display.short_description = 'Total'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#FFC107',
            'processing': '#17A2B8',
            'shipped': '#007BFF',
            'delivered': '#28A745',
            'cancelled': '#DC3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#6C757D'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_status_badge(self, obj):
        colors = {
            'pending': '#FFC107',
            'completed': '#28A745',
            'failed': '#DC3545',
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            colors.get(obj.payment_status, '#6C757D'),
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Payment'
    
    actions = ['mark_shipped', 'mark_delivered', 'mark_cancelled']
    
    def mark_shipped(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='shipped', shipped_at=timezone.now())
        self.message_user(request, f"{updated} orders marked as shipped.")
    mark_shipped.short_description = "Mark selected orders as shipped"
    
    def mark_delivered(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status='delivered', delivered_at=timezone.now())
        self.message_user(request, f"{updated} orders marked as delivered.")
    mark_delivered.short_description = "Mark selected orders as delivered"
    
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f"{updated} orders cancelled.")
    mark_cancelled.short_description = "Cancel selected orders"
