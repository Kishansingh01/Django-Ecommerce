"""
User authentication and profile views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, TemplateView, ListView, UpdateView, DeleteView, CreateView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect

from .models import UserProfile, Address
from .forms import (
    UserRegistrationForm, UserLoginForm, CustomPasswordResetForm,
    CustomSetPasswordForm, UserProfileForm, AddressForm
)


class RegisterView(View):
    """User registration view."""
    template_name = 'users/register.html'
    form_class = UserRegistrationForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('users:login')
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    """User login view."""
    template_name = 'users/login.html'
    form_class = UserLoginForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            remember_me = form.cleaned_data.get('remember_me')

            # Try username first, then email
            user = authenticate(request, username=username, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass

            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username/email or password.')

        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    """User logout view."""
    
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out.')
        return redirect('home')


class UserProfileView(LoginRequiredMixin, TemplateView):
    """User profile view."""
    template_name = 'users/profile.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        profile, created = UserProfile.objects.get_or_create(user=user)
        addresses = user.addresses.all()
        
        context['profile'] = profile
        context['addresses'] = addresses
        context['address_count'] = addresses.count()
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Edit user profile view."""
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('user_profile')
    login_url = 'users:login'

    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class AddressListView(LoginRequiredMixin, ListView):
    """List user addresses."""
    model = Address
    template_name = 'users/address_list.html'
    context_object_name = 'addresses'
    paginate_by = 10
    login_url = 'users:login'

    def get_queryset(self):
        return self.request.user.addresses.all()


class AddressDetailView(LoginRequiredMixin, TemplateView):
    """View address detail."""
    template_name = 'users/address_detail.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        address_id = kwargs.get('pk')
        address = get_object_or_404(Address, pk=address_id, user=self.request.user)
        context['address'] = address
        return context


class AddressCreateView(LoginRequiredMixin, CreateView):
    """Create new address."""
    model = Address
    form_class = AddressForm
    template_name = 'users/address_form.html'
    success_url = reverse_lazy('address_list')
    login_url = 'users:login'

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Address added successfully!')
        return super().form_valid(form)


class AddressUpdateView(LoginRequiredMixin, UpdateView):
    """Update address."""
    model = Address
    form_class = AddressForm
    template_name = 'users/address_form.html'
    success_url = reverse_lazy('address_list')
    login_url = 'users:login'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Address updated successfully!')
        return super().form_valid(form)


class AddressDeleteView(LoginRequiredMixin, DeleteView):
    """Delete address."""
    model = Address
    template_name = 'users/address_confirm_delete.html'
    success_url = reverse_lazy('address_list')
    login_url = 'users:login'

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Address deleted successfully!')
        return super().delete(request, *args, **kwargs)


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view."""
    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset.html'
    email_template_name = 'users/password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

    def form_valid(self, form):
        messages.success(self.request, 'Password reset email has been sent. Check your inbox.')
        return super().form_valid(form)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Custom password reset confirm view."""
    form_class = CustomSetPasswordForm
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

    def form_valid(self, form):
        messages.success(self.request, 'Password has been reset successfully!')
        return super().form_valid(form)


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Custom password change view for logged-in users."""
    template_name = 'users/password_change.html'
    success_url = reverse_lazy('user_profile')
    login_url = 'users:login'

    def form_valid(self, form):
        messages.success(self.request, 'Password changed successfully!')
        return super().form_valid(form)
