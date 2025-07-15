from datetime import date
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from .dto.product import ProcessOrderResponse
from .entities.order import Order
from .entities.product import Product
from .repositories.product_repository import pr
from .repositories.order_repository import or_
from .services.implementations.product_service import ps

@csrf_exempt
@require_POST
def process_order(request, order_id):
    o = or_.find_by_id(order_id).get()
    print(o)
    ids = []
    ids.append(order_id)
    products = o.get_items()
    for p in products:
        if p.type == "NORMAL":
            if p.available > 0:
                p.available = p.available - 1
                pr.save(p)
            else:
                lead_time = p.lead_time
                if lead_time > 0:
                    ps.notify_delay(lead_time, p)

        elif p.type == "SEASONAL":
            if (date.today() > p.season_start_date and date.today() < p.season_end_date and p.available > 0):
                p.available = p.available - 1
                pr.save(p)
            else:
                ps.handle_seasonal_product(p)

        elif p.type == "EXPIRABLE":
            if p.available > 0 and p.expiry_date > date.today():
                p.available = p.available - 1
                pr.save(p)
            else:
                ps.handle_expired_product(p)

    response = ProcessOrderResponse(o.id)
    return JsonResponse({'id': response.id}, status=200)
