from app.models import MedicalRecord
from app.services.medical_record_service import MedicalRecordService


def test_doctor_can_create_and_list_patient_records(client, app, doctor_auth, patient, doctor):
    # Arrange
    payload = {
        "patient_document": patient.document,
        "diagnosis": "Hipertension",
        "treatment": "Seguimiento mensual",
        "notes": "Presion estable",
    }

    # Act
    create_response = client.post("/api/records", json=payload, headers=doctor_auth)
    list_response = client.get(f"/api/patients/{patient.id}/records", headers=doctor_auth)

    # Assert
    assert create_response.status_code == 201
    assert list_response.status_code == 200
    records = list_response.get_json()["data"]
    assert len(records) == 1
    assert records[0]["treatment"] == "Seguimiento mensual"
    with app.app_context():
        assert MedicalRecord.query.filter_by(doctor_id=doctor.id).one().notes == "Presion estable"


def test_medical_record_service_creates_record(app, patient, doctor):
    # Arrange
    payload = {
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "diagnosis": "Dermatitis",
        "treatment": "Crema topica",
        "notes": "Evitar irritantes",
    }

    # Act
    record = MedicalRecordService.create(payload)

    # Assert
    assert record.id is not None
    assert record.diagnosis == "Dermatitis"
    assert MedicalRecord.query.filter_by(patient_id=patient.id).count() == 1
