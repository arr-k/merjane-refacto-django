from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from orders.entities.product import Product
from orders.entities.product_type import ProductType
from orders.entities.order import Order


class TestProcessOrderView(TestCase):
    @patch('orders.services.implementations.notification_service.ns')
    def test_process_order_should_return(self, mock_ns):
        products = [
            Product(available=15, lead_time=30, type=ProductType.NORMAL.value,    name="USB Cable"),
            Product(available=10, lead_time=0,  type=ProductType.NORMAL.value,    name="USB Dongle"),
            Product(available=15, lead_time=30, type=ProductType.EXPIRABLE.value, name="Butter",
                    expiry_date=date.today() + timedelta(days=26)),
            Product(available=90, lead_time=6,  type=ProductType.EXPIRABLE.value, name="Milk",
                    expiry_date=date.today() - timedelta(days=2)),
            Product(available=15, lead_time=30, type=ProductType.SEASONAL.value,  name="Watermelon",
                    season_start_date=date.today() - timedelta(days=2),
                    season_end_date=date.today() + timedelta(days=58)),
            Product(available=15, lead_time=30, type=ProductType.SEASONAL.value,  name="Grapes",
                    season_start_date=date.today() + timedelta(days=180),
                    season_end_date=date.today() + timedelta(days=240)),
        ]
        for p in products:
            p.save()

        o = Order.objects.create()
        o.products.set(products)

        url = reverse('process_order', args=[o.id])
        response = self.client.post(url, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        result_order = Order.objects.get(id=o.id)
        self.assertEqual(result_order.id, o.id)

    @patch('orders.services.implementations.notification_service.ns')
    def test_normal_out_of_stock_with_lead_time_sends_delay(self, mock_ns):
        p = Product.objects.create(name="RJ45 Cable", type=ProductType.NORMAL.value, available=0, lead_time=7)
        o = Order.objects.create()
        o.products.set([p])

        url = reverse('process_order', args=[o.id])
        self.client.post(url, content_type="application/json")

        p.refresh_from_db()
        self.assertEqual(p.available, 0)
        mock_ns.send_delay_notification.assert_called_once_with(7, "RJ45 Cable")

    @patch('orders.services.implementations.notification_service.ns')
    def test_seasonal_before_season_sends_unavailability(self, mock_ns):
        p = Product.objects.create(
            name="Grapes",
            type=ProductType.SEASONAL.value,
            available=5,
            lead_time=5,
            season_start_date=date.today() + timedelta(days=10),
            season_end_date=date.today() + timedelta(days=40),
        )
        o = Order.objects.create()
        o.products.set([p])

        url = reverse('process_order', args=[o.id])
        self.client.post(url, content_type="application/json")

        p.refresh_from_db()
        self.assertEqual(p.available, 5)
        mock_ns.send_out_of_stock_notification.assert_called_once_with("Grapes")

    @patch('orders.services.implementations.notification_service.ns')
    def test_seasonal_out_of_stock_with_short_lead_time_delays(self, mock_ns):
        p = Product.objects.create(
            name="Strawberry",
            type=ProductType.SEASONAL.value,
            available=0,
            lead_time=2,
            season_start_date=date.today() - timedelta(days=1),
            season_end_date=date.today() + timedelta(days=10),
        )
        o = Order.objects.create()
        o.products.set([p])

        url = reverse('process_order', args=[o.id])
        self.client.post(url, content_type="application/json")

        mock_ns.send_delay_notification.assert_called_once_with(2, "Strawberry")

    @patch('orders.services.implementations.notification_service.ns')
    def test_seasonal_out_of_stock_with_long_lead_time_marks_unavailable(self, mock_ns):
        p = Product.objects.create(
            name="Peach",
            type=ProductType.SEASONAL.value,
            available=0,
            lead_time=30,
            season_start_date=date.today() - timedelta(days=1),
            season_end_date=date.today() + timedelta(days=10),
        )
        o = Order.objects.create()
        o.products.set([p])

        url = reverse('process_order', args=[o.id])
        self.client.post(url, content_type="application/json")

        p.refresh_from_db()
        self.assertEqual(p.available, 0)
        mock_ns.send_out_of_stock_notification.assert_called_once_with("Peach")

    @patch('orders.services.implementations.notification_service.ns')
    def test_expirable_in_stock_and_not_expired_decrements(self, mock_ns):
        p = Product.objects.create(
            name="Butter",
            type=ProductType.EXPIRABLE.value,
            available=4,
            lead_time=0,
            expiry_date=date.today() + timedelta(days=3),
        )
        o = Order.objects.create()
        o.products.set([p])

        url = reverse('process_order', args=[o.id])
        self.client.post(url, content_type="application/json")

        p.refresh_from_db()
        self.assertEqual(p.available, 3)
        mock_ns.send_expiry_notification.assert_not_called()

    @patch('orders.services.implementations.notification_service.ns')
    def test_expirable_expired_sets_unavailable_and_notifies(self, mock_ns):
        p = Product.objects.create(
            name="Milk",
            type=ProductType.EXPIRABLE.value,
            available=2,
            lead_time=0,
            expiry_date=date.today(),
        )
        o = Order.objects.create()
        o.products.set([p])

        url = reverse('process_order', args=[o.id])
        self.client.post(url, content_type="application/json")

        p.refresh_from_db()
        self.assertEqual(p.available, 0)
        mock_ns.send_expiry_notification.assert_called_once_with("Milk")
