# Temporarily remove this if it's causing an import issue
# from source.models.Furniture.Furniture import Furniture

import os
from abc import ABC, abstractmethod


class Furniture(ABC):  # Inherit from ABC to define an abstract base class

    def __init__(
        self,
        model_num: str,  # immutable
        model_name: str,
        description: str,
        price: int,
        dimension: dict,
        image_filename: str,
        discount: float = 0.0,
    ):

        if not isinstance(model_num, str) or not model_num.strip():
            raise ValueError("Model number must be a non-empty string.")
        self._model_num = model_num.upper()

        self.model_name = model_name
        self.description = description
        self.price = price
        self.dimension = dimension
        self.image_filename = image_filename
        self.discount = discount

    @property
    def model_num(self):
        return self._model_num  # Access the private attribute

    @property
    def model_name(self):
        return self._model_name  # Access the private attribute

    @model_name.setter
    def model_name(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Model Name must be a non-empty string.")
        self._model_name = value.upper()  # Corrected assignment

    @property
    def description(self):
        return self._description  # Access the private attribute

    @description.setter
    def description(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Description must be a non-empty string.")
        self._description = value.capitalize()  # Assign to the private attribute

    @property
    def price(self):
        return self._price  # Access the private attribute

    @price.setter
    def price(self, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Price must be a non-negative number.")
        self._price = value  # Assign to the private attribute

    @property
    def dimension(self):
        return self._dimension  # Access the private attribute

    @dimension.setter
    def dimension(self, value):
        if not isinstance(value, dict):
            raise ValueError("Dimension must be a dict.")
        self._dimension = value  # Assign to the private attribute

    @property
    def image_filename(self):
        return self._image_filename  # Access the private attribute

    @image_filename.setter
    def image_filename(self, value):
        if not isinstance(value, str) or not value.lower().endswith((".jpg", ".png", ".jpeg")):
            raise ValueError("Image filename must be a valid image file (.jpg, .png, .jpeg).")
        self._image_filename = value  # Assign to the private attribute

    @property
    def discount(self):
        return self._discount  # Access the private attribute

    @discount.setter
    def discount(self, value):
        if not isinstance(value, (int, float)) or not (0 <= value <= 100):
            raise ValueError("Discount must be a percentage between 0 and 100.")
        self._discount = value  # Assign to the private attribute

    @abstractmethod
    def furniture_type(self):
        """Declare the furniture type"""
        pass

    def apply_tax(self, tax_rate: float = 18) -> float:
        """Apply a tax rate to the price and return the new price."""
        return self.price * (1 + tax_rate / 100)

    def get_discounted_price(self) -> float:
        """Return the price after applying the discount and tax."""
        return self.apply_tax() * (1 - self.discount / 100)

    def calculate_discount(self, discount_percent: float) -> float:
        """Set a new discount percentage and return the discounted price."""
        self.discount = discount_percent
        return self.get_discounted_price()

    def get_image_path(self):
        """Return the relative path to the image file."""
        return os.path.join("images", self.image_filename)
