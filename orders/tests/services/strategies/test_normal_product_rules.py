from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from orders.entities.product import Product
from orders.entities.product_type import ProductType
from orders.entities.order import Order


class TestNormalProductRules(TestCase):
    @patch('orders.services.implementations.notification_service.ns')
    def test_normal_in_stock_decrements(self, mock_ns):
        product = Product.objects.create(
            name="USB Cable", type=ProductType.NORMAL.value, available=1, lead_time=0
        )
        order = Order.objects.create()
        order.products.set([product])

        url = reverse('process_order', args=[order.id])
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(200, response.status_code)

        product.refresh_from_db()
        self.assertEqual(0, product.available)
        mock_ns.send_delay_notification.assert_not_called()

    @patch('orders.services.implementations.notification_service.ns')
    def test_normal_out_of_stock_no_notify_when_lead_time_zero(self, mock_ns):
        product = Product.objects.create(
            name="HDMI Cable", type=ProductType.NORMAL.value, available=0, lead_time=0
        )
        order = Order.objects.create()
        order.products.set([product])

        url = reverse('process_order', args=[order.id])
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(200, response.status_code)

        mock_ns.send_delay_notification.assert_not_called()

    @patch('orders.services.implementations.notification_service.ns')
    def test_normal_out_of_stock_notifies_when_lead_time_positive(self, mock_ns):
        product = Product.objects.create(
            name="RJ45", type=ProductType.NORMAL.value, available=0, lead_time=7
        )
        order = Order.objects.create()
        order.products.set([product])

        url = reverse('process_order', args=[order.id])
        response = self.client.post(url, content_type="application/json")
        self.assertEqual(200, response.status_code)

        mock_ns.send_delay_notification.assert_called_once()
        args, kwargs = mock_ns.send_delay_notification.call_args
        self.assertEqual(7, args[0])
