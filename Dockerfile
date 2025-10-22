FROM  python:3.11-slim

# Set working directory
WORKDIR /app
# Install dependencies
RUN poetry config virtualenvs.create false \
    && pip install poetry \
    && poetry install --no-dev
# Copy application code
COPY . /app
# Expose port
EXPOSE 8000

RUN poetry install --no-dev
# Command to run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", ]