class Furniture:
    def _init_(self, serial_number: int, name: str, description: str, price: int,
               dimension: dict, category: str, discount: float = 0.0):
        self.serial_number = serial_number
        self.name = name
        self.description = description
        self.price = price
        self.dimension = dimension  # Expecting a dict with keys: height, width, depth, diameter
        self.category = category
        self.discount = discount


    def get_price(self) -> float:
        """Return the base price of the furniture."""
        return self.price

    def apply_tax(self, tax_rate:float =18) -> float:
        """Apply a tax rate to the price and return the new price."""
        return self.price * (1 + tax_rate / 100)

    def get_discounted_price(self) -> float:
        """Return the updated (including tax) price after applying the discount."""
        return self.apply_tax() * (1 - self.discount / 100)

    def check_availability(self) -> bool:
        """Check if the furniture is available (placeholder for actual logic)."""
        # Placeholder logic; replace with inventory check later
        return True

    def calculate_discount(self, discount_percent: float) -> float:
        """Set a new discount percentage and return the discounted price."""
        self.discount = discount_percent
        return self.get_discounted_price()


