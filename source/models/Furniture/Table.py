from .Furniture import Furniture
from sqlalchemy import Column, String, Integer, Boolean
from ..services.database import Base  # Import the Base object


class Table(Furniture, Base):
    __tablename__ = 'tables'

    # Note: The primary key 'model_number' is inherited from the Furniture table.
    # Since Table inherits from Furniture, 'model_number' is already defined as the primary key.

    shape = Column(String, nullable=False)
    seating_capacity = Column(Integer, nullable=False)
    is_extendable = Column(Boolean, nullable=False)
    material = Column(String, nullable=False)

    def __init__(
        self,
        model_num: str,
        model_name: str,
        description: str,
        price: int,
        dimension: dict,
        image_filename: str,
        shape: str,
        seating_capacity: int,
        is_extendable: bool,
        material: str,
        discount: float = 0.0,
    ):
        super().__init__(
            model_num,
            model_name,
            description,
            price,
            dimension,
            image_filename,
            discount,
        )

        # Validate shape
        if shape not in {"rectangular", "circular"}:
            raise ValueError(
                f"Invalid shape '{shape}'. Supported shapes: 'rectangular', 'circular'."
            )

        # Validate dimensions based on shape
        if shape == "rectangular" and not all(
            k in dimension for k in ("length", "width")
        ):
            raise ValueError(
                "Rectangular tables must have 'length' and 'width' in dimensions."
            )
        if shape == "circular" and "diameter" not in dimension:
            raise ValueError("Circular tables must have 'diameter' in dimensions.")

        if seating_capacity <= 0:
            raise ValueError("Seating capacity must be at least 1.")

        self.shape = shape
        self.seating_capacity = seating_capacity
        self.is_extendable = is_extendable
        self.material = material

    def furniture_type(self):
        return "Table"

    def calculate_area(self) -> float:
        """Calculate the surface area of the table."""
        if self.shape == "rectangular":
            return self.dimension["length"] * self.dimension["width"]
        elif self.shape == "circular":
            radius = self.dimension["diameter"] / 2
            return 3.14 * (radius**2)
        raise ValueError("Unsupported table shape")

    def is_large_table(self) -> bool:
        """Check if the table is large based on seating capacity."""
        return self.seating_capacity > 6

    def __str__(self):
        extendable_status = "Yes" if self.is_extendable else "No"
        return (
            f"Table: {self.model_name} ({self.shape})\n"
            f"Description: {self.description}\n"
            f"Material: {self.material}, Price: ${self.get_discounted_price():.2f} (After Discount)\n"
            f"Seating Capacity: {self.seating_capacity}, Extendable: {extendable_status}\n"
            f"Dimensions: {self.dimension}, Area: {self.calculate_area():.2f} sq units\n"
            f"Image: {self.get_image_path()}"
        )
