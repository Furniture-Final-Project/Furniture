import unittest
from unittest.mock import MagicMock
from source.services.checkout_service import CheckoutService

class MockItem:
    """Mock class to simulate an item object."""
    def __init__(self, item_id, quantity, name="Test Item"):
        self.item_id = item_id
        self.quantity = quantity
        self.name = name  # ✅ Added missing name attribute

class MockOrder:
    """Mock class to replace Order since it's not implemented yet."""
    def __init__(self, order_id, customer_name, phone, username, email, shipping_address, items, total_price):
        self.order_id = order_id
        self.customer_name = customer_name
        self.phone = phone
        self.username = username
        self.email = email
        self.shipping_address = shipping_address
        self.items = items
        self.total_price = total_price

class TestCheckoutService(unittest.TestCase):

    def setUp(self):
        """Runs before every test case - Sets up mock dependencies"""
        self.mock_cart_manager = MagicMock()
        self.mock_inventory_manager = MagicMock()
        self.mock_order_manager = MagicMock()
        self.mock_user_manager = MagicMock()
        self.mock_payment_gateway = MagicMock()
        self.mock_order_class = MockOrder

        self.checkout_service = CheckoutService(
            self.mock_cart_manager,
            self.mock_inventory_manager,
            self.mock_order_manager,
            self.mock_user_manager,
            order_class=self.mock_order_class
        )

        self.checkout_service.payment_gateway = self.mock_payment_gateway  # ✅ Inject mock payment gateway
        self.checkout_service.Order = MockOrder  # ✅ Inject MockOrder directly

    def test_process_payment_success(self):
        """Test that a successful payment returns True"""
        self.mock_payment_gateway.charge.return_value = True  # ✅ Simulate successful payment
        result = self.checkout_service.process_payment(user_id=1, amount=100.0, payment_method="credit_card")
        self.assertTrue(result)  # Expecting True since payment succeeded

    def test_process_payment_failure(self):
        """Test that a failed payment returns False"""
        self.mock_payment_gateway.charge.return_value = False  # ✅ Simulate failed payment
        result = self.checkout_service.process_payment(user_id=1, amount=100.0, payment_method="credit_card")
        self.assertFalse(result)  # Expecting False since payment failed

    def test_finalize_checkout_success(self):
        """Test finalize_checkout() with successful payment and order creation"""
        # ✅ Mock cart items
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2), MockItem(2, 1)]
        self.mock_cart_manager.get_cart.return_value = mock_cart

        # ✅ Mock inventory availability
        self.mock_inventory_manager.is_item_available.return_value = True

        # ✅ Mock successful payment
        self.mock_payment_gateway.charge.return_value = True

        # ✅ Mock user details
        mock_user = MagicMock()
        mock_user.name = "John Doe"
        mock_user.phone = "123-456-7890"
        mock_user.username = "johndoe"
        mock_user.email = "johndoe@example.com"
        self.mock_user_manager.get_user.return_value = mock_user

        # ✅ Mock order creation
        self.mock_order_manager.create_order.return_value = 1001  # Simulate order ID 1001

        result = self.checkout_service.finalize_checkout(user_id=1, address="123 Main St", payment_method="credit_card")

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["order_id"], 1001)
        self.assertEqual(result["message"], "Order placed successfully")

    def test_finalize_checkout_payment_failure(self):
        """Test finalize_checkout() when payment fails"""
        # ✅ Mock cart items
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2), MockItem(2, 1)]
        self.mock_cart_manager.get_cart.return_value = mock_cart

        # ✅ Mock inventory availability
        self.mock_inventory_manager.is_item_available.return_value = True

        # ✅ Simulate failed payment
        self.mock_payment_gateway.charge.return_value = False

        result = self.checkout_service.finalize_checkout(user_id=1, address="123 Main St", payment_method="credit_card")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Payment was declined. Please try another payment method.")

    def test_finalize_checkout_empty_cart(self):
        """Test finalize_checkout() fails when the cart is empty"""
        self.mock_cart_manager.get_cart.return_value = MagicMock(items=[])  # Empty cart
        result = self.checkout_service.finalize_checkout(user_id=1, address="123 Main St", payment_method="credit_card")
        
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Cart is empty")

    def test_finalize_checkout_missing_user(self):
        """Test finalize_checkout() fails when user details are missing"""
        # ✅ Mock cart with items
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2), MockItem(2, 1)]
        self.mock_cart_manager.get_cart.return_value = mock_cart

        self.mock_inventory_manager.is_item_available.return_value = True
        self.mock_payment_gateway.charge.return_value = True
        self.mock_user_manager.get_user.return_value = None  # Simulating missing user

        result = self.checkout_service.finalize_checkout(user_id=1, address="123 Main St", payment_method="credit_card")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "User not found")

    def test_finalize_checkout_order_creation_failure(self):
        """Test finalize_checkout() fails when order creation fails"""
        # ✅ Mock cart with items
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2), MockItem(2, 1)]
        self.mock_cart_manager.get_cart.return_value = mock_cart

        self.mock_inventory_manager.is_item_available.return_value = True
        self.mock_payment_gateway.charge.return_value = True

        mock_user = MagicMock()
        mock_user.name = "John Doe"
        mock_user.phone = "123-456-7890"
        mock_user.username = "johndoe"
        mock_user.email = "johndoe@example.com"
        self.mock_user_manager.get_user.return_value = mock_user

        self.mock_order_manager.create_order.return_value = None  # Simulate order creation failure

        result = self.checkout_service.finalize_checkout(user_id=1, address="123 Main St", payment_method="credit_card")

        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Failed to create order")

if __name__ == '__main__':
    unittest.main()
