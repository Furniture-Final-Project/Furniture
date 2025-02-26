# import json
# import http
import schema

# import flask
from sqlalchemy.orm import Session


def add_user(session: Session, user_data: dict):

    new_user = schema.User.new(
        user_id=user_data["user_id"],
        user_name=user_data["user_name"],
        address=user_data["address"],
        email=user_data["email"],
        password=user_data["password"]
    )
    session.add(new_user)
    session.commit()

