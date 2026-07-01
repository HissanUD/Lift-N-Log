from fastapi import HTTPException, APIRouter, Depends
from app.schemas import ExerciseCreate, ExerciseRead
from sqlalchemy.orm import Session
from app.db import models
from app.db.database import get_db
import sqlalchemy as sqa
from app.dependencies import get_current_user


router = APIRouter(prefix="/exercises", tags=["exercises"])

@router.get("/",response_model=list[ExerciseRead])
async def all_exercises(muscle: str | None = None, db: Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    if muscle is None:
        return db.query(models.Exercise).filter(models.Exercise.is_active == True,sqa.or_(models.Exercise.is_default==True,models.Exercise.user_id == current_user.id)).all()
    
    return db.query(models.Exercise).filter(models.Exercise.muscle == muscle, models.Exercise.is_active == True,sqa.or_(models.Exercise.is_default==True,models.Exercise.user_id == current_user.id)).all()
    
    
@router.get("/{exercise_id}", response_model=ExerciseRead)
async def get_exercise(exercise_id: int, db: Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    result = db.query(models.Exercise).filter(models.Exercise.id == exercise_id, models.Exercise.is_active == True,sqa.or_(models.Exercise.is_default==True,models.Exercise.user_id == current_user.id)).first()
    if result is None: 
        raise HTTPException(status_code=404, detail="Exercise not found")
    return result

@router.post("/", status_code=201, response_model=ExerciseRead)
async def add_exercise(exercise: ExerciseCreate, db: Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    new_exercise = models.Exercise(
        name = exercise.name,
        muscle = exercise.muscle,
        is_default = False,
        is_active = True,
        user_id = current_user.id
    )
    db.add(new_exercise)
    db.commit()
    db.refresh(new_exercise)
    return new_exercise

@router.put("/{exercise_id}", response_model=ExerciseRead)
async def update_exercise(exercise_id:int,exercise_shape:ExerciseCreate,db: Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    exercise_record = db.query(models.Exercise).filter(models.Exercise.id == exercise_id, models.Exercise.is_active == True).first()
    if exercise_record is None:
        raise HTTPException(status_code=404,detail="Exercise does not exist")
    if exercise_record.is_default:
        raise HTTPException(status_code=403,detail="Exercise is default")
    if exercise_record.user_id != current_user.id:
        raise HTTPException(status_code=404,detail="Exercise does not exist")
    exercise_record.muscle = exercise_shape.muscle
    exercise_record.name = exercise_shape.name
    db.commit()
    db.refresh(exercise_record)
    return exercise_record
    
@router.delete("/{exercise_id}",status_code=204)
async def delete_exercise(exercise_id:int,db: Session=Depends(get_db),current_user:models.User=Depends(get_current_user)):
    exercise_record = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if exercise_record is None:
        raise HTTPException(status_code=404,detail="Exercise does not exist")
    if exercise_record.is_default:
        raise HTTPException(status_code=403,detail="Exercise is default")
    if exercise_record.user_id != current_user.id:
        raise HTTPException(status_code=404,detail="Exercise does not exist")
    exercise_record.is_active = False
    db.commit()
