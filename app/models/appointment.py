from enum import Enum

from app.extensions import db


class AppointmentStatus(str, Enum):
    PROGRAMADA = "programada"
    CANCELADA = "cancelada"
    FINALIZADA = "finalizada"


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False, index=True)
    starts_at = db.Column(db.DateTime, nullable=False, index=True)
    ends_at = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default=AppointmentStatus.PROGRAMADA.value)
    cancellation_reason = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False
    )

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")

    def to_dict(self):
        return {
            "id": self.id,
            "patient": self.patient.to_dict() if self.patient else None,
            "doctor": self.doctor.to_dict() if self.doctor else None,
            "starts_at": self.starts_at.isoformat(),
            "ends_at": self.ends_at.isoformat(),
            "status": self.status,
            "cancellation_reason": self.cancellation_reason,
        }
