from django.db import transaction
from django.db.models import DecimalField, ExpressionWrapper, F, Max, Q, Sum
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from products.models import Product
from .models import Order, Sale
from .forms import SaleForm


def filter_by_period(queryset, date_filter, field_name='sale_date'):
    today = timezone.localdate()
    date_lookup = f'{field_name}__date'
    year_lookup = f'{field_name}__year'
    month_lookup = f'{field_name}__month'

    if date_filter == 'today':
        queryset = queryset.filter(**{date_lookup: today})
    elif date_filter == 'week':
        start_of_week = today - timezone.timedelta(days=today.weekday())
        queryset = queryset.filter(**{f'{date_lookup}__gte': start_of_week})
    elif date_filter == 'year':
        queryset = queryset.filter(**{year_lookup: today.year})
    elif date_filter == 'all':
        pass
    else:
        date_filter = 'month'
        queryset = queryset.filter(**{year_lookup: today.year, month_lookup: today.month})

    return queryset, date_filter


@login_required
def sales(request):
    sale_form = SaleForm()

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete_order':
            order_id = request.POST.get('order_id')
            try:
                order_to_delete = Order.objects.get(id=order_id)
                order_number = order_to_delete.order_number

                with transaction.atomic():
                    for sale_item in order_to_delete.sale_set.select_related('product').all():
                        product = sale_item.product
                        product.stock_quantity += sale_item.quantity
                        product.save(update_fields=['stock_quantity'])
                    order_to_delete.delete()

                messages.success(request, f'Order {order_number} deleted successfully.')
            except Order.DoesNotExist:
                messages.error(request, 'Order not found.')
            return redirect('sales')

        if action == 'add_sale':
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
    date_filter = request.GET.get('date_filter', 'month').strip().lower()
    search_query = request.GET.get('search', '').strip()
    sales_qs = Sale.objects.select_related('order', 'product', 'product__category').order_by('-sale_date')
    selected_order_id = None
    selected_order_number = None

    sales_qs, date_filter = filter_by_period(sales_qs, date_filter)

    if order_id_filter:
        try:
            selected_order_id = int(order_id_filter)
            selected_order_number = Order.objects.filter(id=selected_order_id).values_list('order_number', flat=True).first()
            if selected_order_number:
                sales_qs = sales_qs.filter(order_id=selected_order_id)
            else:
                selected_order_id = None
        except (ValueError, TypeError):
            selected_order_id = None
            selected_order_number = None

    if search_query:
        sales_qs = sales_qs.filter(
            Q(order__order_number__icontains=search_query)
        )

    line_subtotal_expression = ExpressionWrapper(
        F('product__price') * F('quantity'),
        output_field=DecimalField(max_digits=12, decimal_places=2),
    )

    selected_order_sales = []
    selected_order_payment_method = None
    selected_order_sale_date = None
    selected_order_discount = 0

    if selected_order_id:
        selected_order_sales = list(sales_qs)
        if selected_order_sales:
            first_sale = selected_order_sales[0]
            selected_order_payment_method = first_sale.get_payment_method_display()
            selected_order_sale_date = first_sale.sale_date
            selected_order_discount = first_sale.discount or 0

    sidebar_totals = sales_qs.aggregate(
        subtotal=Sum(line_subtotal_expression),
        final_total=Sum('total_amount'),
        total_items=Sum('quantity'),
        discount_amount=Sum(
            ExpressionWrapper(
                line_subtotal_expression - F('total_amount'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        ),
    )

    recent_orders = Order.objects.annotate(
        total_amount=Sum('sale__total_amount'),
        total_items=Sum('sale__quantity'),
        latest_sale_date=Max('sale__sale_date'),
    )

    recent_orders, _ = filter_by_period(recent_orders, date_filter, 'sale__sale_date')

    if search_query:
        recent_orders = recent_orders.filter(
            Q(order_number__icontains=search_query)
            | Q(sale__product__name__icontains=search_query)
            | Q(sale__product__brand__name__icontains=search_query)
            | Q(sale__product__category__name__icontains=search_query)
        )

    recent_orders = recent_orders.distinct().order_by('-id')[:50]

    overall_totals = Sale.objects.aggregate(
        total_sales_amount=Sum('total_amount'),
        total_items_sold=Sum('quantity'),
    )

    context = {
        'sales': sales_qs,
        'orders': recent_orders,
        'selected_order_id': selected_order_id,
        'selected_order_number': selected_order_number,
        'selected_order_sales': selected_order_sales,
        'selected_order_payment_method': selected_order_payment_method,
        'selected_order_sale_date': selected_order_sale_date,
        'selected_order_discount': selected_order_discount,
        'date_filter': date_filter,
        'search_query': search_query,
        'total_sales_amount': overall_totals['total_sales_amount'] or 0,
        'total_items_sold': overall_totals['total_items_sold'] or 0,
        'subtotal': sidebar_totals['subtotal'] or 0,
        'discount_amount': sidebar_totals['discount_amount'] or 0,
        'final_total': sidebar_totals['final_total'] or 0,
        'total_items': sidebar_totals['total_items'] or 0,
        'sale_form': sale_form,
        'open_add_sale_modal': bool(sale_form.errors),
    }
    return render(request, 'sales.html', context)
