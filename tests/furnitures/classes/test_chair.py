import unittest
from source.models.Furniture import Chair


class TestChair(unittest.TestCase):

    def setUp(self):
        """Create a Chair object before each test"""
        self.chair = Chair(
            model_num="C001",
            model_name="Office Chair",
            description="Ergonomic office chair",
            price=250,
            dimension={"height": 120, "width": 60, "depth": 50},
            image_filename="chair.jpg",
            material="leather",
            weight=12.5,
            color="black",
            discount=10.0,
        )

    def test_valid_initialization(self):
        """Test if Chair object is initialized correctly"""
        self.assertEqual(self.chair.model_name, "OFFICE CHAIR")
        self.assertEqual(self.chair.model_num, "C001")
        self.assertEqual(self.chair.description, "Ergonomic office chair")
        self.assertEqual(self.chair.price, 250)
        self.assertEqual(self.chair.dimension["height"], 120)
        self.assertEqual(self.chair.image_filename, "chair.jpg")
        self.assertEqual(self.chair.material, "leather")
        self.assertEqual(self.chair.weight, 12.5)
        self.assertEqual(self.chair.color, "Black")  # Should be capitalized
        self.assertEqual(self.chair.discount, 10.0)

    def test_invalid_material(self):
        """Test that an invalid material raises a ValueError"""
        with self.assertRaises(ValueError):
            Chair(
                "C002",
                "Wooden Chair",
                "A solid wood chair",
                100,
                {},
                "wood_chair.jpg",
                "glass",
                10,
                "brown",
            )

    def test_material_setter(self):
        """Test that valid material values are correctly stored as lowercase."""
        self.chair.material = "Wood"
        self.assertEqual(self.chair.material, "wood")

    def test_invalid_material_assignment(self):
        """Test that assigning an invalid material raises ValueError."""
        with self.assertRaises(ValueError):
            self.chair.material = "stone"

    def test_weight_setter(self):
        """Test that weight is correctly assigned when valid."""
        self.chair.weight = 15.2
        self.assertEqual(self.chair.weight, 15.2)

    def test_invalid_weight(self):
        """Test that a non-positive weight raises a ValueError"""
        with self.assertRaises(ValueError):
            Chair(
                "C003",
                "Plastic Chair",
                "A lightweight chair",
                50,
                {},
                "plastic_chair.jpg",
                "plastic",
                -5,
                "white",
            )

    def test_invalid_weight_assignment(self):
        """Test that weight cannot be zero or negative."""
        with self.assertRaises(ValueError):
            self.chair.weight = 0

    def test_color_setter(self):
        """Test that color is correctly capitalized."""
        self.chair.color = "red"
        self.assertEqual(self.chair.color, "Red")

    def test_furniture_type(self):
        """Test that furniture_type method returns 'Chair'"""
        self.assertEqual(self.chair.furniture_type(), "Chair")

    def test_apply_discount(self):
        """Test correct discount application"""
        expected_price = (250 * 1.18) * 0.90  # 18% tax, then 10% discount
        self.assertAlmostEqual(
            self.chair.get_discounted_price(), expected_price, places=2
        )

    def test_discount_default(self):
        """Test that discount defaults to 0.0 when not provided."""
        chair_no_discount = Chair(
            "C004",
            "Dining Chair",
            "Wooden dining chair",
            200,
            {"height": 100, "width": 50, "depth": 40},
            "dining_chair.jpg",
            "wood",
            8.0,
            "brown",
        )
        self.assertEqual(chair_no_discount.discount, 0.0)

    def test_edge_case_weight(self):
        """Test the lowest possible valid weight value (close to zero)."""
        chair_light = Chair(
            "C005",
            "Feather Chair",
            "Super lightweight chair",
            150,
            {"height": 80, "width": 40, "depth": 30},
            "feather_chair.jpg",
            "plastic",
            0.1,
            "white",
        )
        self.assertAlmostEqual(chair_light.weight, 0.1)

    def test_edge_case_discount(self):
        """Test discount calculation for extreme values."""
        chair_no_discount = Chair(
            "C006",
            "Basic Chair",
            "Simple chair",
            100,
            {"height": 90, "width": 45, "depth": 35},
            "basic_chair.jpg",
            "plastic",
            5.0,
            "blue",
            0.0,
        )
        self.assertEqual(chair_no_discount.get_discounted_price(), 100 * 1.18)

        chair_full_discount = Chair(
            "C007",
            "Luxury Chair",
            "Expensive chair",
            500,
            {"height": 120, "width": 60, "depth": 50},
            "luxury_chair.jpg",
            "leather",
            20.0,
            "black",
            100.0,
        )
        self.assertEqual(chair_full_discount.get_discounted_price(), 0.0)

    def test_get_image_path(self):
        """Test correct image file path generation"""
        self.assertEqual(self.chair.get_image_path(), "images/chair.jpg")

    def test_str_representation(self):
        """Test the full string representation of the Chair class, including formatted price"""
        expected_price = "{:.2f}".format(
            self.chair.get_discounted_price()
        )  # Ensure correct rounding
        expected_str = (
            "Chair: OFFICE CHAIR (Black, leather)\n"
            "Description: Ergonomic office chair\n"
            "Material: leather, Weight: 12.5 kg\n"
            f"Price: ${expected_price} (After Discount)\n"  # Use formatted price
            "Dimensions: {'height': 120, 'width': 60, 'depth': 50}\n"
            "Image: images/chair.jpg"
        )
        self.assertEqual(str(self.chair), expected_str)

    def test_str_representation_no_discount(self):
        """Test string representation when no discount is applied."""
        chair_no_discount = Chair(
            "C008",
            "Wood Chair",
            "Classic wooden chair",
            300,
            {"height": 100, "width": 50, "depth": 40},
            "wood_chair.jpg",
            "wood",
            12.0,
            "brown",
        )
        expected_str = (
            "Chair: WOOD CHAIR (Brown, wood)\n"
            "Description: Classic wooden chair\n"
            "Material: wood, Weight: 12.0 kg\n"
            f"Price: ${300 * 1.18:.2f} (After Discount)\n"
            "Dimensions: {'height': 100, 'width': 50, 'depth': 40}\n"
            "Image: images/wood_chair.jpg"
        )
        self.assertEqual(str(chair_no_discount), expected_str)


if __name__ == "__main__":
    unittest.main()
