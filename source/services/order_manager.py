from source.models.Order import Order, OrderStatus

class OrderManager:
    def __init__(self):
        """ Initializes an empty order list. """
        self.orders = []

    def add_order(self, order):
        """ Adds a new order to the order list. """
        if not isinstance(order, Order):
            raise TypeError("Only Order objects can be added.")
        self.orders.append(order)

    def get_order_by_id(self, order_id):
        """ Retrieves an order by its ID. """
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    def update_order_status(self, order_id, new_status):
        """ Updates the status of an order given its ID. """
        order = self.get_order_by_id(order_id)
        if order:
            order.update_status(new_status)
            return True
        return False

    def cancel_order(self, order_id):
        """ Cancels an order if it is still pending. """
        order = self.get_order_by_id(order_id)
        if order:
            try:
                order.cancel_order()
                return True
            except ValueError:
                return False
        return False
