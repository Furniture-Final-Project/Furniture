# import unittest
# from unittest.mock import MagicMock, patch
# from source.services.furniture_service import get_furniture_price_details
# from source.models.Furniture import Furniture
#
#
# class TestFurnitureService(unittest.TestCase):
#
#     @patch("source.services.furniture_service.Inventory")  # Patch for inventory class
#     def test_get_furniture_price_details_found(self, MockInventory):
#         """Test that the function returns correct prices when furniture is in stock"""
#         mock_inventory = MockInventory()  # Using mock instead of he actual inventory
#         mock_inventory.get_furniture_by_id.return_value = Furniture(
#             model_num="TC123",
#             model_name="Test Chair",
#             description="comfortable chair.",
#             price=200,
#             dimension={"height": 100, "width": 50, "depth": 50},
#             image_filename="chair.jpg",
#             discount=10.0,
#         )
#         result = get_furniture_price_details("TC123")
#         expected_result = {
#             "model name": "TEST CHAIR",
#             "price (including tax)": 200 * 1.18,
#             "price after discount": 200 * 1.18 * 0.9,
#         }
#         self.assertEqual(result, expected_result)
#
#     @patch("source.services.furniture_service.Inventory")  # Patch for inventory class
#     def test_get_furniture_details_not_found(self, MockInventory):
#         """Test that the function returns None when no furniture is found in th inventory"""
#         mock_inventory = MockInventory()
#         mock_inventory.get_furniture_by_id.return_value = None
#
#         result = get_furniture_price_details("TC123")
#
#
# if __name__ == "__main__":
#     unittest.main()
