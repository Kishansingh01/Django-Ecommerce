"""
Product and review forms.
"""
from django import forms
from .models import Review, Product


class ReviewForm(forms.ModelForm):
    """Form for submitting product reviews."""
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=Review.RATING_CHOICES, attrs={
                'class': 'form-check-input'
            }),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Review Title (optional)',
                'maxlength': '255'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your thoughts about this product...',
                'rows': 4
            }),
        }


class ProductSearchForm(forms.Form):
    """Form for product search."""
    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products...'
        })
    )
    category = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min Price',
            'type': 'number',
            'step': '0.01'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max Price',
            'type': 'number',
            'step': '0.01'
        })
    )
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Sort by'),
            ('newest', 'Newest'),
            ('price_asc', 'Price: Low to High'),
            ('price_desc', 'Price: High to Low'),
            ('rating', 'Highest Rated'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
