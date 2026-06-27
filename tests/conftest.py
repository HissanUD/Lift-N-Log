import time
import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.main import app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


def unique_email(prefix: str = "test") -> str:
    return f"{prefix}_{int(time.time() * 1000)}_{uuid.uuid4().hex}@example.com"


def register_user(client: TestClient, email: str | None = None, password: str = "password123") -> Response:
    user_email = email or unique_email("user")
    return client.post(
        "/auth/register",
        json={
            "user_name": "Test User",
            "email": user_email,
            "password": password,
        },
    )


def login_user(client: TestClient, email: str, password: str = "password123") -> Response:
    return client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )


def auth_headers(client: TestClient, email: str | None = None, password: str = "password123") -> dict[str, str]:
    user_email = email or unique_email("auth")
    register_user(client, email=user_email, password=password)
    token_response = login_user(client, email=user_email, password=password)
    token_data = token_response.json()
    token = token_data["access_token"]
    return {"Authorization": f"Bearer {token}"}
