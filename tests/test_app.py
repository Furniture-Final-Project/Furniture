import os
import tempfile
import json
import pytest
import shutil
import pathlib

import app
import http
import schema


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

    session.add_all([chair0, chair1, bed, bookshelf, sofa])
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
    response = client.post('/add_item', json=new_item)
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
    assert data["items"]["B-101"]["is_available"] == True


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
    response = client.post('/add_item', json=invalid_item)
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
    response = client.post('/add_item', json=new_item)
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
    assert data["items"]["C-202"]["is_available"] == True


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
    response = client.post('/add_item', json=invalid_item)
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
    response = client.post('/add_item', json=new_item)
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
    assert data["items"]["BS-5001"]["is_available"] == True


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
    response = client.post('/add_item', json=new_item)
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
    assert data["items"]["SF-5005"]["is_available"] == True


# TODO - add: test_add_Sofa_item_not_correct_values(client)


def test_update_quantity(client):
    """Test to update quantity of an item, by its model number"""
    update_info = {
        "model_num": "chair-0",
        "stock_quantity": 0,
    }
    response = client.post('/update_item', json=update_info)
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
    response = client.post('/delete_item', json=deleted_item)
    assert response.status_code == http.HTTPStatus.OK

    # Send a GET request to verify item deleted successfully
    response = client.get('/items', query_string={"model_num": "chair-1"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    assert data == {'items': {}}
