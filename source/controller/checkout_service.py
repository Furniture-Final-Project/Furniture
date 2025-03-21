from typing import Dict, Any
import schema
import flask
import http
import source.controller.cart as cart_controller
import source.controller.user as user_controller
import source.controller.order as order_controller
import source.controller.furniture_inventory as furniture_inventory_controller


class CheckoutService:
    """
    Handles the checkout process, including cart validation, payment processing,
    order creation, and inventory updates.
    """

    def __init__(self, payment_strategy: str) -> None:
        """
        Initializes the checkout service with necessary managers.
        param payment_strategy: Strategy for handling payment processing.
        """
        self.cart_control = cart_controller  # Manages the user's cart operations.
        self.inventory_control = furniture_inventory_controller  # Handles inventory stock checks.
        self.order_control = order_controller  # Manages order creation.
        self.user_control = user_controller  # Manages user-related operations.
        self.payment_strategy = payment_strategy  # Injected payment strategy
        self.cart = {}
        self.user = None
        self.order_num = None
        self.total_price = 0

    def checkout(self, user_id: int, address: str) -> Dict[str, Any]:
        """
        Executes the checkout process.

        param user_id: The ID of the user making the purchase.
        param address: The shipping address for the order.
        return: A dictionary containing the status and order details.
        """
        try:
            self.validate_address(address)

            # STEP 1: Retrieve all user cart items
            cart_items = self.cart_control.system_get_all_user_cart_items(user_id)
            user_cart = cart_items['carts'].get(user_id, [])  # Get user cart safely
            for item in user_cart:  # Iterate through all cart items
                self.cart[item['model_num']] = item['quantity']

            # STEP 2: Validate the cart
            self.validate_cart(user_id)

            # STEP 3: Retrieve total price for payment
            self.total_price = cart_items['total_price']

            # STEP 4: Retrieve and validate user
            self.user = self.user_control.get_user_details(user_id)
            if not self.user:
                flask.abort(http.HTTPStatus.NOT_FOUND, "User not found")

            # STEP 5: Process payment
            self.process_payment(user_id, self.total_price)

            # STEP 6: Create order
            self.order_id = self.create_order(user_id, address)

            # STEP 7: Update inventory
            self.update_inventory(self.cart)

            # STEP 8: Empty user cart
            for key, value in self.cart.items():
                self.delete_item_from_cart(key, user_id)

            return dict(status="success", order_id=self.order_id, message="Order placed successfully.")

        except Exception as e:
            raise e

    def validate_cart(self, user_id: int) -> None:
        """
        Validates that the user's cart contains items and that they are in stock.

        Checks if the cart is empty and raises an error if so.
        Ensures each item's requested quantity does not exceed available stock.

        Args:
            user_id (int): The ID of the user.

        Raises:
            HTTPException: If the cart is empty or if stock is insufficient for any item.
        """
        print("testing the cart", self.cart)  # debug
        if not self.cart or self.cart == {}:
            flask.abort(http.HTTPStatus.NOT_FOUND, f"Cart for user {user_id} is empty!")

        for model_num, asked_quantity in self.cart.items():
            item_details = self.cart_control.get_cart_item_full_details(model_num)
            if item_details[model_num]['stock_quantity'] < asked_quantity:
                flask.abort(http.HTTPStatus.CONFLICT, f"Not enough stock available, stock quantity is {item_details[model_num]['stock_quantity']}")

    def validate_address(self, address: str) -> None:
        """
        Validates the provided shipping address.

        Ensures the address is not empty and meets the minimum length requirement.

        Args:
            address (str): The shipping address.

        Raises:
            HTTPException: If the address is missing or too short.
        """
        if not address or len(address.strip()) < 5:
            flask.abort(http.HTTPStatus.LENGTH_REQUIRED, "Invalid address. Please provide a valid shipping address.")

    def process_payment(self, user_id: int, amount: float) -> None:
        """
        Processes the payment using the selected strategy.

        Args:
            user_id (int): The ID of the user making the payment.
            amount (float): The total amount to be charged.

        Raises:
            HTTPException: If the payment is declined.
        """
        if not self.payment_strategy.process_payment(user_id, amount):
            flask.abort(http.HTTPStatus.PAYMENT_REQUIRED, "Payment was declined. Please try another payment method.")

    def create_order(self, user_id: int, address: str) -> int:
        """
        Creates an order for the user and returns the order ID.

        Args:
            user_id (int): The ID of the user placing the order.
            address (str): The shipping address for the order.

        Returns:
            int: The generated order ID.

        Raises:
            HTTPException: If order creation fails.
        """
        s = schema.session()
        data_for_order = {
            'user_id': user_id,
            'items': self.cart,
            'total_price': self.total_price,
            'shipping_address': address,
            'user_name': self.user['user_name'],
            'user_email': self.user['email'],
        }

        # Create the order, will return order id if succeeded
        order_id = self.order_control.add_order(s, data_for_order)

        if not order_id:
            flask.abort(http.HTTPStatus.INTERNAL_SERVER_ERROR, "Failed to create order.")
        return order_id

    def update_inventory(self, cart: Any) -> None:
        """
        Updates inventory stock based on the purchased cart items.

        Args:
            cart (Any): A dictionary mapping item model numbers to purchased quantities.
        """
        for key, val in cart.items():
            self.inventory_control.system_update_item_quantity(key, -val)

    def delete_item_from_cart(self, item: str, user_id: int) -> None:
        """
        Removes a specific item from the user's cart.

        Args:
            item (str): The model number of the item to remove.
            user_id (int): The ID of the user.
        """
        s = schema.session()
        item_data = {'user_id': user_id, 'model_num': item}
        self.cart_control.delete_cart_item(s, item_data)
