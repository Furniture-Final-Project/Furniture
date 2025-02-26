from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import String, Float, Integer, JSON, create_engine
from typing import Optional, Dict
import copy
import abc


class Base(DeclarativeBase):
    def to_dict(self):
        phase1 = {key: value for (key, value) in self.__dict__.items() if not key.startswith('_')}
        phase2 = copy.deepcopy(phase1)
        return phase2


class Furniture(Base):
    __tablename__ = "furniture"

    model_num: Mapped[str] = mapped_column(String, primary_key=True)
    model_name: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    dimensions: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    details: Mapped[Optional[Dict]] = mapped_column(JSON, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False)
    image_filename: Mapped[str] = mapped_column(String, nullable=False)
    discount: Mapped[float] = mapped_column(Float, nullable=False)

    def to_dict(self):
        result = Base.to_dict(self)
        if self.discount > 0.0:
            discount_price = self.price * (1 - self.discount / 100)
            result['final_price'] = self.apply_tax(discount_price)
        else:
            result['final_price'] = self.apply_tax(self.price)

        return result

    def apply_tax(self, final_price: float, tax_rate: float = 18) -> float:
        """Apply a tax rate to the price and return the new price."""
        return round(final_price * (1 + tax_rate / 100), 1)

    @staticmethod
    def new(
        model_num: str,
        model_name: str,
        description: str,
        price: float,
        dimensions: dict,
        stock_quantity: int,
        details: dict,
        image_filename: str,
        discount: float,
        category: str,
    ):
        class_map = {"Bed": Bed, "Chair": Chair, "Book Shelf": BookShelf, "Sofa": Sofa, "Table": Table}

        class_ = class_map[category]
        result = class_(
            model_num=model_num,
            model_name=model_name,
            description=description,
            price=price,
            dimensions=dimensions,
            stock_quantity=stock_quantity,
            details=details,
            image_filename=image_filename,
            discount=discount,
        )
        result.post_init()
        return result

    @abc.abstractmethod
    def valid(self) -> bool:
        pass

    @abc.abstractmethod
    def post_init(self) -> bool:
        pass


class Bed(Furniture):
    def post_init(self):
        self.category = "Bed"

    def valid(self):
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


class Chair(Furniture):
    def post_init(self):
        self.category = "Chair"

    def valid(self):
        # Validate material type
        VALID_MATERIALS = {"wood", "metal", "plastic", "leather", "fabric"}
        material = self.details.get("material", "").lower()
        if material not in VALID_MATERIALS:
            return False

        # Validate weight
        weight = self.details.get("weight", float)
        if weight <= 0:
            return False

        # Validate color
        if "color" not in self.details:
            return False

        return True


class BookShelf(Furniture):
    def post_init(self):
        self.category = "Book Shelf"

    def valid(self):
        # Validate number of shelves
        num_shelves = self.details.get("num_shelves")
        if not isinstance(num_shelves, int) or num_shelves <= 0:
            return False

        # Validate weight capacity per shelf
        max_capacity_weight_per_shelf = self.details.get("max_capacity_weight_per_shelf")
        if not isinstance(max_capacity_weight_per_shelf, (int, float)) or max_capacity_weight_per_shelf <= 0:
            return False

        # Validate material
        VALID_MATERIALS = {"wood", "metal", "glass", "plastic"}
        material = self.details.get("material", "").lower()
        if material not in VALID_MATERIALS:
            return False

        # Validate color
        if "color" not in self.details:
            return False

        return True

    def _calculate_total_capacity(self) -> float:
        """Calculate the total weight capacity of the bookshelf."""
        return self.details.get("num_shelves") * self.details.get("max_capacity_weight_per_shelf")


class Sofa(Furniture):
    def post_init(self):
        self.category = "Sofa"

    def valid(self):
        if "width" not in self.dimensions:
            return False

        # Validate upholstery material and dimension
        VALID_UPHOLSTERY_TYPES = {"leather", "fabric", "velvet", "synthetic"}
        upholstery = self.details.get("upholstery", "").lower()
        if upholstery not in VALID_UPHOLSTERY_TYPES:
            return False

        return True


class Table(Furniture):  # TODO seating_capacity
    def post_init(self):
        self.category = "Table"

    def valid(self):
        # Validate material
        VALID_MATERIALS = {"wood", "metal", "glass", "stone", "plastic", "acrylic", "laminate"}
        material = self.details.get("material", "").lower()
        if material not in VALID_MATERIALS:
            return False

        # Validate dimensions based on shape
        if self.dimensions.get("shape") == "rectangular" and not all(k in self.dimensions for k in ("length", "width")):
            return False

        if self.dimensions.get("shape") == "circular" and "diameter" not in self.dimensions:
            return False

        # validate "is_extendable"
        is_extendable = self.dimensions.get("is_extendable")
        if not isinstance(is_extendable, bool):
            return False

        return True


class User(Base):  # TODO - make it fit to user
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_name: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=True)

    def to_dict(self):
        result = Base.to_dict(self)
        return result

    def new(user_id: int, user_name: str, adress: str, email: str, password: str):
        result = User(user_id=user_id, user_name=user_name, adress=adress, email=email, password=password)
        return result


_engine = None
_session_maker = None


# Database setup
def create(database_url: str, echo: bool = True):
    global _engine
    global _session_maker
    _engine = create_engine(database_url, echo=echo)
    _session_maker = sessionmaker(bind=_engine)
    Base.metadata.create_all(_engine)


def session():
    return _session_maker()
