from app.db.database import SessionLocal
import app.db.models as models

default_exercises = [
    {"name": "Bench Press", "muscle": "Chest"},
    {"name": "Incline Bench Press", "muscle": "Chest"},
    {"name": "Dumbbell Bench Press", "muscle": "Chest"},
    {"name": "Chest Fly", "muscle": "Chest"},
    {"name": "Push Up", "muscle": "Chest"},

    {"name": "Pull Up", "muscle": "Back"},
    {"name": "Lat Pulldown", "muscle": "Back"},
    {"name": "Barbell Row", "muscle": "Back"},
    {"name": "Dumbbell Row", "muscle": "Back"},
    {"name": "Seated Cable Row", "muscle": "Back"},

    {"name": "Overhead Press", "muscle": "Shoulders"},
    {"name": "Dumbbell Shoulder Press", "muscle": "Shoulders"},
    {"name": "Lateral Raise", "muscle": "Shoulders"},
    {"name": "Rear Delt Fly", "muscle": "Shoulders"},
    {"name": "Face Pull", "muscle": "Shoulders"},

    {"name": "Bicep Curl", "muscle": "Biceps"},
    {"name": "Hammer Curl", "muscle": "Biceps"},
    {"name": "Preacher Curl", "muscle": "Biceps"},

    {"name": "Tricep Pushdown", "muscle": "Triceps"},
    {"name": "Overhead Tricep Extension", "muscle": "Triceps"},
    {"name": "Close Grip Bench Press", "muscle": "Triceps"},

    {"name": "Squat", "muscle": "Legs"},
    {"name": "Leg Press", "muscle": "Legs"},
    {"name": "Romanian Deadlift", "muscle": "Legs"},
    {"name": "Leg Extension", "muscle": "Legs"},
    {"name": "Leg Curl", "muscle": "Legs"},
    {"name": "Lunge", "muscle": "Legs"},
    {"name": "Calf Raise", "muscle": "Calves"},

    {"name": "Deadlift", "muscle": "Back"},
    {"name": "Hip Thrust", "muscle": "Glutes"},

    {"name": "Plank", "muscle": "Core"},
    {"name": "Crunch", "muscle": "Core"},
    {"name": "Hanging Leg Raise", "muscle": "Core"},
    {"name": "Cable Crunch", "muscle": "Core"},
]

db = SessionLocal()

try:
    for exercise in default_exercises:
        target_exercise = db.query(models.Exercise).filter(models.Exercise.name == exercise["name"]).first()
        if target_exercise is None:
            new_exercise = models.Exercise(
                name = exercise["name"],
                muscle = exercise["muscle"],
                is_default = True,
                is_active = True
            )
            db.add(new_exercise)
        else:
            target_exercise.is_active = True
            target_exercise.is_default = True
            
    db.commit()
finally:
    db.close()
