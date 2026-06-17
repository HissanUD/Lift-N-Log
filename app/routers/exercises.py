from fastapi import HTTPException, APIRouter
from app.schemas import ExerciseCreate
from app.database import exercises
from app.utils import get_id

router = APIRouter(prefix="/exercises")

@router.get("/")
async def all_exercises(muscle: str | None = None):
    if muscle is None:
        return exercises
    matching_exercises = []
    
    for exercise in exercises:
        if exercise["muscle"] == muscle:
            matching_exercises.append(exercise)
    return matching_exercises

@router.get("/{exercise_id}")
async def get_exercise(exercise_id: int):
    for exercise in exercises:
        if exercise["id"] == exercise_id:
            return exercise
    raise HTTPException(status_code=404, detail="Exercise not found")

@router.post("/")
async def add_exercise(exercise: ExerciseCreate):
    new_exercise={
        "id": get_id(exercises),
        "name": exercise.name,
        "muscle": exercise.muscle
    }
    
    exercises.append(new_exercise)
    
    return new_exercise

@router.put("/{exercise_id}")
async def update_exercise(exercise_id:int,exercise_shape:ExerciseCreate):
    for exercise in exercises:
        if exercise["id"] == exercise_id:
            exercise["name"] = exercise_shape.name
            exercise["muscle"] = exercise_shape.muscle
            return exercise
    raise HTTPException(status_code=404,detail="Exercise does not exist")

@router.delete("/{exercise_id}")
async def delete_exercise(exercise_id:int):
    for exercise in exercises:
        if exercise["id"] == exercise_id:
            exercises.remove(exercise)
            return exercise
    raise HTTPException(status_code=404,detail="Exercise does not exist")