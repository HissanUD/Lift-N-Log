from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import models
from app.db.database import get_db
from app.dependencies import get_current_user
from app.errors import NotFoundError
from app.schemas import (
    WorkoutCreate,
    WorkoutDetailedRead,
    WorkoutRead,
    WorkoutSetCreate,
    WorkoutSetDetailedRead,
    WorkoutSetRead,
)
from app.services import workout_service

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("/", response_model=list[WorkoutRead])
async def all_workouts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return workout_service.all_workouts(db, current_user)


@router.get("/{workout_id}", response_model=WorkoutDetailedRead)
async def get_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        return workout_service.get_workout(workout_id, db, current_user)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post("/", status_code=201, response_model=WorkoutRead)
async def add_workout(
    workout: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return workout_service.add_workout(workout, db, current_user)


@router.post("/{workout_id}/sets", status_code=201, response_model=WorkoutSetRead)
async def add_set(
    workout_id: int,
    work_set: WorkoutSetCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        return workout_service.add_set(workout_id, work_set, db, current_user)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/{workout_id}/volume")
async def get_volume(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        return workout_service.get_volume(workout_id, db, current_user)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.put("/{workout_id}", response_model=WorkoutRead)
async def update_workout(
    workout_id: int,
    workout_shape: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        return workout_service.update_workout(workout_id, workout_shape, db, current_user)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.delete("/{workout_id}", status_code=204)
async def delete_workout(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        workout_service.delete_workout(workout_id, db, current_user)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.delete("/{workout_id}/sets/{set_id}", status_code=204)
async def delete_set(
    workout_id: int,
    set_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        workout_service.delete_set(workout_id, set_id, db, current_user)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/{workout_id}/sets", response_model=list[WorkoutSetRead])
async def get_all_sets(
    workout_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        return workout_service.get_all_sets(workout_id, db, current_user)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/{workout_id}/sets/{set_id}", response_model=WorkoutSetDetailedRead)
async def get_set(
    workout_id: int,
    set_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    try:
        return workout_service.get_set(workout_id, set_id, db, current_user)
    except NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))
