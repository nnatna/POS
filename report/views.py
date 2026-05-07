from django.contrib.auth.decorators import login_required
from django.db.models import Count, Max, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import render
from django.utils import timezone

from products.models import Product
from sales.models import Order, Sale

@login_required
def report(request):
    date_filter = request.GET.get('date_filter', 'month')
    today = timezone.localdate()
    sales_qs = Sale.objects.select_related('order', 'product', 'product__category')

    if date_filter == 'today':
        sales_qs = sales_qs.filter(sale_date__date=today)
        report_title = 'Today'
    elif date_filter == 'week':
        start_of_week = today - timezone.timedelta(days=today.weekday())
        sales_qs = sales_qs.filter(sale_date__date__gte=start_of_week)
        report_title = 'This week'
    elif date_filter == 'year':
        sales_qs = sales_qs.filter(sale_date__year=today.year)
        report_title = 'This year'
    elif date_filter == 'all':
        report_title = 'All time'
    else:
        date_filter = 'month'
        sales_qs = sales_qs.filter(sale_date__year=today.year, sale_date__month=today.month)
        report_title = 'This month'

    totals = sales_qs.aggregate(
        total_revenue=Sum('total_amount'),
        total_items=Sum('quantity'),
        total_orders=Count('order', distinct=True),
    )

    total_revenue = totals['total_revenue'] or 0
    total_items = totals['total_items'] or 0
    total_orders = totals['total_orders'] or 0
    average_order = total_revenue / total_orders if total_orders else 0

    payment_totals = sales_qs.values('payment_method').annotate(
        revenue=Sum('total_amount'),
        items=Sum('quantity'),
        orders=Count('order', distinct=True),
    ).order_by('-revenue')

    top_products = sales_qs.values(
        'product__name',
        'product__category__name',
    ).annotate(
        items=Sum('quantity'),
        revenue=Sum('total_amount'),
    ).order_by('-items', '-revenue')[:8]

    daily_sales = sales_qs.annotate(day=TruncDate('sale_date')).values('day').annotate(
        revenue=Sum('total_amount'),
        items=Sum('quantity'),
        orders=Count('order', distinct=True),
    ).order_by('-day')[:7]

    recent_orders = Order.objects.filter(sale__in=sales_qs).annotate(
        total_amount=Sum('sale__total_amount'),
        total_items=Sum('sale__quantity'),
        latest_sale_date=Max('sale__sale_date'),
        payment_count=Count('sale__payment_method', distinct=True),
    ).order_by('-latest_sale_date')[:8]

    low_stock_products = Product.objects.select_related('category', 'brand').filter(
        stock_quantity__lte=10
    ).order_by('stock_quantity', 'name')[:8]

    context = {
        'date_filter': date_filter,
        'report_title': report_title,
        'total_revenue': total_revenue,
        'total_items': total_items,
        'total_orders': total_orders,
        'average_order': average_order,
        'payment_totals': payment_totals,
        'top_products': top_products,
        'daily_sales': daily_sales,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
    return render(request, 'report.html', context)
