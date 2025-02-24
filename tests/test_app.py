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
    application = app.create_app({'database_url': f'sqlite:///:memory:'})
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
                                name='Yosef', 
                                description='a nice chair',
                                price=100.0, 
                                dimensions={"height": 90, "width": 45, "depth": 50}, 
                                category="Chair",
                                image_filename='classic_wooden_chair.jpg',
                                stock_quantity=3,
                                discount=0.0,
                                details={'material': 'wood', 'weight': 5, 'color': 'white'})
    chair1 = schema.Furniture(
                                model_num='chair-1', 
                                name='Haim', 
                                description='a Very nice chair',
                                price=200.0, 
                                dimensions={"height": 90, "width": 45, "depth": 50}, 
                                category="Chair",
                                image_filename='classic_wooden_chair.jpg',
                                stock_quantity=4,
                                discount=0.0,
                                details={'material': 'wood', 'weight': 6, 'color': 'white'})
    bed = schema.Furniture(
                                model_num="BD-5005",
                                name="DreamComfort",
                                description="A luxurious memory foam bed with a sturdy solid wood frame.",
                                price=1200.0,
                                dimensions={"height": 50, "width": 160, "depth": 200},
                                category="Bed",
                                image_filename="memory_foam_bed.jpg",
                                stock_quantity=5,
                                discount=10.0,
                                details={
                                    "mattress_type": "Memory Foam",
                                    "frame_material": "Solid Wood"
                                }
                            )
    bookshelf = schema.Furniture(
                                model_num="BS-4004",
                                name="OakElegance",
                                description="A stylish and durable bookshelf made of pine wood with a natural oak finish.",
                                price=110.0,
                                dimensions={"height": 180, "width": 80, "depth": 30},
                                category="BookShelf",
                                image_filename="oak_bookshelf.jpg",
                                stock_quantity=7,
                                discount=50.0,
                                details={
                                    "num_shelves": 5,
                                    "max_capacity_weight_per_shelf": 20.0,
                                    "material": "Pine Wood",
                                    "color": "Natural Oak"
                                }
                            )
    sofa = schema.Furniture(
                                model_num="SF-3003",
                                name="LuxComfort",
                                description="A luxurious three-seater sofa with top-grain leather upholstery, perfect for a modern living room.",
                                price=1200.0,
                                dimensions={"height": 85, "width": 220, "depth": 95},
                                category="Sofa",
                                image_filename="luxury_leather_sofa.jpg",
                                stock_quantity=5,
                                discount=10.0,
                                details={
                                    "upholstery": "Top-Grain Leather",
                                    "color": "Dark Gray",
                                    "num_seats": 3
                                }
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
    such as model number, name, description, price, final price (including tax and
    discounts), dimensions, category, image filename, stock quantity, discount, and
    additional details.
    """
    response = client.get('/items')
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert len(items) == 5
    assert items['chair-0'] == {'model_num': 'chair-0',
                        'name': 'Yosef',
                        'description': 'a nice chair', 
                        'price': 100.0, 
                        'final_price': 118.0,
                        'dimensions': {"height": 90, "width": 45, "depth": 50}, 
                        'category': 'Chair',
                        'image_filename': "classic_wooden_chair.jpg", 
                        'stock_quantity': 3,
                        'discount': 0.0, 
                        'details': {'material': 'wood', 'weight': 5, 'color': 'white'} }
    assert items['chair-1'] == {'model_num': 'chair-1',
                        'name': 'Haim',
                        'description': 'a Very nice chair', 
                        'price': 200.0, 
                        'final_price': 236.0, 
                        'dimensions': {"height": 90, "width": 45, "depth": 50}, 
                        'category': 'Chair',
                        'image_filename': "classic_wooden_chair.jpg", 
                        'stock_quantity': 4,
                        'discount': 0.0, 
                        'details': {'material': 'wood', 'weight': 6, 'color': 'white'} }
    
    assert items['BD-5005'] == {
                    'model_num': "BD-5005",
                    'name': "DreamComfort",
                    'description': "A luxurious memory foam bed with a sturdy solid wood frame.",
                    'price': 1200.0,
                    'final_price': 1274.4,  
                    'dimensions': {"height": 50, "width": 160, "depth": 200},
                    'category': "Bed",
                    'image_filename': "memory_foam_bed.jpg",
                    'stock_quantity': 5,
                    'discount': 10.0,
                    'details': {
                        "mattress_type": "Memory Foam",
                        "frame_material": "Solid Wood"
                    }
                }
    assert items["BS-4004"] == {
                    'model_num': "BS-4004",
                    'name': "OakElegance",
                    'description': "A stylish and durable bookshelf made of pine wood with a natural oak finish.",
                    'price': 110.0,
                    'final_price': 64.9,  
                    'dimensions': {"height": 180, "width": 80, "depth": 30},
                    'category': "BookShelf",
                    'image_filename': "oak_bookshelf.jpg",
                    'stock_quantity': 7,
                    'discount': 50.0,
                    'details': {
                        "num_shelves": 5,
                        "max_capacity_weight_per_shelf": 20.0,
                        "material": "Pine Wood",
                        "color": "Natural Oak"
                    }
                }
    assert items["SF-3003"] == {
                    'model_num': "SF-3003",
                    'name': "LuxComfort",
                    'description': "A luxurious three-seater sofa with top-grain leather upholstery, perfect for a modern living room.",
                    'price': 1200.0,
                    'final_price': 1274.4,
                    'dimensions': {"height": 85, "width": 220, "depth": 95},
                    'category': "Sofa",
                    'image_filename': "luxury_leather_sofa.jpg",
                    'stock_quantity': 5,
                    'discount': 10.0,
                    'details': {
                        "upholstery": "Top-Grain Leather",
                        "color": "Dark Gray",
                        "num_seats": 3
                    }
                }

def test_single_filter(client):
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
                    'name': "DreamComfort",
                    'description': "A luxurious memory foam bed with a sturdy solid wood frame.",
                    'price': 1200.0,
                    'final_price': 1274.4,
                    'dimensions': {"height": 50, "width": 160, "depth": 200},
                    'category': "Bed",
                    'image_filename': "memory_foam_bed.jpg",
                    'stock_quantity': 5,
                    'discount': 10.0,
                    'details': {
                        "mattress_type": "Memory Foam",
                        "frame_material": "Solid Wood"
                    }
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
    assert items['chair-0'] == {'model_num': 'chair-0',
                        'name': 'Yosef',
                        'description': 'a nice chair', 
                        'price': 100.0, 
                        'final_price': 118.0,
                        'dimensions': {"height": 90, "width": 45, "depth": 50}, 
                        'category': 'Chair',
                        'image_filename': "classic_wooden_chair.jpg", 
                        'stock_quantity': 3,
                        'discount': 0.0, 
                        'details': {'material': 'wood', 'weight': 5, 'color': 'white'} 
                        }
                        

def test_get_item_by_model_num(client):
    """
    Tests the retrieval of a specific item by its model number from the inventory API.

    This test simulates a client request to fetch an item's details by providing 
    its `model_num` as a query parameter. The API should return a JSON response 
    containing the full details of the requested item.

    Expected Behavior:
    - The response status code should be HTTP 200 (OK).
    - The response should contain exactly one item matching the requested `model_num`.
    - The returned item's details should include:
        - Model number, name, description, price, and final price.
        - Final price reflects any applied discount and tax calculations.
        - Dimensions (height, width, depth), category, image filename, and stock quantity.
        - Additional details specific to the item's category.

    This ensures that the system correctly retrieves item data, applies tax and discounts, 
    and returns complete product details in the expected format.
    """    
    response = client.get('/items', query_string={"model_num": "BD-5005"})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert len(items) == 1
    assert items['BD-5005'] == {
                    'model_num': "BD-5005",
                    'name': "DreamComfort",
                    'description': "A luxurious memory foam bed with a sturdy solid wood frame.",
                    'price': 1200.0,
                    'final_price': 1274.4, 
                    'dimensions': {"height": 50, "width": 160, "depth": 200},
                    'category': "Bed",
                    'image_filename': "memory_foam_bed.jpg",
                    'stock_quantity': 5,
                    'discount': 10.0,
                    'details': {
                        "mattress_type": "Memory Foam",
                        "frame_material": "Solid Wood"
                    }
                }
