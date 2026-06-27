from fastapi.testclient import TestClient

from tests.conftest import auth_headers


def first_default_exercise(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.get("/exercises/", headers=headers)
    assert response.status_code == 200
    for exercise in response.json():
        if exercise["is_default"] is True:
            return exercise
    raise AssertionError("No default exercise found. Run the seed script before tests.")


def create_custom_exercise(
    client: TestClient,
    headers: dict[str, str],
    name: str = "Custom Test Exercise",
    muscle: str = "Test",
) -> dict:
    response = client.post(
        "/exercises/",
        json={
            "name": name,
            "muscle": muscle,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_get_exercises_requires_auth(client: TestClient) -> None:
    response = client.get("/exercises")
    assert response.status_code == 401


def test_get_exercises_returns_default_exercises(client: TestClient) -> None:
    auth = auth_headers(client)
    response = client.get("/exercises/",headers=auth)

    assert response.status_code == 200

    data = response.json()
    assert len(data) > 0
    assert any(exercise["is_default"] is True for exercise in data)
    assert all(exercise["is_active"] is True for exercise in data)


def test_create_custom_exercise_belongs_to_current_user(client: TestClient) -> None:
    auth = auth_headers(client)
    me_response = client.get("/auth/me", headers=auth)
    exercise = create_custom_exercise(client, auth)

    assert me_response.status_code == 200
    assert exercise["is_default"] is False
    assert exercise["is_active"] is True
    assert exercise["user_id"] == me_response.json()["id"]


def test_user_cannot_see_other_users_custom_exercise(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    exercise = create_custom_exercise(client, user_a_headers)

    response = client.get("/exercises/", headers=user_b_headers)

    assert response.status_code == 200
    assert exercise["id"] not in {item["id"] for item in response.json()}


def test_user_cannot_get_other_users_custom_exercise(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    exercise = create_custom_exercise(client, user_a_headers)

    response = client.get(f"/exercises/{exercise['id']}", headers=user_b_headers)

    assert response.status_code == 404


def test_user_cannot_update_other_users_custom_exercise(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    exercise = create_custom_exercise(client, user_a_headers)

    response = client.put(
        f"/exercises/{exercise['id']}",
        json={
            "name": "Changed",
            "muscle": "Changed",
        },
        headers=user_b_headers,
    )

    assert response.status_code == 404


def test_user_cannot_delete_other_users_custom_exercise(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    exercise = create_custom_exercise(client, user_a_headers)

    response = client.delete(f"/exercises/{exercise['id']}", headers=user_b_headers)

    assert response.status_code == 404


def test_get_exercises_can_filter_by_muscle(client: TestClient) -> None:
    auth = auth_headers(client)

    response = client.get("/exercises/", params={"muscle": "Chest"}, headers=auth)

    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(exercise["muscle"] == "Chest" for exercise in data)


def test_create_exercise_invalid_body_returns_422(client: TestClient) -> None:
    auth = auth_headers(client)

    response = client.post(
        "/exercises/",
        json={
            "name": "",
        },
        headers=auth,
    )

    assert response.status_code == 422


def test_default_exercise_cannot_be_updated(client: TestClient) -> None:
    auth = auth_headers(client)
    exercise = first_default_exercise(client, auth)

    response = client.put(
        f"/exercises/{exercise['id']}",
        json={
            "name": "Changed Default",
            "muscle": "Changed",
        },
        headers=auth,
    )

    assert response.status_code == 403


def test_default_exercise_cannot_be_deleted(client: TestClient) -> None:
    auth = auth_headers(client)
    exercise = first_default_exercise(client, auth)

    response = client.delete(f"/exercises/{exercise['id']}", headers=auth)

    assert response.status_code == 403


def test_custom_exercise_can_be_soft_deleted(client: TestClient) -> None:
    auth = auth_headers(client)
    exercise = create_custom_exercise(client, auth)

    delete_response = client.delete(f"/exercises/{exercise['id']}", headers=auth)
    list_response = client.get("/exercises/", headers=auth)
    get_response = client.get(f"/exercises/{exercise['id']}", headers=auth)

    assert delete_response.status_code == 204
    assert list_response.status_code == 200
    assert exercise["id"] not in {item["id"] for item in list_response.json()}
    assert get_response.status_code == 404
