from fastapi import HTTPException, APIRouter, Depends
from app.schemas import WorkoutCreate,WorkoutSetCreate, WorkoutRead, WorkoutSetRead, WorkoutDetailedRead, WorkoutSetDetailedRead
import sqlalchemy as sqa
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.dependencies import get_current_user

router = APIRouter(prefix="/workouts",tags=["workouts"])

@router.get("/", response_model=list[WorkoutRead])
async def all_workouts(db: Session=Depends(get_db), current_user:models.User=Depends(get_current_user)):
    query = db.query(models.Workout).filter(models.Workout.user_id == current_user.id).all()
    return query

@router.get("/{workout_id}",response_model=WorkoutDetailedRead)
async def get_workout(workout_id:int,db: Session=Depends(get_db), current_user:models.User=Depends(get_current_user)):
    result = db.query(models.Workout).filter(models.Workout.id == workout_id, models.Workout.user_id == current_user.id).first()
    if result is None:
        raise HTTPException(status_code=404,detail="Workout does not exist")
    return result
    
@router.post("/",status_code=201,response_model=WorkoutRead)
async def add_workout(workout:WorkoutCreate,db:Session=Depends(get_db), current_user:models.User=Depends(get_current_user)):
    new_workout= models.Workout(
        name = workout.name,
        date = workout.date,
        user_id = current_user.id
    )
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)
    return new_workout
    

@router.post("/{workout_id}/sets",status_code=201, response_model=WorkoutSetRead)
async def add_set(workout_id:int,work_set:WorkoutSetCreate,db:Session=Depends(get_db), current_user:models.User=Depends(get_current_user)):
    target_workout = db.query(models.Workout).filter(models.Workout.id == workout_id, models.Workout.user_id == current_user.id).first()
    target_exercise = db.query(models.Exercise).filter(
        models.Exercise.id == work_set.exercise_id,
        models.Exercise.is_active == True,
        sqa.or_(models.Exercise.is_default == True, models.Exercise.user_id == current_user.id)
    ).first()
    if target_workout is None:
        raise HTTPException(status_code=404, detail= "The selected workout does not exist")
    if target_exercise is None:
        raise HTTPException(status_code=404, detail= "The selected exercise does not exist")
    
    new_set = models.WorkoutSet(
        workout_id = workout_id,
        exercise_id = work_set.exercise_id,
        reps = work_set.reps,
        weight = work_set.weight
    )
    db.add(new_set)
    db.commit()
    db.refresh(new_set)
    return new_set

    
@router.get("/{workout_id}/volume")
async def get_volume(workout_id:int, db:Session=Depends(get_db), current_user:models.User=Depends(get_current_user)):
    target_workout = db.query(models.Workout).filter(models.Workout.id == workout_id, models.Workout.user_id == current_user.id).first()
    if target_workout is None:
        raise HTTPException(status_code=404,detail="Workout does not exist")
    workout_sets = db.query(models.WorkoutSet).filter(models.WorkoutSet.workout_id == workout_id).all()
    volume = 0.0
    for workout_set in workout_sets:
        volume += workout_set.reps * workout_set.weight
    return volume
        


@router.put("/{workout_id}",response_model=WorkoutRead)
async def update_workout(workout_id:int,workout_shape:WorkoutCreate,db:Session=Depends(get_db), current_user:models.User=Depends(get_current_user)):
    target_workout = db.query(models.Workout).filter(models.Workout.id == workout_id, models.Workout.user_id == current_user.id).first()
    if target_workout is None:
        raise HTTPException(status_code=404,detail="Workout does not exist")
    target_workout.name = workout_shape.name
    target_workout.date = workout_shape.date
    db.commit()
    db.refresh(target_workout)
    return target_workout

@router.delete("/{workout_id}",status_code=204)
async def delete_workout(workout_id:int,db:Session=Depends(get_db), current_user:models.User=Depends(get_current_user)):
    target_workout = db.query(models.Workout).filter(models.Workout.id == workout_id, models.Workout.user_id == current_user.id).first()
    if target_workout is None:
        raise HTTPException(status_code=404,detail="Workout does not exist")
    setlist = db.query(models.WorkoutSet).filter(models.WorkoutSet.workout_id == workout_id).all()
    for workout_set in setlist:
      db.delete(workout_set)
    db.delete(target_workout)
    db.commit()

@router.delete("/{workout_id}/sets/{set_id}",status_code=204)
async def delete_set(workout_id:int,set_id:int,db:Session=Depends(get_db), current_user:models.User=Depends(get_current_user)):
    target_workout = db.query(models.Workout).filter(models.Workout.id == workout_id, models.Workout.user_id == current_user.id).first()
    target_set = db.query(models.WorkoutSet).filter(models.WorkoutSet.workout_id == workout_id, models.WorkoutSet.id == set_id).first()
    if target_workout is None:
        raise HTTPException(status_code=404, detail= "The selected workout does not exist")
    if target_set is None:
        raise HTTPException(status_code=404, detail= "The selected set does not exist")
    db.delete(target_set)
    db.commit()
    

@router.get("/{workout_id}/sets",response_model=list[WorkoutSetRead])
async def get_all_sets(workout_id: int, db:Session=Depends(get_db), current_user:models.User=Depends(get_current_user)):
    target_workout = db.query(models.Workout).filter(models.Workout.id == workout_id, models.Workout.user_id == current_user.id).first()
    if target_workout is None:
        raise HTTPException(status_code=404,detail="Workout does not exist")
    setlist = db.query(models.WorkoutSet).filter(models.WorkoutSet.workout_id == workout_id).all()
    return setlist
    

@router.get("/{workout_id}/sets/{set_id}",response_model=WorkoutSetDetailedRead)
async def get_set(workout_id: int, set_id: int, db:Session=Depends(get_db), current_user:models.User=Depends(get_current_user)):
    target_workout = db.query(models.Workout).filter(models.Workout.id == workout_id, models.Workout.user_id == current_user.id).first()
    if target_workout is None:
        raise HTTPException(status_code=404,detail="Workout does not exist")
    setlist = db.query(models.WorkoutSet).filter(models.WorkoutSet.workout_id == workout_id, models.WorkoutSet.id == set_id).first()
    if setlist is None:
        raise HTTPException(status_code=404,detail="Workout Set does not exist")
    return setlist
    
