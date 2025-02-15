from .Furniture import Furniture


class BookShelf(Furniture):

    def __init__(
        self,
        model_num: str,
        model_name: str,
        description: str,
        price: float,
        dimension: dict,
        image_filename: str,
        num_shelves: int,
        max_capacity_weight_per_shelf: float,
        material: str,
        color: str,
        discount: float = 0.0,
    ):
        super().__init__(
            model_num,
            model_name,
            description,
            price,
            dimension,
            image_filename,
            discount,
        )

        # Validate number of shelves
        if not isinstance(num_shelves, int) or num_shelves <= 0:
            raise ValueError("Number of shelves must be a positive integer.")

        # Validate weight capacity per shelf
        if (
            not isinstance(max_capacity_weight_per_shelf, (int, float))
            or max_capacity_weight_per_shelf <= 0
        ):
            raise ValueError("Max weight per shelf must be a positive number.")

        # Validate material
        valid_materials = {"wood", "metal", "glass", "plastic"}
        if material.lower() not in valid_materials:
            raise ValueError(
                f"Invalid material '{material}'. Choose from {valid_materials}."
            )

        self.num_shelves = num_shelves
        self.max_capacity_weight_per_shelf = max_capacity_weight_per_shelf
        self.material = material.lower()
        self.color = color.capitalize()  # Capitalize color for readability

    def furniture_type(self):
        return "Book Shelf"

    def calculate_total_capacity(self) -> float:
        """Calculate the total weight capacity of the bookshelf."""
        return self.num_shelves * self.max_capacity_weight_per_shelf

    def estimate_book_capacity(self, avg_book_weight: float = 0.5) -> int:
        """
        Estimate the number of books the bookshelf can hold.
        Default average book weight = 0.5 kg.
        """
        if avg_book_weight <= 0:
            raise ValueError("Average book weight must be a positive number.")
        return int(self.calculate_total_capacity() / avg_book_weight)

    def __str__(self):
        return (
            f"BookShelf: {self.model_name} ({self.material.capitalize()}, {self.color})\n"
            f"Description: {self.description}\n"
            f"Number of Shelves: {self.num_shelves}, Weight Capacity per Shelf: {self.max_capacity_weight_per_shelf} kg\n"
            f"Total Capacity: {self.calculate_total_capacity()} kg\n"
            f"Estimated Book Capacity: {self.estimate_book_capacity()} books\n"
            f"Price: ${self.get_discounted_price():.2f} (After Discount)\n"
            f"Dimensions: {self.dimension}\n"
            f"Image: {self.get_image_path()}"
        )
