import json
import http
import schema
import flask
from sqlalchemy.orm import Session


def add_new_user(session: Session, user_id: int, user_name: str, adress: str, email: str, password: str):

    if session.get(schema.User, user_id) != None:
        new_user = schema.User(user_id=user_id, user_name=user_name, adress=adress, email=email, password=password)
        session.add(new_user)
        session.commit()
