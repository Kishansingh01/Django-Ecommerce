"""
Product catalog views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Q, Avg
from django.urls import reverse_lazy
from django.http import JsonResponse

from .models import Product, Category, Review, Wishlist
from .forms import ReviewForm, ProductSearchForm
from .pagination import TemplatePaginator
from .filters import ProductFilter


class ProductListView(ListView):
    """Product listing view with search, filter, and pagination."""
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        """Get filtered and searched queryset."""
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Search
        query = self.request.GET.get('q', '')
        if query:
            queryset = ProductFilter.search_products(queryset, query)
        
        # Category filter
        category_slug = self.request.GET.get('category', '')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Price range filter
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        queryset = ProductFilter.filter_by_price_range(queryset, min_price, max_price)
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'rating':
            queryset = queryset.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_form'] = ProductSearchForm(self.request.GET)
        context['current_query'] = self.request.GET.get('q', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_sort'] = self.request.GET.get('sort', '')
        return context


class ProductDetailView(DetailView):
    """Product detail view with reviews."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        
        # Reviews
        context['reviews'] = product.reviews.filter(is_approved=True)
        context['avg_rating'] = product.get_rating()
        context['rating_display'] = product.get_rating_display()
        context['review_count'] = product.get_review_count()
        
        # Related products
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id)[:4]
        
        # User has reviewed this product
        context['user_has_reviewed'] = False
        if self.request.user.is_authenticated:
            context['user_has_reviewed'] = product.reviews.filter(
                user=self.request.user
            ).exists()
            context['review_form'] = ReviewForm()
        
        # Wishlist status
        context['in_wishlist'] = False
        if self.request.user.is_authenticated:
            wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
            context['in_wishlist'] = wishlist.products.filter(id=product.id).exists()
        
        return context

    def post(self, request, *args, **kwargs):
        """Handle form submissions: reviews, cart, wishlist."""
        product = self.get_object()
        action = request.POST.get('action')
        
        # Handle add to cart
        if action == 'add_to_cart':
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to add items to cart.')
                return redirect('users:login')
            
            if product.is_available:
                from cart.cart_service import CartService
                CartService.add_to_cart(request.user, product, 1)
                messages.success(request, f"{product.name} added to cart!")
                return redirect('cart')
            else:
                messages.error(request, 'This product is out of stock.')
                return redirect(product.get_absolute_url())
        
        # Handle toggle wishlist
        elif action == 'toggle_wishlist':
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to add items to wishlist.')
                return redirect('users:login')
            
            wishlist, created = Wishlist.objects.get_or_create(user=request.user)
            if wishlist.products.filter(id=product.id).exists():
                wishlist.products.remove(product)
                messages.success(request, f"{product.name} removed from wishlist.")
            else:
                wishlist.products.add(product)
                messages.success(request, f"{product.name} added to wishlist!")
            
            return redirect(product.get_absolute_url())
        
        # Handle review submission (default)
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to submit a review.')
            return redirect('users:login')
        
        form = ReviewForm(request.POST)
        
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Thank you! Your review has been submitted.')
            return redirect(product.get_absolute_url())
        
        context = self.get_context_data()
        context['review_form'] = form
        return self.render_to_response(context)


class WishlistView(LoginRequiredMixin, TemplateView):
    """User wishlist view."""
    template_name = 'products/wishlist.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wishlist, created = Wishlist.objects.get_or_create(user=self.request.user)
        context['wishlist_items'] = wishlist.products.all()
        context['wishlist_count'] = wishlist.get_count()
        return context


class AddToWishlistView(LoginRequiredMixin, TemplateView):
    """Add product to wishlist (AJAX)."""
    login_url = 'users:login'

    def post(self, request, *args, **kwargs):
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, id=product_id)
        
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        
        if wishlist.products.filter(id=product.id).exists():
            wishlist.products.remove(product)
            return JsonResponse({'success': True, 'action': 'removed'})
        else:
            wishlist.products.add(product)
            return JsonResponse({'success': True, 'action': 'added'})


class RemoveFromWishlistView(LoginRequiredMixin, DeleteView):
    """Remove product from wishlist."""
    model = Product
    success_url = reverse_lazy('wishlist')
    login_url = 'users:login'

    def delete(self, request, *args, **kwargs):
        wishlist = get_object_or_404(Wishlist, user=request.user)
        product = self.get_object()
        wishlist.products.remove(product)
        messages.success(request, 'Product removed from wishlist.')
        return redirect(self.success_url)
