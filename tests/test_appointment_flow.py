from app.models import Appointment, AppointmentStatus, MedicalRecord


def test_receptionist_can_create_cancel_and_check_availability(
    client, app, receptionist_auth, doctor, patient
):
    # Arrange
    payload = {
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "starts_at": "2026-06-01T08:00:00",
    }

    # Act
    create_response = client.post("/api/appointments", json=payload, headers=receptionist_auth)
    appointment_id = create_response.get_json()["data"]["id"]
    availability_response = client.get(
        f"/api/doctors/{doctor.id}/availability?date=2026-06-01",
        headers=receptionist_auth,
    )
    cancel_response = client.post(
        f"/api/appointments/{appointment_id}/cancel",
        json={"reason": "Paciente no puede asistir"},
        headers=receptionist_auth,
    )

    # Assert
    assert create_response.status_code == 201
    assert availability_response.status_code == 200
    first_slot = availability_response.get_json()["data"]["slots"][0]
    assert first_slot["starts_at"] == "2026-06-01T08:00:00"
    assert first_slot["available"] is False
    assert cancel_response.status_code == 200
    assert cancel_response.get_json()["data"]["status"] == AppointmentStatus.CANCELADA.value
    with app.app_context():
        appointment = Appointment.query.get(appointment_id)
        assert appointment.cancellation_reason == "Paciente no puede asistir"


def test_prevents_overlapping_appointments(client, receptionist_auth, doctor, patient):
    # Arrange
    payload = {
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "starts_at": "2026-06-01T08:20:00",
    }
    client.post("/api/appointments", json=payload, headers=receptionist_auth)

    # Act
    response = client.post("/api/appointments", json=payload, headers=receptionist_auth)

    # Assert
    assert response.status_code == 409
    assert response.get_json()["success"] is False


def test_doctor_can_complete_own_appointment_with_record(
    client, app, receptionist_auth, doctor_auth, doctor, patient
):
    # Arrange
    appointment_response = client.post(
        "/api/appointments",
        json={"patient_id": patient.id, "doctor_id": doctor.id, "starts_at": "2026-06-01T09:00:00"},
        headers=receptionist_auth,
    )
    appointment_id = appointment_response.get_json()["data"]["id"]

    # Act
    response = client.post(
        f"/api/appointments/{appointment_id}/complete",
        json={"diagnosis": "Gripe", "treatment": "Reposo", "notes": "Control en una semana"},
        headers=doctor_auth,
    )

    # Assert
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert data["appointment"]["status"] == AppointmentStatus.FINALIZADA.value
    assert data["record"]["diagnosis"] == "Gripe"
    with app.app_context():
        assert MedicalRecord.query.filter_by(patient_id=patient.id, doctor_id=doctor.id).count() == 1
