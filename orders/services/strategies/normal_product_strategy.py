from typing import TYPE_CHECKING

from orders.entities.product import Product
from orders.services.strategies.product_processing_strategy import ProductProcessingStrategy

if TYPE_CHECKING:
    from orders.repositories.product_repository import ProductRepository
    from orders.services.implementations.notification_service import NotificationService


class NormalProductStrategy(ProductProcessingStrategy):
    def __init__(self, product_repository: 'ProductRepository', notification_service: 'NotificationService') -> None:
        self.product_repository: 'ProductRepository' = product_repository
        self.notification_service: 'NotificationService' = notification_service

    def process(self, product: Product) -> None:
        if product.is_available():
            product.decrease_availability(1)
            self.product_repository.save(product)
        else:
            if product.has_lead_time():
                self.notification_service.send_delay_notification(product.lead_time, product.name)
