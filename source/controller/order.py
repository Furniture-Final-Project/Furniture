import http
import schema
import flask
from sqlalchemy.orm import Session
from source.models.OrderStatus import OrderStatus
from source.controller.furniture_inventory import system_update_item_quantity


def add_order(session: Session, item_data: dict):
    """
    Adds a new order to orders.
    :param session: SQLAlchemy session object.
    :param item_data: Dictionary containing user id, items dict, user email, username, shipping address, total price .
    :return: order_id
    """
    order = schema.Order.new(
        user_id=item_data['user_id'],
        items=item_data['items'],
        user_email=item_data['user_email'],
        user_name=item_data['user_name'],
        shipping_address=item_data['shipping_address'],
        total_price=item_data['total_price'],
    )

    # Validate order details
    is_valid, error_message = order.valid()

    if not is_valid:
        flask.abort(http.HTTPStatus.BAD_REQUEST, error_message)  # Return detailed error message

    session.add(order)
    session.commit()
    return order.order_num


def update_order_status(session: Session, item_data: dict):
    """
    Update the status of the order.
    :param new_status: New status to set for the order.
    :raises ValueError: If new_status is not a valid OrderStatus.
    """
    new_status_str = item_data['status']
    if new_status_str not in {status.value for status in OrderStatus}:
        raise ValueError(f"Invalid status: {new_status_str}. Must be one of {[status.value for status in OrderStatus]}")
    new_status = OrderStatus(new_status_str)  # Convert string back to Enum

    order = session.get(schema.Order, item_data["order_num"])
    if not order:
        return '', HTTPStatus.NOT_FOUND

    order.status = new_status  # Store the Enum instance
    session.commit()

    if new_status == OrderStatus.CANCELLED:
        for key, value in order.items:
            system_update_item_quantity(model_num=key, quantity_to_add=value)

    return '' , HTTPStatus.OK
