import unittest
from source.models import Sofa


class MyTestCase(unittest.TestCase):

    def setUp(self):
        """Create a Sofa object before each test"""
        self.sofa = Sofa(
            model_num="s100",
            model_name="Comfortable Sofa",
            description="Classic synthetic sofa",
            price=1250,
            dimension={"height": 120, "width": 280, "depth": 80},
            image_filename="sofa.jpg",
            upholstery="synthetic",
            color="White",
        )

    def test_valid_initialization(self):
        """Test if sofa object is initialized correctly"""
        self.assertEqual(self.sofa.model_num, "S100")
        self.assertEqual(self.sofa.model_name, "COMFORTABLE SOFA")
        self.assertEqual(self.sofa.description, "Classic synthetic sofa")
        self.assertEqual(self.sofa.price, 1250)
        self.assertEqual(self.sofa.dimension["width"], 280)
        self.assertEqual(self.sofa.image_filename, "sofa.jpg")
        self.assertEqual(self.sofa.upholstery, "synthetic")
        self.assertEqual(self.sofa.color, "White")  # Should be capitalized
        self.assertEqual(self.sofa.discount, 0.0)
        self.assertEqual(self.sofa.num_seats, 5)  # 280 / 55 = 5

    def test_invalid_upholstery(self):
        """Test that an invalid upholstery raises a ValueError"""
        with self.assertRaises(ValueError) as context:
            Sofa(
                model_num="S101",
                model_name="Comfortable Sofa",
                description="Classic synthetic sofa",
                price=1250,
                dimension={"height": 120, "width": 280, "depth": 80},
                image_filename="sofa.jpg",
                upholstery="Invalid upholstery type",
                color="White",
            )
        self.assertIn("Invalid upholstery type", str(context.exception))

    def test_color_capitalization(self):
        """Test if color input is always capitalized"""
        self.sofa.color = "blue"
        self.assertEqual(self.sofa.color, "Blue")

        self.sofa.color = "RED"
        self.assertEqual(self.sofa.color, "Red")

    def test_seating_capacity_edge_cases(self):
        """Test seating capacity calculation with edge case widths"""
        self.assertEqual(Sofa.calculate_seating_capacity(54), 1)  # Just below seat size
        self.assertEqual(Sofa.calculate_seating_capacity(55), 1)  # Exact seat size
        self.assertEqual(Sofa.calculate_seating_capacity(500), 9)  # Large width

    def test_missing_width_dimension(self):
        """Test if missing 'width' in dimension raises ValueError"""
        with self.assertRaises(ValueError) as context:
            Sofa(
                model_num="S101",
                model_name="Comfortable Sofa",
                description="A small, compact sofa",
                price=700,
                dimension={"depth": 80, "height": 75},  # Missing width
                image_filename="compact.jpg",
                upholstery="fabric",
                color="green",
            )
        self.assertIn("Sofa must have 'width' in dimensions.", str(context.exception))

    def test_invalid_dimension_format(self):
        """Test invalid dimension data type"""
        with self.assertRaises(ValueError):
            Sofa(
                model_num="S102",
                model_name="Luxury Sofa",
                description="A luxurious leather sofa",
                price=2000,
                dimension=None,  # Invalid type
                image_filename="luxury.jpg",
                upholstery="leather",
                color="black",
            )

    def test_non_integer_width(self):
        """Test width as a non-integer value"""
        with self.assertRaises(TypeError):
            Sofa(
                model_num="S103",
                model_name="Fancy Sofa",
                description="A stylish sofa",
                price=1500,
                dimension={"width": "two hundred", "height": 100},  # Invalid width
                image_filename="fancy.jpg",
                upholstery="velvet",
                color="pink",
            )

    def test_furniture_type(self):
        """Test if furniture_type() returns 'Sofa'"""
        self.assertEqual(self.sofa.furniture_type(), "Sofa")

    def test_calculate_seating_capacity(self):
        """Test the static method for seating capacity calculation"""
        self.assertEqual(Sofa.calculate_seating_capacity(165), 3)
        self.assertEqual(Sofa.calculate_seating_capacity(110), 2)
        self.assertEqual(Sofa.calculate_seating_capacity(54), 1)  # Minimum is 1 seat

    def test_str_representation(self):
        """Test the full string representation of the Sofa class, including formatted price"""
        expected_price = "{:.2f}".format(self.sofa.get_discounted_price())  # Ensure correct rounding
        expected_str = (
            f"Sofa: COMFORTABLE SOFA (White, synthetic)\n"
            f"Description: Classic synthetic sofa\n"
            f"Material: synthetic\n"
            f"Price: ${expected_price} (After Discount)\n"  # Use formatted price
            f"Number of Seats: {self.sofa.num_seats}\n"
            f"Dimensions: {self.sofa.dimension}\n"
            f"Image: {self.sofa.get_image_path()}"
        )
        self.assertEqual(str(self.sofa), expected_str)


if __name__ == "__main__":
    unittest.main()
