from datetime import datetime, timedelta

from app import create_app
from app.extensions import db
from app.models import Appointment, Doctor, Patient, Receptionist, Room


app = create_app()


def get_or_create_room(name, location):
    room = Room.query.filter_by(name=name).first()
    if room:
        return room
    room = Room(name=name, location=location)
    db.session.add(room)
    db.session.flush()
    return room


def get_or_create_receptionist(data):
    user = Receptionist.query.filter_by(document=data["document"]).first()
    if user:
        return user
    user = Receptionist(
        first_name=data["first_name"],
        last_name=data["last_name"],
        username=data["username"],
        email=data["email"],
        document=data["document"],
        role="recepcionista",
    )
    user.set_password(data["password"])
    db.session.add(user)
    db.session.flush()
    return user


def get_or_create_doctor(data, room):
    doctor = Doctor.query.filter_by(document=data["document"]).first()
    if doctor:
        return doctor
    doctor = Doctor(
        first_name=data["first_name"],
        last_name=data["last_name"],
        username=data["username"],
        email=data["email"],
        document=data["document"],
        role="medico",
        specialty=data["specialty"],
        room=room,
    )
    doctor.set_password(data["password"])
    db.session.add(doctor)
    db.session.flush()
    return doctor


def get_or_create_patient(data):
    patient = Patient.query.filter_by(document=data["document"]).first()
    if patient:
        return patient
    patient = Patient(**data)
    db.session.add(patient)
    db.session.flush()
    return patient


def get_or_create_appointment(patient, doctor, starts_at):
    appointment = Appointment.query.filter_by(
        patient_id=patient.id,
        doctor_id=doctor.id,
        starts_at=starts_at,
    ).first()
    if appointment:
        return appointment
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        starts_at=starts_at,
        ends_at=starts_at + timedelta(minutes=20),
        status="programada",
    )
    db.session.add(appointment)
    db.session.flush()
    return appointment


def seed():
    rooms = [
        get_or_create_room("Consultorio 101", "Piso 1"),
        get_or_create_room("Consultorio 102", "Piso 1"),
        get_or_create_room("Consultorio 201", "Piso 2"),
    ]

    get_or_create_receptionist(
        {
            "first_name": "Ana",
            "last_name": "Rojas",
            "username": "recepcion",
            "email": "recepcion@saludgestion.com",
            "document": "1001001001",
            "password": "Recepcion123",
        }
    )

    doctors = [
        get_or_create_doctor(
            {
                "first_name": "Luis",
                "last_name": "Perez",
                "username": "lperez",
                "email": "lperez@saludgestion.com",
                "document": "2002002001",
                "password": "Medico123",
                "specialty": "Medicina general",
            },
            rooms[0],
        ),
        get_or_create_doctor(
            {
                "first_name": "Maria",
                "last_name": "Gomez",
                "username": "mgomez",
                "email": "mgomez@saludgestion.com",
                "document": "2002002002",
                "password": "Medico123",
                "specialty": "Pediatria",
            },
            rooms[1],
        ),
        get_or_create_doctor(
            {
                "first_name": "Carlos",
                "last_name": "Vargas",
                "username": "cvargas",
                "email": "cvargas@saludgestion.com",
                "document": "2002002003",
                "password": "Medico123",
                "specialty": "Medicina interna",
            },
            rooms[2],
        ),
    ]

    patients = [
        get_or_create_patient(
            {
                "first_name": "Sofia",
                "last_name": "Martinez",
                "document": "3003003001",
                "email": "sofia.martinez@example.com",
                "phone": "3001112233",
            }
        ),
        get_or_create_patient(
            {
                "first_name": "Andres",
                "last_name": "Lopez",
                "document": "3003003002",
                "email": "andres.lopez@example.com",
                "phone": "3002223344",
            }
        ),
        get_or_create_patient(
            {
                "first_name": "Valentina",
                "last_name": "Ruiz",
                "document": "3003003003",
                "email": "valentina.ruiz@example.com",
                "phone": "3003334455",
            }
        ),
    ]

    get_or_create_appointment(patients[0], doctors[0], datetime(2026, 5, 29, 8, 0))
    get_or_create_appointment(patients[1], doctors[0], datetime(2026, 5, 29, 8, 20))
    get_or_create_appointment(patients[2], doctors[1], datetime(2026, 5, 29, 10, 0))

    db.session.commit()
    print("Seed completado.")
    print("Recepcionista: recepcion / Recepcion123")
    print("Medicos: lperez, mgomez, cvargas / Medico123")


if __name__ == "__main__":
    with app.app_context():
        seed()
