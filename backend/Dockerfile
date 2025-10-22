FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME="/opt/poetry" \
    PATH="$POETRY_HOME/bin:$PATH"

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libpq-dev curl git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry --version

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-interaction --no-ansi --no-dev

COPY . /app

EXPOSE 8000

ENV DATABASE_URL="sqlite:///./ranges.db"

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]