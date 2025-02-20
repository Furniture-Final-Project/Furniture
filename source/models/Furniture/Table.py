from .Furniture import Furniture


class Table(Furniture):

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

        # Validate dimensions based on shape
        if shape == "rectangular" and not all(
            k in dimension for k in ("length", "width")
        ):
            raise ValueError(
                "Rectangular tables must have 'length' and 'width' in dimensions."
            )
        if shape == "circular" and "diameter" not in dimension:
            raise ValueError("Circular tables must have 'diameter' in dimensions.")

        self.shape = shape
        self.seating_capacity = seating_capacity
        self.is_extendable = is_extendable
        self.material = material

    def furniture_type(self):
        return "Table"

    @property
    def shape(self):
        return self._shape

    @shape.setter
    def shape(self, value):
        # Validate shape
        if value.lower() not in {"rectangular", "circular"}:
            raise ValueError(
                f"Invalid shape '{value}'. Supported shapes: 'rectangular', 'circular'."
            )
        self._shape = value

    @property
    def seating_capacity(self):
        return self._seating_capacity

    @seating_capacity.setter
    def seating_capacity(self, value):
        if value <= 0:
            raise ValueError("Seating capacity must be at least 1.")
        self._seating_capacity = value

    @property
    def is_extendable(self):
        return self._is_extendable

    @is_extendable.setter
    def is_extendable(self, value):
        if not isinstance(value, bool):
            raise ValueError("is_extendable must be a boolean.")
        self._is_extendable = value

    @property
    def material(self):
        return self._material

    @material.setter
    def material(self, value):
        valid_table_materials = [
            "wood",
            "metal",
            "glass",
            "stone",
            "plastic",
            "acrylic",
            "laminate",
        ]
        if value not in valid_table_materials:
            raise ValueError(f"Material must be one of {valid_table_materials}")
        self._material = value.lower()

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
