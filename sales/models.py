import zoneinfo
from django.db import models
from products.models import Product
from decimal import Decimal
from django.utils import timezone

class Order(models.Model):
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            tz = zoneinfo.ZoneInfo("Asia/Phnom_Penh")
            current_local_time = timezone.now().astimezone(tz)
            date_str = current_local_time.strftime('%Y%m%d')
            prefix = f'ORD-{date_str}-'
            
            last_order = Order.objects.filter(order_number__startswith=prefix).order_by('-order_number').first()
            
            if last_order:
                last_num = int(last_order.order_number.split('-')[-1])
                new_num = f'{(last_num + 1):04d}'
            else:
                new_num = '0001'
            
            self.order_number = f'{prefix}{new_num}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

class Sale(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('khqr', 'KHQR'),
        ('cash', 'Cash'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField() 
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='khqr')
    sale_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        unit_price = self.product.discounted_price
        subtotal = unit_price * self.quantity

        if self.discount > 0:
            multiplier = Decimal('1') - (self.discount / Decimal('100'))
            self.total_amount = (subtotal * multiplier).quantize(Decimal('0.01'))
        else:
            self.total_amount = subtotal.quantize(Decimal('0.01'))

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale {self.id} - {self.product.name} ({self.order.order_number})"
