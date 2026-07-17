"""
REST API Views/ViewSets for Django E-commerce.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404

from users.models import Address
from products.models import Product, Category, Review, Wishlist
from cart.models import Cart
from cart.cart_service import CartService
from orders.models import Order

from api.serializers import (
    UserSerializer, AddressSerializer, ProductSerializer,
    CategorySerializer, ReviewSerializer, CartSerializer,
    OrderSerializer, WishlistSerializer
)
from api.permissions import IsOwnerOrReadOnly
from api.pagination import StandardPagination
from api.filters import ProductFilter


class UserViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for User model.
    List: GET /api/users/
    Detail: GET /api/users/{id}/
    Current User: GET /api/users/me/
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwnerOrReadOnly]
    pagination_class = StandardPagination
    
    def get_object(self):
        if self.kwargs.get('pk') == 'me':
            return self.request.user
        return super().get_object()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class AddressViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Address model.
    List: GET /api/addresses/
    Create: POST /api/addresses/
    Detail: GET /api/addresses/{id}/
    Update: PUT/PATCH /api/addresses/{id}/
    Delete: DELETE /api/addresses/{id}/
    """
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Category model (Read-only).
    List: GET /api/categories/
    Detail: GET /api/categories/{id}/
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Product model.
    List: GET /api/products/ (supports filtering, searching, sorting)
    Detail: GET /api/products/{id}/
    Search: GET /api/products/search/?q=query
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardPagination
    filterset_class = ProductFilter
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def featured(self, request):
        """Get featured products."""
        featured_products = self.queryset.filter(is_featured=True)
        page = self.paginate_queryset(featured_products)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for Review model.
    Create: POST /api/reviews/ (requires product_id in body)
    List: GET /api/reviews/?product={product_id}
    Update: PUT/PATCH /api/reviews/{id}/
    Delete: DELETE /api/reviews/{id}/
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        queryset = Review.objects.filter(is_approved=True)
        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WishlistViewSet(viewsets.ViewSet):
    """
    API ViewSet for Wishlist.
    Get user's wishlist: GET /api/wishlist/
    Add to wishlist: POST /api/wishlist/add/ (requires product_id)
    Remove from wishlist: POST /api/wishlist/remove/ (requires product_id)
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='get')
    def get_wishlist(self, request):
        """Get user's wishlist."""
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if not wishlist:
            wishlist = Wishlist.objects.create(user=request.user)
        
        serializer = WishlistSerializer(wishlist)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        """Add product to wishlist."""
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        wishlist.products.add(product)
        
        return Response({'status': 'Product added to wishlist'})
    
    @action(detail=False, methods=['post'])
    def remove(self, request):
        """Remove product from wishlist."""
        product_id = request.data.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist.products.remove(product)
        
        return Response({'status': 'Product removed from wishlist'})


class CartViewSet(viewsets.ViewSet):
    """
    API ViewSet for Cart.
    Get cart: GET /api/cart/
    Add to cart: POST /api/cart/add/ (requires product_id, quantity)
    Update item quantity: PATCH /api/cart/update-item/ (requires product_id, quantity)
    Remove from cart: DELETE /api/cart/remove/ (requires product_id)
    Clear cart: DELETE /api/cart/clear/
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CartSerializer
    
    @action(detail=False, methods=['get'], url_path='list')
    def get_cart(self, request):
        """Get user's cart."""
        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            cart = Cart.objects.create(user=request.user)
        
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def add(self, request):
        """Add product to cart."""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        product = get_object_or_404(Product, id=product_id)
        CartService.add_to_cart(request.user, product, quantity)
        
        return Response({'status': 'Product added to cart'})
    
    @action(detail=False, methods=['post'])
    def update_item(self, request):
        """Update item quantity in cart."""
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        
        CartService.update_quantity(request.user, product_id, quantity)
        return Response({'status': 'Cart updated'})
    
    @action(detail=False, methods=['post'])
    def remove(self, request):
        """Remove product from cart."""
        product_id = request.data.get('product_id')
        CartService.remove_from_cart(request.user, product_id)
        
        return Response({'status': 'Product removed from cart'})
    
    @action(detail=False, methods=['post'])
    def clear(self, request):
        """Clear cart."""
        CartService.clear_cart(request.user)
        return Response({'status': 'Cart cleared'})


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for Order model.
    List user orders: GET /api/orders/
    Get order detail: GET /api/orders/{id}/
    Cancel order: POST /api/orders/{id}/cancel/
    """
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = StandardPagination
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel order."""
        order = self.get_object()
        
        if order.status in ['shipped', 'delivered']:
            return Response(
                {'error': 'Cannot cancel shipped or delivered orders'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'cancelled'
        order.save()
        return Response({'status': 'Order cancelled'})


