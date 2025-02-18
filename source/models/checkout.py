from typing import Optional
# from source.models.order import Order  # Import Order class
try:
    from source.models.order import Order  # Try importing Order
except ImportError:
    class Order:  # Temporary Mock Class
        pass


class Checkout:
    def __init__(self, user_id: int, address: str, payment_method: str):
        """
        Represents a checkout process instance.
        
        :param user_id: The ID of the user making the purchase.
        :param address: Shipping address provided by the user.
        :param payment_method: Selected payment method (e.g., "credit_card").
        """
        self.user_id = user_id
        self.address = address
        self.payment_method = payment_method
        self.order: Optional[Order] = None  # Order instance after successful checkout

    def set_order(self, order: Order) -> None:
        """Assigns an Order object once checkout is completed successfully."""
        self.order = order

