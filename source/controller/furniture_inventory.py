import http
import schema
import flask
from sqlalchemy.orm import Session


# TODO- Add functionality to check if the model number already exists. If it does, update only the quantity.
def add_item(session: Session, item_data: dict) -> None:
    """
    Adds a new furniture item to the database with validation.

    Args:
        session (Session): SQLAlchemy session object.
        item_data (dict): Dictionary containing item details.

    Returns: None
    """
    item = schema.Furniture.new(
        model_num=item_data["model_num"],
        model_name=item_data["model_name"],
        description=item_data.get("description", ""),
        price=item_data["price"],
        dimensions=item_data["dimensions"],
        stock_quantity=item_data.get("stock_quantity", 0),
        details=item_data["details"],
        image_filename=item_data["image_filename"],
        discount=item_data["discount"],
        category=item_data.get("category", ""),
    )

    if not item.valid():
        flask.abort(http.HTTPStatus.BAD_REQUEST, "Invalid bed details provided.")

    session.add(item)
    session.commit()


def update_item_quantity(session: Session, data) -> None:
    """
    Updates the stock quantity of a furniture item.

    Args:
        session (Session): The database session.
        data (dict): A dictionary containing 'model_num' and the new 'stock_quantity'.
    """
    item = session.get(schema.Furniture, data["model_num"])
    if item:
        item.stock_quantity = data["stock_quantity"]
        session.commit()


def system_update_item_quantity(model_num: str, quantity_to_add: int) -> None:
    """
    Adjusts the stock quantity of a furniture item.

    Args:
        model_num (str): The model number of the item.
        quantity_to_add (int): The amount to add (or subtract if negative).
    """
    s = schema.session()
    item = s.get(schema.Furniture, model_num)
    if item:
        item.stock_quantity += quantity_to_add
    s.commit()


def delete_item(session: Session, model_num: str):
    """
    Removes a furniture item from the inventory.

    Args:
        session (Session): The database session.
        model_num (str): The model number of the item to delete.
    """
    item = session.get(schema.Furniture, model_num)
    if item:
        session.delete(item)
        session.commit()

def update_item_discount(session: Session, data): 
    item = session.get(schema.Furniture, data["model_num"])
    if item:
        item.discount = data["discount"]
        session.commit()   
