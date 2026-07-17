"""
Core views for e-commerce app.
"""
from django.views.generic import TemplateView
from django.shortcuts import render


class HomeView(TemplateView):
    """Home page view."""
    template_name = 'index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Additional context can be added here
        return context
