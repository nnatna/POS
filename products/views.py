from django.db import models
from django.shortcuts import render
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from .models import Product
from .forms import ProductForm
from category.models import Category
from brands.models import Brand


# Create your views here.
@login_required
def product(request):
    form = ProductForm()
    open_add_modal = False
    open_edit_modal_id = None
    edit_form = None
    search_query = request.GET.get('search', '').strip()

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

        # EDIT Section
        elif action == 'edit':
            product_id = request.POST.get('product_id')
            instance = get_object_or_404(Product, id=product_id)
            edit_form = ProductForm(request.POST, request.FILES, instance=instance)

            if edit_form.is_valid():
                updated_product = edit_form.save()
                messages.success(request, f'Product "{updated_product.name}" updated successfully.')
                return redirect('product')
            else:
                messages.error(request, 'Please correct the errors below.')
                open_edit_modal_id = instance.id

        # ADD Section
        elif action == 'add' or action is None:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                new_product = form.save()
                messages.success(request, f'Product "{new_product.name}" added successfully.')
                return redirect('product')
            else:
                messages.error(request, 'Please correct the errors below.')
                open_add_modal = True

    products = Product.objects.select_related('category', 'brand').all().order_by('-created_at')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
        )
    categories = Category.objects.all().order_by('name')
    brands = Brand.objects.all().order_by('name')

    context = {
        'products': products,
        'form': form,
        'categories': categories,
        'brands': brands,
        'open_add_modal': open_add_modal,
        'open_edit_modal_id': open_edit_modal_id,
        'edit_form': edit_form,
        'search_query': search_query,
    }
    return render(request, 'product.html', context)
