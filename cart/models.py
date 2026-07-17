"""
Shopping cart models.
"""
from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.validators import MinValueValidator
from decimal import Decimal


class Cart(models.Model):
    """Shopping cart model."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f"{self.user.username}'s Cart"

    def get_total_items(self):
        """Get total number of items in cart."""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    def get_total_price(self):
        """Get total cart price."""
        total = sum((item.get_item_total() for item in self.items.all()), Decimal('0'))
        return total

    def get_subtotal(self):
        """Get subtotal before tax/shipping."""
        return self.get_total_price()

    def clear(self):
        """Clear all items from cart."""
        self.items.all().delete()


class CartItem(models.Model):
    """Cart item model."""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)]
    )
    price_at_add = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price when item was added to cart"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product']
        verbose_name_plural = 'Cart Items'

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    def get_item_total(self):
        """Get total price for this item."""
        return self.quantity * self.price_at_add

    def save(self, *args, **kwargs):
        """Save price when item is added."""
        if not self.price_at_add:
            self.price_at_add = self.product.price
        super().save(*args, **kwargs)
