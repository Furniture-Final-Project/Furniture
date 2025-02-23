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
                                discount=5.0,
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
    response = client.get('/items')
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert len(items) == 5
    assert items['chair-0'] == {'model_num': 'chair-0',
                        'name': 'Yosef',
                        'description': 'a nice chair', 
                        'price': 100.0, 
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
                    'dimensions': {"height": 180, "width": 80, "depth": 30},
                    'category': "BookShelf",
                    'image_filename': "oak_bookshelf.jpg",
                    'stock_quantity': 7,
                    'discount': 5.0,
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
    response = client.get('/items', query_string={"category": "Chair", "max_price": 150})
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    assert len(items) == 1
    assert items['chair-0'] == {'model_num': 'chair-0',
                        'name': 'Yosef',
                        'description': 'a nice chair', 
                        'price': 100.0, 
                        'dimensions': {"height": 90, "width": 45, "depth": 50}, 
                        'category': 'Chair',
                        'image_filename': "classic_wooden_chair.jpg", 
                        'stock_quantity': 3,
                        'discount': 0.0, 
                        'details': {'material': 'wood', 'weight': 5, 'color': 'white'} }
                        

def test_get_item_by_model_num(client):
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