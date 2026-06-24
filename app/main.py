from fastapi import FastAPI
from app.routers import exercises, workouts
from app.database import engine, Base
from app import models

app = FastAPI()

app.include_router(exercises.router)
app.include_router(workouts.router)



@app.get("/")
async def root():
    return {"message": "Gym API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}



