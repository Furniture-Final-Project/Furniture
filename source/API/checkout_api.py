from flask import Flask, request, jsonify

# ✅ Move try-except to the top so mocks exist before usage
try:
    from source.services.checkout_service import CheckoutService
    from source.services.cart_manager import CartManager
    from source.services.inventory_manager import InventoryManager
    from source.services.order_manager import OrderManager
    from source.services.user_manager import UserManager
except ImportError:
    class CartManager:
        def get_cart(self, user_id):
            return None  # Mock response
    
    class InventoryManager:
        def is_item_available(self, item_id, quantity):
            return True  # Mock response
    
    class OrderManager:
        def get_order(self, order_id):
            return None  # Mock response
    
    class UserManager:
        def get_user(self, user_id):
            return None  # Mock response
    
    class CheckoutService:
        def __init__(self, cart_manager, inventory_manager, order_manager, user_manager):
            """Mock constructor to match real CheckoutService"""
            self.cart_manager = cart_manager
            self.inventory_manager = inventory_manager
            self.order_manager = order_manager
            self.user_manager = user_manager
        
        def finalize_checkout(self, user_id, address, payment_method):
            return {"status": "error", "message": "Mock CheckoutService - Not Implemented"}

# ✅ Now all dependencies exist before they are used
app = Flask(__name__)

# Initialize Dependencies
cart_manager = CartManager()
inventory_manager = InventoryManager()
order_manager = OrderManager()
user_manager = UserManager()

# Initialize Checkout Service
checkout_service = CheckoutService(cart_manager, inventory_manager, order_manager, user_manager)

@app.route('/api/checkout', methods=['POST'])
def start_checkout():
    """
    Start the checkout process.
    """
    data = request.get_json(silent=True)  # Handle invalid JSON

    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON format"}), 400

    user_id = data.get("user_id")
    address = data.get("address")
    payment_method = data.get("payment_method")

    if not user_id or not address or not payment_method:
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    # Call the checkout service
    result = checkout_service.finalize_checkout(user_id, address, payment_method)

    # Return response with correct status code
    status_code = 200 if result["status"] == "success" else 400
    return jsonify(result), status_code

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Retrieve order details by order ID.
    """
    order = order_manager.get_order(order_id)

    if not order:
        return jsonify({"status": "error", "message": "Order not found"}), 404

    # Ensure order is a dictionary before returning JSON
    if hasattr(order, "to_dict"):
        order = order.to_dict()

    return jsonify(order), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)