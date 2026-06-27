from fastapi.testclient import TestClient

from tests.conftest import auth_headers


def current_user_id(client: TestClient, headers: dict[str, str]) -> int:
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    return response.json()["id"]


def create_workout(
    client: TestClient,
    headers: dict[str, str],
    name: str = "Push Day",
    date: str = "2026-06-27",
) -> dict:
    response = client.post(
        "/workouts/",
        json={
            "name": name,
            "date": date,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def first_exercise_id(client: TestClient, headers: dict[str, str]) -> int:
    response = client.get("/exercises/", headers=headers)
    assert response.status_code == 200
    exercises = response.json()
    assert len(exercises) > 0
    return exercises[0]["id"]


def create_custom_exercise(client: TestClient, headers: dict[str, str]) -> dict:
    response = client.post(
        "/exercises/",
        json={
            "name": "Workout Test Custom Exercise",
            "muscle": "Test",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def add_set(
    client: TestClient,
    headers: dict[str, str],
    workout_id: int,
    exercise_id: int,
    reps: int = 10,
    weight: float = 50,
) -> dict:
    response = client.post(
        f"/workouts/{workout_id}/sets",
        json={
            "exercise_id": exercise_id,
            "reps": reps,
            "weight": weight,
        },
        headers=headers,
    )
    assert response.status_code == 201
    return response.json()


def test_get_workouts_requires_auth(client: TestClient) -> None:
    response = client.get("/workouts/")

    assert response.status_code == 401


def test_create_workout_belongs_to_current_user(client: TestClient) -> None:
    headers = auth_headers(client)
    user_id = current_user_id(client, headers)

    workout = create_workout(client, headers)

    assert workout["user_id"] == user_id


def test_get_workouts_returns_empty_list_for_new_user(client: TestClient) -> None:
    headers = auth_headers(client)

    response = client.get("/workouts/", headers=headers)

    assert response.status_code == 200
    assert response.json() == []


def test_user_only_sees_own_workouts(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    workout = create_workout(client, user_a_headers)

    response = client.get("/workouts/", headers=user_b_headers)

    assert response.status_code == 200
    assert workout["id"] not in {item["id"] for item in response.json()}


def test_get_own_workout_returns_detailed_response(client: TestClient) -> None:
    headers = auth_headers(client)
    workout = create_workout(client, headers)

    response = client.get(f"/workouts/{workout['id']}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workout["id"]
    assert data["user_id"] == workout["user_id"]
    assert "sets" in data
    assert data["sets"] == []


def test_user_cannot_get_other_users_workout(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    workout = create_workout(client, user_a_headers)

    response = client.get(f"/workouts/{workout['id']}", headers=user_b_headers)

    assert response.status_code == 404


def test_update_own_workout(client: TestClient) -> None:
    headers = auth_headers(client)
    workout = create_workout(client, headers)

    response = client.put(
        f"/workouts/{workout['id']}",
        json={
            "name": "Updated Workout",
            "date": "2026-06-28",
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Workout"
    assert data["date"] == "2026-06-28"


def test_user_cannot_update_other_users_workout(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    workout = create_workout(client, user_a_headers)

    response = client.put(
        f"/workouts/{workout['id']}",
        json={
            "name": "Blocked Update",
            "date": "2026-06-28",
        },
        headers=user_b_headers,
    )

    assert response.status_code == 404


def test_delete_own_workout(client: TestClient) -> None:
    headers = auth_headers(client)
    workout = create_workout(client, headers)

    delete_response = client.delete(f"/workouts/{workout['id']}", headers=headers)
    get_response = client.get(f"/workouts/{workout['id']}", headers=headers)

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_user_cannot_delete_other_users_workout(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    workout = create_workout(client, user_a_headers)

    response = client.delete(f"/workouts/{workout['id']}", headers=user_b_headers)

    assert response.status_code == 404


def test_add_set_to_own_workout(client: TestClient) -> None:
    headers = auth_headers(client)
    workout = create_workout(client, headers)
    exercise_id = first_exercise_id(client, headers)

    workout_set = add_set(client, headers, workout["id"], exercise_id)

    assert workout_set["workout_id"] == workout["id"]
    assert workout_set["exercise_id"] == exercise_id


def test_user_cannot_add_set_to_other_users_workout(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    workout = create_workout(client, user_a_headers)
    exercise_id = first_exercise_id(client, user_b_headers)

    response = client.post(
        f"/workouts/{workout['id']}/sets",
        json={
            "exercise_id": exercise_id,
            "reps": 10,
            "weight": 50,
        },
        headers=user_b_headers,
    )

    assert response.status_code == 404


def test_add_set_with_invalid_exercise_returns_404(client: TestClient) -> None:
    headers = auth_headers(client)
    workout = create_workout(client, headers)

    response = client.post(
        f"/workouts/{workout['id']}/sets",
        json={
            "exercise_id": 999999999,
            "reps": 10,
            "weight": 50,
        },
        headers=headers,
    )

    assert response.status_code == 404


def test_user_cannot_add_set_with_other_users_custom_exercise(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    exercise = create_custom_exercise(client, user_a_headers)
    workout = create_workout(client, user_b_headers)

    response = client.post(
        f"/workouts/{workout['id']}/sets",
        json={
            "exercise_id": exercise["id"],
            "reps": 10,
            "weight": 50,
        },
        headers=user_b_headers,
    )

    assert response.status_code == 404


def test_get_sets_for_own_workout(client: TestClient) -> None:
    headers = auth_headers(client)
    workout = create_workout(client, headers)
    exercise_id = first_exercise_id(client, headers)
    workout_set = add_set(client, headers, workout["id"], exercise_id)

    response = client.get(f"/workouts/{workout['id']}/sets", headers=headers)

    assert response.status_code == 200
    assert workout_set["id"] in {item["id"] for item in response.json()}


def test_user_cannot_get_sets_for_other_users_workout(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    workout = create_workout(client, user_a_headers)
    exercise_id = first_exercise_id(client, user_a_headers)
    add_set(client, user_a_headers, workout["id"], exercise_id)

    response = client.get(f"/workouts/{workout['id']}/sets", headers=user_b_headers)

    assert response.status_code == 404


def test_get_single_set_for_own_workout(client: TestClient) -> None:
    headers = auth_headers(client)
    workout = create_workout(client, headers)
    exercise_id = first_exercise_id(client, headers)
    workout_set = add_set(client, headers, workout["id"], exercise_id)

    response = client.get(f"/workouts/{workout['id']}/sets/{workout_set['id']}", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workout_set["id"]
    assert data["exercise_id"] == exercise_id
    assert "exercise" in data


def test_user_cannot_get_single_set_for_other_users_workout(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    workout = create_workout(client, user_a_headers)
    exercise_id = first_exercise_id(client, user_a_headers)
    workout_set = add_set(client, user_a_headers, workout["id"], exercise_id)

    response = client.get(f"/workouts/{workout['id']}/sets/{workout_set['id']}", headers=user_b_headers)

    assert response.status_code == 404


def test_delete_set_from_own_workout(client: TestClient) -> None:
    headers = auth_headers(client)
    workout = create_workout(client, headers)
    exercise_id = first_exercise_id(client, headers)
    workout_set = add_set(client, headers, workout["id"], exercise_id)

    delete_response = client.delete(f"/workouts/{workout['id']}/sets/{workout_set['id']}", headers=headers)
    get_response = client.get(f"/workouts/{workout['id']}/sets/{workout_set['id']}", headers=headers)

    assert delete_response.status_code == 204
    assert get_response.status_code == 404


def test_user_cannot_delete_set_from_other_users_workout(client: TestClient) -> None:
    user_a_headers = auth_headers(client)
    user_b_headers = auth_headers(client)
    workout = create_workout(client, user_a_headers)
    exercise_id = first_exercise_id(client, user_a_headers)
    workout_set = add_set(client, user_a_headers, workout["id"], exercise_id)

    response = client.delete(f"/workouts/{workout['id']}/sets/{workout_set['id']}", headers=user_b_headers)

    assert response.status_code == 404


def test_get_workout_volume_for_own_workout(client: TestClient) -> None:
    headers = auth_headers(client)
    workout = create_workout(client, headers)
    exercise_id = first_exercise_id(client, headers)
    add_set(client, headers, workout["id"], exercise_id, reps=10, weight=50)
    add_set(client, headers, workout["id"], exercise_id, reps=5, weight=20)

    response = client.get(f"/workouts/{workout['id']}/volume", headers=headers)

    assert response.status_code == 200
    assert response.json() == 600


def test_create_workout_invalid_body_returns_422(client: TestClient) -> None:
    headers = auth_headers(client)

    response = client.post(
        "/workouts/",
        json={
            "name": "",
            "date": "not-a-date",
        },
        headers=headers,
    )

    assert response.status_code == 422


def test_add_set_invalid_body_returns_422(client: TestClient) -> None:
    headers = auth_headers(client)
    workout = create_workout(client, headers)

    response = client.post(
        f"/workouts/{workout['id']}/sets",
        json={
            "exercise_id": -1,
            "reps": 0,
            "weight": -10,
        },
        headers=headers,
    )

    assert response.status_code == 422
