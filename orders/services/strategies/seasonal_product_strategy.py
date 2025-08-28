from datetime import date, timedelta
from typing import TYPE_CHECKING

from orders.entities.product import Product
from orders.services.strategies.product_processing_strategy import ProductProcessingStrategy

if TYPE_CHECKING:
    from orders.repositories.product_repository import ProductRepository
    from orders.services.implementations.notification_service import NotificationService


class SeasonalProductStrategy(ProductProcessingStrategy):
    def __init__(self, product_repository: 'ProductRepository', notification_service: 'NotificationService') -> None:
        self.product_repository: 'ProductRepository' = product_repository
        self.notification_service: 'NotificationService' = notification_service

    def process(self, product: Product) -> None:
        today = date.today()
        in_season = (
            product.season_start_date is not None
            and product.season_end_date is not None
            and product.season_start_date < today < product.season_end_date
        )

        if in_season and product.is_available():
            product.decrease_availability(1)
            self.product_repository.save(product)
            return

        if not in_season:
            self.notification_service.send_out_of_stock_notification(product.name)
            self.product_repository.save(product)
            return

        if today + timedelta(days=product.lead_time) > product.season_end_date:
            product.reset_availability()
            self.product_repository.save(product)
            self.notification_service.send_out_of_stock_notification(product.name)
        else:
            self.product_repository.save(product)
            if product.has_lead_time():
                self.notification_service.send_delay_notification(product.lead_time, product.name)
