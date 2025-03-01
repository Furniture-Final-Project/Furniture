import http
import schema
import flask
from sqlalchemy.orm import Session


def add_cart_item(session: Session, item_data: dict):
    """
    Adds item to cart - add item and user to the CartItem database
    :param session: SQLAlchemy session object.
    :param item_data: Dictionary containing user id.
    :return: None
    """
    cart = schema.CartItem.new(user_id=item_data['user_id'], model_num=item_data['model_num'], quantity=item_data['quantity'])

    if not cart.valid(): #TODO: update
        flask.abort(http.HTTPStatus.BAD_REQUEST, "Invalid user id. did not find any matching user")

    session.add(cart)
    session.commit()