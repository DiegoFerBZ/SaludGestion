from flask_jwt_extended import create_access_token

from app.errors.exceptions import ConflictError, UnauthorizedError, ValidationError
from app.extensions import db
from app.models import Doctor, Receptionist, Role, User
from app.services.validators import (
    normalize_text,
    require_fields,
    validate_email_address,
    validate_password,
)


class AuthService:
    @staticmethod
    def register_user(data):
        role = normalize_text(data.get("role")).lower()
        required = ["first_name", "last_name", "username", "email", "password", "document", "role"]
        if role == Role.MEDICO.value:
            required.append("specialty")

        require_fields(data, required)
        validate_password(data["password"])
        email = validate_email_address(data["email"])

        if role not in {Role.RECEPCIONISTA.value, Role.MEDICO.value}:
            raise ValidationError("Rol invalido")

        if User.query.filter(
            (User.username == data["username"])
            | (User.email == email)
            | (User.document == data["document"])
        ).first():
            raise ConflictError("Ya existe un usuario con usuario, email o documento")

        user_class = Doctor if role == Role.MEDICO.value else Receptionist
        user = user_class(
            first_name=normalize_text(data["first_name"]),
            last_name=normalize_text(data["last_name"]),
            username=normalize_text(data["username"]),
            email=email,
            document=normalize_text(data["document"]),
            role=role,
        )
        if isinstance(user, Doctor):
            user.specialty = normalize_text(data["specialty"])
            user.room_id = data.get("room_id") or None

        user.set_password(data["password"])
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def login(username, password):
        require_fields({"username": username, "password": password}, ["username", "password"])
        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            raise UnauthorizedError("Credenciales invalidas")

        token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        return {"access_token": token, "user": user.to_dict()}
