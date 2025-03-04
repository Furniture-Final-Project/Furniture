from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
import schema
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from schema import Base
from source.controller.order import add_order


# Create a temporary in-memory SQLite database
@pytest.fixture(scope="function")
def test_db():
    engine = create_engine("sqlite:///:memory:", echo=True)
    TestingSessionLocal = sessionmaker(bind=engine)

    # Create tables
    Base.metadata.create_all(engine)

    # Provide a new session per test
    session = TestingSessionLocal()
    yield session
    session.close()


# def test_create_order_object(test_db):
#     # Sample valid order data
#     order_data = {
#         "user_id": 1,
#         "items": {"chair-1": 2, "table-2": 1},
#         "user_email": "test@example.com",
#         "user_name": "John Doe",
#         "shipping_address": "123 Test Street",
#         "total_price": 150.00,
#     }
#
#     # Call the function to add order
#     add_order(test_db, order_data)
#
#     # Query database to verify the order was added
#     added_order = test_db.query(schema.Order).filter_by(user_id=1).first()
#
#     # Assertions
#     assert added_order is not None
#     assert added_order.user_id == 1
#     assert added_order.total_price == 150.00
#     assert added_order.shipping_address == "123 Test Street"


def test_add_order_invalid(test_db):
    # Sample invalid order data (empty items list)
    order_data = {
        "user_id": 2,
        "items": {},
        "user_email": "test2@example.com",
        "user_name": "Jane Doe",
        "shipping_address": "456 Test Avenue",
        "total_price": 75.00,
    }

    # Expect an exception (Flask abort)
    with pytest.raises(Exception):
        add_order(test_db, order_data)

    # Ensure order was not added
    added_order = test_db.query(schema.Order).filter_by(user_id=2).first()
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


def test_add_order_invalid_items():
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


def test_add_order_negative_price(test_db):
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
        add_order(test_db, order_data)


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


#=====================cart unit tests=========================
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

