import json
import http
import schema
import flask
from sqlalchemy.orm import Session


def add_item(session: Session, item_data: dict):
    """
    Adds a new furniture item to the database with validation.

    Args:
        session (Session): SQLAlchemy session object.
        item_data (dict): Dictionary containing item details.

    Returns:
    # TODO 
    """
    item = schema.new(
                        model_num=item_data["model_num"],
                        model_name=item_data["model_name"],
                        description=item_data.get("description", ""),
                        price=item_data["price"],
                        dimensions=item_data["dimensions"],
                        stock_quantity=item_data.get("stock_quantity", 0),
                        details=item_data["details"], 
                        image_filename=item_data["image_filename"],
                        discount=item_data["discount"],
                        category=item_data.get("category", "")
                      )
    
    if not item.valid():
        flask.abort(http.HTTPStatus.BAD_REQUEST, "Invalid bed details provided.")

    session.add(item)
    session.commit()


def update_item_quantity(session: Session, data):
    item = session.get(schema.Furniture, data["model_num"])
    if item:
        item.stock_quantity = data["stock_quantity"]
        session.commit()


