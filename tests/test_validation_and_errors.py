import pytest

from app.errors.exceptions import NotFoundError, ValidationError
from app.services.appointment_service import AppointmentService
from app.services.patient_service import PatientService
from app.services.validators import require_fields, validate_email_address, validate_password


def test_validators_report_required_fields_and_invalid_values():
    # Arrange
    payload = {"first_name": "Ana", "email": "correo-invalido"}

    # Act / Assert
    with pytest.raises(ValidationError) as missing_error:
        require_fields(payload, ["first_name", "last_name"])
    assert missing_error.value.details["fields"] == ["last_name"]

    with pytest.raises(ValidationError):
        validate_email_address(payload["email"])

    with pytest.raises(ValidationError):
        validate_password("sin-numero")


def test_patient_service_reports_missing_patient(app):
    # Arrange / Act / Assert
    with pytest.raises(NotFoundError):
        PatientService.get(999)

    with pytest.raises(NotFoundError):
        PatientService.get_by_document("no-existe")


def test_appointment_service_rejects_invalid_dates_and_slots(app):
    # Arrange / Act / Assert
    with pytest.raises(ValidationError):
        AppointmentService.parse_start("fecha-rara")

    with pytest.raises(ValidationError):
        AppointmentService.validate_slot(AppointmentService.parse_start("2026-06-01T08:10:00"))

    with pytest.raises(ValidationError):
        AppointmentService.validate_slot(AppointmentService.parse_start("2026-06-01T07:40:00"))

    with pytest.raises(ValidationError):
        AppointmentService.validate_slot(AppointmentService.parse_start("2026-06-01T12:00:00"))
