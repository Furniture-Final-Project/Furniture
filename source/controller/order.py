import http
import schema
import flask
from sqlalchemy.orm import Session


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
