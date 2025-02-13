import unittest
import os
from source.models.Furniture import Furniture


# Since Furniture has an abstract method (furniture_type), we create a dummy subclass TestFurniture that implements it.
class TestFurniture(Furniture):

    def furniture_type(self):
        return "TestType"


class TestFurnitureClass(unittest.TestCase):

    def setUp(self):
        """Creates a valid furniture object before each test"""
        self.furniture = TestFurniture(
            serial_number=101,
            name="Test Chair",
            description="comfortable chair.",
            price=200,
            dimension={"height": 100, "width": 50, "depth": 50},
            category="Office",
            image_filename="chair.jpg",
            discount=10.0,
        )

    def test_valid_initialization(self):
        """Tests that a Furniture object initializes correctly"""
        self.assertEqual(self.furniture.name, "Test Chair")
        self.assertEqual(self.furniture.description, "comfortable chair.")
        self.assertEqual(self.furniture.price, 200)
        self.assertEqual(self.furniture.dimension["height"], 100)
        self.assertEqual(self.furniture.dimension["width"], 50)
        self.assertEqual(self.furniture.dimension["depth"], 50)
        self.assertEqual(self.furniture.category, "Office")
        self.assertEqual(self.furniture.image_filename, "chair.jpg")
        self.assertEqual(self.furniture.discount, 10.0)

    def test_invalid_name(self):
        """Tests that an invalid name raises an exception"""
        with self.assertRaises(ValueError):
            TestFurniture(102, "", "Description", 150, {}, "Office", "image.jpg")

    def test_invalid_description(self):
        """Tests that an invalid description raises an exception"""
        with self.assertRaises(ValueError):
            TestFurniture(103, "Table", "", 150, {}, "Office", "image.jpg")

    def test_invalid_price(self):
        """Tests that a negative price raises an exception"""
        with self.assertRaises(ValueError):
            TestFurniture(104, "Table", "Nice Table", -50, {}, "Office", "image.jpg")

    def test_invalid_category(self):
        """Tests that an invalid category raises an exception"""
        with self.assertRaises(ValueError):
            TestFurniture(
                105, "Table", "Nice Table", 150, {}, "InvalidCategory", "image.jpg"
            )

    def test_invalid_image_filename(self):
        """Tests that an invalid image filename raises an exception"""
        with self.assertRaises(ValueError):
            TestFurniture(106, "Table", "Nice Table", 150, {}, "Office", "image.txt")

    def test_invalid_discount(self):
        """Tests that an invalid discount raises an exception"""
        with self.assertRaises(ValueError):
            TestFurniture(
                107, "Table", "Nice Table", 150, {}, "Office", "image.jpg", 150
            )

    def test_apply_tax(self):
        """Tests applying tax correctly"""
        expected_price = 200 * 1.18  # Default 18% tax
        self.assertAlmostEqual(self.furniture.apply_tax(), expected_price, places=2)

    def test_get_discounted_price(self):
        """Tests correct discounted price calculation"""
        expected_price = (200 * 1.18) * 0.90  # 18% tax, then 10% discount
        self.assertAlmostEqual(
            self.furniture.get_discounted_price(), expected_price, places=2
        )

    def test_calculate_discount(self):
        """Tests setting and calculating a new discount"""
        self.furniture.calculate_discount(20)  # Set new discount to 20%
        expected_price = (200 * 1.18) * 0.80  # 18% tax, then 20% discount
        self.assertAlmostEqual(
            self.furniture.get_discounted_price(), expected_price, places=2
        )

    def test_get_image_path(self):
        """Tests if image path is generated correctly"""
        self.assertEqual(
            self.furniture.get_image_path(), os.path.join("images", "chair.jpg")
        )


if __name__ == "__main__":
    unittest.main()
