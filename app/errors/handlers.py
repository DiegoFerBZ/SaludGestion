from flask import redirect, render_template, request, url_for
from flask_jwt_extended.exceptions import JWTExtendedException
from jwt.exceptions import PyJWTError
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from app.errors.exceptions import AppError
from app.utils.responses import api_response


def wants_json_response():
    return request.path.startswith("/api/") or request.accept_mimetypes.best == "application/json"


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        data = {"message": error.message, "details": error.details}
        if wants_json_response():
            return api_response(False, data, error.status_code)
        return render_template("errors/error.html", error=data), error.status_code

    @app.errorhandler(JWTExtendedException)
    def handle_jwt_error(error):
        data = {"message": str(error), "details": {}}
        if wants_json_response():
            return api_response(False, data, 401)
        return redirect(url_for("auth.login_view"))

    @app.errorhandler(PyJWTError)
    def handle_pyjwt_error(error):
        data = {"message": str(error), "details": {}}
        if wants_json_response():
            return api_response(False, data, 401)
        return redirect(url_for("auth.login_view"))

    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        app.logger.exception(error)
        data = {"message": "Error de base de datos", "details": {}}
        if wants_json_response():
            return api_response(False, data, 500)
        return render_template("errors/error.html", error=data), 500

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        data = {"message": error.description, "details": {}}
        if wants_json_response():
            return api_response(False, data, error.code)
        return render_template("errors/error.html", error=data), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception(error)
        data = {"message": "Error inesperado", "details": {}}
        if wants_json_response():
            return api_response(False, data, 500)
        return render_template("errors/error.html", error=data), 500
