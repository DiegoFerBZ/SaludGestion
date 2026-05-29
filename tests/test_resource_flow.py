from app.models import Doctor, Room
from app.services.resource_service import ResourceService


def test_receptionist_can_create_room_and_doctor(client, app, receptionist_auth):
    # Arrange
    room_payload = {"name": "Consultorio 9", "location": "Piso 3"}
    doctor_payload = {
        "first_name": "Camilo",
        "last_name": "Vargas",
        "username": "cvargas",
        "email": "cvargas@example.com",
        "password": "Medico123",
        "document": "9090",
        "specialty": "Pediatria",
    }

    # Act
    room_response = client.post("/api/rooms", json=room_payload, headers=receptionist_auth)
    doctor_response = client.post("/api/doctors", json=doctor_payload, headers=receptionist_auth)
    rooms_response = client.get("/api/rooms", headers=receptionist_auth)
    doctors_response = client.get("/api/doctors", headers=receptionist_auth)

    # Assert
    assert room_response.status_code == 201
    assert doctor_response.status_code == 201
    assert any(room["name"] == "Consultorio 9" for room in rooms_response.get_json()["data"])
    assert any(doctor["username"] == "cvargas" for doctor in doctors_response.get_json()["data"])
    with app.app_context():
        assert Room.query.filter_by(name="Consultorio 9").count() == 1
        assert Doctor.query.filter_by(username="cvargas").count() == 1


def test_resource_service_assigns_room(app, doctor):
    # Arrange
    room = ResourceService.create_room({"name": "Consultorio 10", "location": "Piso 4"})

    # Act
    updated_doctor = ResourceService.assign_room(doctor.id, room.id)

    # Assert
    assert updated_doctor.room_id == room.id
    assert Doctor.query.get(doctor.id).room.name == "Consultorio 10"
