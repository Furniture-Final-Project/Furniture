from functools import wraps
from flask import session
from http import HTTPStatus

import schema


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return '', HTTPStatus.UNAUTHORIZED
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            # user mot logged in
            return '', HTTPStatus.UNAUTHORIZED

        # check if the user is an admin type
        s = schema.session()
        current_user = s.query(schema.User).get(user_id)
        if not current_user or current_user.role != "admin":
            return '', HTTPStatus.FORBIDDEN

        return f(*args, **kwargs)

    return decorated_function
