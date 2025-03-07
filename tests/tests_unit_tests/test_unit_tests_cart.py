import source.controller.cart as cart
import pytest
import app
import schema

# from unittest.mock import patch


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
    cart_item1 = schema.CartItem(user_id=1002, model_num='chair-0', quantity=2)
    cart_item2 = schema.CartItem(user_id=1003, model_num='BS-4004', quantity=2)
    cart_item3 = schema.CartItem(user_id=1002, model_num='SF-3003', quantity=1)

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
    session.add_all([cart_item1, cart_item2, cart_item3, bookshelf, chair0, sofa])
    session.commit()
    yield


def test_system_get_cart_items_by_user_id(client):
    cart_items = cart.system_get_all_user_cart_items(user_id=1002)
    print(cart_items)
    assert cart_items == {
        'carts': {
            1002: [
                {'model_name': 'LuxComfort', 'model_num': 'SF-3003', 'price': 1274.4, 'price_per_unit': 1274.4, 'quantity': 1, 'user_id': 1002},
                {'model_name': 'Yosef', 'model_num': 'chair-0', 'price': 236.0, 'price_per_unit': 118.0, 'quantity': 2, 'user_id': 1002},
            ]
        },
        'total_price': 1510.4,
    }
