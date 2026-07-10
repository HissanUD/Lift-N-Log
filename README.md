# Lift N Log API

![Backend Tests](https://github.com/HissanUD/Lift-N-Log/actions/workflows/tests.yml/badge.svg)

A FastAPI backend for tracking workouts, exercises, and workout sets. The API supports user registration/login, JWT-protected routes, PostgreSQL persistence, Alembic migrations, default exercise seeding, and an isolated PostgreSQL test database.

This project was built as a backend learning project with a focus on production-style foundations: typed request/response schemas, relational data modeling, authentication, database migrations, service-layer business logic, and automated tests.

## Features

- User registration and login with hashed passwords
- JWT bearer authentication for protected routes
- User-owned workouts and workout sets
- Default exercises seeded into the database
- User-created custom exercises
- Soft delete behavior for custom exercises
- Protection against accessing another user's workouts or custom exercises
- Workout volume calculation
- PostgreSQL database persistence
- Alembic database migrations
- Isolated test database for pytest
- Route and service-layer test coverage
- GitHub Actions CI with PostgreSQL service container
- Docker Compose setup for local API + PostgreSQL
- FastAPI Swagger docs

## Tech Stack

- Python 3.14
- FastAPI
- SQLAlchemy ORM
- PostgreSQL
- Alembic
- Pydantic
- passlib + bcrypt
- python-jose
- pytest
- uv
- GitHub Actions
- Docker

## Project Structure

```text
app/
  core/
    config.py          # environment/config loading
    security.py        # password hashing and JWT creation
  db/
    database.py        # SQLAlchemy engine/session setup
    models.py          # SQLAlchemy ORM models
    seed.py            # default exercise seed data
  routers/
    auth.py            # auth HTTP routes
    exercises.py       # exercise HTTP routes
    workouts.py        # workout and set HTTP routes
  services/
    auth_service.py     # registration/login business logic
    exercise_service.py # exercise business logic
    workout_service.py  # workout and set business logic
  dependencies.py      # auth/current-user dependencies
  errors.py            # service-layer exceptions
  main.py              # FastAPI app entrypoint
  schemas.py           # Pydantic request/response models
tests/
  conftest.py
  test_auth.py
  test_exercises.py
  test_services.py
  test_workouts.py
alembic/
  versions/
```

## API Overview

Authentication:

```text
POST /auth/register
POST /auth/login
GET  /auth/me
```

Exercises:

```text
GET    /exercises/
GET    /exercises/{exercise_id}
POST   /exercises/
PUT    /exercises/{exercise_id}
DELETE /exercises/{exercise_id}
```

Workouts:

```text
GET    /workouts/
GET    /workouts/{workout_id}
POST   /workouts/
PUT    /workouts/{workout_id}
DELETE /workouts/{workout_id}
GET    /workouts/{workout_id}/volume
```

Workout sets:

```text
POST   /workouts/{workout_id}/sets
GET    /workouts/{workout_id}/sets
GET    /workouts/{workout_id}/sets/{set_id}
DELETE /workouts/{workout_id}/sets/{set_id}
```

## Local Setup

Clone the repository:

```bash
git clone https://github.com/HissanUD/Lift-N-Log.git
cd Lift-N-Log
```

Install dependencies:

```bash
uv sync
```

Create a local environment file:

```bash
cp .env.example .env
```

Update `.env` with your own PostgreSQL credentials:

```env
DATABASE_URL=postgresql://gym_user:password@localhost:5432/gym_api_db
TEST_DATABASE_URL=postgresql://gym_user:password@localhost:5432/gym_api_test_db
SECRET_KEY=replace-me-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

If your database password contains special characters, URL-encode it inside the database URLs.

## Database Setup

Create the development and test databases in PostgreSQL:

```bash
createdb gym_api_db
createdb gym_api_test_db
```

Run migrations:

```bash
uv run alembic upgrade head
```

Seed the default exercise list:

```bash
uv run python -m app.seed
```

## Running the App

Start the development server:

```bash
uv run fastapi dev app/main.py
```

Open the API docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
GET /health
```

## Running With Docker

The project includes a Dockerfile and Docker Compose setup for running the API with a PostgreSQL container.

Start the API and database:

```bash
docker compose up --build
```

This will:

- build the FastAPI image
- start a PostgreSQL 16 container
- wait for PostgreSQL to become healthy
- run Alembic migrations
- seed the default exercise list
- start Uvicorn on port 8000

API docs:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

Docker PostgreSQL connection for DBeaver or another database client:

```text
Host: localhost
Port: 5433
Database: gym_api_db
Username: gym_user
Password: password
```

Stop the containers:

```bash
docker compose down
```

Stop the containers and delete the Docker database volume:

```bash
docker compose down -v
```

Use `down -v` only when you want to wipe the Docker PostgreSQL data.

## Running Tests

The test suite uses `TEST_DATABASE_URL`, not the development database.

Run all tests:

```bash
uv run python -m pytest
```

Run tests with coverage:

```bash
uv run python -m pytest --cov=app --cov-report=term-missing
```

Current coverage includes:

- registration and login flows
- auth, exercise, and workout service behavior
- JWT-protected routes
- current user lookup
- exercise ownership and default exercise rules
- workout ownership
- workout set creation/deletion
- workout volume calculation
- invalid request body cases

## Continuous Integration

GitHub Actions runs the backend test suite on every push and pull request.

The CI workflow:

- starts a temporary PostgreSQL service container
- installs Python and uv
- installs project dependencies
- runs Alembic migrations
- runs the pytest suite

The workflow uses CI-only environment variables and does not depend on local `.env` values.

## Authentication Flow

1. A user registers with an email, display name, and password.
2. The password is hashed before storage.
3. The user logs in with email/password.
4. The API returns a JWT bearer token.
5. Protected routes require:

```text
Authorization: Bearer <token>
```

The token contains the user's ID in the JWT `sub` claim. Protected routes decode the token, load the user from the database, and use that user for ownership checks.

## Notes

- `.env` is intentionally ignored and should never be committed.
- `.env.example` contains only placeholder values.
- The project currently uses first-party username/password authentication for learning purposes.
- The API is backend-only; no frontend is included yet.

## Future Improvements

- Refresh tokens and logout/token invalidation
- Password reset and email verification
- More detailed progress/statistics endpoints
- Frontend client
