import unittest
import json
from unittest.mock import patch
from source.API.checkout_api import create_app

class TestCheckoutAPI(unittest.TestCase):
    """Test suite for the Checkout API endpoints."""

    @classmethod
    def setUpClass(cls) -> None:
        """Set up the Flask test client before running tests."""
        cls.app = create_app()
        cls.client = cls.app.test_client()

    @patch("source.API.checkout_api.CartManager", autospec=True)
    @patch("source.API.checkout_api.InventoryManager", autospec=True)
    @patch("source.API.checkout_api.OrderManager", autospec=True)
    @patch("source.API.checkout_api.UserManager", autospec=True)
    @patch("source.API.checkout_api.checkout_service")
    def test_checkout_success(self, mock_checkout_service, *_):
        """Test successful checkout with mocked dependencies."""
        mock_checkout_service.finalize_checkout.return_value = {
            "status": "success",
            "order_id": 1234,
            "message": "Order placed successfully"
        }

        response = self.client.post(
            "/api/checkout",
            data=json.dumps({"user_id": 1, "address": "123 Main St", "payment_method": "credit_card"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")
        self.assertEqual(response.json["order_id"], 1234)

    def test_checkout_missing_fields(self) -> None:
        """Test checkout fails when required fields are missing."""
        response = self.client.post(
            "/api/checkout",
            data=json.dumps({"user_id": 1}),  # Missing address and payment_method
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["status"], "error")
        self.assertIn("Missing required fields", response.json["message"])

    def test_checkout_invalid_json(self) -> None:
        """Test checkout fails with invalid JSON format."""
        response = self.client.post(
            "/api/checkout",
            data="invalid json",  # Not a valid JSON
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(response.json["message"], "Invalid JSON format")

    def test_checkout_invalid_payment_method(self) -> None:
        """Test checkout fails when an invalid payment method is provided."""
        response = self.client.post(
            "/api/checkout",
            data=json.dumps({"user_id": 1, "address": "123 Main St", "payment_method": "bitcoin"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid payment method", response.json["message"])

    @patch("source.API.checkout_api.checkout_service")
    def test_checkout_payment_failure(self, mock_checkout_service) -> None:
        """Test checkout fails when payment is declined."""
        mock_checkout_service.finalize_checkout.return_value = {
            "status": "error",
            "message": "Payment was declined"
        }

        response = self.client.post(
            "/api/checkout",
            data=json.dumps({"user_id": 1, "address": "123 Main St", "payment_method": "credit_card"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["status"], "error")
        self.assertEqual(response.json["message"], "Payment was declined")

if __name__ == "__main__":
    unittest.main()
