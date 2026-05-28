from enum import Enum

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


class Role(str, Enum):
    RECEPCIONISTA = "recepcionista"
    MEDICO = "medico"


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), nullable=False, unique=True, index=True)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    document = db.Column(db.String(30), nullable=False, unique=True, index=True)
    role = db.Column(db.String(30), nullable=False)
    type = db.Column(db.String(30), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now(), nullable=False
    )

    __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "user"}

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "username": self.username,
            "email": self.email,
            "document": self.document,
            "role": self.role,
        }


class Doctor(User):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    specialty = db.Column(db.String(120), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey("rooms.id"), nullable=True)

    room = db.relationship("Room", back_populates="doctor", uselist=False)
    appointments = db.relationship("Appointment", back_populates="doctor", lazy="dynamic")
    medical_records = db.relationship("MedicalRecord", back_populates="doctor", lazy="dynamic")

    __mapper_args__ = {"polymorphic_identity": "doctor"}

    def to_dict(self):
        data = super().to_dict()
        data.update(
            {
                "specialty": self.specialty,
                "room": self.room.to_dict() if self.room else None,
            }
        )
        return data


class Receptionist(User):
    __tablename__ = "receptionists"

    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)

    __mapper_args__ = {"polymorphic_identity": "receptionist"}
