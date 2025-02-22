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
    with tempfile.TemporaryDirectory(delete=False) as directory:
        filename = pathlib.Path(directory) / 'data.sqlite3'
        application = app.create_app({'database_url': f'sqlite:///{filename}'})
        yield application

@pytest.fixture
def client(application):
    with application.test_client() as client:
        yield client



@pytest.fixture(autouse=True)
def preprepared_data(application):
    session = schema.session()
    chair = schema.Furniture(model_num='chair-0', 
                                name='Yosef', 
                                description='a nice chair',
                                price=100.0, 
                                dimensions={"height": 90, "width": 45, "depth": 50}, 
                                category="Chair",
                                image_filename='classic_wooden_chair.jpg',
                                stock_quantity=3,
                                discount=0.0,
                                details={'material': 'wood', 'weight': 5, 'color': 'white'})
    session.add(chair)
    session.commit()
    yield



def test_user_get_all_items(client):
    response = client.get('/items')
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    details = {'material': 'wood', 'weight': 5, 'color': 'white'}
    assert items[0] == {'model_num': 'chair-0',
                        'name': 'Yosef',
                        'description': 'a nice chair', 
                        'price': 100.0, 
                        'dimensions': {"height": 90, "width": 45, "depth": 50}, 
                        'category': 'Chair',
                        'image_filename': "classic_wooden_chair.jpg", 
                        'stock_quantity': 3,
                        'discount': 0.0, 
                        'details': details }

