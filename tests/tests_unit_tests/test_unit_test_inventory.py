import pytest
import functools
import schema
import http
import source.controller.furniture_inventory as furniture_inventory



@pytest.fixture(autouse=True)
def bypass_admin_required(monkeypatch):
    # Define a dummy decorator that does nothing
    def dummy_decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    # Import app after defining the dummy decorator to ensure patching is applied
    import app

    monkeypatch.setattr(app, 'admin_required', dummy_decorator)


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

    session.add_all([chair0, chair1, bed])
    session.commit()
    yield


def test_system_update_item_quantity(client):
    """
    Test updating the quantity of furniture in the inventory from the system (no API call)
    :param client:
    :return: None
    """
    # Increase the stock units in 1
    furniture_inventory.system_update_item_quantity(model_num="BD-5005", quantity_to_add=1)

    # Check the new number is correct
    response = client.get('/items', query_string={"model_num": "BD-5005"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert items['BD-5005']['stock_quantity'] == 6

    # Decrease the stock unit by 2
    furniture_inventory.system_update_item_quantity(model_num="BD-5005", quantity_to_add=-2)

    # Check the new number is correct
    response = client.get('/items', query_string={"model_num": "BD-5005"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert items['BD-5005']['stock_quantity'] == 4


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
