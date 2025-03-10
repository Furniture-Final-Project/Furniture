from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime
from source.controller.order import add_order
from werkzeug.security import generate_password_hash
import pytest
import functools
import schema
from source.models.OrderStatus import OrderStatus


@pytest.fixture(autouse=True)
def bypass_admin_required(monkeypatch):
    """
    Bypasses the `admin_required` decorator for testing.

    This fixture replaces the `admin_required` decorator with a dummy function
    that simply calls the original function without performing any authentication checks.
    """

    def dummy_decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    # Import app after defining the dummy decorator to ensure patching is applied
    import app

    monkeypatch.setattr(app, 'admin_required', dummy_decorator)


@pytest.fixture(autouse=True)
def bypass_login_required(monkeypatch):
    """
    Bypasses the `login_required` decorator for testing.

    This fixture replaces the `login_required` decorator with a dummy function
    that allows access to all protected routes during testing.
    """

    def dummy_decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    import app

    monkeypatch.setattr(app, 'login_required', dummy_decorator)


@pytest.fixture
def application():
    """
    Creates a test application instance with an in-memory database.

    This fixture sets up a test environment using an SQLite in-memory database
    to ensure tests are performed in isolation.
    """
    import app

    application = app.create_app({'database_url': f'sqlite:///:memory:'})  # Use in-memory DB for testing
    yield application


@pytest.fixture
def client(application):
    """
    Provides a test client for sending requests to the application.

    This fixture allows API requests to be made without starting a live server.
    """
    with application.test_client() as client:
        yield client


@pytest.fixture
def test_db(application):
    """
    Provides a test database session.

    This fixture ensures that each test uses a fresh database session
    and properly cleans up afterward.
    """
    import schema

    # Use the application's database session or create a new one
    session = schema.session()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def preprepared_data(application):
    """
    Populates the database with predefined test data.

    This fixture preloads the database with sample orders and user information
    to facilitate testing.
    """
    session = schema.session()
    order1 = schema.Order(
        order_num=1,
        user_id=1002,
        user_email="janesmith@example.com",
        shipping_address="123 Main St, Springfield",
        items={"chair-0": 2, "SF-3003": 1},
        total_price=1750.1,
        status=OrderStatus.PENDING,
        creation_time=datetime(2024, 3, 4, 12, 45, 0),
    )

    order2 = schema.Order(
        order_num=2,
        user_id=1003,
        user_email="michaelbrown@example.com",
        shipping_address="789 Maple Street, Los Angeles, CA",
        items={"BS-4004": 1, "SF-3003": 1},
        total_price=2500.0,
        status=OrderStatus.DELIVERED,
        creation_time=datetime(2024, 3, 3, 12, 30, 0),
    )

    user_1 = schema.User(
        user_id=1005,
        user_name="RobertWilson",
        user_full_name="Robert Wilson",
        user_phone_num="555-3456",
        address="202 Birch Lane, Seattle, WA",
        email="robertwilson@example.com",
        password=generate_password_hash("wilsonRob007"),
        role="admin",
    )
    session.add_all([order1, order2, user_1])
    session.commit()
    yield


def test_create_order_object(test_db):
    """
    Tests the creation of an order object and verifies it is correctly stored in the database.

    Steps:
    - Mocks required functions for retrieving user and cart details.
    - Calls `add_order()` with valid order data.
    - Retrieves the created order from the database and verifies its details.
    """
    # Sample valid order data
    order_data = {
        "user_id": 1,
        "items": {"chair-1": 2, "table-2": 1},
        "user_email": "test@example.com",
        "user_name": "John Doe",
        "shipping_address": "123 Test Street",
        "total_price": 150.00,
    }

    dummy_customer = {
        "user_phone_num": "555-1234",
        "user_name": "John Doe",
        "user_full_name": "John Doe",
    }

    with patch("schema.user.get_user_details", return_value=dummy_customer):
        with patch("schema.cart.get_cart_item_full_details", return_value={"dummy_key": "dummy_value"}):
            add_order(test_db, order_data)

            added_order = test_db.query(schema.Order).filter_by(user_id=1).first()

            assert added_order is not None
            assert added_order.user_id == 1
            assert added_order.total_price == 150.00
            assert added_order.shipping_address == "123 Test Street"


def test_add_order_to_table():
    """
    Tests adding a valid order to the database.

    Steps:
    - Mocks the database session and order creation process.
    - Calls `add_order()` and verifies that it was successfully stored.
    """
    # Mock session
    mock_session = MagicMock(spec=Session)

    # Sample valid order data
    order_data = {
        "user_id": 1,
        "items": {"chair-1": 2, "table-2": 1},
        "user_email": "test@example.com",
        "user_name": "John Doe",
        "shipping_address": "123 Test Street",
        "total_price": 150.00,
    }

    # Mock order class method
    schema.Order.new = MagicMock(return_value=MagicMock(valid=lambda: (True, None)))

    # Call the function
    add_order(mock_session, order_data)

    # Assertions
    schema.Order.new.assert_called_once_with(**order_data)  # Ensure Order.new was called
    mock_session.add.assert_called_once()  # Ensure the order was added to session
    mock_session.commit.assert_called_once()  # Ensure the order was committed


def test_add_order_invalid_items(client):
    """
    Tests that an order with missing or invalid items cannot be added.

    Steps:
    - Mocks order validation failure.
    - Attempts to add an invalid order and expects an exception.
    - Ensures that the database session was not modified.
    """

    # Mock session
    mock_session = MagicMock(spec=Session)

    # Sample invalid order data (missing required fields)
    order_data = {
        "user_id": 1,
        "items": {},
        "user_email": "test@example.com",
        "user_name": "John Doe",
        "shipping_address": "123 Test Street",
        "total_price": 150.00,
    }

    # Mock order validation failure
    mock_order = MagicMock(valid=lambda: (False, "Invalid order details"))
    schema.Order.new = MagicMock(return_value=mock_order)

    # Expect Flask abort to be called (bad request)
    with pytest.raises(Exception):  # Adjust based on your Flask abort handling
        add_order(mock_session, order_data)

    # Ensure order was not added or committed
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


def test_add_order_negative_price(client):
    """
    Tests that an order with a negative price cannot be created.

    Steps:
    - Attempts to add an order with a negative total price.
    - Verifies that the function raises an exception.
    """

    order_data = {
        "user_id": 4,
        "items": {"desk-1": 2},
        "user_email": "test@example.com",
        "user_name": "John Doe",
        "shipping_address": "123 Test Street",
        "total_price": -50.00,  # Invalid price
    }

    with pytest.raises(Exception):
        add_order(client, order_data)


@pytest.mark.parametrize(
    "user_exists, item_exists, expected",
    [
        (True, True, True),  # Both user and item exist -> Valid
        (False, True, False),  # User does not exist -> Invalid
        (True, False, False),  # Item does not exist -> Invalid
        (False, False, False),  # Neither user nor item exist -> Invalid
    ],
)
def test_valid_method_cartitem(user_exists, item_exists, expected):
    """
    Tests the `valid()` function of CartItem.

    This function verifies that the `valid()` method returns `True` only when both the user
    and the cart item exist.
    """
    cart_item = schema.CartItem(user_id=9999, model_num="chair-10", quantity=1)

    with (
        patch("source.controller.user.get_user_details", return_value=user_exists),
        patch("source.controller.cart.get_cart_item_full_details", return_value=item_exists),
    ):
        is_valid = cart_item.valid()

    assert is_valid == expected


# def test_order_cancel():
#     # Mock session and order
#     mock_session = MagicMock()
#     mock_order = MagicMock()
#     mock_order.items = {"model_1": 2, "model_2": 3}
#     mock_session.get.return_value = mock_order
#
#     # Mock system_update_item_quantity function
#     with patch("source.controller.furniture_inventory.system_update_item_quantity") as mock_update_quantity:
#         # Call the function with a cancelled status
#         update_order_status(mock_session, {"order_num": 123, "status": "cancelled"})
#
#         # Assertions
#         assert mock_order.status == OrderStatus.CANCELLED
#         mock_session.commit.assert_called_once()
#         mock_update_quantity.assert_any_call(model_num="model_1", quantity_to_add=2)
#         mock_update_quantity.assert_any_call(model_num="model_2", quantity_to_add=3)


# =====================cart unit tests=========================
# mocking instead of the login process is required

# def test_update_quantity_with_not_enough_units_in_stock(client):
#     """
#     Test that updating a cart item is not possible if the item not in stock or do not have enough units in stock.
#     Expecting an error response.
#     """
#     # TODO: MOCKING -Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed

#     update_info = dict(model_num="chair-0", user_id=1004, quantity=5)

#     with patch("source.controller.cart.get_cart_item_full_details", return_value={update_info["model_num"]: {"stock_quantity": 3}}):
#         response = client.post('/user/add_item_to_cart', json=update_info)
#         assert response.status_code == http.HTTPStatus.CONFLICT


# def test_add_invalid_cart_item(client):
#     """
#     Test adding an item to the cart with a non-existent user ID or non-existent model number.
#     Expecting an error response.
#     """
#     # TODO: MOCKING -Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed

#     cart_item = {"user_id": 9999, "model_num": "chair-1", "quantity": 1}

#     with patch("schema.CartItem.valid", return_value=False):
#         response = client.post('/user/add_item_to_cart', json=cart_item)

#         assert response.status_code == http.HTTPStatus.BAD_REQUEST


# def test_add_item_to_cart_not_enough_units_in_stock(client):
#     """
#     Test  adding item to cart is not possible if the asked quantity is bigger than stock quantity.
#     Expecting an error response.
#     """
#     # TODO: MOCKING -Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed

#     cart_item = {"user_id": 1003, "model_num": "chair-2", "quantity": 2}
#     with patch("source.controller.cart.get_cart_item_full_details", return_value={cart_item["model_num"]: {"stock_quantity": 1}}):
#         response = client.post('/user/add_item_to_cart', json=cart_item)
#         assert response.status_code == http.HTTPStatus.CONFLICT


# def test_add_first_item_to_cart(client):
#     """
#     Test adding new item to a specific cart of a specific user.
#     """
#     # TODO: MOCKING -Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed

#     cart_item = {"user_id": 1003, "model_num": "chair-1", "quantity": 1}

#     # Send a POST request to add the cart for the specific user
#     response = client.post('/user/add_item_to_cart', json=cart_item)
#     data = response.get_json()

#     # Check that the item was added successfully
#     assert response.status_code == http.HTTPStatus.OK

#     # Send a GET request to verify item exists
#     response = client.get('/carts', query_string={"user_id": 1003})
#     data = response.get_json()

#     # Check that the cart is returned correctly
#     assert response.status_code == http.HTTPStatus.OK
#     assert "1003" in data["carts"]
#     assert data["carts"]['1003']['model_num'] == "chair-1"
#     assert data["carts"]['1003']['quantity'] == 1


# def test_order_view_all_orders(client):
#     """
#     Test retrieving all orders in order table.

#     Sends a GET request to the '/order' endpoint to fetch the complete list of orders cart items.
#     Verifies that the response status is HTTP 200 OK.

#     The test validates that:
#     - The response contains a 'order' key.
#     - The number of unique items is as expected.
#     - Each order item includes necessary details such as order ID, user ID, model number, items, .
#     """
#     # TODO: MOCKING
#     # login_info = {"user_name": "JaneSmith", "password": "mypassword456"}

#     response = client.get('/orders')
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     orders = data['orders']
#     assert len(orders) == 2

#     assert orders["1"] == {
#         "order_num": 1,
#         "user_id": 1002,
#         "items": {"chair-0": 2, "SF-3003": 1},
#         "user_email": "janesmith@example.com",
#         "shipping_address": "123 Main St, Springfield",
#         "status": "PENDING",
#         "total_price": 1750.1,
#         "user_name": "JaneSmith",
#         "phone_number": "555-1234",
#         "user_full_name": "Jane Smith",
#         "creation_time": 'Mon, 04 Mar 2024 12:45:00 GMT',
#     }

#     assert orders["2"] == {
#         "order_num": 2,
#         "user_id": 1003,
#         "items": {"BS-4004": 1, "SF-3003": 1},
#         "user_email": "michaelbrown@example.com",
#         "shipping_address": "789 Maple Street, Los Angeles, CA",
#         "status": "DELIVERED",
#         "total_price": 2500.0,
#         "user_name": "MichaelBrown",
#         "phone_number": '555-5678',
#         "user_full_name": "Michael Brown",
#         "creation_time": 'Sun, 03 Mar 2024 12:30:00 GMT',
#     }


# def test_get_order_by_user_id(client):
#     # TODO: MOCKING
#     # login_info = {"user_name": "JaneSmith", "password": "mypassword456"}

#     response = client.get('/orders', query_string={"user_id": 1002})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     orders = data['orders']
#     assert orders == {
#         "1": {
#             "order_num": 1,
#             "user_id": 1002,
#             "items": {"chair-0": 2, "SF-3003": 1},
#             "user_email": "janesmith@example.com",
#             "shipping_address": "123 Main St, Springfield",
#             "status": "PENDING",
#             "total_price": 1750.1,
#             "user_name": "JaneSmith",
#             "phone_number": "555-1234",
#             "user_full_name": "Jane Smith",
#             "creation_time": 'Mon, 04 Mar 2024 12:45:00 GMT',
#         }
#     }


# def test_get_order_by_order_num(client):
#     # TODO: MOCKING
#     # login_info = {"user_name": "JaneSmith", "password": "mypassword456"}

#     response = client.get('/orders', query_string={"order_num": 2})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     orders = data['orders']
#     assert len(orders) == 1
#     assert orders == {
#         "2": {
#             "order_num": 2,
#             "user_id": 1003,
#             "items": {"BS-4004": 1, "SF-3003": 1},
#             "user_email": "michaelbrown@example.com",
#             "shipping_address": "789 Maple Street, Los Angeles, CA",
#             "status": "DELIVERED",
#             "total_price": 2500.0,
#             "user_name": "MichaelBrown",
#             "phone_number": '555-5678',
#             "user_full_name": "Michael Brown",
#             "creation_time": 'Sun, 03 Mar 2024 12:30:00 GMT',
#         }
#     }


# def test_update_order_status(client):
#     # TODO: MOCKING
#     # login_info = {"user_name": "JaneSmith", "password": "mypassword456"}

#     response = client.get('/orders', query_string={"order_num": 1})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     orders = data['orders']
#     assert orders["1"]["status"] == "PENDING"

#     # update order status
#     update_info = dict(order_num=1, status=OrderStatus.SHIPPED.value)  # Convert to string
#     response = client.post('/admin/update_order_status', json=update_info)
#     assert response.status_code == http.HTTPStatus.OK

#     # Send a GET request to verify item stock update
#     response = client.get('/orders', query_string={"order_num": 1})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     orders = data['orders']
#     assert orders["1"]["status"] == "SHIPPED"
