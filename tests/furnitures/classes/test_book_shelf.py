import unittest
from source.models.Furniture import BookShelf


class TestBookShelf(unittest.TestCase):

    def setUp(self):
        self.valid_bookshelf = BookShelf(
            model_num="BS123",
            model_name="Classic Shelf",
            description="A sturdy wooden bookshelf.",
            price=300.0,
            dimension={"height": 180, "width": 80, "depth": 30},
            image_filename="classic_shelf.jpg",
            num_shelves=5,
            max_capacity_weight_per_shelf=20.0,
            material="wood",
            color="brown",
            discount=10.0,
        )

    def test_valid_bookshelf_initialization(self):
        self.assertEqual(self.valid_bookshelf.model_num, "BS123")
        self.assertEqual(self.valid_bookshelf.model_name, "CLASSIC SHELF")
        self.assertEqual(self.valid_bookshelf.description, "A sturdy wooden bookshelf.")
        self.assertEqual(self.valid_bookshelf.furniture_type(), "Book Shelf")
        self.assertEqual(self.valid_bookshelf.price, 300.0)
        self.assertEqual(self.valid_bookshelf.dimension["height"], 180)
        self.assertEqual(self.valid_bookshelf.discount, 10.0)
        self.assertEqual(self.valid_bookshelf.num_shelves, 5)
        self.assertEqual(self.valid_bookshelf.material, "wood")
        self.assertEqual(self.valid_bookshelf.color, "Brown")

    def test_invalid_num_shelves(self):
        with self.assertRaises(ValueError):
            BookShelf(
                "BS124",
                "Shelf",
                "Invalid shelves",
                250.0,
                {"height": 150},
                "shelf.jpg",
                0,
                20.0,
                "wood",
                "white",
            )

    def test_invalid_weight_capacity(self):
        with self.assertRaises(ValueError):
            BookShelf(
                "BS125",
                "Shelf",
                "Invalid weight",
                250.0,
                {"height": 150},
                "shelf.jpg",
                3,
                -10.0,
                "wood",
                "white",
            )

    def test_invalid_material(self):
        with self.assertRaises(ValueError):
            BookShelf(
                "BS126",
                "Shelf",
                "Invalid material",
                250.0,
                {"height": 150},
                "shelf.jpg",
                3,
                15.0,
                "stone",
                "white",
            )

    def test_total_capacity_calculation(self):
        self.assertEqual(self.valid_bookshelf.calculate_total_capacity(), 100.0)

    def test_estimate_book_capacity(self):
        self.assertEqual(self.valid_bookshelf.estimate_book_capacity(), 200)

    def test_estimate_book_capacity_invalid_weight(self):
        with self.assertRaises(ValueError):
            self.valid_bookshelf.estimate_book_capacity(0)

    def test_discount_price(self):
        self.assertAlmostEqual(
            self.valid_bookshelf.get_discounted_price(), 300 * 1.18 * 0.9, places=2
        )

    def test_valid_edge_cases(self):
        shelf = BookShelf(
            "BS127",
            "Small Shelf",
            "Minimalist",
            100.0,
            {"height": 50, "width": 30, "depth": 20},
            "small_shelf.jpg",
            1,
            0.1,
            "glass",
            "black",
        )
        self.assertEqual(shelf.num_shelves, 1)
        self.assertEqual(shelf.max_capacity_weight_per_shelf, 0.1)

    def test_estimate_book_capacity_varied_weights(self):
        self.assertEqual(self.valid_bookshelf.estimate_book_capacity(0.2), 500)
        self.assertEqual(self.valid_bookshelf.estimate_book_capacity(2.0), 50)

    def test_case_insensitive_material(self):
        shelf = BookShelf(
            "BS129",
            "Case Test",
            "Mixed case material",
            150.0,
            {"height": 100, "width": 50},
            "case_shelf.jpg",
            3,
            10.0,
            "WoOd",
            "yellow",
        )
        self.assertEqual(shelf.material, "wood")

    def test_get_image_path(self):
        self.assertTrue(hasattr(self.valid_bookshelf, "get_image_path"))

    def test_str_representation(self):
        expected_price = "{:.2f}".format(self.valid_bookshelf.get_discounted_price())
        expected_str = (
            f"BookShelf: CLASSIC SHELF (Wood, Brown)\n"
            "Description: A sturdy wooden bookshelf.\n"
            "Number of Shelves: 5, Weight Capacity per Shelf: 20.0 kg\n"
            "Total Capacity: 100.0 kg\n"
            "Estimated Book Capacity: 200 books\n"
            f"Price: ${expected_price} (After Discount)\n"
            f"Dimensions: {self.valid_bookshelf.dimension}\n"
            f"Image: {self.valid_bookshelf.get_image_path()}"
        )
        self.assertEqual(str(self.valid_bookshelf), expected_str)


if __name__ == "__main__":
    unittest.main()
