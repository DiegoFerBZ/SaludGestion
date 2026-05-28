from app.extensions import db


class MedicalRecord(db.Model):
    __tablename__ = "medical_records"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False, index=True)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)

    patient = db.relationship("Patient", back_populates="medical_records")
    doctor = db.relationship("Doctor", back_populates="medical_records")

    def to_dict(self):
        return {
            "id": self.id,
            "patient": self.patient.to_dict() if self.patient else None,
            "doctor": self.doctor.to_dict() if self.doctor else None,
            "diagnosis": self.diagnosis,
            "treatment": self.treatment,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
