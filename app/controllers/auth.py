from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_jwt_extended import jwt_required

from app.models import User
from app.services.auth_service import AuthService
from app.utils.responses import api_response

auth_bp = Blueprint("auth", __name__, url_prefix="")


@auth_bp.get("/login")
def login_view():
    return render_template("auth/login.html")


@auth_bp.post("/login")
def login_submit():
    result = AuthService.login(request.form.get("username"), request.form.get("password"))
    session["user_id"] = result["user"]["id"]
    session["role"] = result["user"]["role"]
    return redirect(url_for("patients.list_patients_view"))


@auth_bp.get("/logout")
def logout_view():
    session.clear()
    return redirect(url_for("auth.login_view"))


@auth_bp.get("/register")
def register_view():
    return render_template("auth/register.html")


@auth_bp.post("/register")
def register_submit():
    user = AuthService.register_user(request.form)
    session["user_id"] = user.id
    session["role"] = user.role
    return redirect(url_for("patients.list_patients_view"))


@auth_bp.post("/api/auth/register")
def register_api():
    user = AuthService.register_user(request.get_json() or {})
    return api_response(True, user.to_dict(), 201)


@auth_bp.post("/api/auth/login")
def login_api():
    data = request.get_json() or {}
    return api_response(True, AuthService.login(data.get("username"), data.get("password")))


@auth_bp.get("/api/auth/me")
@jwt_required()
def me_api():
    from flask_jwt_extended import get_jwt_identity

    user = User.query.get(get_jwt_identity())
    return api_response(True, user.to_dict() if user else None)
