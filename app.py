import flask
import os
from flask import session
from collections import defaultdict
from http import HTTPStatus
from werkzeug.security import check_password_hash
import schema
import source.controller.furniture_inventory as furniture_inventory
import source.controller.user as user
import source.controller.cart as cart
import source.controller.order as order
from decorators import login_required, admin_required
from source.controller.payment_gateway import get_payment_strategy
from source.controller.checkout_service import CheckoutService


def create_app(config: dict=None):
    if config is None:
        config = {}
    app = flask.Flask(__name__)
    app.secret_key = os.urandom(24)

    database_url = config.get('database_url', 'sqlite:///./default.db')
    schema.create(database_url)

    @app.route('/items', methods=['GET'])
    def get_items():
        """
        Retrieves items from the furniture inventory.

        This function allows fetching items with optional filtering based on:
        - `category`: Filters items by category.
        - `max_price`: Returns only items priced below the given value.
        - `model_num`: Retrieves a specific item by model number.

        If `model_num` is provided, the response includes an `is_available` field:
        - `is_available: True` if the item has stock (stock_quantity > 0).
        - `is_available: False` if the item is out of stock (stock_quantity == 0).
        - This field is **only included** when retrieving a single item (`model_num` is specified).

        Returns:
            JSON response containing a dictionary of available items,
            where keys are `model_num` and values are the item's full details.

        Example API Requests:
            - GET /items (retrieves all items)
            - GET /items?category=Chair (retrieves only chairs)
            - GET /items?max_price=500 (retrieves all items under $500)
            - GET /items?model_num=BD-5005 (retrieves a specific item, including `is_available`)

        This implementation ensures that the API response remains clean and context-aware,
        only including stock availability when relevant.
        """
        s = schema.session()
        query = s.query(schema.Furniture)

        category = flask.request.args.get('category')
        price = flask.request.args.get('max_price')
        model_num = flask.request.args.get('model_num')
        model_name = flask.request.args.get('model_name')

        if category is not None:
            query = query.filter_by(category=category)
        if price is not None:
            price = float(price)
            query = query.filter(schema.Furniture.price < price)
        if model_num is not None:
            query = query.filter_by(model_num=model_num)
        if model_name is not None:
            query = query.filter(schema.Furniture.model_name == model_name)

        results = query.all()

        # conditionally add "is_available" only if a specific model_num is requested
        if model_num:
            items = {result.model_num: {**result.to_dict(), "is_available": result.stock_quantity > 0} for result in results}
        else:
            items = {result.model_num: result.to_dict() for result in results}

        return flask.jsonify({'items': items})

    @app.route('/admin/add_item', methods=['POST'])
    @admin_required
    def add_item_endpoint():
        """
        API endpoint to add a new furniture item.
        """
        data = flask.request.get_json()  # Get JSON payload from the request
        s = schema.session()  # create a new session for DB operations
        furniture_inventory.add_item(s, data)  # call add_item from services.py
        return flask.jsonify({})

    @app.route('/admin/update_item', methods=['POST'])
    @admin_required
    def update_item_endpoint():
        """
        API endpoint to add a new furniture item.
        """
        data = flask.request.get_json()  # Get JSON payload from the request
        s = schema.session()  # create a new session for DB operations
        furniture_inventory.update_item_quantity(s, data)  # call add_item from services.py
        return flask.jsonify({})

    @app.route('/admin/delete_item', methods=['POST'])
    @admin_required
    def delete_item_endpoint():
        data = flask.request.get_json()
        s = schema.session()
        furniture_inventory.delete_item(s, data["model_num"])
        return flask.jsonify({})

    @app.route('/admin/update_discount', methods=['POST'])
    @admin_required
    def update_discount_endpoint():
        """
        API endpoint for an admin to update the discount of an existing furniture item.

        Example of an expected payload:
        {
            "model_num": "chair-1",
            "new_discount": 15.0
        }

        Returns:
        - 200 OK if the discount was successfully updated
        - 400 BAD REQUEST if required fields are missing
        - 404 NOT FOUND if the item does not exist
        """
        data = flask.request.get_json()

        if "model_num" not in data or "discount" not in data:
            return flask.jsonify({"error": "Missing required fields"}), HTTPStatus.BAD_REQUEST

        if data["discount"] >= 100 or data["discount"] <= 0:
            return flask.jsonify({"error": "Discount must be between 0 to 100"}), HTTPStatus.BAD_REQUEST

        data = flask.request.get_json()
        s = schema.session()
        furniture_inventory.update_item_discount(s, data)
        return flask.jsonify({})

    # ================ User ====================
    @app.route('/admin/users', methods=['GET'])
    @admin_required
    def get_users():
        s = schema.session()
        query = s.query(schema.User)

        user_id = flask.request.args.get('user_id')
        if user_id is not None:
            user_id = int(user_id)
            query = query.filter(schema.User.user_id == user_id)

        results = query.all()
        users = {result.user_id: result.to_dict() for result in results}
        return flask.jsonify({'users': users})

    @app.route('/add_user', methods=['POST'])
    def add_users():
        """
        API endpoint to add a new user.
        """
        data = flask.request.get_json()
        # Validate required fields
        required_fields = ["user_id", "user_name", "user_full_name", "user_phone_num", "address", "email", "password", "role"]
        role = data.get("role")
        if not all(field in data for field in required_fields) or role != "user":
            return (
                flask.jsonify({"success": False, "message": "Either one or more required fields are missing, or 'role' is not set to 'user'."}),
                HTTPStatus.BAD_REQUEST,
            )

        s = schema.session()
        user.add_new_user(s, data)
        return flask.jsonify({})

    @app.route('/add_admin_user', methods=['POST'])
    def add_admin_users():
        """
        API endpoint to add a new admin user.
        """
        data = flask.request.get_json()
        # Validate required fields
        required_fields = ["user_id", "user_name", "user_full_name", "user_phone_num", "address", "email", "password", "role"]
        role = data.get("role")
        if not all(field in data for field in required_fields) or role != "admin":
            return (
                flask.jsonify({"success": False, "message": "Either one or more required fields are missing, or 'role' is not set to 'admin'."}),
                HTTPStatus.BAD_REQUEST,
            )

        s = schema.session()
        user.add_new_user(s, data)
        return flask.jsonify({})

    @app.route('/update_user', methods=['POST'])
    @login_required
    def update_user_info():
        data = flask.request.get_json()
        s = schema.session()
        address = data.get("address")
        user_name = data.get("user_name")
        email = data.get("email")
        user_full_name = data.get("user_full_name")
        user_phone_num = data.get("user_phone_num")
        password = data.get("password")
        if address is not None:
            user.update_info_address(s, data)
        if user_name is not None:
            user.update_info_user_name(s, data)
        if user_full_name is not None:
            user.update_info_user_full_name(s, data)
        if user_phone_num is not None:
            user.update_info_user_phone_num(s, data)
        if email is not None:
            user.update_info_email(s, data)
        if password is not None:
            user.update_info_password(s, data)
        return flask.jsonify({})

    # ===================login====================
    @app.route('/login', methods=['POST'])
    def login():
        if not flask.request.is_json:
            flask.abort(HTTPStatus.BAD_REQUEST)

        data = flask.request.get_json()
        if not data:
            flask.abort(HTTPStatus.BAD_REQUEST)

        if not isinstance(data, dict):
            flask.abort(HTTPStatus.BAD_REQUEST)

        username = data.get("user_name")
        password = data.get("password")

        if not isinstance(username, str) or not isinstance(password, str):
            flask.abort(HTTPStatus.BAD_REQUEST)

        if not username or not password:
            flask.abort(HTTPStatus.BAD_REQUEST)

        s = schema.session()
        user = s.query(schema.User).filter_by(user_name=username).first()

        if not user:
            flask.abort(HTTPStatus.UNAUTHORIZED)

        if check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            return '', HTTPStatus.OK
        else:
            flask.abort(HTTPStatus.UNAUTHORIZED)

    @app.route('/logout', methods=['POST'])
    def logout():
        session.pop('user_id', None)
        return '', HTTPStatus.OK

    # ============== Shopping Cart ====================
    @app.route('/carts', methods=['GET'])
    def get_cart_items():
        s = schema.session()
        query = s.query(schema.CartItem)

        user_id = flask.request.args.get('user_id')
        model_num = flask.request.args.get('model_num')

        # Apply filtering properly
        if user_id is None:
            flask.abort(HTTPStatus.BAD_REQUEST, description="user ID is missing")

        query = query.filter(schema.CartItem.user_id == user_id)
        if model_num is not None:
            query = query.filter(schema.CartItem.model_num == model_num)

        results = query.all()
        cart_items = defaultdict(list)
        total_price = 0  # Only needed if filtering by user_id

        for result in results:
            cart_items[result.user_id].append(result.to_dict())
            total_price += result.to_dict().get('price', 0)

        s.close()  # Properly close session
        return flask.jsonify({'carts': dict(cart_items), 'total_price': total_price})

    @app.route('/admin/carts', methods=['GET'])
    @admin_required
    def get_all_cart_items():
        s = schema.session()
        query = s.query(schema.CartItem)
        results = query.all()
        cart_items = defaultdict(list)
        for result in results:
            cart_items[result.user_id].append(result.to_dict())
        return flask.jsonify({'carts': dict(cart_items)})

    @app.route('/user/add_item_to_cart', methods=['POST'])
    @login_required
    def add_cart_item_endpoint():
        """
        API endpoint to add a new item to cart for a user - will be called when the user will add the first item to the cart.
        """
        data = flask.request.get_json()  # Get JSON payload from the request
        s = schema.session()  # create a new session for DB operations
        cart.add_cart_item(s, data)  # call add_item from cart.py
        return flask.jsonify({})

    @app.route('/user/update_cart_item_quantity', methods=['POST'])
    @login_required
    def update_cart_item_endpoint():
        """
        API endpoint to update the item quantity in shopping cart.
        """
        data = flask.request.get_json()  # Get JSON payload from the request
        s = schema.session()  # create a new session for DB operations
        cart.update_cart_item_quantity(s, data)  # call add_item from controller/cart.py
        return flask.jsonify({})

    @app.route('/user/delete_cart_item', methods=['POST'])
    # add login
    def delete_cart_item_endpoint():
        data = flask.request.get_json()
        s = schema.session()
        item_data = {"model_num": data["model_num"], "user_id": data["user_id"]}
        cart.delete_cart_item(s, item_data)
        return flask.jsonify({})

    # ============== Order ====================
    @app.route('/user/orders/<user_id>', methods=['GET'])
    @login_required
    def get_order_items(user_id: int):
        s = schema.session()
        query = s.query(schema.Order)

        order_num = flask.request.args.get('order_num')

        query = query.filter(schema.Order.user_id == user_id)
        if order_num is not None:
            query = query.filter(schema.Order.order_num == order_num)

        # Order by creation_time in descending order
        query = query.order_by(schema.Order.creation_time.desc())

        results = query.all()
        orders = {result.order_num: result.to_dict() for result in results}
        return flask.jsonify({'orders': orders})

    @app.route('/admin/orders', methods=['GET'])
    @admin_required
    def get_order_items_admin():
        s = schema.session()
        query = s.query(schema.Order)

        user_id = flask.request.args.get('user_id')
        order_num = flask.request.args.get('order_num')

        if user_id is not None:
            query = query.filter(schema.Order.user_id == user_id)

        if order_num is not None:
            query = query.filter(schema.Order.order_num == order_num)

        # Order by creation_time in descending order
        query = query.order_by(schema.Order.creation_time.desc())

        results = query.all()
        orders = {result.order_num: result.to_dict() for result in results}
        return flask.jsonify({'orders': orders})

    @app.route('/admin/update_order_status', methods=['POST'])
    @admin_required
    def update_order_status_endpoint():
        """
        API endpoint to update the status of an order.
        """
        data = flask.request.get_json()

        if "status" not in data:
            flask.abort(HTTPStatus.BAD_REQUEST, description="new order status is missing")

        if "order_num" not in data:
            flask.abort(HTTPStatus.BAD_REQUEST, description="order num  is missing")

        s = schema.session()
        order.update_order_status(s, data)
        return flask.jsonify({})

    # -------------checkout---------------
    @app.route('/checkout', methods=['POST'])
    def start_checkout():
        """Handles the checkout process."""
        data = flask.request.get_json(silent=True)
        if not data:
            return flask.jsonify({"status": "error", "message": "Invalid JSON format"}), 400

        user_id = data.get("user_id")
        address = data.get("address")
        payment_method = data.get("payment_method")

        # Convert the string to a PaymentStrategy object
        payment_strategy = get_payment_strategy(payment_method)

        if user_id is None or not address or not payment_method:
            return flask.jsonify({"status": "error", "message": "Missing required fields"}), 400

        # Handle invalid payment method
        if payment_strategy is None:
            return flask.jsonify({"error": "Invalid payment method"}), 400

        checkout = CheckoutService(payment_strategy=payment_strategy)
        result = checkout.checkout(user_id, address)
        return flask.jsonify(result)

    return app
