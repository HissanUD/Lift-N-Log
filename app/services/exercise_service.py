import sqlalchemy as sqa
from sqlalchemy.orm import Session

from app.db import models
from app.errors import ForbiddenError, NotFoundError
from app.schemas import ExerciseCreate


def all_exercises(muscle: str | None, db: Session, current_user: models.User):
    query = db.query(models.Exercise).filter(
        models.Exercise.is_active.is_(True),
        sqa.or_(
            models.Exercise.is_default.is_(True),
            models.Exercise.user_id == current_user.id,
        ),
    )

    if muscle is not None:
        query = query.filter(models.Exercise.muscle == muscle)

    return query.all()


def get_exercise(exercise_id: int, db: Session, current_user: models.User):
    result = db.query(models.Exercise).filter(
        models.Exercise.id == exercise_id,
        models.Exercise.is_active.is_(True),
        sqa.or_(
            models.Exercise.is_default.is_(True),
            models.Exercise.user_id == current_user.id,
        ),
    ).first()

    if result is None:
        raise NotFoundError("Exercise not found")

    return result


def add_exercise(exercise: ExerciseCreate, db: Session, current_user: models.User):
    new_exercise = models.Exercise(
        name=exercise.name,
        muscle=exercise.muscle,
        is_default=False,
        is_active=True,
        user_id=current_user.id,
    )

    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)

    return new_exercise


def update_exercise(
    exercise_id: int,
    exercise_shape: ExerciseCreate,
    db: Session,
    current_user: models.User,
):
    exercise_record = db.query(models.Exercise).filter(
        models.Exercise.id == exercise_id,
        models.Exercise.is_active.is_(True),
    ).first()

    if exercise_record is None:
        raise NotFoundError("Exercise does not exist")

    if exercise_record.is_default:
        raise ForbiddenError("Exercise is default")

    if exercise_record.user_id != current_user.id:
        raise NotFoundError("Exercise does not exist")

    exercise_record.muscle = exercise_shape.muscle
    exercise_record.name = exercise_shape.name

    db.commit()
    db.refresh(exercise_record)

    return exercise_record


def delete_exercise(exercise_id: int, db: Session, current_user: models.User) -> None:
    exercise_record = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()

    if exercise_record is None:
        raise NotFoundError("Exercise does not exist")

    if exercise_record.is_default:
        raise ForbiddenError("Exercise is default")

    if exercise_record.user_id != current_user.id:
        raise NotFoundError("Exercise does not exist")

    exercise_record.is_active = False
    db.commit()
