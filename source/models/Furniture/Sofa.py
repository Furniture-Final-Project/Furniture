from .Furniture import Furniture


class Sofa(Furniture):

    def __init__(
        self,
        model_num: str,
        model_name: str,
        description: str,
        price: int,
        dimension: dict,
        image_filename: str,
        upholstery: str,
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

        # Validate upholstery material and dimension
        valid_upholstery_types = {"leather", "fabric", "velvet", "synthetic"}
        if upholstery.lower() not in valid_upholstery_types:
            raise ValueError(
                f"Invalid upholstery type '{upholstery}'. Choose from {valid_upholstery_types}."
            )
        if "width" not in self.dimension:
            raise ValueError("Sofa must have 'width' in dimensions.")

        self.upholstery = upholstery.lower()
        self.color = color.capitalize()

        # Call static method - calculate nu,ber of seats
        self.num_seats = Sofa.calculate_seating_capacity(self.dimension["width"])

    def furniture_type(self):
        return "Sofa"

    @staticmethod
    def calculate_seating_capacity(width: int, seat_width: int = 55) -> int:
        """Estimate the number of seats based on sofa length (default: 55 cm per seat)."""
        return max(1, width // seat_width)

    def __str__(self):
        return (
            f"Sofa: {self.model_name} ({self.color}, {self.upholstery})\n"
            f"Description: {self.description}\n"
            f"Material: {self.upholstery}\n"
            f"Price: ${self.get_discounted_price():.2f} (After Discount)\n"
            f"Number of Seats: {self.num_seats}\n"
            f"Dimensions: {self.dimension}\n"
            f"Image: {self.get_image_path()}"
        )
