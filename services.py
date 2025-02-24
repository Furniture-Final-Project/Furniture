import json
import schema
from source.models.furniture.bed import Bed
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
        try:
            # Instantiate Bed class to validate attributes
            bed = Bed(
                model_num=item_data["model_num"],
                model_name=item_data["model_name"],
                description=item_data.get("description", ""),
                price=item_data["price"],
                dimensions=item_data["dimensions"],
                image_filename=item_data["image_filename"],
                details=item_data["details"],  # Contains mattress_type & frame_material
                discount=item_data.get("discount", 0.0)
            )

            # Ensure validation passes
            bed.validate_details()

            # Create Furniture instance to store in DB
            new_furniture = schema.Furniture(
                model_num=bed.model_num,
                model_name=bed.model_name,
                description=bed.description,
                price=bed.price,
                dimensions=bed.dimensions,  # Stored as JSON
                stock_quantity=item_data.get("stock_quantity", 0),
                details=json.dumps(bed.details),  # Store subclass attributes as JSON
                category="Bed",  # Ensure correct category
                image_filename=bed.image_filename,
                discount=bed.discount
            )

            session.add(new_furniture)
            session.commit()
            return f"Item '{bed.model_num}' added successfully!"

        except ValueError as e:
            session.rollback()
            return f"Error: {str(e)}"

    return "Unsupported category!"

