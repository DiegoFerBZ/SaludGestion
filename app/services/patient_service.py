from app.errors.exceptions import ConflictError, NotFoundError
from app.extensions import db
from app.models import Patient
from app.services.validators import normalize_text, require_fields, validate_email_address


class PatientService:
    @staticmethod
    def create(data):
        require_fields(data, ["first_name", "last_name", "document", "email", "phone"])
        email = validate_email_address(data["email"])
        document = normalize_text(data["document"])

        if Patient.query.filter_by(document=document).first():
            raise ConflictError("Ya existe un paciente con este documento")

        patient = Patient(
            first_name=normalize_text(data["first_name"]),
            last_name=normalize_text(data["last_name"]),
            document=document,
            email=email,
            phone=normalize_text(data["phone"]),
        )
        db.session.add(patient)
        db.session.commit()
        return patient

    @staticmethod
    def search(query=None):
        patients_query = Patient.query
        if query:
            like = f"%{query.strip()}%"
            patients_query = patients_query.filter(
                (Patient.first_name.ilike(like))
                | (Patient.last_name.ilike(like))
                | (Patient.document.ilike(like))
            )
        return patients_query.order_by(Patient.last_name, Patient.first_name).limit(50).all()

    @staticmethod
    def get(patient_id):
        patient = Patient.query.get(patient_id)
        if not patient:
            raise NotFoundError("Paciente no encontrado")
        return patient

    @staticmethod
    def get_by_document(document):
        patient = Patient.query.filter_by(document=normalize_text(document)).first()
        if not patient:
            raise NotFoundError("Paciente no encontrado para el documento ingresado")
        return patient

    @staticmethod
    def update(patient_id, data):
        patient = PatientService.get(patient_id)
        require_fields(data, ["first_name", "last_name", "document", "email", "phone"])

        document = normalize_text(data["document"])
        duplicate = Patient.query.filter(Patient.document == document, Patient.id != patient.id).first()
        if duplicate:
            raise ConflictError("Ya existe otro paciente con este documento")

        patient.first_name = normalize_text(data["first_name"])
        patient.last_name = normalize_text(data["last_name"])
        patient.document = document
        patient.email = validate_email_address(data["email"])
        patient.phone = normalize_text(data["phone"])
        db.session.commit()
        return patient
