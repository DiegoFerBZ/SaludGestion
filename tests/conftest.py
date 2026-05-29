import pytest

from app import create_app
from app.extensions import db
from app.models import Doctor, Patient, Receptionist, Role, Room


class TestConfig:
    TESTING = True
    SECRET_KEY = "test-secret-key-with-enough-length"
    JWT_SECRET_KEY = "test-jwt-secret-key-with-enough-length"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


@pytest.fixture()
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def receptionist(app):
    user = Receptionist(
        first_name="Ana",
        last_name="Lopez",
        username="recepcion",
        email="recepcion@example.com",
        document="100",
        role=Role.RECEPCIONISTA.value,
    )
    user.set_password("Recepcion123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def doctor(app):
    room = Room(name="Consultorio 1", location="Piso 2")
    db.session.add(room)
    db.session.flush()

    user = Doctor(
        first_name="Luis",
        last_name="Perez",
        username="lperez",
        email="lperez@example.com",
        document="200",
        role=Role.MEDICO.value,
        specialty="Medicina general",
        room_id=room.id,
    )
    user.set_password("Medico123")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture()
def patient(app):
    patient = Patient(
        first_name="Maria",
        last_name="Garcia",
        document="300",
        email="maria@example.com",
        phone="3001234567",
    )
    db.session.add(patient)
    db.session.commit()
    return patient


def auth_header(client, username, password):
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    token = response.get_json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def receptionist_auth(client, receptionist):
    return auth_header(client, "recepcion", "Recepcion123")


@pytest.fixture()
def doctor_auth(client, doctor):
    return auth_header(client, "lperez", "Medico123")
