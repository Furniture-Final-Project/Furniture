import unittest
import os
from source.models.Furniture import Furniture


# Since Furniture has an abstract method (furniture_type), we create a dummy subclass TestFurniture that implements it.
class TestFurniture(Furniture):
    __test__ = False

    def furniture_type(self):
        return "TestType"


class TestFurnitureClass(unittest.TestCase):

    def setUp(self):
        """Creates a valid furniture object before each test"""
        """Resets the model registry and creates a valid furniture object before each test"""
        print("Resetting VALID_MODELS before test")  # Debug print
        self.furniture = TestFurniture(
            model_num="TC123",
            model_name="Test Chair",
            description="comfortable chair.",
            price=200,
            dimension={"height": 100, "width": 50, "depth": 50},
            image_filename="chair.jpg",
            discount=10.0,
        )

    def test_valid_initialization(self):
        """Tests that a Furniture object initializes correctly"""
        self.assertEqual(self.furniture.model_name, "TEST CHAIR")
        self.assertEqual(self.furniture.model_num, "TC123")
        self.assertEqual(self.furniture.description, "Comfortable chair.")
        self.assertEqual(self.furniture.price, 200)
        self.assertEqual(self.furniture.dimension["height"], 100)
        self.assertEqual(self.furniture.dimension["width"], 50)
        self.assertEqual(self.furniture.dimension["depth"], 50)
        self.assertEqual(self.furniture.image_filename, "chair.jpg")
        self.assertEqual(self.furniture.discount, 10.0)

    def test_invalid_model_number(self):
        """Tests that an invalid model number raises an exception"""
        with self.assertRaises(ValueError):
            TestFurniture(
                "",
                "Test Chair",
                "comfortable chair",
                250,
                {"height": 120, "width": 60},
                "chair2.jpg",
            )

    def test_invalid_description(self):
        """Tests that an invalid description raises an exception"""
        with self.assertRaises(ValueError):
            TestFurniture("TD001", "Nordic dinning table", "", 150, {}, "image.jpg")

    def test_invalid_price(self):
        """Tests that a negative price raises an exception"""
        with self.assertRaises(ValueError):
            TestFurniture(
                "TD001",
                "Nordic dinning table",
                "Nice Table",
                -50,
                {},
                "image.jpg",
            )

    def test_invalid_image_filename(self):
        """Tests that an invalid image filename raises an exception"""
        with self.assertRaises(ValueError):
            TestFurniture(
                "TD001",
                "Nordic",
                "Nice Table",
                150,
                {},
                "image.txt",
            )

    def test_invalid_discount(self):
        """Tests that an invalid discount raises an exception"""
        with self.assertRaises(ValueError):
            TestFurniture(
                "TD001",
                "Nordic",
                "Nice Table",
                150,
                {},
                "image.jpg",
                150,
            )

    def test_apply_tax(self):
        """Tests applying tax correctly"""
        expected_price = 200 * 1.18  # Default 18% tax
        self.assertAlmostEqual(self.furniture.apply_tax(), expected_price, places=2)

    def test_get_discounted_price(self):
        """Tests correct discounted price calculation"""
        expected_price = (200 * 1.18) * 0.90  # 18% tax, then 10% discount
        self.assertAlmostEqual(self.furniture.get_discounted_price(), expected_price, places=2)

    def test_calculate_discount(self):
        """Tests setting and calculating a new discount"""
        self.furniture.calculate_discount(20)  # Set new discount to 20%
        expected_price = (200 * 1.18) * 0.80  # 18% tax, then 20% discount
        self.assertAlmostEqual(self.furniture.get_discounted_price(), expected_price, places=2)

    def test_get_image_path(self):
        """Tests if image path is generated correctly"""
        self.assertEqual(self.furniture.get_image_path(), os.path.join("images", "chair.jpg"))

    def test_update_price(self):
        """Tests updating price correctly"""
        self.furniture.price = 220
        self.assertEqual(self.furniture.price, 220)

    def test_update_discount(self):
        """Tests updating discount correctly"""
        self.furniture.discount = 30
        self.assertEqual(self.furniture.get_discounted_price(), self.furniture.price * 1.18 * 0.7)

    def test_update_description(self):
        """Tests updating description correctly - with capitalization"""
        self.furniture.description = "VERY Comfortable chair."
        self.assertEqual(self.furniture.description, "Very comfortable chair.")

    def test_model_num_immutable(self):
        """Tests that it is not possible to change model number for an existing  furniture"""
        with self.assertRaises(AttributeError):
            self.furniture.model_num = "B456"


if __name__ == "__main__":
    unittest.main()
