from django.db.models import F, Q
from sales.forms import SaleForm
from sales.models import Sale, Order
from products.models import Product
from category.models import Category
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.http import JsonResponse
from decimal import Decimal, InvalidOperation
from django.db.models import Sum
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
import json



@login_required
def home(request):
    category_id = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()
    if category_id and category_id != 'all':
        products = Product.objects.filter(category_id=category_id)
    else:
        products = Product.objects.all()

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
        )

    categories = Category.objects.all()
    recent_sales = Sale.objects.select_related('order', 'product', 'product__category').order_by('-sale_date')[:5]
    recent_orders = Order.objects.order_by('-id')[:5]
    sales_totals = Sale.objects.aggregate(
        total_sales_amount=Sum('total_amount'),
        total_items_sold=Sum('quantity'),
    )

    context = {
        'products': products,
        'categories': categories,
        'sales': recent_sales,
        'orders': recent_orders,
        'total_sales_amount': sales_totals['total_sales_amount'] or 0,
        'total_items_sold': sales_totals['total_items_sold'] or 0,
        'selected_category': category_id or 'all',
        'search_query': search_query,
    }
    return render(request, 'home.html', context)

def login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            next_url = request.POST.get('next') or 'home'
            return redirect(next_url)
    else:
        form = AuthenticationForm()

    context = {'form': form, 'next': request.GET.get('next', '')}
    return render(request, 'login.html', context)

@transaction.atomic
def _create_checkout_order(payload):
    try:
        items = payload.get('items', [])
    except AttributeError:
        return JsonResponse({'error': 'Invalid request payload.'}, status=400)

    discount = payload.get('discount', 0)
    payment_method = payload.get('payment_method', 'khqr')

    if not items:
        return JsonResponse({'error': 'No items selected.'}, status=400)

    try:
        discount = Decimal(str(discount or 0))
    except (InvalidOperation, TypeError):
        return JsonResponse({'error': 'Invalid discount value.'}, status=400)

    if discount < 0 or discount > 100:
        return JsonResponse({'error': 'Discount must be between 0 and 100.'}, status=400)

    if payment_method not in {'khqr', 'cash'}:
        return JsonResponse({'error': 'Invalid payment method.'}, status=400)

    normalized_items = []
    product_ids = []
    for item in items:
        product_id = item.get('id')
        raw_quantity = item.get('quantity', item.get('qty', 0))

        try:
            product_id = int(product_id)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid product id.'}, status=400)

        normalized_items.append({'id': product_id, 'quantity': raw_quantity})
        product_ids.append(product_id)

    products = Product.objects.select_for_update().in_bulk(product_ids)

    if len(products) != len(product_ids):
        return JsonResponse({'error': 'One or more products were not found.'}, status=400)

    new_order = Order.objects.create()
    created_sales = []
    total_amount = Decimal('0.00')
    total_items = 0

    for item in normalized_items:
        product = products.get(item.get('id'))
        quantity = item.get('quantity', 0)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return JsonResponse({'error': f'Invalid quantity for {product.name}.'}, status=400)

        if quantity <= 0:
            return JsonResponse({'error': f'Quantity must be greater than zero for {product.name}.'}, status=400)

        if product.stock_quantity < quantity:
            return JsonResponse({'error': f'Not enough stock for {product.name}.'}, status=400)

        sale = Sale.objects.create(
            order=new_order,
            product=product,
            quantity=quantity,
            total_amount=Decimal('0.00'),
            discount=discount,
            payment_method=payment_method,
        )
        created_sales.append(sale)

        product.stock_quantity -= quantity
        product.save(update_fields=['stock_quantity'])

        total_amount += sale.total_amount
        total_items += quantity

    return JsonResponse({
        'message': 'Sale created successfully.',
        'order_number': new_order.order_number,
        'total_amount': f'{total_amount:.2f}',
        'total_items': total_items,
        'sale_ids': [sale.id for sale in created_sales],
    })


@transaction.atomic
@login_required
def checkout(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request payload.'}, status=400)

    return _create_checkout_order(payload)


@login_required
def process_checkout(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed.'}, status=405)

    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request payload.'}, status=400)

    return _create_checkout_order(payload)
