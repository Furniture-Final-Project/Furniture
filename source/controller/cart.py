import http
import schema
import flask
from sqlalchemy.orm import Session
from collections import defaultdict


def add_cart_item(session: Session, item_data: dict):
    """
    Adds item to cart - add item and user to the CartItem database
    param session: SQLAlchemy session object.
    param item_data: Dictionary containing user id, model number and quantity.
    return: None
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
    """
        Fetches details of a furniture item by model number.

        Queries the database for the item, calculates the final price with tax
        (considering any discount), and returns the details as a dictionary.

        Args:
            model_num (str): The model number of the furniture item.

        Returns:
            dict: Item details including the final price.
        """

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


def system_get_all_user_cart_items(user_id):
    """
        Retrieves all cart items for a given user.

        Fetches all items in the user's cart, calculates the total price, and
        returns the data in a structured format.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: A dictionary containing the user's cart items and the total price.
        """

    s = schema.session()
    query = s.query(schema.CartItem)
    query = query.filter(schema.CartItem.user_id == user_id)
    results = query.all()
    total_price = 0
    cart_items = defaultdict(list)  # Using defaultdict to store lists of items per user_id

    for result in results:
        cart_items[result.user_id].append(result.to_dict())  # Append instead of overwrite
        total_price += result.to_dict()['price']  # Summing prices correctly

    return {'carts': dict(cart_items), 'total_price': total_price}


def get_cart_user_details(user_id):
    """
        Retrieves user details based on user ID.

        Queries the database for the user and returns their details as a dictionary.

        Args:
            user_id (int): The ID of the user.

        Returns:
            dict: User details in dictionary format.
        """
    s = schema.session()
    query = s.query(schema.User)
    query = query.filter_by(user_id=user_id)
    result = query.first()
    return result.to_dict()


def update_cart_item_quantity(session: Session, item_data: dict):
    """
        Updates the quantity of a cart item for a user.

        If the quantity is zero, the item is removed from the cart.
        If the quantity exceeds available stock, an error is raised.
        Otherwise, the quantity is updated in the database.

        Args:
            session (Session): The database session.
            item_data (dict): Dictionary containing 'user_id', 'model_num', and 'quantity'.

        Raises:
            HTTPException: If the quantity is negative, item is not found, or stock is insufficient.
        """

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
    """
        Removes an item from the user's cart.

        If the item exists in the cart, it is deleted from the database.

        Args:
            session (Session): The database session.
            item_data (dict): Dictionary containing 'user_id' and 'model_num'.
        """
    item = session.get(schema.CartItem, (item_data["user_id"], item_data["model_num"]))
    if item:
        session.delete(item)
        session.commit()
