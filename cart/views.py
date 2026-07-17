"""
Shopping cart views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from decimal import Decimal

from products.models import Product
from .models import Cart, CartItem
from .cart_service import CartService


class CartView(TemplateView):
    """Display shopping cart."""
    template_name = 'cart/cart.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Only show cart if user is authenticated
        if self.request.user.is_authenticated:
            cart = CartService.get_or_create_cart(self.request.user)
            
            # Validate cart items
            errors = CartService.validate_cart(cart)
            if errors:
                for error in errors:
                    messages.warning(self.request, error)
            
            context['cart'] = cart
            context['cart_items'] = cart.items.all()
            context['total_items'] = cart.get_total_items()
            context['subtotal'] = cart.get_subtotal()
            context['tax'] = context['subtotal'] * Decimal('0.08')  # 8% tax
            context['shipping'] = Decimal('10.00') if context['subtotal'] > 0 else Decimal('0')
            context['total'] = context['subtotal'] + context['tax'] + context['shipping']
        else:
            # Empty cart for unauthenticated users
            context['cart_items'] = []
            context['total_items'] = 0
            context['subtotal'] = Decimal('0')
            context['tax'] = Decimal('0')
            context['shipping'] = Decimal('0')
            context['total'] = Decimal('0')
        
        return context


class AddToCartView(LoginRequiredMixin, View):
    """Add product to cart."""
    login_url = 'users:login'

    def post(self, request):
        try:
            product_id = request.POST.get('product_id')
            quantity = int(request.POST.get('quantity', 1))
            
            product = get_object_or_404(Product, id=product_id, is_active=True)
            
            # Check stock
            if quantity > product.stock:
                messages.error(request, f"Only {product.stock} items available.")
                return redirect(product.get_absolute_url())
            
            # Add to cart
            cart_item = CartService.add_to_cart(request.user, product, quantity)
            
            messages.success(request, f"{product.name} added to cart!")
            return redirect('cart')
        except Exception as e:
            messages.error(request, "Error adding item to cart.")
            return redirect('products:product_list')


class RemoveFromCartView(LoginRequiredMixin, View):
    """Remove item from cart."""
    login_url = 'users:login'

    def post(self, request, product_id):
        CartService.remove_from_cart(request.user, product_id)
        messages.success(request, "Item removed from cart.")
        return redirect('cart')


class UpdateCartView(LoginRequiredMixin, View):
    """Update cart item quantity."""
    login_url = 'users:login'

    def post(self, request, item_id):
        try:
            quantity = int(request.POST.get('quantity', 1))
            cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
            
            # Check stock
            if quantity > cart_item.product.stock:
                messages.error(
                    request,
                    f"Only {cart_item.product.stock} items of {cart_item.product.name} available."
                )
            else:
                CartService.update_quantity(request.user, cart_item.product_id, quantity)
                messages.success(request, "Cart updated.")
        except Exception as e:
            messages.error(request, "Error updating cart.")
        
        return redirect('cart')


class ClearCartView(LoginRequiredMixin, View):
    """Clear all items from cart."""
    login_url = 'users:login'

    def post(self, request):
        CartService.clear_cart(request.user)
        messages.success(request, "Cart cleared.")
        return redirect('cart')


class CartCountView(View):
    """Get cart item count (AJAX)."""
    
    def get(self, request):
        if request.user.is_authenticated:
            cart = CartService.get_or_create_cart(request.user)
            return JsonResponse({'count': cart.get_total_items()})
        return JsonResponse({'count': 0})
