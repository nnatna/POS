from django.db import models
from django.shortcuts import render
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Product
from .forms import ProductForm


# Create your views here.
@login_required
def product(request):
    form = ProductForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        # DELETE Section
        if action == 'delete':
            product_id = request.POST.get('product_id')
            product_to_delete = get_object_or_404(Product, id=product_id)
            product_name = product_to_delete.name
            
            try:
                product_to_delete.delete()
                messages.success(request, f'Product "{product_name}" deleted successfully.')
            except models.ProtectedError:
                messages.error(request, f'Cannot delete "{product_name}" because it is linked to sales data.')
            
            return redirect('product')

        # ADD Section
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_product = form.save()
            messages.success(request, f'Product "{new_product.name}" added successfully.')
            return redirect('product')
        else:
            messages.error(request, 'Please correct the errors below.')

    products = Product.objects.select_related('category', 'brand').all().order_by('-created_at')
    
    context = {
        'products': products,
        'form': form,
        'open_add_modal': request.method == 'POST' and form.errors,
    }
    return render(request, 'product.html', context)