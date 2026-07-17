"""
Admin configuration for product app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import Category, Product, ProductImage, Review, Wishlist


class ProductImageInline(admin.TabularInline):
    """Inline admin for ProductImage."""
    model = ProductImage
    fields = ('image', 'alt_text', 'is_primary')
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin for Category."""
    list_display = ('name', 'slug', 'product_count', 'created_at')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    def product_count(self, obj):
        """Show product count."""
        count = obj.products.count()
        return format_html(
            '<span style="background-color: #417690; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            count
        )
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin for Product."""
    list_display = ('name', 'category', 'price', 'stock_status', 'avg_rating', 'review_count', 'is_featured', 'created_at')
    list_filter = ('category', 'is_active', 'is_featured', 'created_at')
    search_fields = ('name', 'description', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'rating_display')
    inlines = [ProductImageInline]
    actions = ['mark_featured', 'unmark_featured', 'mark_in_stock', 'mark_out_of_stock']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'stock')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Analytics', {
            'fields': ('rating_display',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def stock_status(self, obj):
        """Show stock status."""
        if obj.stock > 20:
            color = '#28a745'
            status = 'In Stock'
        elif obj.stock > 0:
            color = '#ffc107'
            status = 'Low Stock'
        else:
            color = '#dc3545'
            status = 'Out of Stock'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px;">{}</span>',
            color, f'{status} ({obj.stock})'
        )
    stock_status.short_description = 'Stock'
    
    def avg_rating(self, obj):
        """Show average rating."""
        rating = obj.get_rating()
        if rating > 0:
            stars = '★' * int(rating) + '☆' * (5 - int(rating))
            return format_html(
                '<span style="color: #ffc107; font-size: 14px;">{} ({})</span>',
                stars, f'{rating:.1f}'
            )
        return '—'
    avg_rating.short_description = 'Rating'
    
    def review_count(self, obj):
        """Show review count."""
        count = obj.reviews.count()
        return count
    review_count.short_description = 'Reviews'
    
    def rating_display(self, obj):
        """Display rating info."""
        rating = obj.get_rating()
        count = obj.get_review_count()
        return f'{rating:.1f} stars ({count} reviews)' if count > 0 else 'No reviews yet'
    rating_display.short_description = 'Product Rating'
    
    def mark_featured(self, request, queryset):
        queryset.update(is_featured=True)
    mark_featured.short_description = 'Mark selected as featured'
    
    def unmark_featured(self, request, queryset):
        queryset.update(is_featured=False)
    unmark_featured.short_description = 'Unmark selected as featured'
    
    def mark_in_stock(self, request, queryset):
        queryset.update(stock=100)
    mark_in_stock.short_description = 'Mark as in stock (100 units)'
    
    def mark_out_of_stock(self, request, queryset):
        queryset.update(stock=0)
    mark_out_of_stock.short_description = 'Mark as out of stock'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin for Review."""
    list_display = ('user', 'product', 'rating_stars', 'is_verified_purchase', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'created_at')
    search_fields = ('user__username', 'product__name', 'comment')
    readonly_fields = ('user', 'product', 'created_at', 'updated_at')
    actions = ['approve_reviews', 'disapprove_reviews', 'mark_verified']
    
    fieldsets = (
        ('Review Details', {
            'fields': ('user', 'product', 'rating', 'title', 'comment')
        }),
        ('Verification', {
            'fields': ('is_verified_purchase', 'is_approved')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_stars(self, obj):
        """Display rating as stars."""
        stars = '★' * obj.rating + '☆' * (5 - obj.rating)
        return format_html(
            '<span style="color: #ffc107; font-size: 14px;">{}</span>',
            stars
        )
    rating_stars.short_description = 'Rating'
    
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)
    approve_reviews.short_description = 'Approve selected reviews'
    
    def disapprove_reviews(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_reviews.short_description = 'Disapprove selected reviews'
    
    def mark_verified(self, request, queryset):
        queryset.update(is_verified_purchase=True)
    mark_verified.short_description = 'Mark as verified purchases'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    """Admin for Wishlist."""
    list_display = ('user', 'product_count', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('user', 'created_at', 'updated_at')
    
    def product_count(self, obj):
        """Show product count in wishlist."""
        return obj.get_count()
    product_count.short_description = 'Products in Wishlist'
