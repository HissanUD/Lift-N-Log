from app.db.database import Base
import sqlalchemy as sqa
import sqlalchemy.orm as sqorm

class Exercise(Base):
    __tablename__ = "exercises"
    id =  sqa.Column(sqa.Integer,primary_key=True,index=True)
    name = sqa.Column(sqa.String,nullable=False)
    muscle = sqa.Column(sqa.String,nullable=False)
    is_default = sqa.Column(sqa.Boolean,nullable=False, default=False, server_default=sqa.false())
    is_active = sqa.Column(sqa.Boolean,nullable=False, default=True, server_default=sqa.true())
    sets = sqorm.relationship("WorkoutSet",back_populates="exercise")
    user_id = sqa.Column(sqa.Integer,sqa.ForeignKey("users.id"),nullable=True)
    user = sqorm.relationship("User",back_populates="exercises")
    
    
class Workout(Base):
    __tablename__ = "workouts"
    id = sqa.Column(sqa.Integer,primary_key=True,index=True)
    name = sqa.Column(sqa.String,nullable=False)
    date = sqa.Column(sqa.Date,nullable=False)
    sets = sqorm.relationship("WorkoutSet",back_populates="workout")
    user_id = sqa.Column(sqa.Integer,sqa.ForeignKey("users.id"),nullable=False)
    user = sqorm.relationship("User",back_populates="workouts")
    
class WorkoutSet(Base):
    __tablename__ = "workout_sets"
    id = sqa.Column(sqa.Integer,primary_key=True,index=True)
    workout_id = sqa.Column(sqa.Integer,sqa.ForeignKey("workouts.id"),nullable=False)
    exercise_id = sqa.Column(sqa.Integer,sqa.ForeignKey("exercises.id"),nullable=False)
    reps = sqa.Column(sqa.Integer,nullable=False)
    weight= sqa.Column(sqa.Float,nullable=False)
    workout = sqorm.relationship("Workout", back_populates="sets")
    exercise = sqorm.relationship("Exercise",back_populates="sets")
    
class User(Base):
    __tablename__ = "users"
    id = sqa.Column(sqa.Integer,primary_key=True,index=True)
    user_name = sqa.Column(sqa.String,nullable=False)
    email = sqa.Column(sqa.String,nullable=False,unique=True,index=True)
    hashed_password = sqa.Column(sqa.String,nullable=True)
    created_at = sqa.Column(sqa.DateTime,nullable=False, server_default=sqa.func.now())
    is_active = sqa.Column(sqa.Boolean,nullable=False, default=True, server_default=sqa.true())
    auth_provider = sqa.Column(sqa.String,nullable=False, default="local", server_default="local")
    provider_subject = sqa.Column(sqa.String,nullable=True)
    workouts = sqorm.relationship("Workout",back_populates="user")
    exercises = sqorm.relationship("Exercise",back_populates="user")
