from .Furniture import Furniture


class Chair(Furniture):

    def __init__(
        self,
        serial_number: int,
        name: str,
        description: str,
        price: int,
        dimension: dict,
        category: str,
        image_filename: str,
        material: str,
        weight: float,
        color: str,
        discount: float = 0.0,
    ):
        super().__init__(
            serial_number,
            name,
            description,
            price,
            dimension,
            category,
            image_filename,
            discount,
        )

        # Validate material type
        valid_materials = {"wood", "metal", "plastic", "leather", "fabric"}
        if material.lower() not in valid_materials:
            raise ValueError(
                f"Invalid material '{material}'. Choose from {valid_materials}."
            )

        # Validate weight
        if weight <= 0:
            raise ValueError("Weight must be a positive number.")

        self.material = material.lower()
        self.weight = weight
        self.color = color.capitalize()  # Capitalize color for readability

    def furniture_type(self):
        return "Chair"

    def __str__(self):
        return (
            f"Chair: {self.name} ({self.color}, {self.material})\n"
            f"Description: {self.description}\n"
            f"Material: {self.material}, Weight: {self.weight} kg\n"
            f"Price: ${self.get_discounted_price():.2f} (After Discount)\n"
            f"Dimensions: {self.dimension}\n"
            f"Image: {self.get_image_path()}"
        )
