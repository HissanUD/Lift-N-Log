from pydantic import BaseModel, Field


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1)
    muscle: str = Field(min_length=1)
    
class WorkoutCreate(BaseModel):
    name: str = Field(min_length=1)
    date: str = Field(min_length=1)
    
class WorkoutSetCreate(BaseModel):
    exercise_id: int = Field(gt=0)
    reps: int = Field(gt=0)
    weight: float = Field(ge=0)