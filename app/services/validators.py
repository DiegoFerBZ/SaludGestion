import re

from email_validator import EmailNotValidError, validate_email

from app.errors.exceptions import ValidationError


PASSWORD_PATTERN = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")


def require_fields(data, fields):
    missing = [field for field in fields if not str(data.get(field, "")).strip()]
    if missing:
        raise ValidationError("Campos obligatorios incompletos", details={"fields": missing})


def validate_email_address(email):
    try:
        return validate_email(email, check_deliverability=False).normalized
    except EmailNotValidError as exc:
        raise ValidationError("Correo electronico invalido", details={"email": str(exc)}) from exc


def validate_password(password):
    if not PASSWORD_PATTERN.match(password or ""):
        raise ValidationError(
            "La contraseña debe tener minimo 8 caracteres, una letra y un numero"
        )


def normalize_text(value):
    return str(value or "").strip()
