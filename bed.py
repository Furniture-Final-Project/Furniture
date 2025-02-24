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
        stock_quantity : int = 0,
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

        # Validate BEFORE assigning attributes
        if not self.validate_details(details):
            self.details = None
            raise ValueError("Invalid details: Mattress type or frame material is incorrect.")
             
        
         # Validate dimensions (must contain width)
        if "width" not in dimensions:
            self.dimensions= None
            raise ValueError("Bed dimensions must include 'width'.")
            


    def validate_details(self, details: dict) -> bool:
        """Check if the given details dictionary contains valid mattress type and frame material."""
        valid_mattress_types = {"latex", "memory foam", "bamboo", "spring", "hybrid", "cotton"}
        valid_frame_materials = {"wood", "metal", "upholstered", "bamboo"}

        if not isinstance(details, dict):
            return False

        mattress_type = details.get("mattress_type", "").lower()
        frame_material = details.get("frame_material", "").lower()

        if mattress_type not in valid_mattress_types:
            print(f"Invalid mattress type detected: {mattress_type}")
            return False

        if frame_material not in valid_frame_materials:
            print(f"Invalid frame material detected: {frame_material}")
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
