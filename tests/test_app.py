import os
import json
import pytest

from flask import Flask
from app import app  # Import the Flask app
from source.models.inventory import Inventory


# Fixture for Flask test client
@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


# Fixture for Inventory using test data
@pytest.fixture
def test_inventory():
    # Path to the test data folder containing JSON files
    test_data_folder = os.path.join('tests', 'test_data')
    inventory_instance = Inventory(test_data_folder)
    yield inventory_instance


# Expected result for get_all_available_items using our test data
expected_result = [
    {
        "color": "Dark Brown",
        "description": "A sturdy wooden chair with a comfortable cushioned seat.",
        "dimension": {"depth": 50, "height": 90, "width": 45},
        "discount": 0.1,
        "image_filename": "classic_wooden_chair.jpg",
        "material": "Oak Wood",
        "model_name": "Classic Wooden Chair",
        "model_num": "CH-1001",
        "price": 120,
        "weight": 8.5
    },
    {
        "color": "Dark Gray",
        "description": "A premium three-seater sofa with top-grain leather upholstery.",
        "dimension": {"depth": 90, "height": 85, "width": 200},
        "discount": 0.2,
        "image_filename": "luxury_leather_sofa.jpg",
        "model_name": "Luxury Leather Sofa",
        "model_num": "SF-3003",
        "num_seats": 3,
        "price": 1200,
        "upholstery": "Top-Grain Leather"
    },
    {
        "description": "A modern king-size bed frame with a solid wood finish.",
        "dimension": {"depth": 190, "height": 50, "width": 210},
        "discount": 0.12,
        "frame_material": "Solid Wood",
        "image_filename": "king_size_bed.jpg",
        "mattress_type": "Memory Foam",
        "model_name": "King Size Bed Frame",
        "model_num": "BD-5005",
        "price": 900
    }
]


# Test the get_all_available_items method directly

def test_get_all_available_items(test_inventory):
    items = test_inventory.get_all_available_items()
    assert isinstance(items, list), "Expected a list of items"
    # Check that the items exactly match the expected result
    assert items == expected_result, "The items do not match the expected result"


# Test the API endpoint for '/available-items'
def test_api_available_items(client, monkeypatch):
    # Use the test data folder for the inventory instance within the app
    test_data_folder = os.path.join('tests', 'test_data')
    test_inventory_instance = Inventory(test_data_folder)

    # Monkeypatch the inventory_instance in the app module to use our test_inventory_instance
    import app as flask_app
    flask_app.inventory_instance = test_inventory_instance

    # Make request to the API endpoint
    response = client.get('/available-items')
    assert response.status_code == 200, "Expected status code 200"

    data = json.loads(response.data)
    # Assert the returned API data matches the expected result
    assert data == expected_result, "API response data does not match expected result"

    print('Test for API endpoint passed.')


if __name__ == '__main__':
    pytest.main([os.path.realpath(__file__)])