from typing import TYPE_CHECKING, Iterable

from orders.dto.product import ProcessOrderResponse
from orders.entities.product_type import ProductType

if TYPE_CHECKING:
    from orders.repositories.order_repository import OrderRepository
    from orders.services.product_process_strategy_factory import ProductProcessStrategyFactory
    from orders.entities.product import Product


class OrderService:
    """Orchestrates order processing by delegating per-product logic to strategies."""

    def __init__(self, order_repository: 'OrderRepository', strategy_factory: 'ProductProcessStrategyFactory') -> None:
        self.order_repository: 'OrderRepository' = order_repository
        self.strategy_factory: 'ProductProcessStrategyFactory' = strategy_factory

    def process_order(self, order_id: int) -> ProcessOrderResponse:
        order = self.order_repository.find_by_id(order_id).first()
        if order is None:
            raise ValueError("Order not found")

        products: 'Iterable[Product]' = order.get_items()
        for product in products:
            product_type = product.type
            if isinstance(product_type, str):
                product_type_key: str = product_type
            else:
                product_type_key = product_type.value
            strategy = self.strategy_factory.for_type(product_type_key)
            strategy.process(product)

        return ProcessOrderResponse(order.id)
