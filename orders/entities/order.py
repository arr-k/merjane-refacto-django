from django.db import models

from .product import Product

# WARN: Should not be changed during the exercise
class Order(models.Model):
    products = models.ManyToManyField(Product, related_name="orders")

    def get_items(self):
        return self.products.all()

    def get_id(self):
        return self.id
    class Meta:
        app_label = 'orders'
