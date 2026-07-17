"""
REST API Serializers for Django E-commerce.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from users.models import UserProfile, Address
from products.models import Category, Product, ProductImage, Review, Wishlist
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem


# User Serializers
class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile."""
    class Meta:
        model = UserProfile
        fields = ['bio', 'profile_picture', 'phone', 'date_of_birth']


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for user address."""
    class Meta:
        model = Address
        fields = ['id', 'full_name', 'phone', 'street', 'city', 'state', 'postal_code', 'country', 'address_type', 'is_default']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user."""
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile', 'date_joined']


# Product Serializers
class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for product category."""
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon']


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for product reviews."""
    author = serializers.StringRelatedField(source='user', read_only=True)
    
    class Meta:
        model = Review
        fields = ['id', 'author', 'rating', 'title', 'comment', 'created_at', 'is_verified_purchase', 'is_approved']


class ProductSerializer(serializers.ModelSerializer):
    """Serializer for products."""
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True, source='productimage_set')
    reviews = ReviewSerializer(many=True, read_only=True, source='review_set')
    rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'stock', 'image', 'category', 'images', 'reviews', 'rating', 'is_active', 'is_featured', 'created_at']
    
    def get_rating(self, obj):
        return float(obj.get_rating()) if obj.get_rating() else None


# Cart Serializers
class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for cart items."""
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price_at_add']


class CartSerializer(serializers.ModelSerializer):
    """Serializer for shopping cart."""
    items = CartItemSerializer(many=True, read_only=True, source='cartitem_set')
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']


# Order Serializers
class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for order items."""
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_id', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""
    items = OrderItemSerializer(many=True, read_only=True, source='item_set')
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'order_number', 'user', 'subtotal', 'tax', 'shipping', 'total', 'status', 'payment_status', 'items', 'billing_address', 'shipping_address', 'created_at']


# Wishlist Serializer
class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for wishlist."""
    products = ProductSerializer(many=True, read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'products', 'created_at', 'updated_at']
