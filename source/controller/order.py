import http
import schema
import flask
from sqlalchemy.orm import Session
from source.models.OrderStatus import OrderStatus
from source.controller.furniture_inventory import system_update_item_quantity


def add_order(session: Session, item_data: dict):
    """
    Adds a new order to the database.

    Args:
        session (Session): The database session.
        item_data (dict): A dictionary containing:
            - user_id (int): ID of the user placing the order.
            - items (dict): Dictionary of items in the order.
            - user_email (str): User's email address.
            - user_name (str): User's name.
            - shipping_address (str): Shipping address for the order.
            - total_price (float): Total cost of the order.

    Returns:
        int: The generated order number.

    Raises:
        HTTPException: If the order validation fails.
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
    Updates the status of an existing order.

    Args:
        session (Session): The database session.
        item_data (dict): A dictionary containing:
            - order_num (int): The order number.
            - status (str): The new order status.

    Returns:
        tuple: Empty string and HTTP status code (OK or NOT_FOUND).

    Raises:
        ValueError: If the provided status is invalid.
    """
    new_status_str = item_data['status']
    if new_status_str not in {status.value for status in OrderStatus}:
        flask.abort(http.HTTPStatus.BAD_REQUEST, f"Invalid status: {new_status_str}. Must be one of {[status.value for status in OrderStatus]}")

    new_status = OrderStatus(new_status_str)  # Convert string back to Enum

    order = session.get(schema.Order, item_data["order_num"])
    if not order:
        flask.abort(http.HTTPStatus.NOT_FOUND, "Order not found.")

    order.status = new_status  # Store the Enum instance
    session.commit()

    if new_status == OrderStatus.CANCELLED:
        for key, value in order.items:
            system_update_item_quantity(model_num=key, quantity_to_add=value)
