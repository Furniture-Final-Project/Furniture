from typing import Dict, Any
from abc import ABC, abstractmethod
from source.services.payment_gateway import PaymentStrategy


# ✅ Custom Exceptions for structured error handling
class CheckoutError(Exception):
    """Base exception for checkout errors."""

    pass


class CartEmptyError(CheckoutError):
    """Raised when the cart is empty."""

    pass


class OutOfStockError(CheckoutError):
    """Raised when an item is out of stock."""

    pass


class PaymentFailedError(CheckoutError):
    """Raised when a payment transaction fails."""

    pass


class UserNotFoundError(CheckoutError):
    """Raised when a user is not found."""

    pass


class OrderCreationError(CheckoutError):
    """Raised when order creation fails."""

    pass


class InvalidAddressError(CheckoutError):
    """Raised when the provided shipping address is invalid."""

    pass


# ✅ Template Method Pattern for Checkout Process
class CheckoutTemplate(ABC):
    """Abstract class defining the checkout process template."""

    def checkout(self, user_id: int, address: str) -> Dict[str, Any]:
        """
        Executes the checkout process.

        :param user_id: The ID of the user making the purchase.
        :param address: The shipping address for the order.
        :return: A dictionary containing the status and order details.
        """
        try:
            self.validate_cart(user_id)
            self.validate_address(address)
            cart = self.cart_manager.get_cart(user_id)
            total_amount = cart.calculate_total()
            self.process_payment(user_id, total_amount)
            user = self.user_manager.get_user(user_id)
            if not user:
                raise UserNotFoundError("❌ User not found.")
            order_id = self.create_order(user_id, cart, total_amount, address)
            self.update_inventory(cart)
            return {"status": "success", "order_id": order_id, "message": "✅ Order placed successfully."}
        except CheckoutError as e:
            raise e

    @abstractmethod
    def process_payment(self, user_id: int, amount: float) -> None:
        """Handles the payment processing."""
        pass

    @abstractmethod
    def create_order(self, user_id: int, cart: Any, total_price: float, address: str) -> int:
        """Creates an order and returns the order ID."""
        pass

    @abstractmethod
    def update_inventory(self, cart: Any) -> None:
        """Updates the inventory after a successful checkout."""
        pass


# ✅ CheckoutService now implements the template
class CheckoutService(CheckoutTemplate):
    """
    Handles the checkout process, including cart validation, payment processing,
    order creation, and inventory updates.
    """

    def __init__(
        self,
        cart_manager: Any,
        inventory_manager: Any,
        order_manager: Any,
        user_manager: Any,
        payment_strategy: PaymentStrategy,
    ) -> None:
        """
        Initializes the checkout service with necessary managers.

        :param cart_manager: Manages the user's cart operations.
        :param inventory_manager: Handles inventory stock checks.
        :param order_manager: Manages order creation.
        :param user_manager: Manages user-related operations.
        :param payment_strategy: Strategy for handling payment processing.
        """
        self.cart_manager = cart_manager
        self.inventory_manager = inventory_manager
        self.order_manager = order_manager
        self.user_manager = user_manager
        self.payment_strategy = payment_strategy  # ✅ Injected payment strategy

    def validate_cart(self, user_id: int) -> None:
        """Validates that the cart contains items and they are in stock."""
        cart = self.cart_manager.get_cart(user_id)
        if not cart.items:
            raise CartEmptyError(f"❌ Cart for user {user_id} is empty!")

        for item in cart.items:
            if not self.inventory_manager.is_item_available(item.item_id, item.quantity):
                raise OutOfStockError(f"❌ Item '{item.name}' is out of stock!")

    def validate_address(self, address: str) -> None:
        """Ensures the provided shipping address is valid."""
        if not address or len(address.strip()) < 5:
            raise InvalidAddressError("❌ Invalid address. Please provide a valid shipping address.")

    def process_payment(self, user_id: int, amount: float) -> None:
        """Processes the payment via the selected strategy."""
        if not self.payment_strategy.process_payment(user_id, amount):
            raise PaymentFailedError("❌ Payment was declined. Please try another payment method.")

    def create_order(self, user_id: int, cart: Any, total_price: float, address: str) -> int:
        """Creates an order and returns the order ID."""
        order_id = self.order_manager.create_order(user_id, cart.items, total_price, address)
        if not order_id:
            raise OrderCreationError("❌ Failed to create order.")
        return order_id

    def update_inventory(self, cart: Any) -> None:
        """Updates the inventory stock after a successful order."""
        for item in cart.items:
            self.inventory_manager.update_stock(item.item_id, item.quantity)
