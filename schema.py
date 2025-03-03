from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import String, Float, Integer, JSON, create_engine, PrimaryKeyConstraint, DateTime
from typing import Optional, Dict
import copy
import abc
from datetime import datetime
import source.controller.cart as cart
import source.controller.user as user
from source.models.OrderStatus import OrderStatus
from sqlalchemy import Enum as SQLAlchemyEnum


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
    user_name: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    user_full_name: Mapped[str] = mapped_column(String, nullable=True)
    user_phone_num: Mapped[str] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=True)
    password: Mapped[str] = mapped_column(String, nullable=True)

    def to_dict(self):
        result = Base.to_dict(self)
        return result

    @staticmethod
    def new(user_id: int, user_name: str, user_full_name: str, user_phone_num: str, address: str, email: str, password: str):
        result = User(
            user_id=user_id,
            user_name=user_name,
            user_full_name=user_full_name,
            user_phone_num=user_phone_num,
            address=address,
            email=email,
            password=password,
        )
        return result


class CartItem(Base):
    __tablename__ = "CartItem"

    user_id: Mapped[int] = mapped_column(Integer)
    model_num: Mapped[dict] = mapped_column(String)
    quantity: Mapped[int] = mapped_column(Integer, nullable=True)

    __table_args__ = (PrimaryKeyConstraint("user_id", "model_num"),)

    def to_dict(self):
        result = Base.to_dict(self)
        item_details = cart.get_cart_item_full_details(self.model_num)
        if item_details:
            result['model_name'] = item_details[self.model_num]['model_name']
            result['price_per_unit'] = item_details[self.model_num]['final_price']
            result['price'] = item_details[self.model_num]['final_price'] * result['quantity']
        return result

    @staticmethod
    def new(user_id: int, model_num: str, quantity: int):
        """
        Add new item for a user cart.

        :param user_id: The ID of the user who owns the cart, the model number of the item that has been added to cart.
        :param model_num: The model number of the item that has been added to cart.
        :return: A new instance of CartItem.
        """
        result = CartItem(user_id=user_id, model_num=model_num, quantity=quantity)
        return result

    def valid(self):
        # Validate model number
        item = cart.get_cart_item_full_details(self.model_num)
        client = user.get_user_details(self.user_id)

        if not item or not client:
            return False
        return True
        # TODO: Test integration


# ---------------Order Table----------------
# -----------------Order Table---------------------
class Order(Base):
    __tablename__ = "order"

    order_num: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    user_email: Mapped[str] = mapped_column(String, nullable=True)
    shipping_address: Mapped[str] = mapped_column(String, nullable=True)
    items: Mapped[dict] = mapped_column(JSON, nullable=True)
    total_price: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[OrderStatus] = mapped_column(SQLAlchemyEnum(OrderStatus), nullable=False)
    creation_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def to_dict(self):
        result = Base.to_dict(self)
        customer = user.get_user_details(self.user_id)
        result['phone_number'] = customer[self.user_id]['user_phone_num']
        result['user_name'] = customer[self.user_id]['user_name']
        result['user_full_name'] = customer[self.user_id]['user_full_name']
        result['status'] = self.status.name

        return result

    @staticmethod
    def new(user_id: int, items: dict, user_email: str, user_name: str, shipping_address: str, total_price: float):
        """
        Add new order.

        :param user_id: The ID of the user who made the purchase.
        :param items: Items dictionary, the items that have been purchased in the order [model_num: quantity]
        :param user_email: The email address of the user who made the purchase.
        :param shipping_address: The shipping address of the user who made the purchase.
        :param user_name: The username of the user who made the purchase.
        :param total_price: The total price of the order.
        :return: A new instance of CartItem.
        """
        new_order = Order(
            user_id=user_id,
            items=items,
            user_email=user_email,
            shipping_address=shipping_address,
            total_price=total_price,
            status=OrderStatus.PENDING,
            creation_time=datetime.utcnow(),
        )
        #  Order num is generated automatic

        return new_order

    def valid(self):
        """
        Validate the order and return (True, None) if valid, or (False, error_message) if not.
        """

        # Validate user ID exists
        customer = user.get_user_details(self.user_id)
        if not customer:
            return False, "Invalid user ID. User does not exist."

        # Validate total price is greater than 0
        if self.total_price <= 0:
            return False, "Total price must be greater than zero."

        # Validate items is not an empty dict
        if not self.items:
            return False, "Order must contain at least one item."

        # Validate all items exist and have valid quantities
        for key, value in self.items.items():
            if not cart.get_cart_item_full_details(key):
                return False, f"Item with model_num {key} does not exist."
            if not isinstance(value, (int, float)) or value <= 0:
                return False, f"Invalid quantity for item {key}. Quantity must be greater than zero."

        return True, None  # No errors


# class Order:
#     def __init__(self, order_id, customer_name, phone, username, email, shipping_address, items, total_price,
#                  status=OrderStatus.PENDING):
#         """
#         Initialize an Order object.
#
#         :param order_id: Unique ID for the order.
#         :param customer_name: Name of the customer.
#         :param phone: Phone number of the customer.
#         :param username: Username of the customer.
#         :param email: Email address of the customer.
#         :param shipping_address: Address to deliver the order.
#         :param items: List of purchased items.
#         :param total_price: Total price of the order.
#         :param status: Status of the order (default is 'pending').
#         """
#         self.order_id = order_id
#         self.customer_name = customer_name
#         self.phone = phone
#         self.username = username
#         self.email = email
#         self.shipping_address = shipping_address
#         self.items = items
#         self.total_price = total_price
#         self.status = status
#
#     def update_status(self, new_status):
#         """
#         Update the status of the order.
#
#         :param new_status: New status to set for the order.
#         :raises ValueError: If new_status is not a valid OrderStatus.
#         """
#         if not isinstance(new_status, OrderStatus):
#             raise ValueError(f"Invalid status: {new_status}. Must be an instance of OrderStatus Enum.")
#         self.status = new_status
#
#     def cancel_order(self):
#         """
#         Cancel the order if its status is 'pending'.
#
#         raises ValueError: If the order cannot be cancelled.
#         """
#         if self.status == OrderStatus.PENDING:
#             self.status = OrderStatus.CANCELLED
#         else:
#             raise ValueError("Order cannot be cancelled as it has already been processed.")


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
