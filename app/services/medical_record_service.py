from app.errors.exceptions import NotFoundError
from app.extensions import db
from app.models import Doctor, MedicalRecord, Patient
from app.services.patient_service import PatientService
from app.services.validators import require_fields


class MedicalRecordService:
    @staticmethod
    def build(data, patient_id, doctor_id):
        require_fields(data, ["diagnosis", "treatment"])
        patient = Patient.query.get(patient_id)
        doctor = Doctor.query.get(doctor_id)
        if not patient:
            raise NotFoundError("Paciente no encontrado")
        if not doctor:
            raise NotFoundError("Medico no encontrado")

        return MedicalRecord(
            patient_id=patient.id,
            doctor_id=doctor.id,
            diagnosis=data["diagnosis"].strip(),
            treatment=data["treatment"].strip(),
            notes=(data.get("notes") or "").strip() or None,
        )

    @staticmethod
    def create(data):
        require_fields(data, ["patient_id", "doctor_id", "diagnosis", "treatment"])
        patient = Patient.query.get(data["patient_id"])
        doctor = Doctor.query.get(data["doctor_id"])
        if not patient:
            raise NotFoundError("Paciente no encontrado")
        if not doctor:
            raise NotFoundError("Medico no encontrado")

        record = MedicalRecord(
            patient_id=patient.id,
            doctor_id=doctor.id,
            diagnosis=data["diagnosis"].strip(),
            treatment=data["treatment"].strip(),
            notes=(data.get("notes") or "").strip() or None,
        )
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def create_for_doctor(data, doctor_id):
        patient = (
            PatientService.get_by_document(data.get("patient_document"))
            if data.get("patient_document")
            else PatientService.get(data.get("patient_id"))
        )
        require_fields(data, ["diagnosis", "treatment"])
        record = MedicalRecordService.build(data, patient.id, doctor_id)
        db.session.add(record)
        db.session.commit()
        return record

    @staticmethod
    def list_by_patient(patient_id):
        if not Patient.query.get(patient_id):
            raise NotFoundError("Paciente no encontrado")
        return MedicalRecord.query.filter_by(patient_id=patient_id).order_by(MedicalRecord.created_at.desc()).all()

    @staticmethod
    def list_by_patient_document(document):
        patient = PatientService.get_by_document(document)
        return (
            MedicalRecord.query.filter_by(patient_id=patient.id)
            .order_by(MedicalRecord.created_at.desc())
            .all()
        )
