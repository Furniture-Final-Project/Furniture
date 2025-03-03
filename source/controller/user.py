# import json
# import http
import schema

# import flask
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash


# def add_user(session: Session, user_data: dict):
#
#     new_user = schema.User.new(
#         user_id=user_data["user_id"],
#         user_name=user_data["user_name"],
#         address=user_data["address"],
#         email=user_data["email"],
#         password=user_data["password"],
#     )
#     session.add(new_user)
#     session.commit()


def add_new_user(session: Session, user_data: dict):
    """
    Adds a new user to the database, including duplicate checks and password security.

    :param session: SQLAlchemy Session object
    :param user_data: Dictionary containing user details
    :return: Dictionary indicating success or failure
    """
    try:
        # Check if a user with the same user_id or email already exists
        existing_user = (
            session.query(schema.User).filter((schema.User.user_id == user_data["user_id"]) | (schema.User.email == user_data["email"])).first()
        )

        if existing_user:
            return None

        # Create a new user with a hashed password
        new_user = schema.User(
            user_id=user_data["user_id"],
            user_name=user_data["user_name"],
            user_full_name=user_data["user_full_name"],
            user_phone_num=user_data["user_phone_num"],
            address=user_data["address"],
            email=user_data["email"],
            password=generate_password_hash(user_data["password"]),  # Hashing the password
        )

        session.add(new_user)
        session.commit()

    except IntegrityError:
        # Rollback transaction in case of a database integrity error (for example: duplicate user ID)
        session.rollback()


def update_info_user_full_name(session: Session, user_data: dict):
    user = session.get(schema.User, user_data["user_id"])
    if user:
        user.user_full_name = user_data["user_full_name"]
        session.commit()


def update_info_user_phone_num(session: Session, user_data: dict):
    user = session.get(schema.User, user_data["user_id"])
    if user:
        user.user_phone_num = user_data["user_phone_num"]
        session.commit()


def update_info_address(session: Session, user_data: dict):
    user = session.get(schema.User, user_data["user_id"])
    if user:
        user.address = user_data["address"]
        session.commit()


def update_info_user_name(session: Session, user_data: dict):
    user = session.get(schema.User, user_data["user_id"])
    if user:
        user.user_name = user_data["user_name"]
        session.commit()


def update_info_email(session: Session, user_data: dict):
    user = session.get(schema.User, user_data["user_id"])
    if user:
        user.email = user_data["email"]
        session.commit()

def get_user_details(user_id):
    s = schema.session()
    query = s.query(schema.User)
    query = query.filter_by(user_id=user_id)
    result = query.first()
    return result.to_dict()
