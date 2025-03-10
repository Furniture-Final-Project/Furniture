from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from datetime import datetime
from source.controller.order import add_order
import pytest
import functools
import schema
from source.models.OrderStatus import OrderStatus


@pytest.fixture(autouse=True)
def bypass_admin_required(monkeypatch):
    """
    Automatically bypass the admin_required decorator for testing.

    This fixture defines a dummy decorator that simply calls the original function,
    effectively bypassing admin authentication. It then patches the app's admin_required
    decorator with this dummy version before any routes are created.
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
    Automatically bypass the login_required decorator for testing.

    Similar to bypass_admin_required, this fixture defines a dummy decorator
    that ignores the login check and directly calls the decorated function.
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
    import app

    application = app.create_app({'database_url': f'sqlite:///:memory:'})  # Use in-memory DB for testing
    yield application


@pytest.fixture
def client(application):
    with application.test_client() as client:
        yield client


@pytest.fixture
def test_db(application):
    import schema

    # Use the application's database session or create a new one
    session = schema.session()
    yield session
    session.close()


@pytest.fixture(autouse=True)
def preprepared_data(application):
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

    session.add_all([order1, order2])
    session.commit()
    yield


def test_create_order_object(test_db):
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


def test_add_order_invalid(client):
    """
    Test Invalid order can not be created in the table.
    The order is invalid since the dict is empty.
    """
    order_data = {
        "user_id": 2,
        "items": {},  # Invalid: empty dict
        "user_email": "test2@example.com",
        "user_name": "Jane Doe",
        "shipping_address": "456 Test Avenue",
        "total_price": 75.00,
    }

    # Send request to API endpoint
    response = client.post("/orders", json=order_data)

    # Ensure the correct error message is returned
    assert response.status_code == 405

    # Ensure order was not added to the database
    session = schema.session()
    added_order = session.query(schema.Order).filter_by(user_id=2).first()
    assert added_order is None


def test_add_order_to_table():
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
    """Test order with a negative price."""
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
    Test the valid() function of CartItem.
    It should return True only if both the user and item exist.
    """
    cart_item = schema.CartItem(user_id=9999, model_num="chair-10", quantity=1)

    with (
        patch("source.controller.user.get_user_details", return_value=user_exists),
        patch("source.controller.cart.get_cart_item_full_details", return_value=item_exists),
    ):
        is_valid = cart_item.valid()

    assert is_valid == expected


# def test_order_cancel(client):
#     """
#     Test that when order is cancelled the function to restore the inventory will be called
#     :param test_db:
#     """
#     schema.Order.new.assert_called_once_with(**order_data)


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
