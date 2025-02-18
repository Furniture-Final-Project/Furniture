from typing import Dict, Any
from source.models.checkout import Checkout
# from source.models.order import Order
from source.services.payment_gateway import MockPaymentGateway

try:
    from source.models.order import Order  # Try importing Order
except ImportError:
    class Order:  # Temporary Mock Class
        pass

class CheckoutService:
    def __init__(self, cart_manager, inventory_manager, order_manager, user_manager,order_class=None):
        """
        Handles the checkout process.
        """
        self.cart_manager = cart_manager
        self.inventory_manager = inventory_manager
        self.order_manager = order_manager
        self.user_manager = user_manager
        self.payment_gateway = MockPaymentGateway()
        self.order_class = order_class  # ✅ Inject Order class as a dependency

    def validate_cart(self, user_id: int) -> bool:
        """Checks if all items in the cart are available in inventory."""
        cart = self.cart_manager.get_cart(user_id)

        if not cart.items:
            print(f"❌ Cart for user {user_id} is empty!")
            return False  # ✅ Return False instead of a dictionary

        for item in cart.items:
            if not self.inventory_manager.is_item_available(item.item_id, item.quantity):
                print(f"❌ Item '{item.name}' is out of stock!")
                return False  # ✅ Return False if an item is unavailable

        return True  # ✅ Return True if cart is valid


    def process_payment(self, user_id: int, amount: float, payment_method: str) -> bool:
        """Handles mock payment processing."""
        return self.payment_gateway.charge(user_id, amount, payment_method)

    def finalize_checkout(self, user_id: int, address: str, payment_method: str) -> dict:
        """Completes the checkout process."""
        # Step 1: Validate Cart
        cart = self.cart_manager.get_cart(user_id)
        
        if not cart.items:
            return {"status": "error", "message": "Cart is empty"}  # ✅ Specific message

        for item in cart.items:
            if not self.inventory_manager.is_item_available(item.item_id, item.quantity):
                return {"status": "error", "message": f"Item '{item.name}' is out of stock"}  # ✅ Specific message

        # Step 2: Calculate Total Cost
        total_amount = cart.calculate_total()

        # Step 3: Process Payment
        payment_success = self.process_payment(user_id, total_amount, payment_method)
        if not payment_success:
            return {"status": "error", "message": "Payment was declined. Please try another payment method."}

        # Step 4: Fetch User Details
        user = self.user_manager.get_user(user_id)
        if not user:
            return {"status": "error", "message": "User not found"}

        # Step 5: Create an Order
        order_id = self.order_manager.create_order(user_id, cart.items, total_amount, address)
        if not order_id:
            return {"status": "error", "message": "Failed to create order"}

        order = self.order_class(
            order_id=order_id,
            customer_name=user.name,
            phone=user.phone,
            username=user.username,
            email=user.email,
            shipping_address=address,
            items=cart.items,
            total_price=total_amount
        )

        # Step 6: Update Inventory
        for item in cart.items:
            self.inventory_manager.update_stock(item.item_id, item.quantity)

        return {"status": "success", "order_id": order_id, "message": "Order placed successfully"}

