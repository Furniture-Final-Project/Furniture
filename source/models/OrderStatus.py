from enum import Enum
from sqlalchemy.ext.declarative import declarative_base

# Base class for SQLAlchemy models
Base = declarative_base()


class OrderStatus(Enum):
    """
    Enum representing the possible statuses of an order.

    Attributes:
        PENDING (str): The order has been placed but not yet processed.
        SHIPPED (str): The order has been shipped to the customer.
        DELIVERED (str): The order has been delivered successfully.
        CANCELLED (str): The order has been cancelled.
    """

    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
