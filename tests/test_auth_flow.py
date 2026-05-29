from app.models import Role, User


def test_register_and_login_receptionist_flow(client, app):
    # Arrange
    payload = {
        "first_name": "Claudia",
        "last_name": "Rojas",
        "username": "crojas",
        "email": "claudia@example.com",
        "password": "Clave123",
        "document": "1010",
        "role": Role.RECEPCIONISTA.value,
    }

    # Act
    register_response = client.post("/api/auth/register", json=payload)
    login_response = client.post(
        "/api/auth/login",
        json={"username": payload["username"], "password": payload["password"]},
    )

    # Assert
    assert register_response.status_code == 201
    assert login_response.status_code == 200
    assert login_response.get_json()["data"]["access_token"]
    with app.app_context():
        assert User.query.filter_by(username="crojas").one().role == Role.RECEPCIONISTA.value


def test_login_rejects_invalid_credentials(client, receptionist):
    # Arrange
    payload = {"username": "recepcion", "password": "incorrecta"}

    # Act
    response = client.post("/api/auth/login", json=payload)

    # Assert
    assert response.status_code == 401
    assert response.get_json()["success"] is False


def test_protected_endpoint_requires_token(client):
    # Arrange / Act
    response = client.get("/api/patients")

    # Assert
    assert response.status_code == 401
    assert response.get_json()["success"] is False
