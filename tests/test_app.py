
import os
import tempfile
import json
import pytest
import shutil

from flask import Flask
import app
import http
from source.models.inventory import Inventory


# Fixture for Flask test client
@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


# Fixture for Inventory using test data
@pytest.fixture
def inventory():
    # Path to the test data folder containing JSON files
    with tempfile.TemporaryDirectory() as directory:
        test_data_folder = os.path.join('tests', 'test_data')
        destination = os.path.join(directory, 'test_data')
        shutil.copytree(test_data_folder, destination)
        inventory = Inventory(destination)
        old_inventory = app.inventory
        app.inventory = inventory
        yield inventory
        app.inventory = old_inventory


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

def test_get_all_available_items(inventory):
    items = inventory.get_all_available_items()
    assert items == expected_result


def test_api_available_items(client, inventory):
    response = client.get('/available-items')
    assert response.status_code == 200, "Expected status code 200"
    data = json.loads(response.data)
    assert data == expected_result


def test_admin_adds_new_type_of_chair_to_inventory(client, inventory):
    chair_attributes = {'model_num': 'CH-1002', 'model_name': 'Moshe', 'description': 'nice chair',
                                    'price': 5, 'dimension': {"height": 90, "width": 45, "depth": 50},
                                    'image_filename': 'Moshe.jpg', 'material': 'wood', 'weight': 10, 'color': 'Red', 'discount': 0.0}

    response = client.post('/inventory', json={'quantity': 7, 'details': chair_attributes})
    assert response.status_code == http.HTTPStatus.OK

    response = client.get('/inventory')
    assert response.status_code == http.HTTPStatus.OK

    data = json.loads(response.data)
    assert data['CH-1002'] == {'quantity': 7, 'category': "Chair"}
