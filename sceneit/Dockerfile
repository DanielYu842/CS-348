FROM --platform=$BUILDPLATFORM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies, including PostgreSQL client tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY ./sceneit/requirements.txt /sceneit/requirements.txt
RUN pip install --no-cache-dir -r /sceneit/requirements.txt

# Copy the application code
COPY ./sceneit /app

# Expose the FastAPI default port
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Command to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]