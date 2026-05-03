from django.db import models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Brand
from .forms import BrandForm

@login_required
def brands(request):
    add_form = BrandForm()
    open_add_modal = False
    open_edit_modal_id = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'add':
            add_form = BrandForm(request.POST)
            if add_form.is_valid():
                new_brand = add_form.save()
                messages.success(request, f'Brand "{new_brand.name}" created.')
                return redirect('brands')

            messages.error(request, 'Please correct the errors below.')
            open_add_modal = True

        elif action == 'edit':
            brand_id = request.POST.get('brand_id')
            instance = get_object_or_404(Brand, id=brand_id)
            edit_form = BrandForm(request.POST, instance=instance)

            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, f'Brand "{instance.name}" updated.')
                return redirect('brands')

            messages.error(request, 'Please correct the errors below.')
            open_edit_modal_id = instance.id

        elif action == 'delete':
            brand_id = request.POST.get('brand_id')
            brand_to_delete = get_object_or_404(Brand, id=brand_id)
            name = brand_to_delete.name
            try:
                brand_to_delete.delete()
                messages.success(request, f'Brand "{name}" deleted.')
            except models.ProtectedError:
                messages.error(request, f'Cannot delete "{name}" because it is linked to another record.')
            return redirect('brands')

    brands_list = Brand.objects.all().order_by('name')
    context = {
        'brands': brands_list,
        'add_form': add_form,
        'open_add_modal': open_add_modal,
        'open_edit_modal_id': open_edit_modal_id,
    }
    return render(request, 'brand.html', context)