import json
import http
import schema
import flask
from bed import Bed
from sqlalchemy.orm import Session


def add_item(session: Session, item_data: dict) -> str:
    """
    Adds a new furniture item to the database with validation.

    Args:
        session (Session): SQLAlchemy session object.
        item_data (dict): Dictionary containing item details.

    Returns:
        str: Success or error message.
    """
    category = item_data.get("category")

    if category == "Bed":
        # Instantiate Bed class to validate attributes
        bed = Bed(
            model_num=item_data["model_num"],
            model_name=item_data["model_name"],
            description=item_data.get("description", ""),
            price=item_data["price"],
            dimensions=item_data["dimensions"],
            stock_quantity=item_data.get("stock_quantity", 0),
            details=item_data["details"],  # Contains mattress_type & frame_material
            image_filename=item_data["image_filename"],
            discount=item_data.get("discount", 0.0)
        )
        if not bed.valid():
            flask.abort(http.HTTPStatus.BAD_REQUEST, "Invalid bed details provided.")

        session.add(bed)
        session.commit()
