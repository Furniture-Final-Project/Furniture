from enum import Enum


class OrderStatus(Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order:
    def __init__(self, order_id, customer_name, phone, username, email, shipping_address, items, total_price,
                 status=OrderStatus.PENDING):
        """
        Initialize an Order object.

        :param order_id: Unique ID for the order.
        :param customer_name: Name of the customer.
        :param phone: Phone number of the customer.
        :param username: Username of the customer.
        :param email: Email address of the customer.
        :param shipping_address: Address to deliver the order.
        :param items: List of purchased items.
        :param total_price: Total price of the order.
        :param status: Status of the order (default is 'pending').
        """
        self.order_id = order_id
        self.customer_name = customer_name
        self.phone = phone
        self.username = username
        self.email = email
        self.shipping_address = shipping_address
        self.items = items
        self.total_price = total_price
        self.status = status

    def update_status(self, new_status):
        """
        Update the status of the order.

        :param new_status: New status to set for the order.
        :raises ValueError: If new_status is not a valid OrderStatus.
        """
        if not isinstance(new_status, OrderStatus):
            raise ValueError(f"Invalid status: {new_status}. Must be an instance of OrderStatus Enum.")
        self.status = new_status

    def cancel_order(self):
        """
        Cancel the order if its status is 'pending'.

        raises ValueError: If the order cannot be cancelled.
        """
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.CANCELLED
        else:
            raise ValueError("Order cannot be cancelled as it has already been processed.")
