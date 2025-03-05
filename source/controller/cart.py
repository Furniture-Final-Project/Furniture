import http
import schema
import flask
from sqlalchemy.orm import Session


def add_cart_item(session: Session, item_data: dict):
    """
    Adds item to cart - add item and user to the CartItem database
    :param session: SQLAlchemy session object.
    :param item_data: Dictionary containing user id, model number and quantity.
    :return: None
    """

    cart = schema.CartItem.new(user_id=item_data['user_id'], model_num=item_data['model_num'], quantity=item_data['quantity'])

    # Validate user id in users table and model num in Furniture
    if not cart.valid():
        flask.abort(http.HTTPStatus.BAD_REQUEST, "Invalid user id or model number")

    # Validate item is in stock
    item_details = get_cart_item_full_details(cart.model_num)
    if item_details[item_data['model_num']]['stock_quantity'] < item_data['quantity']:
        flask.abort(
            http.HTTPStatus.CONFLICT, f"Not enough stock available, stock quantity is {item_details[item_data['model_num']]['stock_quantity']}"
        )
    session.add(cart)
    session.commit()


def get_cart_item_full_details(model_num):  # TODO: add integration tests
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
    print(item)
    item['final_price'] = final_price
    return item


def get_cart_user_details(user_id):
    s = schema.session()
    query = s.query(schema.User)
    query = query.filter_by(user_id=user_id)
    result = query.first()
    return result.to_dict()


def update_cart_item_quantity(session: Session, item_data: dict):
    # Validate new quantity is not negative
    if item_data["quantity"] < 0:
        flask.abort(http.HTTPStatus.BAD_REQUEST, "quantity cannot be negative")

    if item_data["quantity"] == 0:
        item = session.get(schema.CartItem, (item_data["user_id"], item_data["model_num"]))
        if item:
            session.delete(item)
            session.commit()
            return

    # Validate the new asked quantity is available in stock
    item_details = get_cart_item_full_details(item_data['model_num'])
    if item_details[item_data['model_num']]['stock_quantity'] < item_data['quantity']:
        flask.abort(
            http.HTTPStatus.CONFLICT, f"Not enough stock available, stock quantity is {item_details[item_data['model_num']]['stock_quantity']}"
        )

    item = session.get(schema.CartItem, (item_data["user_id"], item_data["model_num"]))
    if not item:
        flask.abort(http.HTTPStatus.NOT_FOUND, "Item not found in user's cart")
    else:
        item.quantity = item_data["quantity"]
        session.commit()


def delete_cart_item(session: Session, item_data: dict):
    item = session.get(schema.CartItem, (item_data["user_id"], item_data["model_num"]))
    if item:
        session.delete(item)
        session.commit()
