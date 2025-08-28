import logging
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .repositories.order_repository import order_repository
from .services.implementations.product_service import ps
from .services.product_process_strategy_factory import ProductProcessStrategyFactory
from .services.order_service import OrderService

logger = logging.getLogger(__name__)

@csrf_exempt
@require_POST
def process_order(request, order_id: int):
    """Process an order by delegating business rules to the domain service.

    Returns 404 if the order does not exist.
    """
    strategy_factory = ProductProcessStrategyFactory()
    order_service = OrderService(order_repository, strategy_factory)
    try:
        response = order_service.process_order(order_id)
    except ValueError:
        logger.warning("Order not found: id=%s", order_id)
        raise Http404()
    return JsonResponse({'id': response.id}, status=200)
