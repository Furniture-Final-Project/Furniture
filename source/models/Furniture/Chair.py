# Temporarily remove this if it's causing an import issue
# from source.models.Furniture.Furniture import Furniture

from schema import Furniture


class Chair(Furniture):

    def __init__(
        self,
        model_num: str,
        model_name: str,
        description: str,
        price: int,
        dimension: dict,
        image_filename: str,
        material: str,
        weight: float,
        color: str,
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

        self.material = material
        self.weight = weight
        self.color = color.capitalize()  # Capitalize color for readability

    def furniture_type(self):
        return "Chair"

    @property
    def material(self):
        return self._material  # Access the private attribute

    @material.setter
    def material(self, value):
        # Validate material type
        valid_materials = {"wood", "metal", "plastic", "leather", "fabric"}
        if value.lower() not in valid_materials:
            raise ValueError(
                f"Invalid material '{value}'. Choose from {valid_materials}."
            )
        self._material = value.lower()

    @property
    def weight(self):
        return self._weight  # Access the private attribute

    @weight.setter
    def weight(self, value):
        # Validate weight
        if value <= 0:
            raise ValueError("Weight must be a positive number.")
        self._weight = value

    @property
    def color(self):
        return self._color  # Access the private attribute

    @color.setter
    def color(self, value):
        self._color = value.capitalize()

    def __str__(self):
        return (
            f"Chair: {self.model_name} ({self.color}, {self.material})\n"
            f"Description: {self.description}\n"
            f"Material: {self.material}, Weight: {self.weight} kg\n"
            f"Price: ${self.get_discounted_price():.2f} (After Discount)\n"
            f"Dimensions: {self.dimension}\n"
            f"Image: {self.get_image_path()}"
        )
