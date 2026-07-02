FROM python:3.14-slim
WORKDIR /app

# Installing dependencies
RUN pip install uv
COPY pyproject.toml ./
COPY uv.lock ./
RUN uv sync --frozen

# COPY PROJECT FILES
COPY app/ ./app
COPY alembic.ini ./
COPY alembic/ ./alembic
EXPOSE 8000

# Running the app
CMD ["uv","run","uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
