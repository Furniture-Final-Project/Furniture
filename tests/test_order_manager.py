import pytest
from source.models.Order import Order, OrderStatus
from source.services.order_manager import OrderManager

@pytest.fixture
def order_manager():
    return OrderManager()

@pytest.fixture
def sample_order():
    return Order(
        order_id=1,
        customer_name="Alice Doe",
        phone="987-654-3210",
        username="alicedoe",
        email="alice@example.com",
        shipping_address="456 Elm St, Springfield",
        items=["Bed", "Desk"],
        total_price=500.0
    )

def test_add_order(order_manager, sample_order):
    order_manager.add_order(sample_order)
    assert len(order_manager.orders) == 1

def test_get_order_by_id(order_manager, sample_order):
    order_manager.add_order(sample_order)
    retrieved_order = order_manager.get_order_by_id(1)
    assert retrieved_order is not None
    assert retrieved_order.customer_name == "Alice Doe"

def test_update_order_status(order_manager, sample_order):
    order_manager.add_order(sample_order)
    order_manager.update_order_status(1, OrderStatus.SHIPPED)
    assert sample_order.status == OrderStatus.SHIPPED

def test_cancel_order(order_manager, sample_order):
    order_manager.add_order(sample_order)
    assert order_manager.cancel_order(1) == True
    assert sample_order.status == OrderStatus.CANCELLED
