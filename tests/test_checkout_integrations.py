import source.controller.checkout_service as checkout
from datetime import datetime
import app
import schema
import http
from werkzeug.security import generate_password_hash
import pytest
from unittest.mock import patch
from source.controller.cart import system_get_all_user_cart_items, get_cart_item_full_details
from source.controller.payment_gateway import PaymentMethod, CreditCardPayment, MockPaymentGateway
from source.models.OrderStatus import OrderStatus


@pytest.fixture
def application():
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

    user_1 = schema.User(
        user_id=1002,
        user_name="JaneSmith",
        user_full_name="Jane Smith",
        user_phone_num="555-1234",
        address="456 Oak Avenue, New York, NY",
        email="janesmith@example.com",
        password=generate_password_hash("mypassword456"),
        role="user",
    )

    user_2 = schema.User(
        user_id=1003,
        user_name="MichaelBrown",
        user_full_name="Michael Brown",
        user_phone_num="555-5678",
        address="789 Maple Street, Los Angeles, CA",
        email="michaelbrown@example.com",
        password=generate_password_hash("brownieM123"),
        role="user",
    )

    user_3 = schema.User(
        user_id=1004,
        user_name="EmilyDavis",
        user_full_name="Emily Davis",
        user_phone_num="555-9012",
        address="101 Pine Road, Austin, TX",
        email="emilydavis@example.com",
        password=generate_password_hash("davisEmily!"),
        role="user",
    )

    user_4 = schema.User(
        user_id=1005,
        user_name="RobertWilson",
        user_full_name="Robert Wilson",
        user_phone_num="555-3456",
        address="202 Birch Lane, Seattle, WA",
        email="robertwilson@example.com",
        password=generate_password_hash("wilsonRob007"),
        role="admin",
    )

    cart_item1 = schema.CartItem(user_id=1002, model_num='chair-0', quantity=2)
    cart_item2 = schema.CartItem(user_id=1003, model_num='BS-4004', quantity=2)
    cart_item3 = schema.CartItem(user_id=1002, model_num='SF-3003', quantity=1)
    cart_item4 = schema.CartItem(user_id=1004, model_num='BD-5005', quantity=1)

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

    session.add_all(
        [chair0, chair1, bed, bookshelf, sofa, user_1, user_2, user_3, user_4, cart_item1, cart_item2, cart_item3, cart_item4, order1, order2]
    )
    session.commit()
    yield


@pytest.mark.parametrize(
    "attribute, expected_output",
    [
        ("cart", {'chair-0': 2, "SF-3003": 1}),
        ("total_price", 1510.4),
        (
            "user",
            {
                'user_id': 1002,
                'role': 'user',
                'user_name': "JaneSmith",
                'user_full_name': "Jane Smith",
                'user_phone_num': "555-1234",
                'address': "456 Oak Avenue, New York, NY",
                'email': "janesmith@example.com",
            },
        ),
        ("order_id", 3),
    ],
)
def test_checkout_process(client, attribute, expected_output):
    with patch.object(MockPaymentGateway, 'charge', return_value=True):
        checkout1 = checkout.CheckoutService(payment_strategy=CreditCardPayment())
        user_id = 1002
        address = "Even Gabirol 3, Tel Aviv"
        checkout1.checkout(user_id, address)

        assert getattr(checkout1, attribute) == expected_output


def test_quantity_update(client):
    """Test that the quantity in inventory is updated"""
    user_id = 1004
    address = "Even Gabirol 5, Tel Aviv"

    # check current inventory stock for items in cart
    items = {}
    cart_items = system_get_all_user_cart_items(user_id=user_id)
    user_cart = cart_items['carts'].get(user_id, [])  # Get user cart safely
    for item in user_cart:  # Iterate through all cart items
        items[item['model_num']] = item['quantity']

    stock_quantity = {}
    for key, value in items.items():
        stock_quantity[key] = get_cart_item_full_details(key)[key]['stock_quantity']

    with patch.object(MockPaymentGateway, 'charge', return_value=True):
        checkout1 = checkout.CheckoutService(payment_strategy=CreditCardPayment())
        checkout1.checkout(user_id, address)

        for key, value in items.items():
            assert get_cart_item_full_details(key)[key]['stock_quantity'] == stock_quantity[key] - checkout1.cart[key]


# TODO: move to tests app - after fixing order
def test_checkout_validate_cart_out_of_stock(client):
    """Test that validate_cart raises an HTTP 409 error when an item is out of stock."""
    user_id = 1003  # User not exists
    address = "Even Gabirol 3, Tel Aviv"

    response = client.post(f"/checkout", json={'user_id': user_id, "address": address, 'payment_method': PaymentMethod.CREDIT_CARD.value})
    assert response.status_code == 409


def test_order_creation(client):
    """Test that checkout process creates a valid order in order table"""
    user_id = 1004
    address = "Even Gabirol 3, Tel Aviv"

    # ensure checkout process was successful
    with patch.object(MockPaymentGateway, 'charge', return_value=True):

        response = client.post(f"/checkout", json={'user_id': user_id, "address": address, 'payment_method': PaymentMethod.CREDIT_CARD.value})
        assert response.status_code == http.HTTPStatus.OK
        data = response.get_json()
        created_order_num = data['order_id']

        # Authenticate as an admin to access detailed user data for verification.
        login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
        response = client.post('/login', json=login_info)
        assert response.status_code == http.HTTPStatus.OK

        response = client.get('/orders', query_string={"order_num": created_order_num})
        assert response.status_code == http.HTTPStatus.OK
        data = response.get_json()
        orders = data['orders']
        assert len(orders) == 1
        assert orders[str(created_order_num)]['user_id'] == 1004
        assert orders[str(created_order_num)]['shipping_address'] == address
        assert orders[str(created_order_num)]['items'] == {'BD-5005': 1}
        assert orders[str(created_order_num)]['total_price'] == 1274.4


def test_empty_cart_after_checkout(client):
    """Test that checkout process creates a valid order in order table"""
    login_info = {"user_name": "EmilyDavis", "password": "davisEmily!"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    user_id = 1004
    address = "Even Gabirol 3, Tel Aviv"

    # ensure checkout process was successful
    with patch.object(MockPaymentGateway, 'charge', return_value=True):
        response = client.post(f"/checkout", json={'user_id': user_id, "address": address, 'payment_method': PaymentMethod.CREDIT_CARD.value})
        assert response.status_code == http.HTTPStatus.OK
        data = response.get_json()

    response = client.get('/carts', query_string={"user_id": 1004})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    cart = data['carts']
    assert cart == {}
