from functools import wraps
from flask import session
from http import HTTPStatus

# import schema


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return '', HTTPStatus.UNAUTHORIZED
        return f(*args, **kwargs)

    return decorated_function


# def admin_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         user_id = session.get('user_id')
#         if not user_id:
#             # לא מחובר בכלל
#             return '', HTTPStatus.UNAUTHORIZED

#         # עכשיו נבדוק האם המשתמש אדמין
#         db_session = schema.session()
#         user = db_session.query(schema.User).get(user_id)
#         if not user or not user.is_admin:  # בדוק כאן את התנאי המתאים
#             return '', HTTPStatus.FORBIDDEN

#         return f(*args, **kwargs)
#     return decorated_function
