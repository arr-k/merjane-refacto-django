from .strategies.normal_product_strategy import NormalProductStrategy
from .strategies.seasonal_product_strategy import SeasonalProductStrategy
from .strategies.expirable_product_strategy import ExpirableProductStrategy


from typing import Any, Dict, Type


class ProductProcessStrategyFactory:
    """Factory to build a processing strategy for a given product type.

    Uses late binding for dependencies so test-time patches (mocks) are picked up.
    """

    def __init__(self, product_repo: Any = None, notification_service: Any = None) -> None:
        if product_repo is None:
            from orders.repositories.product_repository import product_repository
        if notification_service is None:
            from orders.services.implementations.notification_service import ns as notification_service  # noqa: WPS433

        self.product_repository: Any = product_repository
        self.notification_service: Any = notification_service

    def for_type(self, product_type: str):
        mapping: Dict[str, Type] = {
            "NORMAL": NormalProductStrategy,
            "SEASONAL": SeasonalProductStrategy,
            "EXPIRABLE": ExpirableProductStrategy,
        }
        try:
            strategy_cls = mapping[product_type]
        except KeyError as exc:
            raise ValueError(f"Unknown product type: {product_type}") from exc
        return strategy_cls(self.product_repository, self.notification_service)
