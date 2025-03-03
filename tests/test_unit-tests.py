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
