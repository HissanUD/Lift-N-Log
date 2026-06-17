from fastapi import HTTPException, APIRouter
from app.schemas import WorkoutCreate,WorkoutSetCreate
from app.database import exercises as exercise_list, workouts as workout_list, setlist
from app.utils import get_id

router = APIRouter(prefix="/workouts")

@router.get("/")
async def all_workouts():
    return workout_list

@router.get("/{workout_id}")
async def get_workout(workout_id:int):
    for workout in workout_list:
        if workout["id"] == workout_id:
            return workout
    raise HTTPException(status_code=404,detail="Workout does not exist")

@router.post("/")
async def add_workout(workout:WorkoutCreate):
    new_workout={
        "id": get_id(workout_list),
        "name": workout.name,
        "date": workout.date
    }
    workout_list.append(new_workout)
    
    return new_workout

@router.post("/{workout_id}/sets")
async def add_set(workout_id:int,work_set:WorkoutSetCreate):
    workout_exists = False
    for workout in workout_list:
        if workout["id"] == workout_id:
            workout_exists = True
    if workout_exists == False:
        raise HTTPException(status_code=404, detail="Workout does not exist")
    exercise_exists = False

    for exercise in exercise_list:
        if exercise["id"] == work_set.exercise_id:
            exercise_exists = True

    if exercise_exists == False:
        raise HTTPException(status_code=404, detail="Exercise does not exist")
    
    
    new_set = {
        "id" : get_id(setlist),
        "workout_id" : workout_id,
        "exercise_id": work_set.exercise_id,
        "reps": work_set.reps,
        "weight": work_set.weight
    }
    setlist.append(new_set)
    return new_set

@router.get("/{workout_id}/volume")
async def get_volume(workout_id:int):
    workout_exists = False
    total = 0
    for workout in workout_list:
        if workout["id"] == workout_id:
            workout_exists = True
    if workout_exists == False:
        raise HTTPException(status_code=404,detail="Workout does not exist")
    for set_workout in setlist:
        if set_workout["workout_id"] == workout_id:
            total += set_workout["reps"]*set_workout["weight"]
    return{
        "workout_id":workout_id,
        "total_volume": total
    }


@router.put("/{workout_id}")
async def update_workout(workout_id:int,workout_shape:WorkoutCreate):
    for workout in workout_list:
        if workout["id"] == workout_id:
            workout["name"] = workout_shape.name
            workout["date"] = workout_shape.date
            return workout
    raise HTTPException(status_code=404,detail="Workout does not exist")

@router.delete("/{workout_id}")
async def delete_workout(workout_id:int):
    for workout in workout_list:
        if workout["id"] == workout_id:
            workout_list.remove(workout)
            return workout
    raise HTTPException(status_code=404,detail="Workout does not exist")

@router.delete("/{workout_id}/sets/{set_id}")
async def delete_set(workout_id:int,set_id:int):
    for setpri in setlist:
        if setpri["id"] == set_id and setpri["workout_id"] == workout_id:
            setlist.remove(setpri)
            return setpri
    raise HTTPException(status_code=404,detail="Set does not exist")