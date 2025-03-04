# import json
import http
import schema

import flask
from flask import session
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash



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


def update_info_password(session: Session, user_data: dict):
    user = session.get(schema.User, user_data["user_id"])
    if user:
        # Hash the new password before storing it
        user.password = generate_password_hash(user_data["password"])
        session.commit()


def get_user_details(user_id):
    s = schema.session()
    query = s.query(schema.User)
    query = query.filter_by(user_id=user_id)
    result = query.first()

    if result:
        user_data = result.to_dict()
        user_data.pop("password", None)  # Remove data from details- sensitive info
        return user_data

    return None


# def is_user_logged_in() -> bool:
#     """
#     Checks if a user is currently logged in based on the 'user_id' in the session.

#     Returns:
#         bool: True if 'user_id' is found in the session, False otherwise.
#     """
#     return 'user_id' in session


# def is_specific_user_logged_in(user_id: int) -> bool:
#     """
#     Checks if a *specific user* is currently logged in based on the 'user_id' in the session.
#     """
#     return session.get('user_id') == user_id





# def is_user_logged_in(user_id: int):
#     return flask.session.get("logged_in", False) and flask.session.get("user_id") == user_id


# def logout_user(user_id: int):
#     if flask.session.get("user_id") == user_id:
#         flask.session.pop("user_id", None)
#         flask.session.pop("logged_in", None)
#         return {"success": True, "message": "User logged out"}
#     return {"success": False, "message": "Invalid user or not logged in"}
