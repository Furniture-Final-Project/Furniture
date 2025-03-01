# import unittest
# from unittest.mock import MagicMock

# # from source.models.Furniture import Furniture

# from source.controller.furniture_inventory import (
#     get_furniture_summary,
#     get_furniture_details,
# )


# class TestFurnitureFunctions(unittest.TestCase):

#     def setUp(self):
#         self.mock_inventory = MagicMock()
#         self.mock_furniture = MagicMock(spec=Furniture)

#         # Mocking furniture attributes
#         self.mock_furniture.model_name = "Luxury Chair"
#         self.mock_furniture.color = "Blue"
#         self.mock_furniture.material = "Wood"
#         self.mock_furniture.description = "A luxury wooden chair."
#         self.mock_furniture.weight = 12.5
#         self.mock_furniture.apply_tax.return_value = 117.00
#         self.mock_furniture.dimension = "40x40x90 cm"
#         self.mock_furniture.discount = 10
#         self.mock_furniture.get_discounted_price.return_value = 105.00
#         self.mock_furniture.get_image_path.return_value = "path/to/image.jpg"
#         self.mock_furniture.__str__.return_value = (
#             f"Chair: Luxury Chair (Blue, Wood)\n"
#             f"Description: A luxury wooden chair.\n"
#             f"Material: Wood, Weight: 12.5 kg\n"
#             f"Price: $105.00 (After Discount)\n"
#             f"Dimensions: 40x40x90 cm\n"
#             f"Image: path/to/image.jpg"
#         )

#         # Explicitly setting the method since `spec=Inventory` may not include it
#         self.mock_inventory.get_furniture_by_id = MagicMock(return_value=self.mock_furniture)
#         self.mock_inventory.check_availability = MagicMock(return_value=3)  # Low stock scenario

#     def test_get_furniture_summary_found(self):
#         summary = get_furniture_summary("123", self.mock_inventory)
#         self.assertIn("Luxury Chair", summary)
#         self.assertIn("117.00", summary)
#         self.assertIn("105.00", summary)  # Discounted price
#         self.assertIn("Hurry up!", summary)  # Low stock warning

#     def test_get_furniture_summary_not_found(self):
#         self.mock_inventory.get_furniture_by_id.return_value = None
#         summary = get_furniture_summary("999", self.mock_inventory)
#         self.assertEqual(summary, "Furniture not found.")

#     def test_get_furniture_summary_out_of_stock(self):
#         self.mock_inventory.check_availability.return_value = 0
#         summary = get_furniture_summary("123", self.mock_inventory)
#         self.assertIn("out of stock", summary)

#     def test_get_furniture_details_found(self):
#         details = get_furniture_details("123", self.mock_inventory)
#         self.assertIsInstance(details, dict)
#         self.assertIn("model_name", details)
#         self.assertIn("stock_quantity", details)
#         self.assertEqual(details["stock_quantity"], 3)

#     def test_get_furniture_details_not_found(self):
#         self.mock_inventory.get_furniture_by_id.return_value = None
#         details = get_furniture_details("999", self.mock_inventory)
#         self.assertIsNone(details)

#     def test_get_furniture_details_includes_properties(self):
#         type(self.mock_furniture).some_property = property(lambda self: "Property Value")
#         details = get_furniture_details("123", self.mock_inventory)

#         self.assertIn("some_property", details)
#         self.assertEqual(details["some_property"], "Property Value")


# if __name__ == "__main__":
#     unittest.main()
