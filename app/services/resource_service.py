from app.errors.exceptions import ConflictError, NotFoundError
from app.extensions import db
from app.models import Doctor, Room
from app.services.auth_service import AuthService
from app.services.validators import normalize_text, require_fields


class ResourceService:
    @staticmethod
    def create_room(data):
        require_fields(data, ["name"])
        name = normalize_text(data["name"])
        if Room.query.filter_by(name=name).first():
            raise ConflictError("Ya existe un consultorio con este nombre")
        room = Room(name=name, location=normalize_text(data.get("location")))
        db.session.add(room)
        db.session.commit()
        return room

    @staticmethod
    def list_rooms():
        return Room.query.order_by(Room.name).all()

    @staticmethod
    def create_doctor(data):
        doctor = AuthService.register_user({**data, "role": "medico"})
        return doctor

    @staticmethod
    def list_doctors():
        return Doctor.query.order_by(Doctor.last_name, Doctor.first_name).all()

    @staticmethod
    def assign_room(doctor_id, room_id):
        doctor = Doctor.query.get(doctor_id)
        room = Room.query.get(room_id)
        if not doctor:
            raise NotFoundError("Medico no encontrado")
        if not room:
            raise NotFoundError("Consultorio no encontrado")
        doctor.room_id = room.id
        db.session.commit()
        return doctor
