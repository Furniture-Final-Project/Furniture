import unittest
from werkzeug.exceptions import HTTPException
from unittest.mock import MagicMock
from source.controller.checkout_service import CheckoutService
from unittest.mock import patch


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
        self.mock_payment_strategy = MagicMock()

        # Patch the imported controllers inside the CheckoutService module
        self.cart_patch = patch("source.controller.cart.system_get_all_user_cart_items")
        self.user_patch = patch("source.controller.user.get_user_details")
        self.order_patch = patch("source.controller.order.add_order")
        self.inventory_patch = patch("source.controller.furniture_inventory.system_update_item_quantity")

        # Start patches
        self.mock_cart_controller = self.cart_patch.start()
        self.mock_user_controller = self.user_patch.start()
        self.mock_order_controller = self.order_patch.start()
        self.mock_inventory_controller = self.inventory_patch.start()

        # Initialize CheckoutService with only the payment strategy
        self.checkout_service = CheckoutService(payment_strategy=self.mock_payment_strategy)

    def test_process_payment_success(self) -> None:
        """Test successful payment processing."""
        self.mock_payment_strategy.process_payment.return_value = True
        result = self.checkout_service.process_payment(user_id=1, amount=100.0)
        self.assertIsNone(result)

    @patch("flask.abort")
    def test_process_payment_failure(self, mock_abort) -> None:
        """Test failed payment raises HTTPException (Payment Required - 402)."""

        # Mock flask.abort to simulate a PAYMENT_REQUIRED (402) error
        http_exception = HTTPException(description="Payment was declined. Please try another payment method.")
        http_exception.response = MagicMock(status_code=402)  # Manually set the response status
        mock_abort.side_effect = http_exception

        # Mock payment processing failure
        self.mock_payment_strategy.process_payment.return_value = False

        # Expect HTTPException instead of PaymentFailedError
        with self.assertRaises(HTTPException) as context:
            self.checkout_service.process_payment(user_id=1, amount=100.0)

        # Assert the correct HTTP status code and message
        self.assertEqual(context.exception.response.status_code, 402)  # HTTPStatus.PAYMENT_REQUIRED
        self.assertIn("Payment was declined", str(context.exception.description))

    @patch("source.controller.cart.system_get_all_user_cart_items")
    @patch("source.controller.user.get_user_details")
    @patch("source.controller.order.add_order")
    @patch("source.controller.furniture_inventory.system_update_item_quantity")
    @patch("schema.session")  # Mock database session
    @patch("source.controller.cart.get_cart_item_full_details")  # Mock this function properly
    def test_checkout_success(
        self, mock_get_cart_item_details, mock_schema_session, mock_update_inventory, mock_add_order, mock_get_user, mock_get_cart
    ) -> None:
        """Test successful checkout process with all valid parameters."""

        # Mock the database session
        mock_schema_session.return_value = MagicMock()  # Prevent 'NoneType' error

        # Mock the cart response
        mock_get_cart.return_value = {"carts": {1: [{"model_num": 1, "quantity": 2}, {"model_num": 2, "quantity": 1}]}, "total_price": 150.0}

        # Mock the user response
        mock_get_user.return_value = {"user_name": "John Doe", "email": "johndoe@example.com"}

        # Mock order creation
        mock_add_order.return_value = 1001  # Simulated order ID

        # Mock payment processing
        self.mock_payment_strategy.process_payment.return_value = True

        # Mock `get_cart_item_full_details` to return a valid object
        mock_get_cart_item_details.side_effect = lambda model_num: {model_num: {"stock_quantity": 10, "discount": 0.1}}  # Simulating real structure

        # Execute checkout
        result = self.checkout_service.checkout(user_id=1, address="123 Main St")

        # Assertions
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["order_id"], 1001)
        self.assertEqual(result["message"], "Order placed successfully.")

        # Ensure inventory update was called
        mock_update_inventory.assert_called()

    def test_checkout_empty_cart(self) -> None:
        """Test checkout fails when the cart is empty."""
        self.mock_cart_controller.get_cart.return_value = MagicMock(items=[])

        with self.assertRaises(HTTPException) as context:
            self.checkout_service.checkout(user_id=1, address="123 Main St")

        # Check that the raised exception is a 404 error
        self.assertEqual(context.exception.code, 404)
        self.assertIn("Cart for user 1 is empty", str(context.exception.description))

    @patch("flask.abort")
    def test_checkout_out_of_stock(self, mock_abort) -> None:
        """Test checkout fails when an item is out of stock."""
        # Mock flask.abort to simulate a CONFLICT (409) error
        http_exception = HTTPException(description="Not enough stock available.")
        http_exception.response = MagicMock(status_code=409)  # Manually set the response status
        mock_abort.side_effect = http_exception

        # Mock dependencies
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2)]
        self.mock_cart_controller.get_cart.return_value = mock_cart
        self.mock_inventory_controller.is_item_available.return_value = False  # Simulating out-of-stock condition

        # Expect HTTPException instead of OutOfStockError
        with self.assertRaises(HTTPException) as context:
            self.checkout_service.checkout(user_id=1, address="123 Main St")

        # Assert the correct HTTP status code and message
        self.assertEqual(context.exception.response.status_code, 409)  # HTTPStatus.CONFLICT
        self.assertIn("Not enough stock available", str(context.exception.description))

    @patch("flask.abort")
    def test_checkout_payment_failure(self, mock_abort) -> None:
        """Test checkout fails when payment is declined."""
        # Mock flask.abort to simulate a PAYMENT_REQUIRED (402) error
        http_exception = HTTPException(description="Payment was declined. Please try another payment method.")
        http_exception.response = MagicMock(status_code=402)  # Manually set the response status
        mock_abort.side_effect = http_exception

        # Mock dependencies
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2)]
        mock_cart.calculate_total.return_value = 150.0
        self.mock_cart_controller.get_cart.return_value = mock_cart
        self.mock_inventory_controller.is_item_available.return_value = True
        self.mock_user_controller.get_user.return_value = MagicMock()

        self.mock_payment_strategy.process_payment.return_value = False  # Simulating payment failure

        # Expect HTTPException instead of PaymentFailedError
        with self.assertRaises(HTTPException) as context:
            self.checkout_service.checkout(user_id=1, address="123 Main St")

        # Assert the correct HTTP status code and message
        self.assertEqual(context.exception.response.status_code, 402)  # HTTPStatus.PAYMENT_REQUIRED
        self.assertIn("Payment was declined", str(context.exception.description))

    @patch("flask.abort")
    def test_checkout_missing_user(self, mock_abort) -> None:
        """Test checkout fails when user details are missing."""
        # Mock flask.abort to simulate a NOT_FOUND error
        http_exception = HTTPException(description="User not found")
        http_exception.response = MagicMock(status_code=404)  # Manually set the response status
        mock_abort.side_effect = http_exception

        # Mock dependencies
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2)]
        mock_cart.calculate_total.return_value = 150.0
        self.mock_cart_controller.get_cart.return_value = mock_cart
        self.mock_inventory_controller.is_item_available.return_value = True
        self.mock_payment_strategy.process_payment.return_value = True
        self.mock_user_controller.get_user.return_value = None  # Simulating missing user

        # Expect HTTPException instead of UserNotFoundError
        with self.assertRaises(HTTPException) as context:
            self.checkout_service.checkout(user_id=1, address="123 Main St")

        # Assert the correct HTTP status code and message
        self.assertEqual(context.exception.response.status_code, 404)
        self.assertIn("User not found", str(context.exception.description))

    @patch("flask.abort")
    def test_checkout_order_creation_failure(self, mock_abort) -> None:
        """Test checkout fails when order creation fails."""
        # Mock flask.abort to simulate INTERNAL_SERVER_ERROR (500)
        http_exception = HTTPException(description="Failed to create order.")
        http_exception.response = MagicMock(status_code=500)  # Manually set the response status
        mock_abort.side_effect = http_exception

        # Mock dependencies
        mock_cart = MagicMock()
        mock_cart.items = [MockItem(1, 2)]
        mock_cart.calculate_total.return_value = 150.0
        self.mock_cart_controller.get_cart.return_value = mock_cart
        self.mock_inventory_controller.is_item_available.return_value = True
        self.mock_payment_strategy.process_payment.return_value = True
        self.mock_user_controller.get_user.return_value = MagicMock()

        self.mock_order_controller.create_order.return_value = None  # Simulating order creation failure

        # Expect HTTPException instead of OrderCreationError
        with self.assertRaises(HTTPException) as context:
            self.checkout_service.checkout(user_id=1, address="123 Main St")

        # Assert the correct HTTP status code and message
        self.assertEqual(context.exception.response.status_code, 500)
        self.assertIn("Failed to create order", str(context.exception.description))

    @patch("flask.abort")
    def test_checkout_invalid_address(self, mock_abort) -> None:
        """Test checkout fails when an invalid address is provided."""
        # Set up mock behavior
        http_exception = HTTPException(description="Invalid address. Please provide a valid shipping address.")
        http_exception.response = MagicMock(status_code=411)  # Manually set the response status
        mock_abort.side_effect = http_exception

        # Execute checkout with an invalid address
        with self.assertRaises(HTTPException) as context:
            self.checkout_service.checkout(user_id=1, address="")

        # Assert that the correct HTTP status and message are returned
        self.assertEqual(context.exception.response.status_code, 411)  # Use `.response.status_code`
        self.assertIn("Invalid address", str(context.exception.description))

    @patch("schema.session")  # Mock database session
    @patch("source.controller.cart.delete_cart_item")  # Mock delete_cart_item function
    @patch("source.controller.cart.system_get_all_user_cart_items")  # Mock getting cart items
    @patch("source.controller.user.get_user_details")  # Mock getting user details
    @patch("source.controller.order.add_order")  # Mock order creation
    @patch("source.controller.furniture_inventory.system_update_item_quantity")  # Mock inventory update
    @patch("source.controller.cart.get_cart_item_full_details")  # FIX: Mock get_cart_item_full_details
    def test_cart_items_deleted_after_checkout(
        self,
        mock_get_cart_item_details,
        mock_update_inventory,
        mock_add_order,
        mock_get_user,
        mock_get_cart,
        mock_delete_cart_item,
        mock_schema_session,
    ) -> None:
        """Test that all cart items are deleted after successful checkout."""

        # Mock the database session
        mock_schema_session.return_value = MagicMock()

        # Mock cart contents
        mock_get_cart.return_value = {"carts": {1: [{"model_num": 1, "quantity": 2}, {"model_num": 2, "quantity": 1}]}, "total_price": 150.0}

        # Mock user details
        mock_get_user.return_value = {"user_name": "John Doe", "email": "johndoe@example.com"}

        # Mock order creation success
        mock_add_order.return_value = 1001  # Simulated order ID

        # Mock successful payment processing
        self.mock_payment_strategy.process_payment.return_value = True

        # FIX: Properly mock get_cart_item_full_details to return expected structure
        mock_get_cart_item_details.side_effect = lambda model_num: {model_num: {"stock_quantity": 10, "discount": 0.1}}

        # Perform checkout
        result = self.checkout_service.checkout(user_id=1, address="123 Main St")

        # Assertions
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["order_id"], 1001)
        self.assertEqual(result["message"], "Order placed successfully.")

        # Verify that delete_cart_item was called twice (once per item in cart)
        self.assertEqual(mock_delete_cart_item.call_count, 2)

        # Ensure delete_cart_item was called with correct parameters
        mock_delete_cart_item.assert_any_call(mock_schema_session.return_value, {'user_id': 1, 'model_num': 1})
        mock_delete_cart_item.assert_any_call(mock_schema_session.return_value, {'user_id': 1, 'model_num': 2})

    def tearDown(self) -> None:
        """Stop all patches after tests."""
        self.cart_patch.stop()
        self.user_patch.stop()
        self.order_patch.stop()
        self.inventory_patch.stop()


if __name__ == '__main__':
    unittest.main()
