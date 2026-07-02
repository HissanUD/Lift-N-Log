from fastapi import HTTPException, APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import models
from app.db.database import get_db
from app.dependencies import get_current_user
from app.errors import NotFoundError, ForbiddenError
from app.schemas import ExerciseCreate, ExerciseRead
from app.services import exercise_service


router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("/", response_model=list[ExerciseRead])
async def all_exercises(
    muscle: str | None = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return exercise_service.all_exercises(muscle, db, current_user)


@router.get("/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        result = exercise_service.get_exercise(exercise_id, db, current_user)
        return result
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/", status_code=201, response_model=ExerciseRead)
async def add_exercise(
    exercise: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return exercise_service.add_exercise(exercise, db, current_user)


@router.put("/{exercise_id}", response_model=ExerciseRead)
async def update_exercise(
    exercise_id: int,
    exercise_shape: ExerciseCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        return exercise_service.update_exercise(exercise_id, exercise_shape, db, current_user)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ForbiddenError as error:
        raise HTTPException(status_code=403, detail=str(error))


@router.delete("/{exercise_id}", status_code=204)
async def delete_exercise(
    exercise_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        exercise_service.delete_exercise(exercise_id, db, current_user)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
    except ForbiddenError as error:
        raise HTTPException(status_code=403, detail=str(error))
