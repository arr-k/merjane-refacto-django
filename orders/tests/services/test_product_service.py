import unittest
from unittest.mock import patch

from orders.entities.product import Product
from orders.services.implementations.product_service import ProductService

class TestProductService(unittest.TestCase):
    @patch('orders.services.implementations.product_service.ns')
    @patch('orders.services.implementations.product_service.product_repository')
    def test_notify_delay(self, mock_pr, mock_ns):
        product = Product(
            name="RJ45 Cable",
            type="NORMAL",
            available=0,
            lead_time=15,
        )
        mock_pr.save.return_value = product
        product_service = ProductService()

        product_service.notify_delay(product.lead_time, product)

        self.assertEqual(0, product.available)
        self.assertEqual(15, product.lead_time)
        mock_pr.save.assert_called_once_with(product)
        mock_ns.send_delay_notification.assert_called_once_with(product.lead_time, product.name)

    @patch('orders.services.implementations.product_service.ns')
    @patch('orders.services.implementations.product_service.product_repository')
    def test_handle_seasonal_lead_time_exceeds_end_marks_unavailable(self, mock_pr, mock_ns):
        from datetime import date, timedelta

        product = Product(
            name="Seasonal A",
            type="SEASONAL",
            available=5,
            lead_time=20,
            season_start_date=date.today() - timedelta(days=1),
            season_end_date=date.today() + timedelta(days=10),
        )
        product_service = ProductService()

        product_service.handle_seasonal_product(product)

        self.assertEqual(product.available, 0)
        mock_pr.save.assert_called()
        mock_ns.send_out_of_stock_notification.assert_called_once_with("Seasonal A")

    @patch('orders.services.implementations.product_service.ns')
    @patch('orders.services.implementations.product_service.product_repository')
    def test_handle_seasonal_before_start_notifies_out_of_stock(self, mock_pr, mock_ns):
        from datetime import date, timedelta

        product = Product(
            name="Seasonal B",
            type="SEASONAL",
            available=5,
            lead_time=5,
            season_start_date=date.today() + timedelta(days=2),
            season_end_date=date.today() + timedelta(days=20),
        )
        product_service = ProductService()

        product_service.handle_seasonal_product(product)

        self.assertEqual(product.available, 5)
        mock_pr.save.assert_called()
        mock_ns.send_out_of_stock_notification.assert_called_once_with("Seasonal B")

    @patch('orders.services.implementations.product_service.ns')
    @patch('orders.services.implementations.product_service.product_repository')
    def test_handle_seasonal_otherwise_delays(self, mock_pr, mock_ns):
        from datetime import date, timedelta

        product = Product(
            name="Seasonal C",
            type="SEASONAL",
            available=0,
            lead_time=2,
            season_start_date=date.today() - timedelta(days=1),
            season_end_date=date.today() + timedelta(days=10),
        )
        product_service = ProductService()

        product_service.handle_seasonal_product(product)

        mock_ns.send_delay_notification.assert_called_once_with(2, "Seasonal C")
        mock_pr.save.assert_called()

    @patch('orders.services.implementations.product_service.ns')
    @patch('orders.services.implementations.product_service.product_repository')
    def test_handle_expired_product_paths(self, mock_pr, mock_ns):
        from datetime import date, timedelta

        before_expiry_product = Product(name="Butter", type="EXPIRABLE", available=3, expiry_date=date.today() + timedelta(days=1))
        product_service = ProductService()
        product_service.handle_expired_product(before_expiry_product)
        self.assertEqual(before_expiry_product.available, 2)
        mock_ns.send_expiry_notification.assert_not_called()

        mock_ns.reset_mock()

        at_expiry_product = Product(name="Milk", type="EXPIRABLE", available=1, expiry_date=date.today())
        product_service.handle_expired_product(at_expiry_product)
        self.assertEqual(at_expiry_product.available, 0)
        mock_ns.send_expiry_notification.assert_called_once_with("Milk")

if __name__ == '__main__':
    unittest.main()
