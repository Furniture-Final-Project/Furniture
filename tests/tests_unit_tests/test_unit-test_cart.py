import pytest
import functools
import http
import schema

# import source.controller.cart as cart
from unittest.mock import patch

# from werkzeug.security import check_password_hash, generate_password_hash
# from source.models.OrderStatus import OrderStatus
# from datetime import datetime


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


@pytest.fixture(autouse=True)
def preprepared_data(application):
    session = schema.session()
    chair0 = schema.Furniture(
        model_num='chair-0',
        model_name='Yosef',
        description='a nice chair',
        price=100.0,
        dimensions={"height": 90, "width": 45, "depth": 50},
        category="Chair",
        image_filename='classic_wooden_chair.jpg',
        stock_quantity=3,
        discount=0.0,
        details={'material': 'wood', 'weight': 5, 'color': 'white'},
    )
    chair1 = schema.Furniture(
        model_num='chair-1',
        model_name='Haim',
        description='a Very nice chair',
        price=200.0,
        dimensions={"height": 90, "width": 45, "depth": 50},
        category="Chair",
        image_filename='classic_wooden_chair.jpg',
        stock_quantity=4,
        discount=0.0,
        details={'material': 'wood', 'weight': 6, 'color': 'white'},
    )
    bed = schema.Furniture(
        model_num="BD-5005",
        model_name="DreamComfort",
        description="A luxurious memory foam bed with a sturdy solid wood frame.",
        price=1200.0,
        dimensions={"height": 50, "width": 160, "depth": 200},
        category="Bed",
        image_filename="memory_foam_bed.jpg",
        stock_quantity=5,
        discount=10.0,
        details={"mattress_type": "Memory Foam", "frame_material": "Solid Wood"},
    )
    bookshelf = schema.Furniture(
        model_num="BS-4004",
        model_name="OakElegance",
        description="A stylish and durable bookshelf made of pine wood with a natural oak finish.",
        price=110.0,
        dimensions={"height": 180, "width": 80, "depth": 30},
        category="BookShelf",
        image_filename="oak_bookshelf.jpg",
        stock_quantity=0,
        discount=50.0,
        details={"num_shelves": 5, "max_capacity_weight_per_shelf": 20.0, "material": "Pine Wood", "color": "Natural Oak"},
    )
    sofa = schema.Furniture(
        model_num="SF-3003",
        model_name="LuxComfort",
        description="A luxurious three-seater sofa with top-grain leather upholstery, perfect for a modern living room.",
        price=1200.0,
        dimensions={"height": 85, "width": 220, "depth": 95},
        category="Sofa",
        image_filename="luxury_leather_sofa.jpg",
        stock_quantity=5,
        discount=10.0,
        details={"upholstery": "Top-Grain Leather", "color": "Dark Gray", "num_seats": 3},
    )
    cart_item1 = schema.CartItem(user_id=1002, model_num='chair-0', quantity=2)
    cart_item2 = schema.CartItem(user_id=1003, model_num='BS-4004', quantity=2)
    cart_item3 = schema.CartItem(user_id=1002, model_num='SF-3003', quantity=1)

    session.add_all([chair0, chair1, bed, bookshelf, sofa, cart_item1, cart_item2, cart_item3])
    session.commit()
    yield


def test_update_quantity_with_item_not_in_cart(client):
    """
    Tests that updating a cart item fails if the item is not in the user's cart.

    Steps:
    - Sends a POST request to update the quantity of an item that is not in the cart.
    - Verifies that the response status is 404 NOT FOUND.
    """
    update_info = dict(model_num="chair-0", user_id=1004, quantity=1)

    response = client.post('/user/update_cart_item_quantity', json=update_info)
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    "user_exists, item_exists, expected",
    [
        (True, True, True),  # Both user and item exist, expecting success.
        (False, True, False),  # User does not exist, expecting failure.
        (True, False, False),  # Item does not exist, expecting failure.
        (False, False, False),  # Neither user nor item exist, expecting failure.
    ],
)
def test_valid_method_cartitem(user_exists, item_exists, expected):
    """
    Tests the valid() function of CartItem.

    Steps:
    - Mocks the user existence check.
    - Mocks the item existence check.
    - Verifies that valid() returns True only when both user and item exist.
    """
    cart_item = schema.CartItem(user_id=9999, model_num="chair-10", quantity=1)

    with (
        patch("schema.user.get_user_details", return_value=user_exists),
        patch("schema.cart.get_cart_item_full_details", return_value=item_exists),
    ):

        assert cart_item.valid() == expected


def test_update_cart_item_quantity(client):
    """
    Tests updating a cart item quantity and verifies that the price updates accordingly.

    Steps:
    - Sends a POST request to update the quantity of an existing cart item.
    - Mocks the stock availability check.
    - Sends a GET request to verify that the updated quantity and price are reflected correctly.
    """

    update_info = dict(model_num="chair-0", user_id=1002, quantity=4)

    with patch("source.controller.cart.get_cart_item_full_details", return_value={update_info["model_num"]: {"stock_quantity": 5}}):
        response = client.post('/user/update_cart_item_quantity', json=update_info)
        assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item stock update
    response = client.get('/carts', query_string={"user_id": 1002})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    assert data["carts"]["1002"][0]["quantity"] == 1

    assert data["carts"]['1002'] == [
        {'model_name': 'LuxComfort', 'model_num': 'SF-3003', 'price': 1274.4, 'price_per_unit': 1274.4, 'quantity': 1, 'user_id': 1002},
        {'model_name': 'Yosef', 'model_num': 'chair-0', 'price': 472.0, 'price_per_unit': 118.0, 'quantity': 4, 'user_id': 1002},
    ]


def test_updating_cart_item_quantity_to_0(client):
    """
    Tests that updating a cart item quantity to zero removes it from the cart.

    Steps:
    - Ensures the item is in the cart before updating.
    - Sends a POST request to set the quantity to 0.
    - Sends a GET request to confirm that the item has been deleted.
    """

    # Ensure the cart item in the cart
    response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    cart = data['carts']
    assert cart['1002'] == [{'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}]

    # update quantity to 0
    update_info = dict(model_num="chair-0", user_id=1002, quantity=0)
    response = client.post('/user/update_cart_item_quantity', json=update_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item deleted successfully
    response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data['carts'] == {}


def test_cart_get_all_cart_table(client):
    """
    Test retrieving all items in carts.

    Sends a GET request to the '/carts' endpoint to fetch the complete list of shopping cart items.
    Verifies that the response status is HTTP 200 OK. Ensures that all expected items are
    returned, regardless of their stock status.

    The test validates that:
    - The response contains a 'carts' key.
    - The number of unique items is as expected.
    - Each cart item includes necessary details such as user ID, model number, and quantity.
    """
    response = client.get('/admin/carts')
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    carts = data['carts']
    assert len(carts) == 2

    assert carts['1002'] == [
        {'model_name': 'Yosef', 'model_num': 'chair-0', 'price': 236.0, 'price_per_unit': 118.0, 'quantity': 2, 'user_id': 1002},
        {'model_name': 'LuxComfort', 'model_num': 'SF-3003', 'price': 1274.4, 'price_per_unit': 1274.4, 'quantity': 1, 'user_id': 1002},
    ]
    assert carts['1003'] == [
        {'model_name': 'OakElegance', 'model_num': 'BS-4004', 'price': 129.8, 'price_per_unit': 64.9, 'quantity': 2, 'user_id': 1003}
    ]


def test_cart_get_cart_by_userid(client):
    """
    Tests retrieving a cart for a specific user.

    Steps:
    - Sends a GET request with a 'user_id' query parameter.
    - Verifies that the response contains the correct items for the specified user.
    - Ensures that the total price calculation is accurate.
    """

    response = client.get('/carts', query_string={"user_id": 1002})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    cart = data['carts']
    assert len(cart) == 1

    assert cart['1002'] == [
        {'model_name': 'LuxComfort', 'model_num': 'SF-3003', 'price': 1274.4, 'price_per_unit': 1274.4, 'quantity': 1, 'user_id': 1002},
        {'model_name': 'Yosef', 'model_num': 'chair-0', 'price': 236.0, 'price_per_unit': 118.0, 'quantity': 2, 'user_id': 1002},
    ]

    assert data['total_price'] == 1510.4


def test_get_specific_item_in_cart(client):
    """
    Tests retrieving a specific item in the cart by user ID and model number.

    Steps:
    - Sends a GET request to retrieve the cart item.
    - Ensures that the response contains the correct item details.
    """

    response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    cart = data['carts']
    assert len(cart) == 1

    assert cart['1002'] == [{'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}]


def test_delete_cart_item(client):
    """
    Tests deleting a cart item.

    Steps:
    - Ensures the item is in the cart before deletion.
    - Sends a POST request to remove the item.
    - Sends a GET request to confirm that the item has been successfully deleted.
    """

    # Ensure the cart item in the cart
    response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    cart = data['carts']
    assert cart['1002'] == [{'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}]

    delete_item = {'model_num': 'chair-0', 'user_id': 1002}
    # Send a POST request to delete the item
    response = client.post('/user/delete_cart_item', json=delete_item)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item deleted successfully
    response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data['carts'] == {}
