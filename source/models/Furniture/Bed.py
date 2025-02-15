from .Furniture import Furniture
from sqlalchemy import Column, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from ..services.database import Base  # create the Base object


class Bed(Furniture, Base):
    __tablename__ = 'beds'  # Define the table name

    mattress_type = Column(String, nullable=False)
    frame_material = Column(String, nullable=False)
    # Note: The primary key 'model_number' is inherited from the Furniture table.
    # Since Bed inherits from Furniture, the 'model_number' column is already defined
    # in the Furniture table and serves as the primary key for the Bed table as well.

    def __init__(
        self,
        model_number: str,
        model_name: str,
        description: str,
        price: float,
        dimension: dict,
        image_filename: str,
        mattress_type: str,
        frame_material: str,
        discount: float = 0.0,
    ):
        super().__init__(
            model_number,
            model_name,
            description,
            price,
            dimension,
            image_filename,
            discount,
        )

        # Validate mattress type
        valid_mattress_types = {
            "latex",
            "memory foam",
            "bamboo",
            "spring",
            "hybrid",
            "cotton",
        }
        if mattress_type.lower() not in valid_mattress_types:
            raise ValueError(
                f"Invalid mattress type '{mattress_type}'. Must be one of {valid_mattress_types}."
            )

        # Validate frame material
        valid_frame_materials = {"wood", "metal", "upholstered", "bamboo"}
        if frame_material.lower() not in valid_frame_materials:
            raise ValueError(
                f"Invalid frame material '{frame_material}'. Must be one of {valid_frame_materials}."
            )

        # Validate dimensions (must contain width)
        if "width" not in dimension:
            raise ValueError("Bed dimensions must include 'width'.")

        self.mattress_type = mattress_type.lower()
        self.frame_material = frame_material.lower()

    def furniture_type(self):
        return "Bed"

    def get_size(self) -> str:
        """Determine the bed size based on its width."""
        width = self.dimension["width"]

        if width <= 100:
            return "Single"
        elif width <= 140:
            return "Double"
        elif width <= 160:
            return "Queen"
        else:
            return "King"

    def is_hypoallergenic(self) -> bool:
        """Check if the mattress material is hypoallergenic."""
        hypoallergenic_materials = {"latex", "memory foam", "bamboo"}
        return self.mattress_type in hypoallergenic_materials

    def __str__(self):
        hypoallergenic_status = "Yes" if self.is_hypoallergenic() else "No"
        return (
            f"Bed: {self.model_name} ({self.get_size()} size)\n"
            f"Description: {self.description}\n"
            f"Mattress Type: {self.mattress_type.capitalize()}, Hypoallergenic: {hypoallergenic_status}\n"
            f"Frame Material: {self.frame_material.capitalize()}\n"
            f"Price: ${self.get_discounted_price():.2f} (After Discount)\n"
            f"Dimensions: {self.dimension}\n"
            f"Image: {self.get_image_path()}"
        )
