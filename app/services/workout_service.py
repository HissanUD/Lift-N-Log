import sqlalchemy as sqa
from sqlalchemy.orm import Session

from app.db import models
from app.errors import NotFoundError
from app.schemas import WorkoutCreate, WorkoutSetCreate


def _get_user_workout(
    workout_id: int,
    db: Session,
    current_user: models.User,
    message: str = "Workout does not exist",
) -> models.Workout:
    workout = db.query(models.Workout).filter(
        models.Workout.id == workout_id,
        models.Workout.user_id == current_user.id,
    ).first()

    if workout is None:
        raise NotFoundError(message)

    return workout


def _get_visible_exercise(
    exercise_id: int,
    db: Session,
    current_user: models.User,
    message: str = "The selected exercise does not exist",
) -> models.Exercise:
    exercise = db.query(models.Exercise).filter(
        models.Exercise.id == exercise_id,
        models.Exercise.is_active.is_(True),
        sqa.or_(
            models.Exercise.is_default.is_(True),
            models.Exercise.user_id == current_user.id,
        ),
    ).first()

    if exercise is None:
        raise NotFoundError(message)

    return exercise


def all_workouts(db: Session, current_user: models.User):
    return db.query(models.Workout).filter(models.Workout.user_id == current_user.id).all()


def get_workout(workout_id: int, db: Session, current_user: models.User):
    return _get_user_workout(workout_id, db, current_user)


def add_workout(workout: WorkoutCreate, db: Session, current_user: models.User):
    new_workout = models.Workout(
        name=workout.name,
        date=workout.date,
        user_id=current_user.id,
    )

    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)

    return new_workout


def add_set(
    workout_id: int,
    work_set: WorkoutSetCreate,
    db: Session,
    current_user: models.User,
):
    _get_user_workout(workout_id, db, current_user, "The selected workout does not exist")
    _get_visible_exercise(work_set.exercise_id, db, current_user)

    new_set = models.WorkoutSet(
        workout_id=workout_id,
        exercise_id=work_set.exercise_id,
        reps=work_set.reps,
        weight=work_set.weight,
    )

    db.add(new_set)
    db.commit()
    db.refresh(new_set)

    return new_set


def get_volume(workout_id: int, db: Session, current_user: models.User) -> float:
    _get_user_workout(workout_id, db, current_user)

    workout_sets = db.query(models.WorkoutSet).filter(
        models.WorkoutSet.workout_id == workout_id,
    ).all()

    volume = 0.0
    for workout_set in workout_sets:
        volume += workout_set.reps * workout_set.weight

    return volume


def update_workout(
    workout_id: int,
    workout_shape: WorkoutCreate,
    db: Session,
    current_user: models.User,
):
    target_workout = _get_user_workout(workout_id, db, current_user)

    target_workout.name = workout_shape.name
    target_workout.date = workout_shape.date

    db.commit()
    db.refresh(target_workout)

    return target_workout


def delete_workout(workout_id: int, db: Session, current_user: models.User) -> None:
    target_workout = _get_user_workout(workout_id, db, current_user)

    setlist = db.query(models.WorkoutSet).filter(
        models.WorkoutSet.workout_id == workout_id,
    ).all()

    for workout_set in setlist:
        db.delete(workout_set)

    db.delete(target_workout)
    db.commit()


def delete_set(
    workout_id: int,
    set_id: int,
    db: Session,
    current_user: models.User,
) -> None:
    _get_user_workout(workout_id, db, current_user, "The selected workout does not exist")

    target_set = db.query(models.WorkoutSet).filter(
        models.WorkoutSet.workout_id == workout_id,
        models.WorkoutSet.id == set_id,
    ).first()

    if target_set is None:
        raise NotFoundError("The selected set does not exist")

    db.delete(target_set)
    db.commit()


def get_all_sets(workout_id: int, db: Session, current_user: models.User):
    _get_user_workout(workout_id, db, current_user)

    return db.query(models.WorkoutSet).filter(
        models.WorkoutSet.workout_id == workout_id,
    ).all()


def get_set(workout_id: int, set_id: int, db: Session, current_user: models.User):
    _get_user_workout(workout_id, db, current_user)

    workout_set = db.query(models.WorkoutSet).filter(
        models.WorkoutSet.workout_id == workout_id,
        models.WorkoutSet.id == set_id,
    ).first()

    if workout_set is None:
        raise NotFoundError("Workout Set does not exist")

    return workout_set
