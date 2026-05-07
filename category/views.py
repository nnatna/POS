from django.db import models # Needed for ProtectedError
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Category
from .froms import CategoryForm

@login_required
def category(request):
    add_form = CategoryForm()
    open_add_modal = False
    open_edit_modal_id = None
    search_query = request.GET.get('search', '').strip()

    if request.method == 'POST':
        action = request.POST.get('action')

        # --- ADD ACTION ---
        if action == 'add':
            add_form = CategoryForm(request.POST)
            if add_form.is_valid():
                new_category = add_form.save()
                messages.success(request, f'Category "{new_category.name}" created.')
                return redirect('category')
            
            messages.error(request, 'Please correct the errors below.')
            open_add_modal = True

        # --- EDIT ACTION ---
        elif action == 'edit':
            category_id = request.POST.get('category_id')
            instance = get_object_or_404(Category, id=category_id)
            edit_form = CategoryForm(request.POST, instance=instance)
            
            if edit_form.is_valid():
                edit_form.save()
                messages.success(request, f'Category updated to "{instance.name}".')
                return redirect('category')
            
            messages.error(request, 'Invalid update. Name is required.')
            open_edit_modal_id = instance.id

        # --- DELETE ACTION ---
        elif action == 'delete':
            category_id = request.POST.get('category_id')
            category_to_delete = get_object_or_404(Category, id=category_id)
            name = category_to_delete.name
            
            try:
                category_to_delete.delete()
                messages.success(request, f'Category "{name}" deleted.')
            except models.ProtectedError:
                messages.error(request, f'Cannot delete "{name}" because it contains products.')
            
            return redirect('category')

    categories = Category.objects.all().order_by('name')
    if search_query:
        categories = categories.filter(name__icontains=search_query)
    
    context = {
        'categories': categories,
        'add_form': add_form,
        'open_add_modal': open_add_modal,
        'open_edit_modal_id': open_edit_modal_id,
        'search_query': search_query,
    }
    return render(request, 'category.html', context)
