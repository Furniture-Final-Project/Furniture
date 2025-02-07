import pytest
from source.models.Order import Order, OrderStatus


@pytest.fixture
def sample_order():
    """Fixture to create a sample order for testing."""
    return Order(
        order_id=1,
        customer_name="John Doe",
        phone="123-456-7890",
        username="johndoe",
        email="johndoe@example.com",
        shipping_address="123 Main St, Springfield",
        items=["Chair", "Table", "Lamp"],
        total_price=250.0
    )


def test_order_initialization(sample_order):
    """Test if the order initializes correctly."""
    assert sample_order.order_id == 1
    assert sample_order.customer_name == "John Doe"
    assert sample_order.status == OrderStatus.PENDING
    assert sample_order.total_price == 250.0


def test_update_status(sample_order):
    """Test updating the status of an order."""
    sample_order.update_status(OrderStatus.SHIPPED)
    assert sample_order.status == OrderStatus.SHIPPED

    sample_order.update_status(OrderStatus.DELIVERED)
    assert sample_order.status == OrderStatus.DELIVERED


def test_cancel_order_pending(sample_order):
    """Test cancelling an order with status 'pending'."""
    sample_order.cancel_order()
    assert sample_order.status == OrderStatus.CANCELLED


def test_cancel_order_after_shipped(sample_order):
    """Test cancelling an order that is not 'pending'."""
    sample_order.update_status(OrderStatus.SHIPPED)
    with pytest.raises(ValueError, match="Order cannot be cancelled as it has already been processed."):
        sample_order.cancel_order()


def test_order_history():
    """Test if the order history works properly (mocked example)."""
    orders = [
        Order(order_id=1, customer_name="John Doe", phone="123-456-7890", username="johndoe", email="johndoe@example.com",
              shipping_address="123 Main St, Springfield", items=["Chair"], total_price=100.0),
        Order(order_id=2, customer_name="John Doe", phone="123-456-7890", username="johndoe", email="johndoe@example.com",
              shipping_address="123 Main St, Springfield", items=["Table"], total_price=150.0),
    ]
    user_orders = [order for order in orders if order.username == "johndoe"]

    assert len(user_orders) == 2
    assert user_orders[0].order_id == 1
    assert user_orders[1].order_id == 2
