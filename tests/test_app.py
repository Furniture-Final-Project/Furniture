from datetime import datetime
import pytest
import app
import http
import schema
from unittest.mock import patch
from werkzeug.security import check_password_hash, generate_password_hash
from source.models.OrderStatus import OrderStatus

# import source.controller.user as user
from source.controller.payment_gateway import PaymentMethod


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

    session.add_all([chair0, chair1, bed, bookshelf, sofa, user_1, user_2, user_3, user_4, cart_item1, cart_item2, cart_item3, order1, order2])
    session.commit()
    yield


def test_user_get_all_items(client):
    """
    Tests retrieving all furniture items, including out-of-stock ones.

    Sends a GET request to '/items' and verifies:
    - Response status is 200 OK.
    - The expected number of items is returned.
    - Each item contains the correct details, including model number, name,
      description, price, final price (with tax and discounts), dimensions,
      category, image, stock quantity, discount, and additional details.
    """
    response = client.get('/items')
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert len(items) == 5
    assert items['chair-0'] == {
        'model_num': 'chair-0',
        'model_name': 'Yosef',
        'description': 'a nice chair',
        'price': 100.0,
        'final_price': 118.0,
        'dimensions': {"height": 90, "width": 45, "depth": 50},
        'category': 'Chair',
        'image_filename': "classic_wooden_chair.jpg",
        'stock_quantity': 3,
        'discount': 0.0,
        'details': {'material': 'wood', 'weight': 5, 'color': 'white'},
    }
    assert items['chair-1'] == {
        'model_num': 'chair-1',
        'model_name': 'Haim',
        'description': 'a Very nice chair',
        'price': 200.0,
        'final_price': 236.0,
        'dimensions': {"height": 90, "width": 45, "depth": 50},
        'category': 'Chair',
        'image_filename': "classic_wooden_chair.jpg",
        'stock_quantity': 4,
        'discount': 0.0,
        'details': {'material': 'wood', 'weight': 6, 'color': 'white'},
    }

    assert items['BD-5005'] == {
        'model_num': "BD-5005",
        'model_name': "DreamComfort",
        'description': "A luxurious memory foam bed with a sturdy solid wood frame.",
        'price': 1200.0,
        'final_price': 1274.4,
        'dimensions': {"height": 50, "width": 160, "depth": 200},
        'category': "Bed",
        'image_filename': "memory_foam_bed.jpg",
        'stock_quantity': 5,
        'discount': 10.0,
        'details': {"mattress_type": "Memory Foam", "frame_material": "Solid Wood"},
    }
    assert items["BS-4004"] == {
        'model_num': "BS-4004",
        'model_name': "OakElegance",
        'description': "A stylish and durable bookshelf made of pine wood with a natural oak finish.",
        'price': 110.0,
        'final_price': 64.9,
        'dimensions': {"height": 180, "width": 80, "depth": 30},
        'category': "BookShelf",
        'image_filename': "oak_bookshelf.jpg",
        'stock_quantity': 0,
        'discount': 50.0,
        'details': {"num_shelves": 5, "max_capacity_weight_per_shelf": 20.0, "material": "Pine Wood", "color": "Natural Oak"},
    }
    assert items["SF-3003"] == {
        'model_num': "SF-3003",
        'model_name': "LuxComfort",
        'description': "A luxurious three-seater sofa with top-grain leather upholstery, perfect for a modern living room.",
        'price': 1200.0,
        'final_price': 1274.4,
        'dimensions': {"height": 85, "width": 220, "depth": 95},
        'category': "Sofa",
        'image_filename': "luxury_leather_sofa.jpg",
        'stock_quantity': 5,
        'discount': 10.0,
        'details': {"upholstery": "Top-Grain Leather", "color": "Dark Gray", "num_seats": 3},
    }


def test_single_filter_by_category(client):
    """
    Test retrieving items by category.

    Sends a GET request to '/items' with 'category' as a query parameter.
    Verifies the response status is 200 OK and that the returned items match
    the specified category. Ensures each item's 'stock_quantity' is included
    for inventory status display (e.g., "1 piece left" or "out of stock").
    """
    response = client.get('/items', query_string={"category": "Bed"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert len(items) == 1
    assert items['BD-5005'] == {
        'model_num': "BD-5005",
        'model_name': "DreamComfort",
        'description': "A luxurious memory foam bed with a sturdy solid wood frame.",
        'price': 1200.0,
        'final_price': 1274.4,
        'dimensions': {"height": 50, "width": 160, "depth": 200},
        'category': "Bed",
        'image_filename': "memory_foam_bed.jpg",
        'stock_quantity': 5,
        'discount': 10.0,
        'details': {"mattress_type": "Memory Foam", "frame_material": "Solid Wood"},
    }


def test_single_filter_by_name(client):
    """
    Tests filtering items by category.

    Sends a GET request to '/items' with a 'category' query parameter.
    Verifies that:
    - The response status is 200 OK.
    - The returned items belong to the requested category.
    - Each item includes 'stock_quantity' for inventory status display.
    """
    response = client.get('/items', query_string={"model_name": "LuxComfort"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert len(items) == 1
    assert items['SF-3003'] == {
        'model_num': "SF-3003",
        'model_name': "LuxComfort",
        'description': "A luxurious three-seater sofa with top-grain leather upholstery, perfect for a modern living room.",
        'price': 1200.0,
        'final_price': 1274.4,
        'dimensions': {"height": 85, "width": 220, "depth": 95},
        'category': "Sofa",
        'image_filename': "luxury_leather_sofa.jpg",
        'stock_quantity': 5,
        'discount': 10.0,
        'details': {"upholstery": "Top-Grain Leather", "color": "Dark Gray", "num_seats": 3},
    }


def test_double_filter(client):
    """
    Tests filtering items by category and maximum price.

    Sends a GET request to '/items' with 'category' and 'max_price' as query parameters.
    Verifies that:
    - The response status is 200 OK.
    - Returned items match the specified category.
    - No item exceeds the given maximum price.
    - Each item includes 'stock_quantity' for inventory status display.
    """
    response = client.get('/items', query_string={"category": "Chair", "max_price": 150})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert len(items) == 1
    assert items['chair-0'] == {
        'model_num': 'chair-0',
        'model_name': 'Yosef',
        'description': 'a nice chair',
        'price': 100.0,
        'final_price': 118.0,
        'dimensions': {"height": 90, "width": 45, "depth": 50},
        'category': 'Chair',
        'image_filename': "classic_wooden_chair.jpg",
        'stock_quantity': 3,
        'discount': 0.0,
        'details': {'material': 'wood', 'weight': 5, 'color': 'white'},
    }


def test_get_item_by_model_num_and_verify_availability(client):
    """
    Tests retrieving an item by model number and verifying its availability.

    Sends a GET request to '/items' with a `model_num` query parameter.
    Verifies that:
    - The response status is 200 OK.
    - The correct item details are returned.
    - The `is_available` field correctly reflects stock availability.
    - Discounts and tax calculations are properly applied.
    """

    response = client.get('/items', query_string={"model_num": "BD-5005"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert len(items) == 1
    assert items['BD-5005'] == {
        'model_num': "BD-5005",
        'model_name': "DreamComfort",
        'description': "A luxurious memory foam bed with a sturdy solid wood frame.",
        'price': 1200.0,
        'final_price': 1274.4,
        'dimensions': {"height": 50, "width": 160, "depth": 200},
        'category': "Bed",
        'image_filename': "memory_foam_bed.jpg",
        'stock_quantity': 5,
        'discount': 10.0,
        "is_available": True,
        'details': {"mattress_type": "Memory Foam", "frame_material": "Solid Wood"},
    }


def test_verify_availability_out_of_stock(client):
    """
    Tests that an out-of-stock item is correctly marked as unavailable.

    Sends a GET request to '/items' with a `model_num` query parameter.
    Verifies that:
    - The response status is 200 OK.
    - The correct item details are returned.
    - The `is_available` field is False for an out-of-stock item.
    """

    response = client.get('/items', query_string={"model_num": "BS-4004"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert len(items) == 1
    assert items['BS-4004'] == {
        'model_num': "BS-4004",
        'model_name': "OakElegance",
        'description': "A stylish and durable bookshelf made of pine wood with a natural oak finish.",
        'price': 110.0,
        'final_price': 64.9,
        'dimensions': {"height": 180, "width": 80, "depth": 30},
        'category': "BookShelf",
        'image_filename': "oak_bookshelf.jpg",
        'stock_quantity': 0,
        'discount': 50.0,
        "is_available": False,
        'details': {"num_shelves": 5, "max_capacity_weight_per_shelf": 20.0, "material": "Pine Wood", "color": "Natural Oak"},
    }


def test_add_bed_item(client):
    """
    Tests adding a new bed item via a POST request.

    Steps:
    - Logs in as an admin user.
    - Sends a POST request to add a new bed item.
    - Verifies the response status is 200 OK.
    - Sends a GET request to ensure the item was successfully added.
    - Confirms the item's details and availability.
    """

    new_item = {
        "model_num": "B-101",
        "model_name": "King Bed",
        "description": "A comfortable king-size bed.",
        "price": 1500.0,
        "dimensions": {"width": 180, "length": 200, "height": 50},
        "stock_quantity": 10,
        "details": {"mattress_type": "memory foam", "frame_material": "wood"},
        "image_filename": "king_bed.jpg",
        "discount": 5.0,
        "category": "Bed",
    }

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a POST request to add the item
    response = client.post('/admin/add_item', json=new_item)
    data = response.get_json()

    # Check that the item was added successfully
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item exists
    response = client.get('/items', query_string={"model_num": "B-101"})
    data = response.get_json()

    # Check that the item is returned correctly
    assert response.status_code == http.HTTPStatus.OK
    assert "B-101" in data["items"]
    assert data["items"]["B-101"]["model_name"] == "King Bed"
    assert data["items"]["B-101"]["is_available"] is True


def test_add_bed_item_not_correct_values(client):
    """
    Tests adding a bed item with invalid values.

    Steps:
    - Logs in as an admin user.
    - Sends a POST request with an invalid mattress type.
    - Verifies that the response returns a 400 BAD REQUEST error.
    - Sends a GET request to ensure the invalid item was not added.
    """

    invalid_item = {
        "model_num": "B-999",
        "model_name": "Faulty Bed",
        "description": "This bed has an invalid mattress type.",
        "price": 1200.0,
        "dimensions": {"width": 160, "length": 200, "height": 45},
        "stock_quantity": 5,
        "details": {"mattress_type": "plastic", "frame_material": "wood"},  # Invalid value!
        "image_filename": "faulty_bed.jpg",
        "discount": 0.0,
        "category": "Bed",
    }

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a POST request to add invalid item
    response = client.post('/admin/add_item', json=invalid_item)
    data = response.get_json()
    # Check that the response returns an error
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Send a GET request to verify item exists
    response = client.get('/items', query_string={"model_num": "B-999"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()

    # Check that the item does NOT exist in the database
    assert "B-999" not in data["items"]


def test_add_chair(client):
    """
    Tests adding a new chair item via a POST request.

    Steps:
    - Logs in as an admin user.
    - Sends a POST request to add a new chair item.
    - Verifies the response status is 200 OK.
    - Sends a GET request to ensure the item was successfully added.
    - Confirms the item's details and availability.
    """

    new_item = {
        "model_num": "C-202",
        "model_name": "ErgoChair",
        "description": "An ergonomic office chair with lumbar support.",
        "price": 350.0,
        "dimensions": {"width": 50, "depth": 55, "height": 110},
        "stock_quantity": 8,
        "details": {"material": "fabric", "weight": 12, "color": "black"},  # Chosen from VALID_MATERIALS
        "image_filename": "ergonomic_office_chair.jpg",
        "discount": 10.0,
        "category": "Chair",
    }

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a POST request to add the item
    response = client.post('/admin/add_item', json=new_item)
    data = response.get_json()

    # Check that the item was added successfully
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item exists
    response = client.get('/items', query_string={"model_num": "C-202"})
    data = response.get_json()

    # Check that the item is returned correctly
    assert response.status_code == http.HTTPStatus.OK
    assert "C-202" in data["items"]
    assert data["items"]["C-202"]["model_name"] == "ErgoChair"
    assert data["items"]["C-202"]["is_available"] is True


def test_add_chair_item_not_correct_values(client):
    """
    Tests adding a chair item with invalid values.

    Steps:
    - Logs in as an admin user.
    - Sends a POST request with an invalid material type.
    - Verifies that the response returns a 400 BAD REQUEST error.
    - Sends a GET request to ensure the invalid item was not added.
    """

    invalid_item = {
        "model_num": "C-203",
        "model_name": "ErgoChair",
        "description": "An ergonomic office chair with lumbar support.",
        "price": 350.0,
        "dimensions": {"width": 50, "depth": 55, "height": 110},
        "stock_quantity": 8,
        "details": {"material": "stone", "weight": 12, "color": "white"},  # Invalid value!
        "image_filename": "ergonomic_office_chair.jpg",
        "discount": 10.0,
        "category": "Chair",
    }

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a POST request to add invalid item
    response = client.post('/admin/add_item', json=invalid_item)
    data = response.get_json()
    # Check that the response returns an error
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Send a GET request to verify item exists
    response = client.get('/items', query_string={"model_num": "C-203"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()

    # Check that the item does NOT exist in the database
    assert "C-203" not in data["items"]


def test_add_BookShelf(client):
    """
    Tests adding a new bookshelf item via a POST request.

    Steps:
    - Logs in as an admin user.
    - Sends a POST request to add a new bookshelf item.
    - Verifies the response status is 200 OK.
    - Sends a GET request to ensure the item was successfully added.
    - Confirms the item's details and availability.
    """

    new_item = {
        "model_num": "BS-5001",
        "model_name": "ModernGlassShelf",
        "description": "A sleek, modern bookshelf with tempered glass shelves and a metal frame.",
        "price": 180.0,
        "dimensions": {"width": 90, "depth": 35, "height": 200},
        "stock_quantity": 5,
        "details": {
            "num_shelves": 4,
            "max_capacity_weight_per_shelf": 15.0,
            "material": "glass",  # Chosen from VALID_MATERIALS
            "color": "transparent",
        },
        "image_filename": "modern_glass_bookshelf.jpg",
        "discount": 15.0,
        "category": "Book Shelf",
    }

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a POST request to add the item
    response = client.post('/admin/add_item', json=new_item)
    data = response.get_json()

    # Check that the item was added successfully
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item exists
    response = client.get('/items', query_string={"model_num": "BS-5001"})
    data = response.get_json()

    # Check that the item is returned correctly
    assert response.status_code == http.HTTPStatus.OK
    assert "BS-5001" in data["items"]
    assert data["items"]["BS-5001"]["model_name"] == "ModernGlassShelf"
    assert data["items"]["BS-5001"]["is_available"] is True


def test_add_Bookshelf_item_not_correct_values(client):
    """
    Tests adding a bookshelf item with invalid values via a POST request.

    Steps:
    - Logs in as an admin user.
    - Sends a POST request with invalid data (empty model number, negative price, invalid material).
    - Verifies the response status is 400 BAD REQUEST.
    - Ensures the response contains appropriate error messages for each invalid field.
    """
    # Invalid item data: missing required field, negative price, invalid material
    invalid_item_data = {
        "model_num": "",  # Model number should not be empty
        "model_name": "ModernGlassShelf",
        "description": "A sleek, modern bookshelf with tempered glass shelves and a metal frame.",
        "price": -50.0,  # Invalid price
        "dimensions": {"width": 90, "depth": 35, "height": 200},
        "stock_quantity": 5,
        "details": {
            "num_shelves": 4,
            "max_capacity_weight_per_shelf": 15.0,
            "material": "non_existent_material",  # Invalid material
            "color": "transparent",
        },
        "image_filename": "modern_glass_bookshelf.jpg",
        "discount": 15.0,
        "category": "Book Shelf",
    }

    # Log in as an admin user to enable access to detailed user information
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    login_response = client.post('/login', json=login_info)
    assert login_response.status_code == 200  # Ensure login is successful

    # Send a POST request to add the invalid item to the inventory
    response = client.post('/admin/add_item', json=invalid_item_data)

    # Assert that the response status code is 400 (Bad Request) because the data is invalid
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Check the response body and handle the case where it's None
    data = response.get_json()
    if data:
        assert "error" in data
        assert "model_num" in data["error"]  # Check if 'model_num' is required and not empty
        assert "price" in data["error"]  # Check if price is positive
        assert "material" in data["error"]  # Check if material is valid


def test_add_Sofa(client):
    """
    Tests adding a new sofa item via a POST request.

    Steps:
    - Logs in as an admin user.
    - Sends a POST request to add a new sofa item.
    - Verifies the response status is 200 OK.
    - Sends a GET request to ensure the item was successfully added.
    - Confirms the item's details and availability.
    """

    new_item = {
        "model_num": "SF-5005",
        "model_name": "CozyVelvet",
        "description": "A stylish and comfortable two-seater sofa with plush velvet upholstery, perfect for cozy living spaces.",
        "price": 850.0,
        "dimensions": {"width": 180, "depth": 85, "height": 80},
        "stock_quantity": 7,
        "details": {"upholstery": "velvet", "color": "navy blue", "num_seats": 2},  # Chosen from VALID_UPHOLSTERY_TYPES
        "image_filename": "cozy_velvet_sofa.jpg",
        "discount": 12.0,
        "category": "Sofa",
    }

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a POST request to add the item
    response = client.post('/admin/add_item', json=new_item)
    data = response.get_json()

    # Check that the item was added successfully
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item exists
    response = client.get('/items', query_string={"model_num": "SF-5005"})
    data = response.get_json()

    # Check that the item is returned correctly
    assert response.status_code == http.HTTPStatus.OK
    assert "SF-5005" in data["items"]
    assert data["items"]["SF-5005"]["model_name"] == "CozyVelvet"
    assert data["items"]["SF-5005"]["is_available"] is True


def test_add_Sofa_item_not_correct_values(client):
    """
    Tests adding a sofa item with invalid values via a POST request.

    Steps:
    - Logs in as an admin user.
    - Sends a POST request with invalid data (empty model number, negative price, invalid upholstery).
    - Verifies the response status is 400 BAD REQUEST.
    - Ensures the response contains appropriate error messages for each invalid field.
    """

    # Invalid item data: missing required field, negative price, invalid material
    invalid_item_data = {
        "model_num": "",  # Model number should not be empty
        "model_name": "CozyVelvet",
        "description": "A stylish and comfortable two-seater sofa with plush velvet upholstery, perfect for cozy living spaces.",
        "price": -100.0,  # Invalid price
        "dimensions": {"width": 180, "depth": 85, "height": 80},
        "stock_quantity": 7,
        "details": {
            "upholstery": "non_existent_material",  # Invalid upholstery material
            "color": "navy blue",
            "num_seats": 2,
        },
        "image_filename": "cozy_velvet_sofa.jpg",
        "discount": 12.0,
        "category": "Sofa",
    }

    # Log in as an admin user to enable access to detailed user information
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    login_response = client.post('/login', json=login_info)
    assert login_response.status_code == 200  # Ensure login is successful

    # Send a POST request to add the invalid item to the inventory
    response = client.post('/admin/add_item', json=invalid_item_data)

    # Assert that the response status code is 400 (Bad Request) because the data is invalid
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Check that the error message contains information about the invalid fields
    data = response.get_json()

    # Proceed if the response has data
    if data:
        assert "error" in data
        assert "model_num" in data["error"]  # Check if 'model_num' is required and not empty
        assert "price" in data["error"]  # Check if price is positive
        assert "upholstery" in data["error"]  # Check if upholstery is valid


def test_update_quantity(client):
    """
    Tests updating the stock quantity of an item via a POST request.

    Steps:
    - Logs in as an admin user.
    - Sends a POST request to update the stock quantity of an item.
    - Verifies the response status is 200 OK.
    - Sends a GET request to ensure the stock quantity was updated correctly.
    """

    update_info = {
        "model_num": "chair-0",
        "stock_quantity": 0,
    }

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.post('/admin/update_item', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    # Send a GET request to verify item stock update
    response = client.get('/items', query_string={"model_num": "chair-0"})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["items"]["chair-0"]["stock_quantity"] == 0


def test_delete_item(client):
    """
    Tests deleting an item via a POST request.

    Steps:
    - Logs in as an admin user.
    - Sends a POST request to delete an item by model number.
    - Verifies the response status is 200 OK.
    - Sends a GET request to ensure the item was successfully deleted.
    """

    deleted_item = {"model_num": "chair-1"}
    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK
    # Send a POST request to delete the item
    response = client.post('/admin/delete_item', json=deleted_item)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item deleted successfully
    response = client.get('/items', query_string={"model_num": "chair-1"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data == {'items': {}}


# ============user=============================


def test_get_user_by_id(client):
    """
    Tests retrieving user details by user ID via a GET request.

    Steps:
    - Logs in as an admin user.
    - Sends a GET request to fetch user details by user ID.
    - Verifies the response status is 200 OK.
    - Ensures the returned user details are correct.
    - Confirms the stored password is hashed.
    """

    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/admin/users', query_string={"user_id": 1002})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    users = data['users']
    assert len(users) == 1
    assert users['1002']["user_id"] == 1002
    assert users['1002']["user_name"] == "JaneSmith"
    assert users['1002']["user_full_name"] == "Jane Smith"
    assert users['1002']["user_phone_num"] == "555-1234"
    assert users['1002']["address"] == "456 Oak Avenue, New York, NY"
    assert users['1002']["email"] == "janesmith@example.com"
    assert users['1002']["role"] == "user"
    hashed_password = users['1002']["password"]
    assert hashed_password != "mypassword456"
    assert check_password_hash(hashed_password, "mypassword456")


def test_add_new_user(client):
    """
    Tests adding a new user via a POST request.

    Steps:
    - Sends a POST request to create a new user.
    - Verifies the response status is 200 OK.
    - Logs in as an admin to retrieve user details.
    - Sends a GET request to verify the user was added successfully.
    - Ensures the returned user data matches the expected values.
    """

    user_info = {
        "user_id": 207105880,
        "user_name": "JonCohen",
        "user_full_name": "Jon Cohen",
        "user_phone_num": "555-7824",
        "address": "123 Elm Street, Springfield, IL",
        "email": "johndoe@example.com",
        "password": "securepassword123",
        "role": "user",
    }
    response = client.post('/add_user', json=user_info)
    assert response.status_code == http.HTTPStatus.OK

    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user was asses successfully
    response = client.get('/admin/users', query_string={"user_id": 207105880})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data["users"]['207105880']["user_name"] == "JonCohen"


def test_password_hashing(client):
    """
    Tests that user passwords are securely hashed upon registration.

    Steps:
    - Sends a POST request to create a new user.
    - Verifies the response status is 200 OK.
    - Logs in as an admin to retrieve user details.
    - Sends a GET request to fetch the user's stored password.
    - Ensures the stored password is hashed and does not match the original plaintext password.
    - Verifies that the stored hash correctly matches the original password.
    """

    user_info = {
        "user_id": 67890,
        "user_name": "AliceDoe",
        "user_full_name": "Alice Doe",
        "user_phone_num": "555-8821",
        "address": "789 Oak St, New York, NY",
        "email": "alicedoe@example.com",
        "password": "mypassword123",
        "role": "user",
    }

    response = client.post('/add_user', json=user_info)
    assert response.status_code == http.HTTPStatus.OK

    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/admin/users', query_string={"user_id": 67890})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()

    hashed_password = data["users"]["67890"]["password"]
    assert hashed_password != user_info["password"]
    assert check_password_hash(hashed_password, user_info["password"])


def test_add_existing_user(client):
    """
    Tests that attempting to add an existing user results in a 400 BAD REQUEST error.

    Steps:
    - Sends a POST request to create a user that already exists in the system.
    - Verifies that the response status is 400 BAD REQUEST.
    """

    existing_user = {
        "user_id": 1002,
        "user_name": "JaneSmith",
        "user_full_name": "Jane Smith",
        "user_phone_num": "555-1234",
        "address": "456 Oak Avenue, New York, NY",
        "email": "janesmith@example.com",
        "password": "mypassword456",
        "role": "user",
    }
    response = client.post('/add_user', json=existing_user)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_add_admin_user(client):
    """
    Tests adding a new admin user via a POST request.

    Steps:
    - Sends a POST request to create a new admin user.
    - Verifies the response status is 200 OK.
    - Logs in as an admin to retrieve user details.
    - Sends a GET request to verify the admin user was added successfully.
    - Ensures the returned user data matches the expected values.
    """

    user_info = {
        "user_id": 207105881,
        "user_name": "RonCohen",
        "user_full_name": "Ron Cohen",
        "user_phone_num": "555-7824",
        "address": "120 Elm Street, Springfield, IL",
        "email": "johndoe@example.com",
        "password": "securepassword123",
        "role": "admin",
    }
    response = client.post('/add_admin_user', json=user_info)
    assert response.status_code == http.HTTPStatus.OK

    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user was asses successfully
    response = client.get('/admin/users', query_string={"user_id": 207105881})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data["users"]['207105881']["user_name"] == "RonCohen"


def test_add_admin_user_invalid(client):
    """
    Ensures '/add_admin_user' returns 400 BAD REQUEST if 'role' is 'user',
    and verifies no user is created.
    """
    user_info = {
        "user_id": 207105881,
        "user_name": "RonCohen",
        "user_full_name": "Ron Cohen",
        "user_phone_num": "555-7824",
        "address": "120 Elm Street, Springfield, IL",
        "email": "johndoe@example.com",
        "password": "securepassword123",
        "role": "user",
    }
    response = client.post('/add_admin_user', json=user_info)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user was asses successfully
    response = client.get('/admin/users', query_string={"user_id": 207105881})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data["users"] == {}


def test_add_user_invalid_role(client):
    """
        Ensures '/add_user' returns 400 BAD REQUEST if 'role' is 'admin',
    and verifies no user is created.
    """
    user_info = {
        "user_id": 207105881,
        "user_name": "RonCohen",
        "user_full_name": "Ron Cohen",
        "user_phone_num": "555-7824",
        "address": "120 Elm Street, Springfield, IL",
        "email": "johndoe@example.com",
        "password": "securepassword123",
        "role": "admin",
    }
    response = client.post('/add_user', json=user_info)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST

    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user was asses successfully
    response = client.get('/admin/users', query_string={"user_id": 207105881})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data["users"] == {}


def test_user_update_address(client):
    """
    Tests updating a user's address via a POST request.

    Steps:
    - Logs in as the user who wants to update their address.
    - Sends a POST request to update the address.
    - Verifies the response status is 200 OK.
    - Logs in as an admin to retrieve updated user details.
    - Sends a GET request to verify the address was updated correctly.
    """

    # The user that wants to change its address logs in
    login_info = {"user_name": "MichaelBrown", "password": "brownieM123"}  # user id 1003
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    updated_info = {"user_id": 1003, "address": "21 Yaakov Meridor, Tel Aviv"}
    response = client.post('/update_user', json=updated_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated corretly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["address"] == "21 Yaakov Meridor, Tel Aviv"


def test_user_update_user_name(client):
    """
    Tests updating a user's username via a POST request.

    Steps:
    - Logs in as the user who wants to update their username.
    - Sends a POST request to update the username.
    - Verifies the response status is 200 OK.
    - Logs in as an admin to retrieve updated user details.
    - Sends a GET request to verify the username was updated correctly.
    """

    # The user that wants to change its user_name logs in
    login_info = {"user_name": "MichaelBrown", "password": "brownieM123"}  # user id 1003
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    update_info = {"user_id": 1003, "user_name": "Michael_Cohen"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["user_name"] == "Michael_Cohen"


def test_user_update_user_full_name(client):
    """
    Tests updating a user's full name via a POST request.

    Steps:
    - Logs in as the user who wants to update their full name.
    - Sends a POST request to update the full name.
    - Verifies the response status is 200 OK.
    - Logs in as an admin to retrieve updated user details.
    - Sends a GET request to verify the full name was updated correctly.
    """

    # The user that wants to change its full name logs in
    login_info = {"user_name": "MichaelBrown", "password": "brownieM123"}  # user id 1003
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    update_info = {"user_id": 1003, "user_full_name": "Michael Levi"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["user_full_name"] == "Michael Levi"


def test_user_update_user_phone_num(client):
    """
    Tests updating a user's phone number via a POST request.

    Steps:
    - Logs in as the user who wants to update their phone number.
    - Sends a POST request to update the phone number.
    - Verifies the response status is 200 OK.
    - Logs in as an admin to retrieve updated user details.
    - Sends a GET request to verify the phone number was updated correctly.
    """

    # The user that wants to change its phone number logs in
    login_info = {"user_name": "MichaelBrown", "password": "brownieM123"}  # user id 1003
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    update_info = {"user_id": 1003, "user_phone_num": "555-1094"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["user_phone_num"] == "555-1094"


def test_user_update_email(client):
    """
    Tests updating a user's email via a POST request.

    Steps:
    - Logs in as the user who wants to update their email.
    - Sends a POST request to update the email address.
    - Verifies the response status is 200 OK.
    - Logs in as an admin to retrieve updated user details.
    - Sends a GET request to verify the email was updated correctly.
    """

    # The user that wants to change its email logs in
    login_info = {"user_name": "MichaelBrown", "password": "brownieM123"}  # user id 1003
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    update_info = {"user_id": 1003, "email": "MichaelCohen@gmail.com"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Retrieve the user details to verify that the email was updated correctly.
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["email"] == "MichaelCohen@gmail.com"


def test_user_update_password(client):
    """
    Tests updating a user's password and ensuring it is hashed.

    Steps:
    - Logs in as the user who wants to update their password.
    - Sends a POST request to update the password.
    - Verifies the response status is 200 OK.
    - Logs in as an admin to retrieve updated user details.
    - Sends a GET request to fetch the stored password.
    - Ensures the stored password is hashed and does not match the plaintext password.
    - Confirms the stored hash correctly matches the new password.
    """

    # The user that wants to change its password logs in
    login_info = {"user_name": "MichaelBrown", "password": "brownieM123"}  # user id 1003
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    update_info = {"user_id": 1003, "password": "NewSecurePass123"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Log in as an admin user to enable access to detailed user information.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    hashed_password = data["users"]['1003']["password"]
    # Verify that the new password saved as hash password
    assert hashed_password != "NewSecurePass123"
    assert check_password_hash(hashed_password, "NewSecurePass123")


def test_user_login(client):
    """
    Tests user login with valid credentials.

    Steps:
    - Sends a POST request to the login endpoint with correct username and password.
    - Verifies the response status is 200 OK, indicating successful login.
    """

    login_info = {"user_name": "MichaelBrown", "password": "brownieM123"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK


def test_login_with_nonexistent_user(client):
    """
    Tests user login with a non-existent username.

    Steps:
    - Sends a POST request to the login endpoint with a non-existent username.
    - Verifies the response status is 401 UNAUTHORIZED, indicating failed login.
    """

    login_info = {"user_name": "non_existent_user", "password": "randompassword"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_login_with_wrong_password(client):
    """
    Tests user login with an incorrect password.

    Steps:
    - Sends a POST request to the login endpoint with a valid username but incorrect password.
    - Verifies the response status is 401 UNAUTHORIZED, indicating failed login.
    """

    login_info = {"user_name": "JaneSmith", "password": "wrongpassword"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_login_with_no_parameters(client):
    """
    Tests user login without providing credentials.

    Steps:
    - Sends a POST request to the login endpoint with an empty JSON payload.
    - Verifies the response status is 400 BAD REQUEST, indicating missing credentials.
    """

    response = client.post('/login', json={})
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


@pytest.mark.parametrize("invalid_json", [["user_name", "password"], {"user_name": 123, "password": 456}, "this is not a json", None])
def test_login_with_invalid_json(client, invalid_json):
    """
    Tests user login with an invalid JSON payload.

    Steps:
    - Sends a POST request to the login endpoint with malformed or incorrect JSON data.
    - Verifies the response status is 400 BAD REQUEST, indicating invalid request format.
    """
    response = client.post('/login', json=invalid_json)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


# TODO- התחברות עם שם משתמש לא קיים (אמור להחזיר 401 UNAUTHORIZED). done
# TODO- התחברות עם סיסמה שגויה (401). done
# TODO- שליחת בקשת התחברות ללא פרמטרים (400). done
# TODO- שליחת בקשת התחברות עם מבנה JSON שגוי (400). done


def test_user_logout(client):
    """
    Tests user logout after a successful login.

    Steps:
    - Logs in with valid credentials.
    - Sends a POST request to the logout endpoint.
    - Verifies the response status is 200 OK, indicating successful logout.
    """
    # Login first
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Logout
    response = client.post('/logout')
    assert response.status_code == http.HTTPStatus.OK


def test_logout_when_not_logged_in(client):
    """
    Tests logging out when no user is logged in.

    Steps:
    - Sends a POST request to the logout endpoint without an active session.
    - Verifies the response status is 200 OK with an empty response body.
    """
    response = client.post('/logout')
    assert response.status_code == http.HTTPStatus.OK
    assert response.data == b""


def test_access_protected_endpoint_after_logout(client):
    """
    Tests that access to a protected route is denied after logging out.

    Steps:
    - Logs in with valid credentials.
    - Logs out the user.
    - Attempts to access a protected endpoint.
    - Verifies the response status is 401 UNAUTHORIZED, indicating access is denied.
    """

    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.post('/logout')
    assert response.status_code == http.HTTPStatus.OK

    response = client.post('/user/update_cart_item_quantity', json={"item_id": 1, "quantity": 2})
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED


def test_add_item_to_cart_requires_login(client):
    """
    Tests that adding an item to the cart requires authentication.

    Steps:
    - Attempts to add an item to the cart without logging in.
    - Verifies the response status is 401 UNAUTHORIZED.
    - Logs in with valid credentials.
    - Retries adding the item to the cart.
    - Verifies the response status is 200 OK, indicating success.
    """

    # Attempt to add item to cart without logging in
    cart_item = {"user_id": 1003, "model_num": "chair-1", "quantity": 1}

    # Send a POST request to add the cart for the specific user
    response = client.post('/user/add_item_to_cart', json=cart_item)
    assert response.status_code == http.HTTPStatus.UNAUTHORIZED

    # Log in with valid credentials
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # Now that we're logged in, try again
    response = client.post('/user/add_item_to_cart', json={"user_id": 1003, "model_num": "chair-1", "quantity": 1})
    # Expect a success code (200 OK, 201 CREATED, etc.), depending on your implementation
    assert response.status_code == http.HTTPStatus.OK


def test_admin_required_operator(client):
    """
    Tests that accessing an admin-only endpoint requires admin authentication.

    Steps:
    - Logs in as an admin user.
    - Sends a GET request to an admin-protected endpoint.
    - Verifies the response status is 200 OK.
    - Ensures the retrieved user password is securely hashed.
    """

    # log in as admin user
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    # request that needs admin permission
    response = client.get('/admin/users', query_string={"user_id": 1005})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    hashed_password = data["users"]["1005"]["password"]
    assert hashed_password != "wilsonRob007"
    assert check_password_hash(hashed_password, "wilsonRob007")


# def test_user_login_nonexistent_user(client):
#     """Test user login with non-existent user ID"""
#     login_info = {"user_id": 9999, "password": "AnyPassword"}
#     response = client.post('/login', json=login_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.UNAUTHORIZED


# ===============cart============================================
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
    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/admin/carts')
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    carts = data['carts']
    assert carts['1002'] == [
        {'model_name': 'Yosef', 'model_num': 'chair-0', 'price': 236.0, 'price_per_unit': 118.0, 'quantity': 2, 'user_id': 1002},
        {'model_name': 'LuxComfort', 'model_num': 'SF-3003', 'price': 1274.4, 'price_per_unit': 1274.4, 'quantity': 1, 'user_id': 1002},
    ]


def test_cart_get_cart_by_userid(client):
    """
    Test retrieving a cart by user id.

    send a GET request to the '/carts' with 'user_id' as a query parameter.
    Verifies the response status is 200 OK and that the returned cart match
    the specified user id.
    param client:
    return: Cart
    """
    # Login first
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

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


def test_add_first_item_to_cart(client):
    """
    Tests adding the first item to a specific user's cart.

    Steps:
    - Logs in as a valid user.
    - Sends a POST request to add an item to the user's cart.
    - Verifies the response status is 200 OK.
    - Sends a GET request to retrieve the user's cart.
    - Ensures the cart contains the newly added item with the correct quantity.
    """

    # Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    cart_item = {"user_id": 1003, "model_num": "chair-1", "quantity": 1}

    # Send a POST request to add the cart for the specific user
    response = client.post('/user/add_item_to_cart', json=cart_item)
    data = response.get_json()

    # Check that the item was added successfully
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item exists
    response = client.get('/carts', query_string={"user_id": 1003})
    data = response.get_json()
    print("test 123", data)
    # Check that the cart is returned correctly
    assert response.status_code == http.HTTPStatus.OK
    assert "1003" in data["carts"]
    assert data["carts"]['1003'][0]['model_num'] == 'BS-4004'
    assert data["carts"]['1003'][1]['model_num'] == 'chair-1'
    assert data["carts"]['1003'][0]['quantity'] == 2
    assert data["carts"]['1003'][1]['quantity'] == 1


def test_add_item_to_cart_not_enough_units_in_stock(client):
    """
    Tests that adding an item to the cart fails if the requested quantity exceeds available stock.

    Steps:
    - Logs in as a valid user.
    - Sends a POST request to add an item with a quantity greater than stock availability.
    - Mocks the stock quantity to be lower than the requested amount.
    - Verifies the response status is 409 CONFLICT, indicating insufficient stock.
    """
    # Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    cart_item = {"user_id": 1003, "model_num": "chair-2", "quantity": 2}
    with patch("source.controller.cart.get_cart_item_full_details", return_value={cart_item["model_num"]: {"stock_quantity": 1}}):
        response = client.post('/user/add_item_to_cart', json=cart_item)
        assert response.status_code == http.HTTPStatus.CONFLICT


def test_add_invalid_cart_item(client):
    """
    Tests that adding an item to the cart fails if the user ID or model number does not exist.

    Steps:
    - Logs in as a valid user.
    - Sends a POST request to add an item with a non-existent user ID or model number.
    - Mocks the validation to return False.
    - Verifies the response status is 400 BAD REQUEST, indicating invalid input.
    """

    # Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    cart_item = {"user_id": 9999, "model_num": "chair-1", "quantity": 1}

    with patch("schema.CartItem.valid", return_value=False):
        response = client.post('/user/add_item_to_cart', json=cart_item)

        assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_get_specific_item_in_cart(client):
    """
    Tests retrieving a specific item from a user's cart by model number.

    Steps:
    - Logs in as a valid user.
    - Sends a GET request to retrieve a specific item from the user's cart.
    - Verifies the response status is 200 OK.
    - Ensures the returned cart contains the requested item with correct details.
    """

    # Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    cart = data['carts']
    assert len(cart) == 1

    assert cart['1002'] == [{'model_name': 'Yosef', 'model_num': 'chair-0', 'price': 236.0, 'price_per_unit': 118.0, 'quantity': 2, 'user_id': 1002}]


def test_update_cart_item_quantity(client):
    """
    Tests updating the quantity of a cart item and verifying the price update.

    Steps:
    - Logs in as a valid user.
    - Sends a POST request to update the quantity of an item in the cart.
    - Mocks stock availability to ensure the update is allowed.
    - Verifies the response status is 200 OK.
    - Sends a GET request to confirm the updated quantity and price in the cart.
    """
    # Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    update_info = dict(model_num="chair-0", user_id=1002, quantity=4)
    with patch("source.controller.cart.get_cart_item_full_details", return_value={update_info["model_num"]: {"stock_quantity": 5}}):
        response = client.post('/user/update_cart_item_quantity', json=update_info)
        assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item stock update
    response = client.get('/carts', query_string={"user_id": 1002})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    assert data["carts"]["1002"][1]["quantity"] == 4

    assert data["carts"]['1002'][1] == {
        'user_id': 1002,
        'model_num': 'chair-0',
        'quantity': 4,
        'price_per_unit': 118.0,
        'price': 472.0,
        'model_name': 'Yosef',
    }


def test_update_quantity_with_item_not_in_cart(client):
    """
    Tests that updating a cart item fails if the item is not in the user's cart.

    Steps:
    - Logs in as a valid user.
    - Sends a POST request to update the quantity of an item not in the user's cart.
    - Verifies the response status is 404 NOT FOUND, indicating the item does not exist in the cart.
    """

    update_info = dict(model_num="chair-0", user_id=1004, quantity=1)

    # Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed
    login_info = {"user_name": "EmilyDavis", "password": "davisEmily!"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.post('/user/update_cart_item_quantity', json=update_info)
    assert response.status_code == http.HTTPStatus.NOT_FOUND


def test_update_quantity_with_not_enough_units_in_stock(client):
    """
    Tests that updating a cart item fails if there are not enough units in stock.

    Steps:
    - Logs in as a valid user.
    - Sends a POST request to update the quantity of an item in the cart.
    - Mocks stock availability to be lower than the requested quantity.
    - Verifies the response status is 409 CONFLICT, indicating insufficient stock.
    """

    # Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    update_info = dict(model_num="chair-0", user_id=1004, quantity=5)

    with patch("source.controller.cart.get_cart_item_full_details", return_value={update_info["model_num"]: {"stock_quantity": 3}}):
        response = client.post('/user/add_item_to_cart', json=update_info)
        assert response.status_code == http.HTTPStatus.CONFLICT


def test_delete_cart_item(client):
    """
    Tests deleting an item from a user's cart.

    Steps:
    - Logs in as a valid user.
    - Verifies the item exists in the cart before deletion.
    - Sends a POST request to delete the cart item.
    - Verifies the response status is 200 OK.
    - Sends a GET request to confirm the item was successfully removed from the cart.
    """

    # Log in first to ensure the @login_required endpoint (/user/add_item_to_cart) can be accessed
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

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


def test_updating_cart_item_quantity_to_0(client):
    """
    Tests that updating a cart item's quantity to 0 removes it from the cart.

    Steps:
    - Logs in as a valid user.
    - Verifies the item exists in the cart before the update.
    - Sends a POST request to update the cart item quantity to 0.
    - Verifies the response status is 200 OK.
    - Sends a GET request to confirm the item was successfully removed from the cart.
    """

    # Log in first to ensure the @login_required endpoint (/cart and /user/add_item_to_cart) can be accessed
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

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


def test_order_view_all_orders(client):
    """
    Test retrieving all orders in order table.

    Sends a GET request to the '/order' endpoint to fetch the complete list of orders cart items.
    Verifies that the response status is HTTP 200 OK.

    The test validates that:
    - The response contains a 'order' key.
    - The number of unique items is as expected.
    - Each order item includes necessary details such as order ID, user ID, model number, items, .
    """
    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/admin/orders')
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    orders = data['orders']
    assert len(orders) == 2

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

    assert orders["2"] == {
        "order_num": 2,
        "user_id": 1003,
        "items": {"BS-4004": 1, "SF-3003": 1},
        "user_email": "michaelbrown@example.com",
        "shipping_address": "789 Maple Street, Los Angeles, CA",
        "status": "DELIVERED",
        "total_price": 2500.0,
        "user_name": "MichaelBrown",
        "phone_number": '555-5678',
        "user_full_name": "Michael Brown",
        "creation_time": 'Sun, 03 Mar 2024 12:30:00 GMT',
    }


def test_get_order_by_user_id_for_admin(client):
    """
    Tests retrieving a user's order details as an admin.

    Steps:
    - Logs in as an admin user.
    - Sends a GET request to retrieve orders for a specific user.
    - Verifies the response status is 200 OK.
    - Ensures the returned order details match the expected data.
    """

    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/admin/orders', query_string={"user_id": 1002})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    orders = data['orders']
    assert orders == {
        "1": {
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
    }


def test_user_view_my_orders(client):
    """
    Tests that a user can view their own orders.

    Steps:
    - Logs in as a valid user.
    - Sends a GET request to retrieve the user's order history.
    - Verifies the response status is 200 OK.
    - Ensures the returned order details match the expected data.
    """
    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/user/orders/1002')
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    orders = data['orders']
    assert orders == {
        "1": {
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
    }


def test_view_user_order_no_user_id(client):
    """
    Tests that accessing the /user/orders endpoint without a user ID results in a server error.

    Steps:
    - Logs in as a valid user.
    - Sends a GET request to retrieve orders without providing a user ID.
    - Verifies the response status is 404 NOT FOUND.
    """

    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/user/orders')
    assert response.status_code == 404


def test_user_view_all_orders_block(client):
    """
    Tests that a regular user cannot access all orders (admin-only access).

    Steps:
    - Logs in as a regular user.
    - Sends a GET request to the admin orders endpoint.
    - Verifies the response status is 403 FORBIDDEN, indicating restricted access.
    """

    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/admin/orders')
    assert response.status_code == 403


def test_get_order_by_order_num_for_admin(client):
    """
    Tests retrieving an order by order number as an admin.

    Steps:
    - Logs in as an admin user.
    - Sends a GET request to retrieve a specific order by order number.
    - Verifies the response status is 200 OK.
    - Ensures the returned order details match the expected data.
    """

    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
    response = client.post('/login', json=login_info)
    assert response.status_code == 200

    response = client.get('/admin/orders', query_string={"order_num": 2})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    orders = data['orders']
    assert len(orders) == 1
    assert orders == {
        "2": {
            "order_num": 2,
            "user_id": 1003,
            "items": {"BS-4004": 1, "SF-3003": 1},
            "user_email": "michaelbrown@example.com",
            "shipping_address": "789 Maple Street, Los Angeles, CA",
            "status": "DELIVERED",
            "total_price": 2500.0,
            "user_name": "MichaelBrown",
            "phone_number": '555-5678',
            "user_full_name": "Michael Brown",
            "creation_time": 'Sun, 03 Mar 2024 12:30:00 GMT',
        }
    }


def test_user_view_specific_order(client):
    """
    Tests that a user can view a specific order by order number.

    Steps:
    - Logs in as a valid user.
    - Sends a GET request to retrieve a specific order by order number.
    - Verifies the response status is 200 OK.
    - Ensures the returned order details match the expected data.
    """

    # Authenticate as an admin to access detailed user data for verification.
    login_info = {"user_name": "JaneSmith", "password": "mypassword456"}
    response = client.post('/login', json=login_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/user/orders/1003', query_string={"order_num": 2})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    orders = data['orders']
    assert len(orders) == 1
    assert orders == {
        "2": {
            "order_num": 2,
            "user_id": 1003,
            "items": {"BS-4004": 1, "SF-3003": 1},
            "user_email": "michaelbrown@example.com",
            "shipping_address": "789 Maple Street, Los Angeles, CA",
            "status": "DELIVERED",
            "total_price": 2500.0,
            "user_name": "MichaelBrown",
            "phone_number": '555-5678',
            "user_full_name": "Michael Brown",
            "creation_time": 'Sun, 03 Mar 2024 12:30:00 GMT',
        }
    }


# TODO: fix the testss
# def test_update_order_status(client):
#     # Authenticate as an admin to access detailed user data for verification.
#     login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
#     response = client.post('/login', json=login_info)
#     assert response.status_code == http.HTTPStatus.OK
#
#     response = client.get('/orders', query_string={"order_num": 1})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     orders = data['orders']
#     assert orders["1"]["status"] == "PENDING"
#
#     # update order status
#     update_info = dict(order_num=1, status=OrderStatus.SHIPPED.value)  # Convert to string
#     response = client.post('/admin/update_order_status', json=update_info)
#     assert response.status_code == http.HTTPStatus.OK
#
#     # Send a GET request to verify item stock update
#     response = client.get('/orders', query_string={"order_num": 1})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     orders = data['orders']
#     assert orders["1"]["status"] == "SHIPPED"

#
# def test_update_order_status_invalid_status(client):
#     """Test that sending an invalid status to update_order_status raises an error"""
#
#     login_info = {"user_name": "RobertWilson", "password": "wilsonRob007"}
#     response = client.post('/login', json=login_info)
#     assert response.status_code == http.HTTPStatus.OK

#     response = client.get('/admin/orders', query_string={"order_num": 1})
#     assert response.status_code == http.HTTPStatus.OK
#     data = response.get_json()
#     orders = data['orders']
#     assert orders["1"]["status"] == "PENDING"
#

#     invalid_status_data = {"order_id": 123, "status": "invalid_status"}
#     response = client.post('/admin/update_order_status', json=invalid_status_data)
#    assert response.status_code == http.HTTPStatus.BAD_REQUEST


# ===============checkout============================================
def test_check_out_process(client):
    """
    Tests the checkout process initiation via the API.

    Steps:
    - Sends a POST request to start the checkout process with user ID, address, and payment method.
    - Verifies the response status is 200 OK, indicating the checkout process started successfully.
    """

    user_id = 1002  # User not exists
    address = "Even Gabirol 3, Tel Aviv"

    response = client.post(f"/checkout", json={'user_id': user_id, "address": address, 'payment_method': PaymentMethod.CREDIT_CARD.value})
    assert response.status_code == http.HTTPStatus.OK


def test_checkout_user_not_exists(client):
    """
    Tests that checkout fails for a non-existent user.

    Steps:
    - Sends a POST request to initiate checkout with a non-existent user ID.
    - Verifies the response status is 404 NOT FOUND, indicating the user does not exist.
    """

    user_id = 1007  # User not exists
    address = "Even Gabirol 3, Tel Aviv"

    response = client.post(f"/checkout", json={'user_id': user_id, "address": address, 'payment_method': PaymentMethod.CREDIT_CARD.value})
    assert response.status_code == 404


def test_checkout_empty_cart(client):
    """
    Tests that checkout fails when the user's cart is empty.

    Steps:
    - Sends a POST request to initiate checkout for a user with an empty cart.
    - Verifies the response status is 404 NOT FOUND, indicating no items in the cart.
    """

    user_id = 1005  # User exists but has no items in cart
    address = "Even Gabirol 3, Tel Aviv"

    response = client.post(f"/checkout", json={'user_id': user_id, "address": address, 'payment_method': PaymentMethod.CREDIT_CARD.value})
    assert response.status_code == 404
