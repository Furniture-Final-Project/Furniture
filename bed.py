import schema


class Bed(schema.Furniture):

    def __init__(
        self,
        model_num: str,
        model_name: str,
        description: str,
        price: float,
        dimensions: dict,
        image_filename: str,
        details: dict,  # Stores mattress_type & frame_material
        stock_quantity : int,
        discount: float = 0.0,
    ):
        
        super().__init__(
            model_num=model_num,
            model_name=model_name,
            description=description,
            price=price,
            dimensions=dimensions,
            stock_quantity=stock_quantity,  # Default to 0 until updated
            details=details,  # Store all bed-specific attributes in details
            category="Bed",  # Ensure this is always set correctly
            image_filename=image_filename,
            discount=discount
        )

    def valid(self) -> bool:
        """Check if the given details dictionary contains valid mattress type and frame material."""
        VALID_MATTRESS_TYPES = {"latex", "memory foam", "bamboo", "spring", "hybrid", "cotton"}
        VALID_FRAME_MATERIALS = {"wood", "metal", "upholstered", "bamboo"}

        if not isinstance(self.details, dict):
            return False

        mattress_type = self.details.get("mattress_type", "").lower()
        frame_material = self.details.get("frame_material", "").lower()

        if mattress_type not in VALID_MATTRESS_TYPES:
            return False

        if frame_material not in VALID_FRAME_MATERIALS:
            return False
        
        if "width" not in self.dimensions:
            return False

        return True


    def get_size(self) -> str:
        """Determine the bed size based on its width."""
        width = self.dimensions["width"]

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
        return self.details["mattress_type"].lower() in hypoallergenic_materials

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
