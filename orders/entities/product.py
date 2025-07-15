from django.db import models, connection

class Product(models.Model):
    name              = models.CharField(max_length=100)
    type              = models.CharField(max_length=20)
    available         = models.IntegerField(default=0)
    lead_time         = models.IntegerField(default=0)
    expiry_date       = models.DateField(null=True, blank=True)
    season_start_date = models.DateField(null=True, blank=True)
    season_end_date   = models.DateField(null=True, blank=True)

    def adjust_availability_raw(self, new_amount):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders_product SET available = %s WHERE id = %s",
                [new_amount, self.id]
            )
    class Meta:
        app_label = 'orders'
