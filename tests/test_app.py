import os
import tempfile
import json
import pytest
import shutil

from flask import Flask
import app
import http


# Fixture for Flask test client
@pytest.fixture
def client():
    app.app.config['TESTING'] = True
    with app.app.test_client() as client:
        yield client


def test_user_get_all_items(client):
    response = client.get('/items')
    assert response.status_code == http.HTTPStatus.OK
    data = response.get_json()
    items = data['items']
    details = {'material': 'wood', 'weight': 5, 'color': 'white'}
    assert items[0] == {'type': 'chair', 'model_num': 'chair-0','description': 'chair-0-description', 'price': 100.0, 'dimensions': {"height": 90, "width": 45, "depth": 50}, 'image_filename': "classic_wooden_chair.jpg", 'discount': 0.0, 'details': details }
