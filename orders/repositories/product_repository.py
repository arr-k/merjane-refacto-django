from django.db.models import QuerySet

from ..entities.product import Product

class ProductRepository:
    def find_by_id(self, id: int) -> QuerySet[Product]:
        return Product.objects.filter(pk=id)

    def save(self, p: Product) -> None:
        p.save()

product_repository = ProductRepository()
