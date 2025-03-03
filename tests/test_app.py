from datetime import datetime
import pytest
import app
import http
import schema
from unittest.mock import patch
from werkzeug.security import check_password_hash, generate_password_hash
import source.controller.user as user
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
    )

    user_2 = schema.User(
        user_id=1003,
        user_name="MichaelBrown",
        user_full_name="Michael Brown",
        user_phone_num="555-5678",
        address="789 Maple Street, Los Angeles, CA",
        email="michaelbrown@example.com",
        password=generate_password_hash("brownieM123"),
    )

    user_3 = schema.User(
        user_id=1004,
        user_name="EmilyDavis",
        user_full_name="Emily Davis",
        user_phone_num="555-9012",
        address="101 Pine Road, Austin, TX",
        email="emilydavis@example.com",
        password=generate_password_hash("davisEmily!"),
    )

    user_4 = schema.User(
        user_id=1005,
        user_name="RobertWilson",
        user_full_name="Robert Wilson",
        user_phone_num="555-3456",
        address="202 Birch Lane, Seattle, WA",
        email="robertwilson@example.com",
        password=generate_password_hash("wilsonRob007"),
    )

    cart_item1 = schema.CartItem(user_id=1002, model_num='chair-0', quantity=2)

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

    session.add_all([chair0, chair1, bed, bookshelf, sofa, user_1, user_2, user_3, user_4, cart_item1, order1, order2])
    session.commit()
    yield


def test_user_get_all_items(client):
    """
    Test retrieving all items, including out-of-stock items.

    Sends a GET request to '/items' to fetch the complete list of items.
    Verifies the response status is 200 OK and that all expected items are returned,
    regardless of their stock status. Ensures each item includes necessary details
    such as model number, model_name, description, price, final price (including tax and
    discounts), dimensions, category, image filename, stock quantity, discount, and
    additional details.
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
    Test retrieving items by model_name.

    Sends a GET request to '/items' with 'model_name' as a query parameter.
    Verifies the response status is 200 OK and that the returned items match
    the specified model_name.
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
    Test filtering items by category and maximum price.

    Sends a GET request to '/items' with 'category' and 'max_price' as query parameters.
    Verifies the response status is 200 OK and that the returned items match the specified
    category and do not exceed the maximum price. Ensures each item's 'stock_quantity' is
    included for inventory status display.
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
    Tests the retrieval of a specific item by its model number from the inventory API
    and verifies its stock availability.

    This test sends a GET request to '/items' with a `model_num` query parameter
    to fetch details about a specific furniture item.

    Expected Behavior:
    - The response status code should be HTTP 200 (OK).
    - The response should contain exactly one item matching the requested `model_num`.
    - The returned item's details should include:
        - Model number, name, description, price, and final price.
        - Final price reflecting any applied discount and tax calculations.
        - Dimensions (height, width, depth), category, image filename, and stock quantity.
        - Additional details specific to the item's category.
    - If the item is in stock (`stock_quantity > 0`), the response must include `"is_available": True`.
    - If the item is out of stock (`stock_quantity == 0`), the response must include `"is_available": False`.

    This ensures that:
    - The API correctly retrieves item details.
    - The `is_available` field accurately reflects stock availability.
    - The system properly applies discounts and tax calculations in the response.
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
    Tests that an out-of-stock item is correctly returned with `is_available: False`.
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
    """Test adding a new Bed item using POST request."""
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
    """Test adding a Bed item with an invalid mattress type."""
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
    """Test adding a new Chair item using POST request."""
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
    """Test adding a Bed item with an invalid mattress type."""
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
    """Test adding a new BookShelf item using POST request."""
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


# TODO - add: test_add_Bookshelf_item_not_correct_values(client)


def test_add_Sofa(client):
    """Test adding a new Sofa item using POST request."""
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


# TODO - add: test_add_Sofa_item_not_correct_values(client)


def test_update_quantity(client):
    """Test to update quantity of an item, by its model number"""
    update_info = {
        "model_num": "chair-0",
        "stock_quantity": 0,
    }
    response = client.post('/admin/update_item', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    # Send a GET request to verify item stock update
    response = client.get('/items', query_string={"model_num": "chair-0"})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["items"]["chair-0"]["stock_quantity"] == 0


def test_delete_item(client):
    deleted_item = {"model_num": "chair-1"}
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
    hashed_password = users['1002']["password"]
    assert hashed_password != "mypassword456"
    assert check_password_hash(hashed_password, "mypassword456")


def test_add_new_user(client):
    user_info = {
        "user_id": 207105880,
        "user_name": "JonCohen",
        "user_full_name": "Jon Cohen",
        "user_phone_num": "555-7824",
        "address": "123 Elm Street, Springfield, IL",
        "email": "johndoe@example.com",
        "password": "securepassword123",
    }
    response = client.post('/add_user', json=user_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user was asses successfully
    response = client.get('/admin/users', query_string={"user_id": 207105880})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data["users"]['207105880']["user_name"] == "JonCohen"


def test_password_hashing(client):
    user_info = {
        "user_id": 67890,
        "user_name": "AliceDoe",
        "user_full_name": "Alice Doe",
        "user_phone_num": "555-8821",
        "address": "789 Oak St, New York, NY",
        "email": "alicedoe@example.com",
        "password": "mypassword123",
    }

    response = client.post('/add_user', json=user_info)
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/admin/users', query_string={"user_id": 67890})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()

    hashed_password = data["users"]["67890"]["password"]
    assert hashed_password != user_info["password"]
    assert check_password_hash(hashed_password, user_info["password"])


def test_existing_user(client):
    existing_user = {
        "user_id": 1002,
        "user_name": "JaneSmith",
        "user_full_name": "Jane Smith",
        "user_phone_num": "555-1234",
        "address": "456 Oak Avenue, New York, NY",
        "email": "janesmith@example.com",
        "password": "mypassword456",
    }
    response = client.post('/add_user', json=existing_user)
    assert response.status_code == http.HTTPStatus.BAD_REQUEST


# TODO - add test to get user info


def test_user_update_address(client):
    """Test to update address of a user, by its user_id"""
    updated_info = {"user_id": 1003, "address": "21 Yaakov Meridor, Tel Aviv"}
    response = client.post('/update_user', json=updated_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated corretly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["address"] == "21 Yaakov Meridor, Tel Aviv"


def test_user_update_user_name(client):
    """Test to update user_name of a user, by its user_id"""
    update_info = {"user_id": 1003, "user_name": "Michael_Cohen"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["user_name"] == "Michael_Cohen"


def test_user_update_user_full_name(client):
    """Test to update user_full_name of a user, by its user_id"""
    update_info = {"user_id": 1003, "user_full_name": "Michael Levi"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["user_full_name"] == "Michael Levi"


def test_user_update_user_phone_num(client):
    """Test to update user_phone_num of a user, by its user_id"""
    update_info = {"user_id": 1003, "user_phone_num": "555-1094"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["user_phone_num"] == "555-1094"


def test_user_update_email(client):
    """Test to update email of a user, by its user_id"""
    update_info = {"user_id": 1003, "email": "MichaelCohen@gmail.com"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    assert data["users"]['1003']["email"] == "MichaelCohen@gmail.com"


def test_user_update_password(client):
    """Test to update password of a user and hash it, by its user_id"""
    update_info = {"user_id": 1003, "password": "NewSecurePass123"}
    response = client.post('/update_user', json=update_info)
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify user details were updated correctly
    response = client.get('/admin/users', query_string={"user_id": 1003})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK
    hashed_password = data["users"]['1003']["password"]
    # Verify that the new password saved as hash password
    assert hashed_password != "NewSecurePass123"
    assert check_password_hash(hashed_password, "NewSecurePass123")


def test_get_user_details_existing():
    """Test retrieving details of an existing user from the test database"""
    user_id = 1003
    user_data = user.get_user_details(user_id)

    assert user_data["user_id"] == 1003
    assert user_data["user_name"] == "MichaelBrown"
    assert user_data["user_full_name"] == "Michael Brown"
    assert user_data["user_phone_num"] == "555-5678"
    assert user_data["address"] == "789 Maple Street, Los Angeles, CA"
    assert user_data["email"] == "michaelbrown@example.com"


# TODO - make sure tests for login and log out works for hash password

# def test_user_login(client):
#     """Test user login with correct credentials"""
#     login_info = {"user_name":"MichaelBrown", "password": "brownieM123"}
#     response = client.post('/login', json=login_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     assert data["success"] is True
#     assert data["message"] == "Login successful"
#     assert data["user_name"] == "MichaelBrown"

# def test_user_login_wrong_password(client):
#     """Test user login with incorrect password"""
#     login_info = {"user_name":"MichaelBrown", "password": "WrongPass"}
#     response = client.post('/login', json=login_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.UNAUTHORIZED


# def test_user_login_nonexistent_user(client):
#     """Test user login with non-existent user ID"""
#     login_info = {"user_id": 9999, "password": "AnyPassword"}
#     response = client.post('/login', json=login_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.UNAUTHORIZED


# def test_user_login_and_logout(client):
#     login_info = {"user_id": 1003, "password": "brownieM123"}

#     response = client.post('/login', json=login_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     assert data["success"] is True
#     assert data["message"] == "Login successful"
#     assert data["user_id"] == 1003

#     response = client.get('/is_logged_in', query_string={"user_id": 1003})
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     assert data["success"] is True
#     assert data["logged_in"] is True

#     response = client.get('/admin/users', query_string={"user_id": 1003})
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     hashed_password = data["users"]["1003"]["password"]
#     assert hashed_password != "brownieM123"
#     assert check_password_hash(hashed_password, "brownieM123")

#     logout_info = {"user_id": 1003}
#     response = client.post('/logout', json=logout_info)
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     assert data == {"success": True, "message": "User logged out"}

#     response = client.get('/is_logged_in', query_string={"user_id": 1003})
#     data = response.get_json()
#     assert response.status_code == http.HTTPStatus.OK
#     assert data["success"] is True
#     assert data["logged_in"] is False


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
    response = client.get('/carts')
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    carts = data['carts']
    assert len(carts) == 1

    assert carts['1002'] == {'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}


def test_cart_get_cart_by_userid(client):
    """
    Test retrieving a cart by user id.

    send a GET request to the '/carts' with 'user_id' as a query parameter.
    Verifies the response status is 200 OK and that the returned cart match
    the specified user id.
    :param client:
    :return: Cart
    """
    response = client.get('/carts', query_string={"user_id": 1002})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    cart = data['carts']
    assert len(cart) == 1

    assert cart['1002'] == {'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}
    assert data['cart_total_price'] == 236.0


@pytest.mark.parametrize(
    "user_exists, item_exists, expected",
    [
        (True, True, True),  # True
        (False, True, False),  # False
        (True, False, False),  # False
        (False, False, False),  # False
    ],
)
def test_valid_method_cartitem(user_exists, item_exists, expected):
    """
    Test the valid() function of CartItem.
    It should return True only if both the user and item exist.
    """
    cart_item = schema.CartItem(user_id=9999, model_num="chair-10", quantity=1)

    with (
        patch("schema.user.get_user_details", return_value=user_exists),
        patch("schema.cart.get_cart_item_full_details", return_value=item_exists),
    ):

        assert cart_item.valid() == expected


def test_add_first_item_to_cart(client):
    """
    Test adding new item to a specific cart of a specific user.
    """
    cart_item = {"user_id": 1003, "model_num": "chair-1", "quantity": 1}

    # Send a POST request to add the cart for the specific user
    response = client.post('/user/add_item_to_cart', json=cart_item)
    data = response.get_json()

    # Check that the item was added successfully
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item exists
    response = client.get('/carts', query_string={"user_id": 1003})
    data = response.get_json()

    # Check that the cart is returned correctly
    assert response.status_code == http.HTTPStatus.OK
    assert "1003" in data["carts"]
    assert data["carts"]['1003']['model_num'] == "chair-1"
    assert data["carts"]['1003']['quantity'] == 1


def test_add_item_to_cart_not_enough_units_in_stock(client):
    """
    Test  adding item to cart is not possible if the asked quantity is bigger than stock quantity.
    Expecting an error response.
    """
    cart_item = {"user_id": 1003, "model_num": "chair-2", "quantity": 2}
    with patch("source.controller.cart.get_cart_item_full_details", return_value={cart_item["model_num"]: {"stock_quantity": 1}}):
        response = client.post('/user/add_item_to_cart', json=cart_item)
        assert response.status_code == http.HTTPStatus.CONFLICT


def test_add_invalid_cart_item(client):
    """
    Test adding an item to the cart with a non-existent user ID or non-existent model number.
    Expecting an error response.
    """
    cart_item = {"user_id": 9999, "model_num": "chair-1", "quantity": 1}

    with patch("schema.CartItem.valid", return_value=False):
        response = client.post('/user/add_item_to_cart', json=cart_item)

        assert response.status_code == http.HTTPStatus.BAD_REQUEST


def test_get_specific_item_in_cart(client):
    """
    Test retrieving an item by model number and user id.
    """
    response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    cart = data['carts']
    assert len(cart) == 1

    assert cart['1002'] == {'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}


def test_update_cart_item_quantity(client):
    """
    Test updating a cart item quantity and that the price updates.
    """

    update_info = dict(model_num="chair-0", user_id=1002, quantity=4)
    with patch("source.controller.cart.get_cart_item_full_details", return_value={update_info["model_num"]: {"stock_quantity": 5}}):
        response = client.post('/user/update_cart_item_quantity', json=update_info)
        assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item stock update
    response = client.get('/carts', query_string={"user_id": 1002})
    data = response.get_json()
    assert response.status_code == http.HTTPStatus.OK

    assert data["carts"]["1002"]["quantity"] == 4

    assert data["carts"]['1002'] == {
        'user_id': 1002,
        'model_num': 'chair-0',
        'quantity': 4,
        'price_per_unit': 118.0,
        'price': 472.0,
        'model_name': 'Yosef',
    }


def test_update_quantity_with_item_not_in_cart(client):
    """Test that updating a cart item is not possible if the item not in user's cart"""
    update_info = dict(model_num="chair-0", user_id=1004, quantity=1)
    response = client.post('/user/update_cart_item_quantity', json=update_info)
    assert response.status_code == http.HTTPStatus.NOT_FOUND


def test_update_quantity_with_not_enough_units_in_stock(client):
    """
    Test that updating a cart item is not possible if the item not in stock or do not have enough units in stock.
    Expecting an error response.
    """
    update_info = dict(model_num="chair-0", user_id=1004, quantity=5)

    with patch("source.controller.cart.get_cart_item_full_details", return_value={update_info["model_num"]: {"stock_quantity": 3}}):
        response = client.post('/user/add_item_to_cart', json=update_info)
        assert response.status_code == http.HTTPStatus.CONFLICT


def test_delete_cart_item(client):
    """Test deleting a cart item from CartItem table"""
    # Ensure the cart item in the cart
    response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    cart = data['carts']
    assert cart['1002'] == {'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}

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
    """Test updating a cart item quantity to 0 will delete it from the table"""
    # Ensure the cart item in the cart
    response = client.get('/carts', query_string={"user_id": 1002, 'model_num': 'chair-0'})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    cart = data['carts']
    assert cart['1002'] == {'user_id': 1002, 'model_num': 'chair-0', 'quantity': 2, 'price_per_unit': 118.0, 'price': 236.0, 'model_name': 'Yosef'}

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
    #
    # def mock_get_user_details(user_id):
    #     if user_id == 1002:
    #         return {
    #             1002: {
    #                 "user_id": 1002,
    #                 "user_name": "JaneSmith",
    #                 "user_full_name": "Jane Smith",
    #                 "address": "456 Oak Avenue, New York, NY",
    #                 "shipping_address": "123 Main St, Springfield",
    #                 "email": "janesmith@example.com",
    #                 "user_phone_num": "052-2541024",
    #             }
    #         }
    #
    #     elif user_id == 1003:
    #         return {
    #             1003: {
    #                 "user_id": 1003,
    #                 "user_name": "MichaelBrown",
    #                 "user_full_name": "Michael Brown",
    #                 "address": "789 Maple Street, Los Angeles, CA",
    #                 "shipping_address": "789 Maple Street, Los Angeles, CA",
    #                 "email": "michaelbrown@example.com",
    #                 "user_phone_num": "052-2541025",
    #             }
    #         }
    #     return {}
    #
    # with patch("source.controller.user.get_user_details", side_effect=mock_get_user_details):
    response = client.get('/orders')
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


def test_get_order_by_user_id(client):
    response = client.get('/orders', query_string={"user_id": 1002})
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


def test_get_order_by_order_num(client):
    response = client.get('/orders', query_string={"order_num": 2})
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


def test_update_order_status(client):
    response = client.get('/orders', query_string={"order_num": 1})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    orders = data['orders']
    assert orders["1"]["status"] == "PENDING"

    # update order status
    update_info = dict(order_num=1, status=OrderStatus.SHIPPED.value)  # Convert to string
    response = client.post('/admin/update_order_status', json=update_info)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item stock update
    response = client.get('/orders', query_string={"order_num": 1})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    orders = data['orders']
    assert orders["1"]["status"] == "SHIPPED"


# TODO: test that invalid status will raise error
