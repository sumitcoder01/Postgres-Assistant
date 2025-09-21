# Step 1: Use an official, lightweight Python image
FROM python:3.12-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Install system dependencies needed to build psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends build-essential

# Step 4: Copy only the requirements file first for layer caching

COPY requirements.txt .

# Step 5: Install the Python dependencies
# Using psycopg2-binary is recommended to avoid the build step, but this works too.
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the entire backend source code from the build context
COPY . .

# Step 7 Set the PYTHONPATH environment variable

ENV PYTHONPATH="/app"

# Step 8: Expose the port the app will run on
EXPOSE 8000

# Step 9: The command to run the application for the CURRENT project
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]