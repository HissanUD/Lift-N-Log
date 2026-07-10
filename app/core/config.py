import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL_RAW = os.getenv("DATABASE_URL")
SECRET_KEY_RAW = os.getenv("SECRET_KEY")
ALGORITHM_RAW = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES_RAW = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
BACKEND_CORS_ORIGINS_RAW = os.getenv("BACKEND_CORS_ORIGINS", "")

required_env_vars = {
    "DATABASE_URL": DATABASE_URL_RAW,
    "SECRET_KEY": SECRET_KEY_RAW,
    "ALGORITHM": ALGORITHM_RAW,
    "ACCESS_TOKEN_EXPIRE_MINUTES": ACCESS_TOKEN_EXPIRE_MINUTES_RAW,
}

missing_env_vars = [
    name
    for name, value in required_env_vars.items()
    if value is None
]

if missing_env_vars:
    missing_names = ", ".join(missing_env_vars)
    raise RuntimeError(f"Missing required environment variable(s): {missing_names}")

ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES_RAW)
DATABASE_URL = str(DATABASE_URL_RAW)
ALGORITHM = str(ALGORITHM_RAW)
SECRET_KEY = str(SECRET_KEY_RAW)
BACKEND_CORS_ORIGINS = [
    origin.strip()
    for origin in BACKEND_CORS_ORIGINS_RAW.split(",")
    if origin.strip()
]
