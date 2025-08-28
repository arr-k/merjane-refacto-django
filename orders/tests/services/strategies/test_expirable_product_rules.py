from datetime import date, timedelta
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from orders.entities.product import Product
from orders.entities.product_type import ProductType
from orders.entities.order import Order


class TestExpirableProductRules(TestCase):
    @patch('orders.services.implementations.notification_service.ns')
    def test_before_expiry_decrements(self, mock_ns):
        product = Product.objects.create(
            name="Milk",
            type=ProductType.EXPIRABLE.value,
            available=3,
            lead_time=0,
            expiry_date=date.today() + timedelta(days=1),
        )
        order = Order.objects.create()
        order.products.set([product])

        url = reverse('process_order', args=[order.id])
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(200, response.status_code)
        product.refresh_from_db()
        self.assertEqual(2, product.available)

    @patch('orders.services.implementations.notification_service.ns')
    def test_on_or_after_expiry_notifies(self, mock_ns):
        product = Product.objects.create(
            name="Butter",
            type=ProductType.EXPIRABLE.value,
            available=2,
            lead_time=0,
            expiry_date=date.today() - timedelta(days=0),
        )
        order = Order.objects.create()
        order.products.set([product])

        url = reverse('process_order', args=[order.id])
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(200, response.status_code)
        mock_ns.send_expiry_notification.assert_called()
