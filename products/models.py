from decimal import Decimal
import random
import string
from django.db import models
from POS.image_utils import convert_uploaded_image_to_png


def product_image_upload_to(instance, filename):
    return f'products/product{instance.pk}.png'


class Product(models.Model):
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE)
    category = models.ForeignKey('category.Category', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    procode = models.CharField(max_length=20, unique=True, blank=True) 
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock_quantity = models.IntegerField(default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to=product_image_upload_to, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.procode:
            while True:
                new_code = ''.join(random.choices(string.digits, k=8))
                if not Product.objects.filter(procode=new_code).exists():
                    self.procode = new_code
                    break

        if self._state.adding and self.image:
            image_file = self.image
            self.image = None
            super(Product, self).save(*args, **kwargs)
            self.image = convert_uploaded_image_to_png(image_file, f'product{self.pk}.png')
            super(Product, self).save(update_fields=['image'])
            return

        if self.pk and self.image and not getattr(self.image, '_committed', False):
            old_image = Product.objects.filter(pk=self.pk).values_list('image', flat=True).first()
            self.image = convert_uploaded_image_to_png(self.image, f'product{self.pk}.png')
            if old_image:
                self.image.storage.delete(old_image)

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
