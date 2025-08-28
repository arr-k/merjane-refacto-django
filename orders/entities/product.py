from datetime import date
from typing import Optional

from django.db import models, connection

class Product(models.Model):
    name: str = models.CharField(max_length=100)
    type: str = models.CharField(max_length=20)
    available: int = models.IntegerField(default=0)
    lead_time: int = models.IntegerField(default=0)
    expiry_date: Optional[date] = models.DateField(null=True, blank=True)
    season_start_date: Optional[date] = models.DateField(null=True, blank=True)
    season_end_date: Optional[date] = models.DateField(null=True, blank=True)

    def adjust_availability_raw(self, new_amount: int) -> None:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE orders_product SET available = %s WHERE id = %s",
                [new_amount, self.id]
            )

    def decrease_availability(self, quantity: int = 1) -> int:
        self.available -= quantity
        return self.available

    def reset_availability(self) -> None:
        self.available = 0

    def is_available(self) -> bool:
        return (self.available or 0) > 0

    def has_lead_time(self) -> bool:
        return (self.lead_time or 0) > 0

    class Meta:
        app_label = 'orders'
