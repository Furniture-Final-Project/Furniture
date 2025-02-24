from .Furniture import Furniture


class Bed(Furniture):

    def __init__(
        self,
        model_num: str,
        model_name: str,
        description: str,
        price: float,
        dimension: dict,
        image_filename: str,
        mattress_type: str,
        frame_material: str,
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

        # Validate dimensions (must contain width)
        if "width" not in dimension:
            raise ValueError("Bed dimensions must include 'width'.")

        self.mattress_type = mattress_type
        self.frame_material = frame_material

    def furniture_type(self):
        return "Bed"

    @property
    def mattress_type(self):
        return self._mattress_type  # Access the private attribute

    @mattress_type.setter
    def mattress_type(self, value):
        # Validate mattress type
        valid_mattress_types = {
            "latex",
            "memory foam",
            "bamboo",
            "spring",
            "hybrid",
            "cotton",
        }
        if value.lower() not in valid_mattress_types:
            raise ValueError(
                f"Invalid mattress type '{value}'. Must be one of {valid_mattress_types}."
            )
        self._mattress_type = value.lower()

    @property
    def frame_material(self):
        return self._frame_material

    @frame_material.setter
    def frame_material(self, value):
        # Validate frame material
        valid_frame_materials = {"wood", "metal", "upholstered", "bamboo"}
        if value.lower() not in valid_frame_materials:
            raise ValueError(
                f"Invalid frame material '{value}'. Must be one of {valid_frame_materials}."
            )
        self._frame_material = value.lower()

    def get_size(self) -> str:
        """Determine the bed size based on its width."""
        width = self.dimension["width"]

        if width <= 100:
            return "Single"
        elif width <= 140:
            return "Double"
        elif width <= 160:
            return "Queen"
        else:
            return "King"

    def is_hypoallergenic(self) -> bool:
        """Check if the mattress material is hypoallergenic."""
        hypoallergenic_materials = {"latex", "memory foam", "bamboo"}
        return self.mattress_type in hypoallergenic_materials

    def __str__(self):
        hypoallergenic_status = "Yes" if self.is_hypoallergenic() else "No"
        return (
            f"Bed: {self.model_name} ({self.get_size()} size)\n"
            f"Description: {self.description}\n"
            f"Mattress Type: {self.mattress_type.capitalize()}, Hypoallergenic: {hypoallergenic_status}\n"
            f"Frame Material: {self.frame_material.capitalize()}\n"
            f"Price: ${self.get_discounted_price():.2f} (After Discount)\n"
            f"Dimensions: {self.dimension}\n"
            f"Image: {self.get_image_path()}"
        )
