# orders/tests/test_product_service_unit.py

import unittest
from unittest.mock import patch

from orders.entities.product import Product
from orders.services.implementations.product_service import ProductService

class MyUnitTests(unittest.TestCase):
    @patch('orders.services.implementations.product_service.ns')
    @patch('orders.services.implementations.product_service.pr')
    def test_notify_delay(self, mock_pr, mock_ns):
        p = Product(
            name="RJ45 Cable",
            type="NORMAL",
            available=0,
            lead_time=15,
        )
        mock_pr.save.return_value = p
        ps = ProductService()

        ps.notify_delay(p.lead_time, p)

        self.assertEqual(0, p.available)
        self.assertEqual(15, p.lead_time)
        mock_pr.save.assert_called_once_with(p)
        mock_ns.send_delay_notification.assert_called_once_with(p.lead_time, p.name)

if __name__ == '__main__':
    unittest.main()
