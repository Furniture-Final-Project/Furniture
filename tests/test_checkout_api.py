import unittest
from unittest.mock import patch

try:
    from source.API.checkout_api import app
except ImportError:
    from flask import Flask
    app = Flask(__name__)  # ✅ Mock Flask app if `checkout_api.py` is missing

class TestCheckoutAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up the Flask test client before all tests."""
        cls.client = app.test_client()

    @patch("source.API.checkout_api.checkout_service.finalize_checkout", return_value={"status": "success", "order_id": 1001, "message": "Order placed successfully"})
    @patch("source.API.checkout_api.cart_manager.get_cart", return_value=None)
    @patch("source.API.checkout_api.inventory_manager.is_item_available", return_value=True)
    @patch("source.API.checkout_api.order_manager.get_order", return_value=None)
    @patch("source.API.checkout_api.user_manager.get_user", return_value=None)
    def test_checkout_success(self, *mocks):
        """Test successful checkout request."""
        response = self.client.post("/api/checkout", json={
            "user_id": 1,
            "address": "123 Main St",
            "payment_method": "credit_card"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")
        self.assertEqual(response.json["order_id"], 1001)

    @patch("source.API.checkout_api.checkout_service.finalize_checkout", return_value={"status": "error", "message": "Payment was declined. Please try another payment method."})
    @patch("source.API.checkout_api.cart_manager.get_cart", return_value=None)
    @patch("source.API.checkout_api.inventory_manager.is_item_available", return_value=True)
    def test_checkout_failure(self, *mocks):
        """Test checkout request failure due to payment failure."""
        response = self.client.post("/api/checkout", json={
            "user_id": 1,
            "address": "123 Main St",
            "payment_method": "credit_card"
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(response.json["message"], "Payment was declined. Please try another payment method.")

    @patch("source.API.checkout_api.order_manager.get_order", return_value={"order_id": 1001, "user_id": 1, "items": [{"item_id": 1, "name": "Laptop", "quantity": 1}], "total_price": 999.99, "status": "processing"})
    def test_get_order_success(self, *mocks):
        """Test retrieving an order successfully."""
        response = self.client.get("/api/orders/1001")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["order_id"], 1001)
        self.assertEqual(response.json["status"], "processing")

    @patch("source.API.checkout_api.order_manager.get_order", return_value=None)
    def test_get_order_not_found(self, *mocks):
        """Test retrieving a non-existent order."""
        response = self.client.get("/api/orders/9999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(response.json["message"], "Order not found")

if __name__ == '__main__':
    unittest.main()
