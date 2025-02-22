from source.models.Furniture import Furniture
from source.models.Inventory import Inventory
import inspect

# from PIL import Image
import os


# needs tests
def get_furniture_summary(model_num: str, inventory: Inventory = None) -> str:
    """Returns summery description of a furniture: model name, the price after tax + discounted price (is discount >0), if it's in stock and the image),
    according to the model number of the furniture"""
    if inventory is None:
        inventory = Inventory()  # Default behavior: Use real Inventory

    furniture = inventory.get_furniture_by_id(model_num)

    if not furniture:  # If no furniture exists in inventory with this model number
        return "Furniture not found."

    stock_quantity = inventory.check_availability(furniture)
    details = []

    # Out of stock message
    if stock_quantity == 0:
        details.append("Item is out of stock.")

    # Basic details
    details.append(f"Model Name: {furniture.model_name}")
    details.append(f"Price (including tax): {furniture.apply_tax():.2f}")

    # Include price after discount only if discount is applied
    if furniture.discount > 0:
        details.append(f"Price after discount: {furniture.get_discounted_price():.2f}")

    # Low stock warning
    if stock_quantity < 5:
        details.append("Hurry up! This item is low in stock.")

    # Retrieve and display the image
    image_path = furniture.get_image_path()

    #    if os.path.exists(image_path):  # If it's a local file, show it
    #        img = Image.open(image_path)
    #        img.show()  # Opens the image in the default viewer (works in PyCharm)
    #    else:
    #
    # details.append(f"Image not found: {image_path}")  # Print path if missing

    return "\n".join(details)


def get_furniture_full_summery(model_num: str, inventory: Inventory = None) -> str:
    """Returns all information  for presenting on the furniture's web page
    according to the model number of the furniture"""
    if inventory is None:
        inventory = Inventory()  # Default behavior: Use real Inventory

    furniture = inventory.get_furniture_by_id(model_num)

    if not furniture:  # If no furniture exists in inventory with this model number
        return "Furniture not found."

    stock_quantity = inventory.check_availability(furniture)
    details = []

    # Out of stock message
    if stock_quantity == 0:
        details.append("Item is out of stock.")
    else:
        details.append(f"In stock: {stock_quantity} units.")

    # Identify the class of furniture
    furniture_type = type(furniture).__name__
    details.append(f"Furniture Type: {furniture_type}")

    # Basic details
    details.append(str(furniture))

    # Low stock warning
    if stock_quantity < 5:
        details.append("Hurry up! This item is low in stock.")

    # Retrieve and display the image
    image_path = furniture.get_image_path()

    #    if os.path.exists(image_path):  # If it's a local file, show it
    #        img = Image.open(image_path)
    #        img.show()  # Opens the image in the default viewer (works in PyCharm)
    #    else:
    #        details.append(f"Image not found: {image_path}")  # Print path if missing

    return "\n".join(details)


# this one is for internal system use - everything should return
def get_furniture_details(model_num: str, inventory: Inventory = None) -> dict:
    """Returns all information of a product as a dict
    according to the model number of the furniture"""

    if inventory is None:
        inventory = Inventory()  # Default behavior: Use real Inventory

    furniture = inventory.get_furniture_by_id(model_num)

    if not furniture:  # If no furniture exists in inventory with this model number
        return None

    stock_quantity = inventory.check_availability(furniture)

    details = vars(furniture).copy()
    # Find all property attributes
    properties = {
        name: getattr(furniture, name)
        for name, value in inspect.getmembers(
            type(furniture), lambda x: isinstance(x, property)
        )
    }

    details.update(properties)
    details["stock_quantity"] = stock_quantity

    return details
