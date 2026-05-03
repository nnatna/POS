from django import forms
from .models import Brand

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control bg-secondary-subtle', 'placeholder': 'Enter brand name'}),
            'description': forms.Textarea(attrs={'class': 'form-control bg-secondary-subtle', 'rows': 3, 'placeholder': 'Enter brand description'}),
        }
