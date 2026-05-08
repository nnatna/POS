from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import TruncDate, TruncHour, Coalesce
from datetime import timedelta

from products.models import Product
from sales.models import Sale, Order


# ── Dashboard HTML ────────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    return render(request, 'dashboard.html')


# ── Helper: Date Range ────────────────────────────────────────────────────────
def get_date_range(period):
    now = timezone.now()
    if period == 'today':
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == 'week':
        start = now - timedelta(days=7)
    elif period == 'month':
        start = now - timedelta(days=30)
    elif period == 'year':
        start = now - timedelta(days=365)
    else:
        start = now - timedelta(days=7)
    return start, now


# ── API: Dashboard Data ───────────────────────────────────────────────────────
@login_required
def dashboard_data(request):
    period = request.GET.get('period', 'week')
    start, end = get_date_range(period)

    sales_qs = Sale.objects.filter(sale_date__gte=start, sale_date__lte=end)

    # ── KPI ───────────────────────────────────────────────────────────────────
    total_revenue = float(
        sales_qs.aggregate(
            t=Coalesce(Sum('total_amount'), 0, output_field=DecimalField())
        )['t']
    )
    total_sales   = sales_qs.count()
    total_expense = round(total_revenue * 0.4, 2)
    net_profit    = round(total_revenue - total_expense, 2)

    order_count = Order.objects.filter(
        sale__sale_date__gte=start,
        sale__sale_date__lte=end
    ).distinct().count()

    # ── Sales Trend ───────────────────────────────────────────────────────────
    if period == 'today':
        trend_qs = (
            sales_qs
            .annotate(bucket=TruncHour('sale_date'))
            .values('bucket')
            .annotate(total=Sum('total_amount'))
            .order_by('bucket')
        )
        trend = [
            {'label': t['bucket'].strftime('%H:%M'), 'amount': float(t['total'])}
            for t in trend_qs
        ]
    else:
        trend_qs = (
            sales_qs
            .annotate(bucket=TruncDate('sale_date'))
            .values('bucket')
            .annotate(total=Sum('total_amount'))
            .order_by('bucket')
        )
        trend = [
            {'label': t['bucket'].strftime('%d/%m'), 'amount': float(t['total'])}
            for t in trend_qs
        ]

    # ── Revenue by Category (donut) ───────────────────────────────────────────
    cat_qs = (
        sales_qs
        .values(cat_name=F('product__category__name'))
        .annotate(total=Sum('total_amount'))
        .order_by('-total')
    )
    donut = [
        {'name': c['cat_name'] or 'Unknown', 'value': float(c['total'])}
        for c in cat_qs
    ]

    # ── Top Products ──────────────────────────────────────────────────────────
    top_qs = (
        sales_qs
        .values(
            prod_name=F('product__name'),
            prod_price=F('product__price'),
            cat_name=F('product__category__name'),
        )
        .annotate(
            total_qty=Sum('quantity'),
            total_rev=Sum('total_amount'),
        )
        .order_by('-total_qty')[:8]
    )
    top_products = [
        {
            'name':     p['prod_name'],
            'price':    float(p['prod_price']),
            'category': p['cat_name'] or '—',
            'qty':      p['total_qty'],
            'revenue':  float(p['total_rev']),
        }
        for p in top_qs
    ]

    # ── Low Stock ─────────────────────────────────────────────────────────────
    low_stock = list(
        Product.objects
        .filter(stock_quantity__lte=50)
        .select_related('category')
        .values('name', 'stock_quantity', cat_name=F('category__name'))
        .order_by('stock_quantity')[:6]
    )

    return JsonResponse({
        'period': period,
        'kpi': {
            'total_revenue': total_revenue,
            'total_sales':   total_sales,
            'order_count':   order_count,
            'total_expense': total_expense,
            'net_profit':    net_profit,
        },
        'trend':        trend,
        'donut':        donut,
        'top_products': top_products,
        'low_stock':    low_stock,
    })


# ── API: Sales List ───────────────────────────────────────────────────────────
@login_required
def sales_list(request):
    qs = (
        Sale.objects
        .select_related('product', 'product__category', 'order')
        .order_by('-sale_date')[:50]
    )
    data = [
        {
            'id':             s.id,
            'order_number':   s.order.order_number,
            'product':        s.product.name,
            'category':       s.product.category.name if s.product.category else '—',
            'quantity':       s.quantity,
            'discount':       float(s.discount),
            'payment_method': s.payment_method,
            'total_price':    float(s.total_amount),  # ✅
            'sale_date':      s.sale_date.strftime('%Y-%m-%d %H:%M'),
        }
        for s in qs
    ]
    return JsonResponse(data, safe=False)