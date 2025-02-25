import unittest
from source.models.Furniture import Bed


class TestBed(unittest.TestCase):

    def setUp(self):
        self.valid_bed = Bed(
            model_num="B123",
            model_name="Cozy Bed",
            description="A comfortable and stylish bed",
            price=1000.0,
            dimension={"width": 150, "length": 200},
            image_filename="cozy_bed.jpg",
            mattress_type="memory foam",
            frame_material="wood",
            discount=10,
        )

    def test_valid_bed_initialization(self):
        self.assertEqual(self.valid_bed.model_num, "B123")
        self.assertEqual(self.valid_bed.model_name, "COZY BED")
        self.assertEqual(self.valid_bed.description, "A comfortable and stylish bed")
        self.assertEqual(self.valid_bed.price, 1000)
        self.assertEqual(self.valid_bed.dimension["length"], 200)
        self.assertEqual(self.valid_bed.dimension["width"], 150)
        self.assertEqual(self.valid_bed.image_filename, "cozy_bed.jpg")
        self.assertEqual(self.valid_bed.mattress_type, "memory foam")
        self.assertEqual(self.valid_bed.frame_material, "wood")
        self.assertEqual(self.valid_bed.discount, 10)
        self.assertEqual(self.valid_bed.get_size(), "Queen")
        self.assertTrue(self.valid_bed.is_hypoallergenic())
        self.assertEqual(self.valid_bed.furniture_type(), "Bed")

    def test_invalid_mattress_type(self):
        with self.assertRaises(ValueError):
            Bed(
                "B124",
                "Luxury Bed",
                "A luxury bed.",
                2000.0,
                {"width": 180},
                "luxury.jpg",
                "plastic",
                "wood",
            )

    def test_invalid_frame_material(self):
        with self.assertRaises(ValueError):
            Bed(
                "B125",
                "Simple Bed",
                "A simple bed.",
                500.0,
                {"width": 120},
                "simple.jpg",
                "latex",
                "paper",
            )

    def test_missing_width_in_dimensions(self):
        with self.assertRaises(ValueError):
            Bed(
                "B126",
                "No Width Bed",
                "Missing width in dimensions.",
                800.0,
                {"length": 200},
                "nowidth.jpg",
                "bamboo",
                "metal",
            )

    def test_invalid_width_dimension(self):
        """Ensure ValueError is raised when 'width' is missing"""
        with self.assertRaises(ValueError):
            Bed(
                "B126",
                "No Width Bed",
                "Missing width in dimensions.",
                800.0,
                {"length": 200},  # Missing width
                "nowidth.jpg",
                "bamboo",
                "metal",
            )

    def test_setters_mattress_type(self):
        """Ensure the setter properly updates mattress type with valid input"""
        self.valid_bed.mattress_type = "latex"
        self.assertEqual(self.valid_bed.mattress_type, "latex")

        with self.assertRaises(ValueError):
            self.valid_bed.mattress_type = "plastic"  # Invalid type

    def test_setters_frame_material(self):
        """Ensure the setter properly updates frame material with valid input"""
        self.valid_bed.frame_material = "metal"
        self.assertEqual(self.valid_bed.frame_material, "metal")

        with self.assertRaises(ValueError):
            self.valid_bed.frame_material = "glass"  # Invalid material

    def test_get_size_boundaries(self):
        self.assertEqual(
            Bed(
                "B127",
                "Small Bed",
                "Small size.",
                300.0,
                {"width": 100},
                "small.jpg",
                "spring",
                "metal",
            ).get_size(),
            "Single",
        )
        self.assertEqual(
            Bed(
                "B128",
                "Double Bed",
                "Double size.",
                400.0,
                {"width": 140},
                "double.jpg",
                "latex",
                "wood",
            ).get_size(),
            "Double",
        )
        self.assertEqual(
            Bed(
                "B129",
                "Queen Bed",
                "Queen size.",
                600.0,
                {"width": 160},
                "queen.jpg",
                "memory foam",
                "upholstered",
            ).get_size(),
            "Queen",
        )
        self.assertEqual(
            Bed(
                "B130",
                "King Bed",
                "King size.",
                800.0,
                {"width": 200},
                "king.jpg",
                "hybrid",
                "wood",
            ).get_size(),
            "King",
        )

    def test_discount_price(self):
        self.assertAlmostEqual(self.valid_bed.get_discounted_price(), 1062.0)

    def test_extreme_discount(self):
        """Test discount calculation with extreme values"""
        self.valid_bed.discount = 100  # 100% discount
        self.assertEqual(self.valid_bed.get_discounted_price(), 0.0)

        with self.assertRaises(ValueError):
            self.valid_bed.discount = -5  # Negative discount (should not apply)

    def test_hypoallergenic_mattress(self):
        self.assertTrue(self.valid_bed.is_hypoallergenic())
        self.assertFalse(
            Bed(
                "B131",
                "Non-Hypo Bed",
                "Non-hypoallergenic.",
                700.0,
                {"width": 120},
                "nonhypo.jpg",
                "spring",
                "metal",
            ).is_hypoallergenic()
        )

    def test_str_representation(self):
        """Test the full string representation of the Bed class, including formatted price"""
        expected_price = "{:.2f}".format(self.valid_bed.get_discounted_price())  # Ensure correct rounding
        expected_str = (
            f"Bed: COZY BED (Queen size)\n"
            "Description: A comfortable and stylish bed\n"
            f"Mattress Type: Memory foam, Hypoallergenic: Yes\n"
            f"Frame Material: Wood\n"
            f"Price: ${expected_price} (After Discount)\n"
            f"Dimensions: {self.valid_bed.dimension}\n"
            f"Image: {self.valid_bed.get_image_path()}"
        )
        self.assertEqual(str(self.valid_bed), expected_str)


if __name__ == "__main__":
    unittest.main()
