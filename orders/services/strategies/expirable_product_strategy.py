from datetime import date
from typing import TYPE_CHECKING

from orders.entities.product import Product
from orders.services.strategies.product_processing_strategy import ProductProcessingStrategy

if TYPE_CHECKING:
    from orders.repositories.product_repository import ProductRepository
    from orders.services.implementations.notification_service import NotificationService


class ExpirableProductStrategy(ProductProcessingStrategy):
    def __init__(self, product_repository: 'ProductRepository', notification_service: 'NotificationService') -> None:
        self.product_repository: 'ProductRepository' = product_repository
        self.notification_service: 'NotificationService' = notification_service

    def process(self, product: Product) -> None:
        if product.is_available() and product.expiry_date and product.expiry_date > date.today():
            product.decrease_availability(1)
            self.product_repository.save(product)
        else:
            product.reset_availability()
            self.product_repository.save(product)
            self.notification_service.send_expiry_notification(product.name)
