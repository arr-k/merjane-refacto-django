from abc import ABC, abstractmethod

from orders.entities.product import Product


class ProductProcessingStrategy(ABC):
    @abstractmethod
    def process(self, product: Product) -> None:
        ...
