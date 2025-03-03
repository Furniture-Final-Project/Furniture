from enum import Enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class OrderStatus(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
