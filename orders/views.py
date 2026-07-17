from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from decimal import Decimal

from orders.models import Order, OrderItem
from products.models import Product
from cart.models import Cart
from cart.cart_service import CartService
from users.models import Address
from orders.payment_service import DummyPaymentProcessor


class CheckoutView(LoginRequiredMixin, TemplateView):
    """Checkout view for order creation."""
    template_name = 'orders/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = Cart.objects.filter(user=self.request.user).first()
        context['cart'] = cart
        context['addresses'] = Address.objects.filter(user=self.request.user)
        context['tax_rate'] = Decimal('0.08')  # 8% tax
        context['shipping_cost'] = Decimal('10.00') if cart and cart.get_total_items() > 0 else Decimal('0.00')
        
        # Calculate tax amount
        if cart:
            subtotal = cart.get_subtotal()
            context['tax_amount'] = (subtotal * context['tax_rate']).quantize(Decimal('0.01'))
        else:
            context['tax_amount'] = Decimal('0.00')
        
        return context
    
    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart or cart.items.count() == 0:
            return redirect('cart')
        
        shipping_address_id = request.POST.get('shipping_address')
        payment_method = request.POST.get('payment_method', 'credit_card')
        
        if not shipping_address_id:
            return redirect('orders:checkout')
        
        try:
            address = Address.objects.get(id=shipping_address_id, user=request.user)
        except Address.DoesNotExist:
            return redirect('orders:checkout')
        
        # Create order with transaction
        with transaction.atomic():
            subtotal = cart.get_total_price()
            tax = (subtotal * Decimal('0.08')).quantize(Decimal('0.01'))
            shipping = Decimal('10.00')
            total = subtotal + tax + shipping
            
            order = Order.objects.create(
                user=request.user,
                subtotal=subtotal,
                tax=tax,
                shipping=shipping,
                total=total,
                billing_address=str(address),
                shipping_address=str(address),
                payment_status='pending'
            )
            
            # Create order items
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.price_at_add
                )
            
            # Process payment
            processor = DummyPaymentProcessor()
            # In production, pass actual payment method data
            payment_result = processor.process_payment(total, payment_method)
            
            if payment_result['success']:
                order.payment_status = 'completed'
                order.status = 'processing'
                order.save()
                
                # Clear cart
                CartService.clear_cart(request.user)
                
                return redirect('orders:order_confirmation', pk=order.id)
            else:
                order.payment_status = 'failed'
                order.status = 'cancelled'
                order.save()
                return redirect('orders:checkout')
        
        return redirect('orders:checkout')


class OrderConfirmationView(LoginRequiredMixin, DetailView):
    """Order confirmation page."""
    model = Order
    template_name = 'orders/order_confirmation.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderListView(LoginRequiredMixin, ListView):
    """User's order history."""
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class OrderDetailView(LoginRequiredMixin, DetailView):
    """Order detail view."""
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
