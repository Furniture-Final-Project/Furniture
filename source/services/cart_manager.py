import http
import schema
import flask
from sqlalchemy.orm import Session


def create_new_cart_for_user(session: Session, item_data: dict):
    """
    Adds a new cart to the database
    :param session: SQLAlchemy session object.
    :param item_data: Dictionary containing user id.
    :return: None
    """
    cart = schema.ShoppingCart.new(user_id=item_data['user_id'], items={})

    if not cart.valid():
        flask.abort(http.HTTPStatus.BAD_REQUEST, "Invalid user id. did not find any matching user")

    session.add(cart)
    session.commit()
