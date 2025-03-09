from datetime import datetime
import pytest
import app
import http
import schema
from unittest.mock import patch
from werkzeug.security import generate_password_hash
from source.models.OrderStatus import OrderStatus

# import source.controller.user as user
from source.controller.payment_gateway import PaymentMethod, MockPaymentGateway

# import source.controller.checkout_service as checkout
from freezegun import freeze_time


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
        stock_quantity=6,
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
        stock_quantity=1,
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
    cart_item2 = schema.CartItem(user_id=1002, model_num='SF-3003', quantity=1)
    cart_item3 = schema.CartItem(user_id=1003, model_num='BS-4004', quantity=1)
    cart_item4 = schema.CartItem(user_id=1003, model_num='BD-5005', quantity=1)
    cart_item5 = schema.CartItem(user_id=1003, model_num='SF-3003', quantity=1)
    cart_item6 = schema.CartItem(user_id=1004, model_num='chair-0', quantity=1)
    cart_item7 = schema.CartItem(user_id=1005, model_num='chair-1', quantity=3)

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
        [
            chair0,
            chair1,
            bed,
            bookshelf,
            sofa,
            user_1,
            user_2,
            user_3,
            user_4,
            cart_item1,
            cart_item2,
            cart_item3,
            cart_item4,
            cart_item5,
            cart_item6,
            cart_item7,
            order1,
            order2,
        ]
    )
    session.commit()
    yield


@freeze_time("2024-03-03 12:30:00")
def test_scenario1(client):
    """
    New User Registration and Purchase Flow
    """
    # STEP 1- The user accesses the website and locates the registration option.
    user_info = {
        "user_id": 1006,
        "user_name": "JohnCohen",
        "user_full_name": "John Cohen",
        "user_phone_num": "555-7824",
        "address": "Rothschild Boulevard 4, Tel Aviv",
        "email": "johncohen@example.com",
        "password": "securepassword123",
        "role": "user",
    }
    response = client.post('/add_user', json=user_info)
    assert response.status_code == http.HTTPStatus.OK

    # The user logs into the newly created account.
    login_info = {"user_name": "JohnCohen", "password": "securepassword123"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # The user browses the catalog, selects a product, and adds it to the shopping cart.
    response = client.post('/user/add_item_to_cart', json={"user_id": 1006, "model_num": "chair-1", "quantity": 1})
    assert response.status_code == http.HTTPStatus.OK

    # The user proceeds to the checkout page, confirms the order, enters a shipping
    # address, and selects a payment method (credit card).
    # The system processes the payment and confirms the order.
    with patch.object(MockPaymentGateway, 'charge', return_value=True):

        response = client.post(
            f"/checkout", json={"user_id": 1006, "address": 'Rothschild Boulevard 4, Tel Aviv', "payment_method": PaymentMethod.CREDIT_CARD.value}
        )
        assert response.status_code == http.HTTPStatus.OK

    data = response.get_json()
    created_order_num = data['order_id']

    # The user retrieves the order status using the order ID and sees that it is marked as "Pending".
    response = client.get('/orders', query_string={"order_num": created_order_num})
    assert response.status_code == http.HTTPStatus.OK

    data = response.get_json()
    orders = data['orders']
    assert len(orders) == 1
    assert orders == {
        str(created_order_num): {
            "order_num": created_order_num,
            "user_id": 1006,
            "items": {"chair-1": 1},
            "user_email": "johncohen@example.com",
            "shipping_address": "Rothschild Boulevard 4, Tel Aviv",
            "status": "PENDING",
            "total_price": 236.0,
            "user_name": "JohnCohen",
            "phone_number": '555-7824',
            "user_full_name": "John Cohen",
            "creation_time": "Sun, 03 Mar 2024 12:30:00 GMT",  # Mocked Time
        }
    }


def test_scenario2(client):
    """
    Guest Browsing and Login Requirement for Checkout
    """
    # The guest user (Jane Smith) accesses the website without logging in.
    # Jane Smith browses product categories and selects an item to add to the cart.
    # The system detects that the user is not logged in and displays a prompt requiring login or registration.

    # 1) Attempt to add item to cart without logging in
    cart_item1 = {"user_id": 1002, "model_num": "BS-4004", "quantity": 1}

    # Send a POST request to add the cart for the specific user
    response = client.post('/user/add_item_to_cart', json=cart_item1)
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED

    # 2) Log in with valid credentials
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # 3) Now that we're logged in, try again
    response = client.post('/user/add_item_to_cart', json=cart_item1)
    assert response.status_code == http.HTTPStatus.OK  # Jane Smith successfully adds items to the cart.

    # Meanwhile ANOTHER USER, named Michael Brown logs into his existicting account.
    login_info = {"user_name": "MichaelBrown", "password": "brownieM123"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Michael Brown browses the catalog, selects the product "BS-4004", and adds it to his cart also.
    response = client.post('/user/add_item_to_cart', json={"user_id": 1003, "model_num": "BS-4004", "quantity": 1})
    assert response.status_code == http.HTTPStatus.OK

    # Michael Brown proceeds to the checkout page, confirms the order and enters the required fields.
    # The system processes the payment and confirms the order.
    with patch.object(MockPaymentGateway, 'charge', return_value=True):
        response = client.post(
            f"/checkout", json={"user_id": 1003, "address": '789 Maple Street, Los Angeles, CA', "payment_method": PaymentMethod.CREDIT_CARD.value}
        )
        assert response.status_code == http.HTTPStatus.OK

    # At this point Michael Brown's order is accepted and BS-4004 quantity drops to 0 -
    # meaning Jane Smith should not have the option to complete the purchase process with this item.

    # Jane Smith  add another item to his cart after logged in
    cart_item2 = {"user_id": 1002, "model_num": "chair-1", "quantity": 1}
    response = client.post('/user/add_item_to_cart', json=cart_item2)
    assert response.status_code == http.HTTPStatus.OK

    # The user proceeds to checkout but finds that one of the selected items is out of stock.
    response = client.post(
        f"/checkout", json={"user_id": 1002, "address": '456 Oak Avenue, New York, NY', "payment_method": PaymentMethod.CREDIT_CARD.value}
    )
    assert response.status_code == 409

    # The user removes the out-of-stock item and completes the checkout process.
    delete_item = {"user_id": 1002, "model_num": "BS-4004", "quantity": 1}
    response = client.post('/user/delete_cart_item', json=delete_item)
    assert response.status_code == http.HTTPStatus.OK

    with patch.object(MockPaymentGateway, 'charge', return_value=True):
        response = client.post(
            f"/checkout", json={"user_id": 1002, "address": '456 Oak Avenue, New York, NY', "payment_method": PaymentMethod.CREDIT_CARD.value}
        )
        assert response.status_code == http.HTTPStatus.OK

@freeze_time("2024-03-05 12:30:00")
def test_scenario3(client):
    """
    Advanced Product Search and Cart Management
    """
    # The user logs into their account.
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK
    
    # The user searches for:
    
    # 1) A table under ₪2000.
    response = client.get('/items', query_string={"category": "Bed", "max_price": 2000.0})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']

    cart_item1 = {"user_id": 1002, "model_num": items['BD-5005']['model_num'], "quantity": 1}
    response = client.post('/user/add_item_to_cart', json=cart_item1)
    assert response.status_code == http.HTTPStatus.OK

    # 2) A sofa using a specific model name.
    response = client.get('/items', query_string={"model_name": "LuxComfort"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']

    cart_item2 = {"user_id": 1002, "model_num": items['SF-3003']['model_num'], "quantity": 1}
    response = client.post('/user/add_item_to_cart', json=cart_item2)
    assert response.status_code == http.HTTPStatus.OK   

    # 3) Two types chairs (filter by category)
    response = client.get('/items', query_string={"category": "Chair"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']

    cart_item3 = {"user_id": 1002, "model_num": items['chair-0']['model_num'], "quantity": 1}
    response = client.post('/user/add_item_to_cart', json=cart_item3)
    assert response.status_code == http.HTTPStatus.OK   

    cart_item4 = {"user_id": 1002, "model_num": items['chair-1']['model_num'], "quantity": 2}
    response = client.post('/user/add_item_to_cart', json=cart_item4)
    assert response.status_code == http.HTTPStatus.OK   

    # The user decides to remove one chair from the cart.
    update_info = dict(model_num="chair-1", user_id=1002, quantity=1)
    response = client.post('/user/update_cart_item_quantity', json=update_info)
    assert response.status_code == http.HTTPStatus.OK

    # The user proceeds to checkout and verifies that the correct items and prices are displayed.
    with patch.object(MockPaymentGateway, 'charge', return_value=True):
        response = client.post(
            f"/checkout", json={"user_id": 1002, "address": '456 Oak Avenue, New York, NY', "payment_method": PaymentMethod.CREDIT_CARD.value}
        )
        assert response.status_code == http.HTTPStatus.OK

    # The user retrieves all of his order statuses using the USER ID.
    response = client.get('/user/orders/1002')
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    orders = data['orders']
    assert len(orders) == 2

    created_order_num = data['order_id']

    assert orders["1"] == {
        "order_num": 1,
        "user_id": 1002,
        "items": {"chair-0": 2, "SF-3003": 1},
        "user_email": "janesmith@example.com",
        "shipping_address": "123 Main St, Springfield",
        "status": "PENDING",
        "total_price": 1750.1,
        "user_name": "JaneSmith",
        "phone_number": "555-1234",
        "user_full_name": "Jane Smith",
        "creation_time": 'Mon, 04 Mar 2024 12:45:00 GMT',
    }

    assert orders[str(created_order_num)] == {
        "order_num": created_order_num,
        "user_id": 1002,
        "items": {"BD-5005": 1, "SF-3003": 1, "chair-0": 1, "chair-1": 1},
        "user_email": "janesmith@example.com",
        "shipping_address": "123 Main St, Springfield",
        "status": "PENDING",
        "total_price": 2460.0,
        "user_name": "JaneSmith",
        "phone_number": "555-1234",
        "user_full_name": "Jane Smith",
        "creation_time": 'Mon, 05 Mar 2024 12:30:00 GMT',
    }



