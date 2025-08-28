from typing import Any

from django.db.models import QuerySet

from ..entities.order import Order

class OrderRepository:
    def find_by_id(self, id: int) -> QuerySet[Order]:
        return Order.objects.filter(pk=id)

    def save(self, o: Order) -> None:
        o.save()

order_repository = OrderRepository()
