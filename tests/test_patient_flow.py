from app.models import Patient


def test_receptionist_can_create_search_and_update_patient(client, app, receptionist_auth):
    # Arrange
    create_payload = {
        "first_name": " Pedro ",
        "last_name": "Sanchez",
        "document": "4455",
        "email": "pedro@example.com",
        "phone": "3112223344",
    }

    # Act
    create_response = client.post("/api/patients", json=create_payload, headers=receptionist_auth)
    search_response = client.get("/api/patients?q=4455", headers=receptionist_auth)
    patient_id = create_response.get_json()["data"]["id"]
    update_response = client.put(
        f"/api/patients/{patient_id}",
        json={**create_payload, "first_name": "Pedro Pablo", "phone": "3223334455"},
        headers=receptionist_auth,
    )

    # Assert
    assert create_response.status_code == 201
    assert search_response.status_code == 200
    assert len(search_response.get_json()["data"]) == 1
    assert update_response.status_code == 200
    assert update_response.get_json()["data"]["first_name"] == "Pedro Pablo"
    with app.app_context():
        assert Patient.query.filter_by(document="4455").one().phone == "3223334455"


def test_doctor_cannot_create_patient(client, doctor_auth):
    # Arrange
    payload = {
        "first_name": "Laura",
        "last_name": "Mejia",
        "document": "7788",
        "email": "laura@example.com",
        "phone": "3000000000",
    }

    # Act
    response = client.post("/api/patients", json=payload, headers=doctor_auth)

    # Assert
    assert response.status_code == 403
    assert response.get_json()["success"] is False
