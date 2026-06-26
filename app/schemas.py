from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import date


class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1)
    muscle: str = Field(min_length=1)
    
class WorkoutCreate(BaseModel):
    name: str = Field(min_length=1)
    date: date
    
class WorkoutSetCreate(BaseModel):
    exercise_id: int = Field(gt=0)
    reps: int = Field(gt=0)
    weight: float = Field(ge=0)
    
class WorkoutRead(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    date: date
    user_id: int = Field(gt=0)


class ExerciseRead(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int =Field(gt=0)
    name: str = Field(min_length=1)
    muscle: str = Field(min_length=1)
    is_default: bool
    is_active: bool
    user_id: int | None
    
class WorkoutSetRead(BaseModel):
    
    model_config = ConfigDict(from_attributes=True)
    
    workout_id: int =Field(gt=0)
    id: int =Field(gt=0)
    exercise_id: int =Field(gt=0)
    reps: int =Field(gt=0)
    weight: float = Field(ge=0)
    

class WorkoutSetDetailedRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int =Field(gt=0)
    workout_id: int =Field(gt=0)
    exercise_id: int =Field(gt=0)
    reps: int =Field(gt=0)
    weight: float = Field(ge=0)
    exercise: ExerciseRead
    
class WorkoutDetailedRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(gt=0)
    name: str = Field(min_length=1)
    date: date
    user_id: int = Field(gt=0)
    sets : list[WorkoutSetDetailedRead]
    
class UserCreate(BaseModel):
    
    user_name: str = Field(min_length=1)
    email: EmailStr 
    password: str = Field(min_length=8)
    
class UserRead(BaseModel):
    model_config= ConfigDict(from_attributes=True)
    
    id: int =Field(gt=0)
    user_name: str = Field(min_length=1)
    email: EmailStr
    is_active: bool
    auth_provider: str= Field(min_length=1)
    
class Token(BaseModel):

    access_token: str = Field(min_length=1)
    token_type: str = Field(min_length=1)
    
class UserLogin(BaseModel):

    email: EmailStr 
    password: str = Field(min_length=8)
    

    
