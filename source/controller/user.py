import http
import schema
import flask
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash


def add_new_user(session: Session, user_data: dict):
    """
    Adds a new user to the database with validation and password security.

    Args:
        session (Session): The database session.
        user_data (dict): A dictionary containing user details.

    Raises:
        HTTPException: If a user with the same ID or email already exists.
        IntegrityError: If a database integrity issue occurs.
    """
    try:
        # Check if a user with the same user_id or email already exists
        existing_user = (
            session.query(schema.User).filter((schema.User.user_id == user_data["user_id"]) | (schema.User.email == user_data["email"])).first()
        )

        if existing_user:
            flask.abort(http.HTTPStatus.BAD_REQUEST, "User already exists in the system.")

        # Create a new user with a hashed password
        new_user = schema.User(
            user_id=user_data["user_id"],
            user_name=user_data["user_name"],
            user_full_name=user_data["user_full_name"],
            user_phone_num=user_data["user_phone_num"],
            address=user_data["address"],
            email=user_data["email"],
            password=generate_password_hash(user_data["password"]),  # Hashing the password
            role=user_data["role"],
        )

        session.add(new_user)
        session.commit()

    except IntegrityError:
        # Rollback transaction in case of a database integrity error (for example: duplicate user ID)
        session.rollback()


def update_info_user_full_name(session: Session, user_data: dict) -> None:
    """
    Updates the full name of a user in the database.

    Args:
        session (Session): The database session.
        user_data (dict): A dictionary containing 'user_id' and the new 'user_full_name'.
    """
    user = session.get(schema.User, user_data["user_id"])
    if user:
        user.user_full_name = user_data["user_full_name"]
        session.commit()


def update_info_user_phone_num(session: Session, user_data: dict) -> None:
    """
    Updates the phone number of a user in the database.

    Args:
        session (Session): The database session.
        user_data (dict): A dictionary containing 'user_id' and the new 'user_phone_num'.
    """
    user = session.get(schema.User, user_data["user_id"])
    if user:
        user.user_phone_num = user_data["user_phone_num"]
        session.commit()


def update_info_address(session: Session, user_data: dict) -> None:
    user = session.get(schema.User, user_data["user_id"])
    if user:
        user.address = user_data["address"]
        session.commit()


def update_info_user_name(session: Session, user_data: dict):
    """
    Updates the address of a user in the database.

    Args:
        session (Session): The database session.
        user_data (dict): A dictionary containing 'user_id' and the new 'address'.
    """
    user = session.get(schema.User, user_data["user_id"])
    if user:
        user.user_name = user_data["user_name"]
        session.commit()


def update_info_email(session: Session, user_data: dict) -> None:
    """
    Updates the email address of a user in the database.

    Args:
        session (Session): The database session.
        user_data (dict): A dictionary containing 'user_id' and the new 'email'.
    """
    user = session.get(schema.User, user_data["user_id"])
    if user:
        user.email = user_data["email"]
        session.commit()


def update_info_password(session: Session, user_data: dict) -> None:
    """
    Updates the user's password in the database after hashing it.

    Args:
        session (Session): The database session.
        user_data (dict): A dictionary containing 'user_id' and the new 'password'.
    """

    user = session.get(schema.User, user_data["user_id"])
    if user:
        # Hash the new password before storing it
        user.password = generate_password_hash(user_data["password"])
        session.commit()


def get_user_details(user_id: int) -> dict | None:
    """
    Retrieves user details from the database, excluding the password.

    Args:
        user_id (int): The ID of the user.

    Returns:
        dict | None: A dictionary containing user details, or None if the user is not found.
    """
    s = schema.session()
    query = s.query(schema.User)
    query = query.filter_by(user_id=user_id)
    result = query.first()

    if result:
        user_data = result.to_dict()
        user_data.pop("password", None)  # Remove data from details- sensitive info
        return user_data

    return None
