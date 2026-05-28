from functools import wraps

from flask import redirect, session, url_for
from flask_jwt_extended import get_jwt, jwt_required

from app.errors.exceptions import ForbiddenError, UnauthorizedError
from app.models import User


def role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorated(*args, **kwargs):
            claims = get_jwt()
            if claims.get("role") not in roles:
                raise ForbiddenError("No tienes permisos para esta accion")
            return fn(*args, **kwargs)

        return decorated

    return wrapper


def view_login_required(fn):
    @wraps(fn)
    def decorated(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login_view"))
        return fn(*args, **kwargs)

    return decorated


def view_role_required(*roles):
    def wrapper(fn):
        @wraps(fn)
        @view_login_required
        def decorated(*args, **kwargs):
            if session.get("role") not in roles:
                raise ForbiddenError("No tienes permisos para esta accion")
            return fn(*args, **kwargs)

        return decorated

    return wrapper


def current_view_user():
    user_id = session.get("user_id")
    if not user_id:
        raise UnauthorizedError("Sesion no iniciada")
    return User.query.get(user_id)
