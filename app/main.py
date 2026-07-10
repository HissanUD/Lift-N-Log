from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import exercises, workouts, auth
from app.core.config import BACKEND_CORS_ORIGINS

app = FastAPI()


if BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router)
app.include_router(exercises.router)
app.include_router(workouts.router)


@app.get("/")
async def root():
    return {"message": "Gym API is running"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
