import os
import tempfile
import json
import pytest
import shutil
import pathlib

from flask import Flask
import app
import http
import schema


# Fixture for Flask test client
@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


@pytest.fixture
def database():
    with tempfile.TemporaryDirectory(delete=False) as directory:
        database_file = pathlib.Path(directory) / 'data.sqlite'
        schema.create(database_file)
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



def test_user_get_all_items(database, client):
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
