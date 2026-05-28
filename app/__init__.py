from flask import Flask, redirect, request, url_for

from app.config import Config
from app.controllers.appointments import appointments_bp
from app.controllers.auth import auth_bp
from app.controllers.medical_records import records_bp
from app.controllers.patients import patients_bp
from app.controllers.resources import resources_bp
from app.errors.handlers import register_error_handlers
from app.extensions import db, jwt, migrate
from app.utils.responses import api_response


def jwt_unauthorized_response(message):
    if request.path.startswith("/api/"):
        return api_response(False, {"message": message, "details": {}}, 401)
    return redirect(url_for("auth.login_view"))


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jwt_unauthorized_response("Sesion vencida")

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        return jwt_unauthorized_response("Token invalido")

    @jwt.unauthorized_loader
    def missing_token_callback(reason):
        return jwt_unauthorized_response("Sesion no iniciada")

    register_error_handlers(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(records_bp)
    app.register_blueprint(resources_bp)

    @app.get("/")
    def index():
        return redirect(url_for("patients.list_patients_view"))

    return app
