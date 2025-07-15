from ..entities.product import Product

class ProductRepository:
    def find_by_id(self, id):
        return Product.objects.filter(pk=id)

    def save(self, p):
        p.save()

pr = ProductRepository()
