# --- Stage 1: Builder ---
# This stage installs dependencies and builds the application.
FROM python:3.12-slim as builder

WORKDIR /app

# Install system dependencies needed for building some packages
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

RUN pip install --upgrade pip

COPY requirements.txt .

# Install Python dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# --- Stage 2: Final Image ---
# This is the lean image that will be deployed.
FROM python:3.12-slim

WORKDIR /app

# Create a non-root user for security
RUN useradd --create-home appuser
USER appuser

# Set the PYTHONPATH so Python can find your 'app' module from '/app'
ENV PYTHONPATH="/app"

# Copy the installed Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy the executables (like uvicorn) from the builder stage
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy the application code from the builder stage
COPY --from=builder /app .

EXPOSE 8000

# The command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]