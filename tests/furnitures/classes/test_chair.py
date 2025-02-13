import unittest
from source.models.Furniture import Chair


class TestChair(unittest.TestCase):

    def setUp(self):
        """Create a Chair object before each test"""
        self.chair = Chair(
            serial_number=101,
            name="Office Chair",
            description="Ergonomic office chair",
            price=250,
            dimension={"height": 120, "width": 60, "depth": 50},
            category="Office",
            image_filename="chair.jpg",
            material="leather",
            weight=12.5,
            color="black",
            discount=10.0,
        )

    def test_valid_initialization(self):
        """Test if Chair object is initialized correctly"""
        self.assertEqual(self.chair.name, "Office Chair")
        self.assertEqual(self.chair.description, "Ergonomic office chair")
        self.assertEqual(self.chair.price, 250)
        self.assertEqual(self.chair.dimension["height"], 120)
        self.assertEqual(self.chair.category, "Office")
        self.assertEqual(self.chair.image_filename, "chair.jpg")
        self.assertEqual(self.chair.material, "leather")
        self.assertEqual(self.chair.weight, 12.5)
        self.assertEqual(self.chair.color, "Black")  # Should be capitalized
        self.assertEqual(self.chair.discount, 10.0)

    def test_invalid_material(self):
        """Test that an invalid material raises a ValueError"""
        with self.assertRaises(ValueError):
            Chair(
                102,
                "Wooden Chair",
                "A solid wood chair",
                100,
                {},
                "Office",
                "wood_chair.jpg",
                "glass",
                10,
                "brown",
            )

    def test_invalid_weight(self):
        """Test that a non-positive weight raises a ValueError"""
        with self.assertRaises(ValueError):
            Chair(
                103,
                "Plastic Chair",
                "A lightweight chair",
                50,
                {},
                "Office",
                "plastic_chair.jpg",
                "plastic",
                -5,
                "white",
            )

    def test_furniture_type(self):
        """Test that furniture_type method returns 'Chair'"""
        self.assertEqual(self.chair.furniture_type(), "Chair")

    def test_apply_discount(self):
        """Test correct discount application"""
        expected_price = (250 * 1.18) * 0.90  # 18% tax, then 10% discount
        self.assertAlmostEqual(
            self.chair.get_discounted_price(), expected_price, places=2
        )

    def test_get_image_path(self):
        """Test correct image file path generation"""
        self.assertEqual(self.chair.get_image_path(), "images/chair.jpg")

    def test_str_representation(self):
        """Test the string representation of the Chair class"""
        expected_str = (
            "Chair: Office Chair (Black, leather)\n"
            "Description: Ergonomic office chair\n"
            "Material: leather, Weight: 12.5 kg\n"
            "Price: $238.05 (After Discount)\n"
            "Dimensions: {'height': 120, 'width': 60, 'depth': 50}\n"
            "Image: images/chair.jpg"
        )
        self.assertIn(
            "Chair: Office Chair (Black, leather)", str(self.chair)
        )  # Check a key part of the string


if __name__ == "__main__":
    unittest.main()
