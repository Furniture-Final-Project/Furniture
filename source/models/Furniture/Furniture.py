import os
from abc import ABC, abstractmethod


# This class implements a Singleton-like pattern for managing a shared registry (VALID_MODELS) of model names and their corresponding model numbers,
# ensuring consistency and preventing mismatches across multiple instances of Furniture.
class Furniture:

    def __init__(
        self,
        model_num: str,  # key - unique between same models with different colors, dimension ... This value is given from the user
        model_name: str,  # Identify between same models with different sizes, color...
        description: str,
        price: int,
        dimension: dict,
        image_filename: str,
        discount: float = 0.0,
    ):
        # Validate model number
        if not isinstance(model_num, str) or not model_num.strip():
            raise ValueError("Model number must be a non-empty string.")

        # Validate model name
        if not isinstance(model_name, str) or not model_name.strip():
            raise ValueError("Model name must be a non-empty string.")

        # Validate description
        if not isinstance(description, str) or not description.strip():
            raise ValueError("Description must be a non-empty string.")

        # Validate price
        if not isinstance(price, (int, float)) or price < 0:
            raise ValueError("Price must be a non-negative number.")

        # Validate image filename
        if not isinstance(image_filename, str) or not image_filename.lower().endswith(
            (".jpg", ".png", ".jpeg")
        ):
            raise ValueError(
                "Image filename must be a valid image file (.jpg, .png, .jpeg)."
            )

        # Validate discount
        if not isinstance(discount, (int, float)) or not (0 <= discount <= 100):
            raise ValueError("Discount must be a percentage between 0 and 100.")

        self.model_num = model_num.upper()
        self.model_name = model_name.upper()
        self.description = description
        self.price = price
        self.dimension = (
            dimension  # Expecting a dict with keys: height, width, depth, diameter
        )
        self.image_filename = image_filename
        self.discount = discount

    @abstractmethod
    def furniture_type(self):
        """function that will declare the furniture type"""
        pass

    def get_price(self) -> float:
        """Return the base price of the furniture."""
        return self.price

    def apply_tax(self, tax_rate: float = 18) -> float:
        """Apply a tax rate to the price and return the new price."""
        return self.price * (1 + tax_rate / 100)

    def get_discounted_price(self) -> float:
        """Return the updated (including tax) price after applying the discount."""
        return self.apply_tax() * (1 - self.discount / 100)

    def check_availability(self) -> bool:
        """Check if the furniture is available (placeholder for actual logic)."""
        # Placeholder logic; replace with inventory check later
        return True

    def calculate_discount(self, discount_percent: float) -> float:
        """Set a new discount percentage and return the discounted price."""
        self.discount = discount_percent
        return self.get_discounted_price()

    def get_image_path(self):
        """Returns the relative path to the image file."""
        return os.path.join("images", self.image_filename)
