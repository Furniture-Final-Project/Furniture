import unittest
from unittest.mock import MagicMock
from source.services.checkout_service import (
    CheckoutService, CartEmptyError, OutOfStockError, PaymentFailedError,
    UserNotFoundError, OrderCreationError, InvalidAddressError
)

class MockItem:
    """Mock class to simulate an item object."""
    
    def __init__(self, item_id: int, quantity: int, name: str = "Test Item") -> None:
        self.item_id = item_id
        self.quantity = quantity
        self.name = name  

class TestCheckoutService(unittest.TestCase):
    """Test suite for the CheckoutService class."""

    def setUp(self) -> None:
        """Setup mock dependencies before each test case."""
        self.mock_cart_manager = MagicMock()
        self.mock_inventory_manager = MagicMock()
        self.mock_order_manager = MagicMock()
        self.mock_user_manager = MagicMock()
        self.mock_payment_strategy = MagicMock()

        self.checkout_service = CheckoutService(
            self.mock_cart_manager,
            self.mock_inventory_manager,
            self.mock_order_manager,
            self.mock_user_manager,
            payment_strategy=self.mock_payment_strategy,
        )

    def test_process_payment_success(self) -> None:
        """Test successful payment processing."""
        self.mock_payment_strategy.process_payment.return_value = True
        result = self.checkout_service.process_payment(user_id=1, amount=100.0)
        self.assertIsNone(result)

    def test_process_payment_failure(self) -> None:
        """Test failed payment raises PaymentFailedError."""
        self.mock_payment_strategy.process_payment.return_value = False
        with self.assertRaises(PaymentFailedError):
            self.checkout_service.process_payment(user_id=1, amount=100.0)

    def test_checkout_success(self) -> None:
        """Test successful checkout process with all valid parameters."""
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2), MockItem(2, 1)]
        mock_cart.calculate_total.return_value = 150.0
        self.mock_cart_manager.get_cart.return_value = mock_cart

        self.mock_inventory_manager.is_item_available.return_value = True
        self.mock_payment_strategy.process_payment.return_value = True
        mock_user = MagicMock()
        mock_user.name = "John Doe"
        self.mock_user_manager.get_user.return_value = mock_user
        self.mock_order_manager.create_order.return_value = 1001

        result = self.checkout_service.checkout(user_id=1, address="123 Main St")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["order_id"], 1001)
        self.assertEqual(result["message"], "✅ Order placed successfully.")

    def test_checkout_empty_cart(self) -> None:
        """Test checkout fails when the cart is empty."""
        self.mock_cart_manager.get_cart.return_value = MagicMock(items=[])
        with self.assertRaises(CartEmptyError):
            self.checkout_service.checkout(user_id=1, address="123 Main St")

    def test_checkout_out_of_stock(self) -> None:
        """Test checkout fails when an item is out of stock."""
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2)]
        self.mock_cart_manager.get_cart.return_value = mock_cart
        self.mock_inventory_manager.is_item_available.return_value = False

        with self.assertRaises(OutOfStockError):
            self.checkout_service.checkout(user_id=1, address="123 Main St")

    def test_checkout_payment_failure(self) -> None:
        """Test checkout fails when payment is declined."""
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2)]
        mock_cart.calculate_total.return_value = 150.0
        self.mock_cart_manager.get_cart.return_value = mock_cart
        self.mock_inventory_manager.is_item_available.return_value = True
        self.mock_user_manager.get_user.return_value = MagicMock()

        self.mock_payment_strategy.process_payment.return_value = False

        with self.assertRaises(PaymentFailedError):
            self.checkout_service.checkout(user_id=1, address="123 Main St")

    def test_checkout_missing_user(self) -> None:
        """Test checkout fails when user details are missing."""
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2)]
        mock_cart.calculate_total.return_value = 150.0
        self.mock_cart_manager.get_cart.return_value = mock_cart
        self.mock_inventory_manager.is_item_available.return_value = True
        self.mock_payment_strategy.process_payment.return_value = True
        self.mock_user_manager.get_user.return_value = None

        with self.assertRaises(UserNotFoundError):
            self.checkout_service.checkout(user_id=1, address="123 Main St")

    def test_checkout_order_creation_failure(self) -> None:
        """Test checkout fails when order creation fails."""
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2)]
        mock_cart.calculate_total.return_value = 150.0
        self.mock_cart_manager.get_cart.return_value = mock_cart
        self.mock_inventory_manager.is_item_available.return_value = True
        self.mock_payment_strategy.process_payment.return_value = True
        self.mock_user_manager.get_user.return_value = MagicMock()

        self.mock_order_manager.create_order.return_value = None

        with self.assertRaises(OrderCreationError):
            self.checkout_service.checkout(user_id=1, address="123 Main St")

    def test_checkout_invalid_address(self) -> None:
        """Test checkout fails when an invalid address is provided."""
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2)]
        self.mock_cart_manager.get_cart.return_value = mock_cart
        self.mock_inventory_manager.is_item_available.return_value = True
        self.mock_payment_strategy.process_payment.return_value = True
        self.mock_user_manager.get_user.return_value = MagicMock()
        self.mock_order_manager.create_order.return_value = 1001

        with self.assertRaises(InvalidAddressError):
            self.checkout_service.checkout(user_id=1, address="")

if __name__ == '__main__':
    unittest.main()
