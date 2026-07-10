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

# Copy the start script into the container
COPY start.sh ./
# Give the container permission to execute the script
RUN chmod +x ./start.sh

# Render manages ports automatically via $PORT, so EXPOSE is optional,
# but we run the script to kick off the multi-command sequence
CMD ["./start.sh"]
