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

    if not cart.valid():  # TODO: update
        flask.abort(http.HTTPStatus.BAD_REQUEST, "Invalid user id. did not find any matching user")

    session.add(cart)
    session.commit()


def get_cart_item_full_details(model_num):
    s = schema.session()
    query = s.query(schema.Furniture)
    query = query.filter_by(model_num=model_num)
    result = query.first()
    if result.discount > 0.0:
        discount_price = result.price * (1 - result.discount / 100)
        final_price = result.apply_tax(discount_price)
    else:
        final_price = result.apply_tax(result.price)

    item = {result.model_num: result.to_dict()}
    item['final_price'] = final_price
    return item
