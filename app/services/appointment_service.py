from datetime import date, datetime, time, timedelta

from sqlalchemy import and_

from app.errors.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.extensions import db
from app.models import Appointment, AppointmentStatus, Doctor, MedicalRecord, Patient, Role
from app.services.patient_service import PatientService
from app.services.validators import require_fields


class AppointmentService:
    WORK_START = time(8, 0)
    LUNCH_START = time(12, 0)
    LUNCH_END = time(14, 0)
    WORK_END = time(18, 0)
    SLOT_MINUTES = 20

    @staticmethod
    def parse_start(value):
        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError) as exc:
            raise ValidationError("Fecha de cita invalida. Usa formato ISO YYYY-MM-DDTHH:MM") from exc

    @staticmethod
    def validate_slot(starts_at):
        ends_at = starts_at + timedelta(minutes=AppointmentService.SLOT_MINUTES)
        start_time = starts_at.time()
        end_time = ends_at.time()

        if starts_at.minute % AppointmentService.SLOT_MINUTES != 0 or starts_at.second != 0:
            raise ValidationError("Las citas deben iniciar en bloques de 20 minutos")
        if start_time < AppointmentService.WORK_START or end_time > AppointmentService.WORK_END:
            raise ValidationError("La cita esta fuera del horario laboral")
        if start_time < AppointmentService.LUNCH_END and end_time > AppointmentService.LUNCH_START:
            raise ValidationError("El medico no atiende durante el almuerzo")
        return ends_at

    @staticmethod
    def has_overlap(doctor_id, starts_at, ends_at):
        return Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.PROGRAMADA.value,
            Appointment.starts_at < ends_at,
            Appointment.ends_at > starts_at,
        ).first()

    @staticmethod
    def create(data):
        patient = (
            PatientService.get_by_document(data.get("patient_document"))
            if data.get("patient_document")
            else Patient.query.get(data.get("patient_id"))
        )
        doctor = Doctor.query.get(data.get("doctor_id"))
        if not patient:
            raise NotFoundError("Paciente no encontrado")
        if not doctor:
            raise NotFoundError("Medico no encontrado")

        starts_at = AppointmentService.parse_start(data.get("starts_at"))
        ends_at = AppointmentService.validate_slot(starts_at)

        if AppointmentService.has_overlap(doctor.id, starts_at, ends_at):
            raise ConflictError("El medico no tiene disponibilidad en ese horario")

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            starts_at=starts_at,
            ends_at=ends_at,
            status=AppointmentStatus.PROGRAMADA.value,
        )
        db.session.add(appointment)
        db.session.commit()
        return appointment

    @staticmethod
    def cancel(appointment_id, reason=None):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise NotFoundError("Cita no encontrada")
        appointment.status = AppointmentStatus.CANCELADA.value
        appointment.cancellation_reason = reason
        db.session.commit()
        return appointment

    @staticmethod
    def get_for_user(appointment_id, user_id, role):
        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            raise NotFoundError("Cita no encontrada")
        if role == Role.MEDICO.value and appointment.doctor_id != int(user_id):
            raise ForbiddenError("No puedes consultar citas de otros medicos")
        return appointment

    @staticmethod
    def complete_with_record(appointment_id, doctor_id, data):
        appointment = AppointmentService.get_for_user(appointment_id, doctor_id, Role.MEDICO.value)
        if appointment.status != AppointmentStatus.PROGRAMADA.value:
            raise ConflictError("Solo se pueden finalizar citas programadas")

        require_fields(data, ["diagnosis", "treatment"])
        record = MedicalRecord(
            patient_id=appointment.patient_id,
            doctor_id=appointment.doctor_id,
            diagnosis=data["diagnosis"].strip(),
            treatment=data["treatment"].strip(),
            notes=(data.get("notes") or "").strip() or None,
        )
        appointment.status = AppointmentStatus.FINALIZADA.value
        db.session.add(record)
        db.session.commit()
        return appointment, record

    @staticmethod
    def list(doctor_id=None, patient_id=None, patient_document=None, doctor_query=None):
        query = Appointment.query
        if doctor_id:
            query = query.filter_by(doctor_id=doctor_id)
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        if patient_document:
            like = f"%{patient_document.strip()}%"
            query = query.filter(Appointment.patient.has(Patient.document.ilike(like)))
        if doctor_query:
            like = f"%{doctor_query.strip()}%"
            query = query.filter(
                Appointment.doctor.has(
                    (Doctor.first_name.ilike(like))
                    | (Doctor.last_name.ilike(like))
                    | (Doctor.username.ilike(like))
                    | (Doctor.document.ilike(like))
                )
            )
        return query.order_by(Appointment.starts_at).all()

    @staticmethod
    def availability(doctor_id, target_date):
        doctor = Doctor.query.get(doctor_id)
        if not doctor:
            raise NotFoundError("Medico no encontrado")
        if isinstance(target_date, str):
            try:
                target_date = date.fromisoformat(target_date)
            except ValueError as exc:
                raise ValidationError("Fecha invalida. Usa YYYY-MM-DD") from exc

        day_start = datetime.combine(target_date, AppointmentService.WORK_START)
        day_end = datetime.combine(target_date, AppointmentService.WORK_END)
        appointments = Appointment.query.filter(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.status == AppointmentStatus.PROGRAMADA.value,
                Appointment.starts_at >= day_start,
                Appointment.starts_at < day_end,
            )
        ).all()
        busy = {(item.starts_at.time(), item.ends_at.time()) for item in appointments}

        slots = []
        current = day_start
        while current + timedelta(minutes=AppointmentService.SLOT_MINUTES) <= day_end:
            end = current + timedelta(minutes=AppointmentService.SLOT_MINUTES)
            if not (current.time() < AppointmentService.LUNCH_END and end.time() > AppointmentService.LUNCH_START):
                slots.append(
                    {
                        "starts_at": current.isoformat(),
                        "ends_at": end.isoformat(),
                        "available": (current.time(), end.time()) not in busy,
                    }
                )
            current = end
        return {"doctor": doctor.to_dict(), "date": target_date.isoformat(), "slots": slots}
