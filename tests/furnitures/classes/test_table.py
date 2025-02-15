import unittest
from source.models.Furniture import Table


class TestTable(unittest.TestCase):

    def setUp(self):
        self.valid_table = Table(
            model_num="t123",
            model_name="Dining Table",
            description="A sturdy wooden dining table.",
            price=500,
            dimension={"length": 200, "width": 100},
            image_filename="dining_table.jpg",
            shape="rectangular",
            seating_capacity=6,
            is_extendable=True,
            material="wood",
            discount=10.0,
        )

    def test_valid_table_initialization(self):
        self.assertEqual(self.valid_table.model_num, "T123")
        self.assertEqual(self.valid_table.model_name, "DINING TABLE")
        self.assertEqual(self.valid_table.furniture_type(), "Table")
        self.assertEqual(self.valid_table.description, "A sturdy wooden dining table.")
        self.assertEqual(self.valid_table.price, 500)
        self.assertEqual(self.valid_table.shape, "rectangular")
        self.assertEqual(self.valid_table.seating_capacity, 6)
        self.assertTrue(self.valid_table.is_extendable)
        self.assertEqual(self.valid_table.material, "wood")

    def test_invalid_shape(self):
        with self.assertRaises(ValueError):
            Table(
                "T124",
                "Invalid Table",
                "Shape not supported.",
                400,
                {"length": 100},
                "invalid.jpg",
                "hexagonal",
                4,
                False,
                "metal",
            )

    def test_missing_dimensions_for_rectangular(self):
        with self.assertRaises(ValueError):
            Table(
                "T125",
                "Rect Table",
                "Missing dimensions.",
                450,
                {"length": 150},
                "rect.jpg",
                "rectangular",
                4,
                False,
                "wood",
            )

    def test_missing_dimensions_for_circular(self):
        with self.assertRaises(ValueError):
            Table(
                "T126",
                "Circular Table",
                "Missing diameter.",
                350,
                {},
                "circ.jpg",
                "circular",
                4,
                False,
                "metal",
            )

    def test_invalid_seating_capacity(self):
        with self.assertRaises(ValueError):
            Table(
                "T127",
                "Tiny Table",
                "Invalid seating capacity.",
                200,
                {"diameter": 80},
                "tiny.jpg",
                "circular",
                0,
                False,
                "glass",
            )

    def test_calculate_area_rectangular(self):
        self.assertAlmostEqual(self.valid_table.calculate_area(), 20000.0)

    def test_calculate_area_circular(self):
        circular_table = Table(
            "T128",
            "Round Table",
            "A circular table.",
            300,
            {"diameter": 100},
            "round.jpg",
            "circular",
            4,
            False,
            "plastic",
        )
        self.assertAlmostEqual(circular_table.calculate_area(), 7850.0, places=1)

    def test_is_large_table(self):
        self.assertFalse(self.valid_table.is_large_table())
        large_table = Table(
            "T129",
            "Big Table",
            "A large table.",
            600,
            {"length": 250, "width": 120},
            "big.jpg",
            "rectangular",
            8,
            True,
            "wood",
        )
        self.assertTrue(large_table.is_large_table())

    def test_discount_price(self):
        self.assertAlmostEqual(
            self.valid_table.get_discounted_price(), 500 * 1.18 * 0.9, places=2
        )

    def test_str_representation(self):
        expected_price = "{:.2f}".format(self.valid_table.get_discounted_price())
        expected_str = (
            f"Table: DINING TABLE (rectangular)\n"
            "Description: A sturdy wooden dining table.\n"
            f"Material: wood, Price: ${expected_price} (After Discount)\n"
            "Seating Capacity: 6, Extendable: Yes\n"
            f"Dimensions: {self.valid_table.dimension}, Area: {self.valid_table.calculate_area():.2f} sq units\n"
            f"Image: {self.valid_table.get_image_path()}"
        )
        self.assertEqual(str(self.valid_table), expected_str)


if __name__ == "__main__":
    unittest.main()
