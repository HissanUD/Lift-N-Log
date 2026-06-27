from fastapi.testclient import TestClient

from tests.conftest import auth_headers, login_user, register_user, unique_email


def test_register_user(client: TestClient) -> None:
    response = register_user(client)

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert "user_name" in data
    assert "email" in data
    assert "is_active" in data
    assert "auth_provider" in data
    assert "password" not in data
    assert "hashed_password" not in data



def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    email = unique_email("duplicate")

    first_response = register_user(client, email=email)
    second_response = register_user(client, email=email)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_register_invalid_email_returns_422(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "user_name": "Test User",
            "email": "not-an-email",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_register_missing_email_returns_422(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "user_name": "Test User",
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_register_short_password_returns_422(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "user_name": "Test User",
            "email": unique_email("short_password"),
            "password": "short",
        },
    )

    assert response.status_code == 422


def test_register_missing_password_returns_422(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "user_name": "Test User",
            "email": unique_email("missing_password"),
        },
    )

    assert response.status_code == 422


def test_register_empty_user_name_returns_422(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "user_name": "",
            "email": unique_email("empty_username"),
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_register_missing_user_name_returns_422(client: TestClient) -> None:
    response = client.post(
        "/auth/register",
        json={
            "email": unique_email("missing_username"),
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_login_returns_bearer_token(client: TestClient) -> None:
    email = unique_email("login")

    register_response = register_user(client, email=email)
    login_response = login_user(client, email=email)

    assert register_response.status_code == 201
    assert login_response.status_code == 200

    data = login_response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    email = unique_email("wrong_password")

    register_response = register_user(client, email=email)
    login_response = login_user(client, email=email, password="wrongpassword")

    assert register_response.status_code == 201
    assert login_response.status_code == 401


def test_login_unregistered_email_returns_401(client: TestClient) -> None:
    response = login_user(client, email=unique_email("unregistered"))

    assert response.status_code == 401


def test_login_invalid_email_format_returns_401(client: TestClient) -> None:
    response = login_user(client, email="not-an-email")

    assert response.status_code == 401


def test_login_missing_username_returns_422(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        data={
            "password": "password123",
        },
    )

    assert response.status_code == 422


def test_login_missing_password_returns_422(client: TestClient) -> None:
    response = client.post(
        "/auth/login",
        data={
            "username": unique_email("missing_login_password"),
        },
    )

    assert response.status_code == 422


def test_me_requires_token(client: TestClient) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_me_returns_current_user(client: TestClient) -> None:
    email = unique_email("me")
    headers = auth_headers(client, email=email)

    response = client.get("/auth/me", headers=headers)

    assert response.status_code == 200

    data = response.json()
    assert data["email"] == email
    assert data["user_name"] == "Test User"
    assert data["is_active"] is True
    assert data["auth_provider"] == "local"
    assert "password" not in data
    assert "hashed_password" not in data
