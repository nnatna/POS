from django import forms
from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'brand', 'name', 'price', 'stock_quantity', 'discount', 'description', 'image']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select bg-secondary-subtle'}),
            'brand': forms.Select(attrs={'class': 'form-select bg-secondary-subtle'}),
            'name': forms.TextInput(attrs={'class': 'form-control bg-secondary-subtle', 'placeholder': 'Enter product name'}),
            'price': forms.NumberInput(attrs={'class': 'form-control bg-secondary-subtle', 'placeholder': '0.00', 'step': '0.01', 'min': '0'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control bg-secondary-subtle', 'placeholder': '0', 'min': '0'}),
            'discount': forms.NumberInput(attrs={'class': 'form-control bg-secondary-subtle', 'placeholder': '0', 'step': '0.01', 'min': '0'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-secondary-subtle', 'rows': 3, 'placeholder': 'Enter product description'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control bg-secondary-subtle', 'accept': 'image/*'}),
        }
