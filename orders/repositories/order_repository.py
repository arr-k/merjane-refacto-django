from ..entities.order import Order

class OrderRepository:
    def find_by_id(self, id):
        return Order.objects.filter(pk=id)

    def save(self, o):
        o.save()

or_ = OrderRepository()
