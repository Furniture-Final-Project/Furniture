# Temporarily remove this if it's causing an import issue
# from source.models.Furniture.Furniture import Furniture

from schema import Furniture


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

        if "width" not in self.dimension:
            raise ValueError("Sofa must have 'width' in dimensions.")

        self.upholstery = upholstery
        self.color = color

        # Call static method - calculate nu,ber of seats
        self.num_seats = Sofa.calculate_seating_capacity(self.dimension["width"])

    def furniture_type(self):
        return "Sofa"

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value.capitalize()

    @property
    def upholstery(self):
        return self._upholstery

    @upholstery.setter
    def upholstery(self, value):
        # Validate upholstery material and dimension
        valid_upholstery_types = {"leather", "fabric", "velvet", "synthetic"}
        if value.lower() not in valid_upholstery_types:
            raise ValueError(f"Invalid upholstery type '{value}'. Choose from {valid_upholstery_types}.")
        self._upholstery = value.lower()

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
