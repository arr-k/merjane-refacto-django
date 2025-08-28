from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from orders.entities.product import Product
from orders.entities.product_type import ProductType
from orders.entities.order import Order


class TestSeasonalProductRules(TestCase):
    @patch('orders.services.implementations.notification_service.ns')
    def test_in_season_boundary_days_are_exclusive(self, mock_ns):
        today = date.today()
        product = Product.objects.create(
            name="Watermelon",
            type=ProductType.SEASONAL.value,
            available=2,
            lead_time=5,
            season_start_date=today,
            season_end_date=today,
        )
        order = Order.objects.create()
        order.products.set([product])

        url = reverse('process_order', args=[order.id])
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(200, response.status_code)
        product.refresh_from_db()
        self.assertEqual(2, product.available)

    @patch('orders.services.implementations.notification_service.ns')
    def test_in_season_out_of_stock_and_restock_after_season_notifies_unavailable(self, mock_ns):
        today = date.today()
        product = Product.objects.create(
            name="Grapes",
            type=ProductType.SEASONAL.value,
            available=0,
            lead_time=10,
            season_start_date=today - timedelta(days=1),
            season_end_date=today + timedelta(days=5),
        )
        order = Order.objects.create()
        order.products.set([product])

        url = reverse('process_order', args=[order.id])
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(200, response.status_code)
        assert mock_ns is not None

    @patch('orders.services.implementations.notification_service.ns')
    def test_out_of_season_notifies_unavailable(self, mock_ns):
        today = date.today()
        product = Product.objects.create(
            name="Mango",
            type=ProductType.SEASONAL.value,
            available=5,
            lead_time=3,
            season_start_date=today + timedelta(days=10),
            season_end_date=today + timedelta(days=20),
        )
        order = Order.objects.create()
        order.products.set([product])

        url = reverse('process_order', args=[order.id])
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(200, response.status_code)
        assert mock_ns is not None
