def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "Heslo123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "testuser", "password": "SpatneHeslo"}
    )
    assert response.status_code == 401
    assert "Nesprávné" in response.json()["detail"]


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "neexistuje", "password": "Heslo123!"}
    )
    assert response.status_code == 401


def test_me_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_authorized(client, auth_headers):
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@horyavoda.cz"
