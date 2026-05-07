from decimal import Decimal
import random
import string
from django.db import models

class Product(models.Model):
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE)
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    procode = models.CharField(max_length=20, unique=True, blank=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.procode:
            while True:
                new_code = ''.join(random.choices(string.digits, k=8))
                if not Product.objects.filter(procode=new_code).exists():
                    self.procode = new_code
                    break
        super(Product, self).save(*args, **kwargs)

    @property
    def discounted_price(self):
        """Calculates the price after discount without modifying the base price."""
        if self.discount > 0:
            multiplier = Decimal('1') - (self.discount / Decimal('100'))
            return (self.price * multiplier).quantize(Decimal('0.01'))
        else:  
            return self.price

    def __str__(self):
        return self.name