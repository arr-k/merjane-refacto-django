from datetime import date, timedelta
from ...repositories.product_repository import product_repository
from .notification_service import ns

class ProductService:
    def notify_delay(self, lead_time: int, p) -> None:
        p.lead_time = lead_time
        product_repository.save(p)
        ns.send_delay_notification(lead_time, p.name)

    def handle_seasonal_product(self, p) -> None:
        if date.today() + timedelta(days=p.lead_time) > p.season_end_date:
            ns.send_out_of_stock_notification(p.name)
            p.reset_availability()
            product_repository.save(p)
        elif p.season_start_date > date.today():
            ns.send_out_of_stock_notification(p.name)
            product_repository.save(p)
        else:
            self.notify_delay(p.lead_time, p)

    def handle_expired_product(self, p) -> None:
        if p.is_available() and p.expiry_date > date.today():
            p.available -= 1
            product_repository.save(p)
        else:
            p.reset_availability()
            product_repository.save(p)
            ns.send_expiry_notification(p.name)

ps = ProductService()
