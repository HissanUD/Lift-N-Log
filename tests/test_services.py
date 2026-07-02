import pytest
from sqlalchemy.orm import Session

from app.errors import AuthenticationError, ConflictError, ForbiddenError, NotFoundError
from app.schemas import ExerciseCreate, UserCreate, WorkoutCreate, WorkoutSetCreate
from app.services import auth_service, exercise_service, workout_service
from tests.conftest import TestingSessionLocal, unique_email


@pytest.fixture()
def db(reset_database: None):
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def create_user(db: Session, prefix: str = "service"):
    return auth_service.register_user(
        UserCreate(
            user_name="Service Test User",
            email=unique_email(prefix),
            password="password123",
        ),
        db,
    )


def create_exercise(db: Session, user, name: str = "Service Custom Exercise"):
    return exercise_service.add_exercise(
        ExerciseCreate(name=name, muscle="Test"),
        db,
        user,
    )


def create_workout(db: Session, user, name: str = "Service Workout"):
    return workout_service.add_workout(
        WorkoutCreate(name=name, date="2026-06-27"),
        db,
        user,
    )


def create_workout_set(db: Session, user, workout, exercise=None):
    selected_exercise = exercise or exercise_service.all_exercises(None, db, user)[0]
    return workout_service.add_set(
        workout.id,
        WorkoutSetCreate(exercise_id=selected_exercise.id, reps=10, weight=50),
        db,
        user,
    )


def test_auth_service_duplicate_email_raises_conflict(db: Session) -> None:
    email = unique_email("service_duplicate")
    details = UserCreate(
        user_name="Service Test User",
        email=email,
        password="password123",
    )

    auth_service.register_user(details, db)

    with pytest.raises(ConflictError, match="Email already registered"):
        auth_service.register_user(details, db)


def test_auth_service_login_returns_token(db: Session) -> None:
    email = unique_email("service_login")
    auth_service.register_user(
        UserCreate(
            user_name="Service Test User",
            email=email,
            password="password123",
        ),
        db,
    )

    token = auth_service.login_user(email, "password123", db)

    assert token["access_token"]
    assert token["token_type"] == "bearer"


def test_auth_service_login_wrong_password_raises_authentication_error(db: Session) -> None:
    email = unique_email("service_wrong_password")
    auth_service.register_user(
        UserCreate(
            user_name="Service Test User",
            email=email,
            password="password123",
        ),
        db,
    )

    with pytest.raises(AuthenticationError, match="Incorrect details"):
        auth_service.login_user(email, "wrongpassword", db)


def test_auth_service_login_missing_user_raises_authentication_error(db: Session) -> None:
    with pytest.raises(AuthenticationError, match="Incorrect details"):
        auth_service.login_user(unique_email("service_missing_login"), "password123", db)


def test_exercise_service_hides_other_users_custom_exercises(db: Session) -> None:
    user_a = create_user(db, "exercise_owner")
    user_b = create_user(db, "exercise_viewer")

    exercise = exercise_service.add_exercise(
        ExerciseCreate(name="Private Curl", muscle="Arms"),
        db,
        user_a,
    )

    visible_exercises = exercise_service.all_exercises(None, db, user_b)

    assert exercise.id not in {item.id for item in visible_exercises}


def test_exercise_service_get_returns_visible_custom_exercise(db: Session) -> None:
    user = create_user(db, "exercise_get")
    exercise = create_exercise(db, user)

    result = exercise_service.get_exercise(exercise.id, db, user)

    assert result.id == exercise.id
    assert result.user_id == user.id


def test_exercise_service_get_other_users_custom_exercise_raises_not_found(db: Session) -> None:
    user_a = create_user(db, "exercise_get_owner")
    user_b = create_user(db, "exercise_get_viewer")
    exercise = create_exercise(db, user_a)

    with pytest.raises(NotFoundError, match="Exercise not found"):
        exercise_service.get_exercise(exercise.id, db, user_b)


def test_exercise_service_filters_by_muscle(db: Session) -> None:
    user = create_user(db, "exercise_filter")
    create_exercise(db, user, name="Filter Test Exercise")

    exercises = exercise_service.all_exercises("Test", db, user)

    assert exercises
    assert all(exercise.muscle == "Test" for exercise in exercises)


def test_exercise_service_blocks_default_exercise_updates(db: Session) -> None:
    user = create_user(db, "default_block")
    default_exercise = next(
        exercise for exercise in exercise_service.all_exercises(None, db, user)
        if exercise.is_default
    )

    with pytest.raises(ForbiddenError, match="Exercise is default"):
        exercise_service.update_exercise(
            default_exercise.id,
            ExerciseCreate(name="Changed Default", muscle="Changed"),
            db,
            user,
        )


def test_exercise_service_updates_custom_exercise(db: Session) -> None:
    user = create_user(db, "exercise_update")
    exercise = create_exercise(db, user)

    updated = exercise_service.update_exercise(
        exercise.id,
        ExerciseCreate(name="Updated Exercise", muscle="Updated"),
        db,
        user,
    )

    assert updated.name == "Updated Exercise"
    assert updated.muscle == "Updated"


def test_exercise_service_delete_soft_deletes_custom_exercise(db: Session) -> None:
    user = create_user(db, "exercise_delete")
    exercise = create_exercise(db, user)

    exercise_service.delete_exercise(exercise.id, db, user)

    with pytest.raises(NotFoundError, match="Exercise not found"):
        exercise_service.get_exercise(exercise.id, db, user)


def test_exercise_service_delete_default_exercise_raises_forbidden(db: Session) -> None:
    user = create_user(db, "exercise_delete_default")
    default_exercise = next(
        exercise for exercise in exercise_service.all_exercises(None, db, user)
        if exercise.is_default
    )

    with pytest.raises(ForbiddenError, match="Exercise is default"):
        exercise_service.delete_exercise(default_exercise.id, db, user)


def test_workout_service_hides_other_users_workouts(db: Session) -> None:
    user_a = create_user(db, "workout_owner")
    user_b = create_user(db, "workout_viewer")
    workout = workout_service.add_workout(
        WorkoutCreate(name="Private Workout", date="2026-06-27"),
        db,
        user_a,
    )

    with pytest.raises(NotFoundError, match="Workout does not exist"):
        workout_service.get_workout(workout.id, db, user_b)


def test_workout_service_lists_only_current_users_workouts(db: Session) -> None:
    user_a = create_user(db, "workout_list_owner")
    user_b = create_user(db, "workout_list_viewer")
    workout = create_workout(db, user_a)

    workouts = workout_service.all_workouts(db, user_b)

    assert workout.id not in {item.id for item in workouts}


def test_workout_service_updates_workout(db: Session) -> None:
    user = create_user(db, "workout_update")
    workout = create_workout(db, user)

    updated = workout_service.update_workout(
        workout.id,
        WorkoutCreate(name="Updated Workout", date="2026-06-28"),
        db,
        user,
    )

    assert updated.name == "Updated Workout"
    assert str(updated.date) == "2026-06-28"


def test_workout_service_deletes_workout(db: Session) -> None:
    user = create_user(db, "workout_delete")
    workout = create_workout(db, user)

    workout_service.delete_workout(workout.id, db, user)

    with pytest.raises(NotFoundError, match="Workout does not exist"):
        workout_service.get_workout(workout.id, db, user)


def test_workout_service_add_set_rejects_other_users_custom_exercise(db: Session) -> None:
    user_a = create_user(db, "set_exercise_owner")
    user_b = create_user(db, "set_workout_owner")
    exercise = create_exercise(db, user_a)
    workout = create_workout(db, user_b)

    with pytest.raises(NotFoundError, match="The selected exercise does not exist"):
        workout_service.add_set(
            workout.id,
            WorkoutSetCreate(exercise_id=exercise.id, reps=10, weight=50),
            db,
            user_b,
        )


def test_workout_service_get_all_sets_returns_workout_sets(db: Session) -> None:
    user = create_user(db, "sets_list")
    workout = create_workout(db, user)
    workout_set = create_workout_set(db, user, workout)

    sets = workout_service.get_all_sets(workout.id, db, user)

    assert workout_set.id in {item.id for item in sets}


def test_workout_service_get_set_returns_detailed_set(db: Session) -> None:
    user = create_user(db, "set_get")
    workout = create_workout(db, user)
    workout_set = create_workout_set(db, user, workout)

    result = workout_service.get_set(workout.id, workout_set.id, db, user)

    assert result.id == workout_set.id
    assert result.exercise is not None


def test_workout_service_get_missing_set_raises_not_found(db: Session) -> None:
    user = create_user(db, "set_missing")
    workout = create_workout(db, user)

    with pytest.raises(NotFoundError, match="Workout Set does not exist"):
        workout_service.get_set(workout.id, 999999999, db, user)


def test_workout_service_delete_set_removes_set(db: Session) -> None:
    user = create_user(db, "set_delete")
    workout = create_workout(db, user)
    workout_set = create_workout_set(db, user, workout)

    workout_service.delete_set(workout.id, workout_set.id, db, user)

    with pytest.raises(NotFoundError, match="Workout Set does not exist"):
        workout_service.get_set(workout.id, workout_set.id, db, user)


def test_workout_service_calculates_volume(db: Session) -> None:
    user = create_user(db, "volume")
    workout = workout_service.add_workout(
        WorkoutCreate(name="Volume Workout", date="2026-06-27"),
        db,
        user,
    )
    exercise = exercise_service.all_exercises(None, db, user)[0]

    workout_service.add_set(
        workout.id,
        WorkoutSetCreate(exercise_id=exercise.id, reps=10, weight=50),
        db,
        user,
    )
    workout_service.add_set(
        workout.id,
        WorkoutSetCreate(exercise_id=exercise.id, reps=5, weight=20),
        db,
        user,
    )

    assert workout_service.get_volume(workout.id, db, user) == 600
