import os
import time
import uuid
from collections.abc import Iterator

import pytest
import sqlalchemy as sqa
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base, get_db
from app.main import app

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if TEST_DATABASE_URL is None:
    raise RuntimeError("TEST_DATABASE_URL env variable not set")

test_engine = sqa.create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

DEFAULT_TEST_EXERCISES = [
    {"name": "Bench Press", "muscle": "Chest"},
    {"name": "Squat", "muscle": "Legs"},
    {"name": "Deadlift", "muscle": "Back"},
]


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_default_exercises() -> None:
    db = TestingSessionLocal()
    try:
        for exercise in DEFAULT_TEST_EXERCISES:
            db.add(
                models.Exercise(
                    name=exercise["name"],
                    muscle=exercise["muscle"],
                    is_default=True,
                    is_active=True,
                )
            )
        db.commit()
    finally:
        db.close()


@pytest.fixture()
def reset_database() -> Iterator[None]:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    seed_default_exercises()

    yield

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client(reset_database: None) -> Iterator[TestClient]:
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


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
