from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Order, Sale
from .forms import SaleForm

@login_required
def sales(request):
    sale_form = SaleForm()

    if request.method == 'POST' and request.POST.get('action') == 'add_sale':
        sale_form = SaleForm(request.POST)
        if sale_form.is_valid():
            try:
                with transaction.atomic():
                    product_data = sale_form.cleaned_data['product']
                    quantity = sale_form.cleaned_data['quantity']

                    product = Product.objects.select_for_update().get(id=product_data.id)

                    if product.stock_quantity < quantity:
                        sale_form.add_error('quantity', f'Insufficient stock. Only {product.stock_quantity} remaining.')
                    else:
                        new_order = Order.objects.create()

                        new_sale = sale_form.save(commit=False)
                        new_sale.order = new_order
                        new_sale.save()

                        product.stock_quantity -= quantity
                        product.save(update_fields=['stock_quantity'])

                        messages.success(request, f'Sale #{new_sale.id} completed successfully.')
                        return redirect('sales')
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")

    order_id_filter = request.GET.get('orders')
    sales_qs = Sale.objects.select_related('order', 'product', 'product__category').order_by('-sale_date')
    selected_order_id = None

    if order_id_filter:
        try:
            selected_order_id = int(order_id_filter)
            sales_qs = sales_qs.filter(order_id=selected_order_id)
        except (ValueError, TypeError):
            selected_order_id = None

    sidebar_totals = sales_qs.aggregate(
        subtotal=Sum('total_price'),
        total_items=Sum('quantity'),
    )

    recent_orders = Order.objects.annotate(
        total_amount=Sum('sale__total_price'),
        total_items=Sum('sale__quantity'),
    ).order_by('-id')[:50]

    overall_totals = Sale.objects.aggregate(
        total_sales_amount=Sum('total_price'),
        total_items_sold=Sum('quantity'),
    )

    context = {
        'sales': sales_qs,
        'orders': recent_orders,
        'selected_order_id': selected_order_id,
        'total_sales_amount': overall_totals['total_sales_amount'] or 0,
        'total_items_sold': overall_totals['total_items_sold'] or 0,
        'subtotal': sidebar_totals['subtotal'] or 0,
        'total_items': sidebar_totals['total_items'] or 0,
        'sale_form': sale_form,
        'open_add_sale_modal': bool(sale_form.errors),
    }
    return render(request, 'sales.html', context)