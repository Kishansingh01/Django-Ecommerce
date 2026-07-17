"""
Cart business logic and services.
"""
from django.contrib.auth.models import User
from products.models import Product
from .models import Cart, CartItem


class CartService:
    """Service for managing cart operations."""
    
    @staticmethod
    def get_or_create_cart(user):
        """Get or create cart for user."""
        cart, created = Cart.objects.get_or_create(user=user)
        return cart
    
    @staticmethod
    def add_to_cart(user, product, quantity=1):
        """Add product to cart."""
        cart = CartService.get_or_create_cart(user)
        
        # Check if product already in cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity, 'price_at_add': product.price}
        )
        
        if not created:
            # Update quantity if item already exists
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item
    
    @staticmethod
    def remove_from_cart(user, product_id):
        """Remove product from cart."""
        cart = CartService.get_or_create_cart(user)
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
    
    @staticmethod
    def update_quantity(user, product_id, quantity):
        """Update quantity of item in cart."""
        cart = CartService.get_or_create_cart(user)
        
        if quantity <= 0:
            CartService.remove_from_cart(user, product_id)
            return None
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            return None
    
    @staticmethod
    def clear_cart(user):
        """Clear all items from user's cart."""
        cart = CartService.get_or_create_cart(user)
        cart.clear()
    
    @staticmethod
    def get_cart_summary(user):
        """Get cart summary."""
        cart = CartService.get_or_create_cart(user)
        return {
            'total_items': cart.get_total_items(),
            'total_price': cart.get_total_price(),
            'items': list(cart.items.all().values_list('product_id', 'quantity')),
        }
    
    @staticmethod
    def validate_cart(cart):
        """Validate cartitems (check stock, prices, etc.)."""
        errors = []
        items_to_remove = []
        
        for item in cart.items.all():
            # Check if product still exists and is active
            if not item.product.is_active:
                errors.append(f"{item.product.name} is no longer available.")
                items_to_remove.append(item.id)
                continue
            
            # Check stock
            if item.quantity > item.product.stock:
                errors.append(
                    f"{item.product.name} only has {item.product.stock} items available. "
                    f"Reduced quantity to {item.product.stock}."
                )
                if item.product.stock > 0:
                    item.quantity = item.product.stock
                    item.save()
                else:
                    items_to_remove.append(item.id)
        
        # Remove invalid items
        if items_to_remove:
            CartItem.objects.filter(id__in=items_to_remove).delete()
        
        return errors
